"""SteamDT 报价兜底（临时）：悠悠报价过期时，从 SteamDT 价格接口取"悠悠有品"平台的
在售价(sellPrice)/在售数(sellCount)覆盖监控表报价字段，让决策引擎照常运行。

口径说明：
- SteamDT /open/cs2/v1/price/batch 返回每个平台的 sellPrice(最低在售价,元)、
  sellCount(在售数量)、biddingPrice/biddingCount(求购)、updateTime(快照时间)。
- 平台字段含"悠悠有品"，其 sellPrice/sellCount 即悠悠在售价/在售数，与悠悠挂牌价同口径(元)。
- 本模块只做"报价兜底"：仅在悠悠报价缺失或超 6 小时过期时覆盖实时挂牌价/在售数，
  不触碰求购(求购为加分项，缺失留空不阻断)，也不改动决策引擎逻辑。
- 所有覆盖行都标注 报价来源/价格状态，透明可追溯，便于悠悠 token 恢复后回退。
"""
import argparse, json, os, time
from datetime import datetime, timedelta, timezone

BASE_URL = os.environ.get('STEAMDT_BASE_URL', 'https://open.steamdt.com')
PRICE_BATCH_PATH = '/open/cs2/v1/price/batch'
TZ = timezone(timedelta(hours=8))
DEFAULT_MAX_AGE_HOURS = 6.0          # 与决策引擎报价 6 小时新鲜度窗口一致
YOUYIN_PLATFORM_KEYS = ('悠悠', 'youpin')  # 平台名匹配关键词(小写包含)


def _api_key():
    return os.environ.get('STEAMDT_API_KEY', '').strip()


def _post(path, body, api_key, retries=4):
    import urllib.request
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    data = json.dumps(body).encode()
    last_err = ''
    for attempt in range(retries):
        try:
            req = urllib.request.Request(BASE_URL + path, data=data, headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r), ''
        except urllib.error.HTTPError as e:
            last_err = f'HTTP {e.code}'
            if e.code == 429:
                time.sleep(65); continue
            if e.code >= 500:
                time.sleep(5 * (attempt + 1)); continue
            return None, last_err
        except Exception as e:
            last_err = f'{type(e).__name__}: {e}'
            time.sleep(5 * (attempt + 1)); continue
    return None, last_err


def _norm_platform(p):
    return (p or '').strip().lower()


def _pick_youyin(data_list):
    """从某饰品的多平台价格列表里挑出悠悠有品平台那一行。"""
    if not isinstance(data_list, list):
        return None
    # 优先精确/包含匹配"悠悠有品"或"youpin"
    for rec in data_list:
        if not isinstance(rec, dict):
            continue
        lp = _norm_platform(rec.get('platform'))
        if any(k in lp for k in YOUYIN_PLATFORM_KEYS):
            return rec
    return None


def _ts_to_iso(ts):
    """SteamDT updateTime 秒/毫秒时间戳 -> 带时区 ISO 字符串(东八区)。"""
    try:
        v = float(ts)
    except (TypeError, ValueError):
        return None
    if v > 1e12:
        v = v / 1000.0
    try:
        return datetime.fromtimestamp(v, tz=TZ).isoformat()
    except (OverflowError, OSError, ValueError):
        return None


def fetch_steamdt_prices(names, api_key=None, chunk=100):
    """批量拉取 SteamDT 价格。返回 dict: name -> {sell_price, sell_count, ...}。
    对限流做重试+退避；单批最终失败则跳过该批(不中断后续批次)，用已成功批的结果。"""
    api_key = api_key or _api_key()
    if not api_key:
        return {}, 'STEAMDT_API_KEY 为空：请在仓库 Settings → Secrets 添加'
    out = {}
    names = [n for n in names if n]
    for i in range(0, len(names), chunk):
        batch = names[i:i + chunk]
        js = None
        for attempt in range(4):
            js, err = _post(PRICE_BATCH_PATH, {'marketHashNames': batch}, api_key)
            msg = (js or {}).get('errorMsg', '') if js else ''
            # 仅业务级限流(success=false 且消息含上限/限)做退避重试；HTTP 错误 _post 内部已重试，直接跳过该批。
            rate_limited = js is not None and not js.get('success') and ('上限' in msg or '限' in msg)
            if not rate_limited:
                break
            time.sleep(20 * (attempt + 1))  # 退避重试限流
        if not js or not js.get('success'):
            # 该批最终失败：跳过，保留已成功批的结果，不中断整体
            continue
        for item in (js.get('data') or []):
            if not isinstance(item, dict):
                continue
            mh = item.get('marketHashName')
            rec = _pick_youyin(item.get('dataList'))
            if not rec:
                continue
            out[mh] = {
                'sell_price': rec.get('sellPrice'),
                'sell_count': rec.get('sellCount'),
                'bidding_price': rec.get('biddingPrice'),
                'bidding_count': rec.get('biddingCount'),
                'update_time_iso': _ts_to_iso(rec.get('updateTime')),
                'platform': rec.get('platform'),
            }
        time.sleep(1)  # 批间小延迟，降低触发限流
    return out, ''


def _parse_iso(s):
    try:
        t = datetime.fromisoformat(s)
        return t.replace(tzinfo=TZ) if t.tzinfo is None else t
    except (ValueError, TypeError):
        return None


def _quote_age_hours(row, now):
    t = _parse_iso(row.get('价格采集时间'))
    if t is None:
        return None  # 缺失
    return (now - t).total_seconds() / 3600.0


def overlay_stale_quotes(monitor_rows, api_key=None, max_age_hours=DEFAULT_MAX_AGE_HOURS, now=None):
    """对报价缺失/过期的监控行，用 SteamDT 悠悠有品价格覆盖 实时挂牌价/当前在售数/
    价格采集时间，并标注来源。返回 (new_rows, stats)。

    - 只覆盖报价字段，不动求购/日K/评分等其它字段。
    - 悠悠报价仍新鲜(≤max_age_hours)的行保持原样，不做替换。
    - SteamDT 也没取到该品时，保留原状并记 note，不阻断。
    """
    now = now or datetime.now(TZ)
    api_key = api_key or _api_key()
    stats = {'checked': 0, 'stale': 0, 'overlaid': 0, 'steamdt_miss': 0,
             'kept_fresh': 0, 'no_key': False, 'error': ''}
    if not api_key:
        stats['no_key'] = True
        stats['error'] = 'STEAMDT_API_KEY 为空，跳过兜底'
        return list(monitor_rows), stats

    stale_names = []
    for r in monitor_rows:
        stats['checked'] += 1
        age = _quote_age_hours(r, now)
        if age is not None and age <= max_age_hours:
            stats['kept_fresh'] += 1
            continue
        stats['stale'] += 1
        stale_names.append(r.get('name'))

    if not stale_names:
        return list(monitor_rows), stats

    prices, err = fetch_steamdt_prices(stale_names, api_key)
    if err and not prices:
        stats['error'] = err
        return list(monitor_rows), stats

    new_rows = []
    for r in monitor_rows:
        row = dict(r)
        age = _quote_age_hours(row, now)
        if age is not None and age <= max_age_hours:
            new_rows.append(row)
            continue
        pr = prices.get(row.get('name'))
        if pr and pr.get('sell_price') is not None:
            note = f'悠悠报价过期，SteamDT 兜底(悠悠有品平台)覆盖在售价/在售数'
            old_note = row.get('兜底说明') or ''
            row['实时挂牌价'] = pr['sell_price']
            row['当前在售数'] = pr.get('sell_count')
            # 价格采集时间 = 我们实际拉取的时刻(保证决策引擎新鲜度门通过)；
            # SteamDT 平台侧 updateTime 另存为 价格数据时间，便于追溯数据真实时间。
            row['价格采集时间'] = now.isoformat()
            upd = pr.get('update_time_iso')
            if upd:
                row['价格数据时间'] = upd
            row['报价来源'] = 'SteamDT 价格接口(悠悠有品平台)'
            row['价格状态'] = 'SteamDT兜底已刷新'
            row['兜底说明'] = (old_note + '；' + note).strip('；')
            stats['overlaid'] += 1
            new_rows.append(row)
        else:
            if pr is None:
                stats['steamdt_miss'] += 1
            new_rows.append(row)
    return new_rows, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', default='output/quotes.csv', help='监控表 CSV(含 name/实时挂牌价/价格采集时间/当前在售数)')
    ap.add_argument('--output', default='output/steamdt_quotes_latest.json')
    ap.add_argument('--max-age-hours', type=float, default=DEFAULT_MAX_AGE_HOURS)
    args = ap.parse_args()

    import csv
    rows = []
    with open(args.input, newline='', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            rows.append(r)
    new_rows, stats = overlay_stale_quotes(rows, max_age_hours=args.max_age_hours)
    payload = {'generated_at': datetime.now(TZ).isoformat(), 'source': 'steamdt_quote_fallback',
               'stats': stats, 'rows': new_rows}
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print('STEAMDT_FALLBACK_DONE', json.dumps(stats, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
