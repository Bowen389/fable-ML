"""Whale 监控覆盖度自检。

回答三个问题，避免"看着像没动作、其实根本没扫"：
1. 监控商品清单有多旧？（TOP30 快照 + 显式白名单）
2. 鲸鱼池多大、一轮扫几只、多久轮转一圈？
3. 每个标的最近一次事件是什么时候？覆盖新鲜度如何？

只读本地状态文件，不调用任何外部接口，不改动任何数据。
"""
import argparse, json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATE = ROOT / 'state/whale_monitor'
TZ = timezone(timedelta(hours=8))
WATCH_STALE_DAYS = 3          # 监控商品清单超过这个天数没更新就告警
ROTATION_WARN_DAYS = 10       # 池子轮转周期超过这个天数就告警
ITEM_STALE_DAYS = 7           # 标的超过这个天数没有新事件就告警


def readjson(path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8-sig'))
    except (OSError, ValueError):
        return default


def age_days(moment, now):
    return round((now - moment).total_seconds() / 86400, 2)


def parse_dt(text):
    if not text:
        return None
    try:
        dt = datetime.fromisoformat(str(text).replace('Z', '+00:00'))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=TZ)


def watch_list(state, now):
    """监控商品清单：TOP30 快照 + 显式白名单。"""
    raw = readjson(state / 'data/top30_latest.json', [])
    top = raw.get('goods', []) if isinstance(raw, dict) else (raw or [])
    extra_raw = readjson(state / 'data/extra_goods.json', None)
    if isinstance(extra_raw, dict):
        extra = extra_raw.get('goods', [])
    else:
        extra = extra_raw or []
    snapshot_path = state / 'data/top30_latest.json'
    snapshot_age_days = None
    snapshot_stamp = parse_dt(raw.get('generated_at')) if isinstance(raw, dict) else None
    if snapshot_stamp:
        snapshot_age_days = age_days(snapshot_stamp, now)
    elif snapshot_path.exists():
        snapshot_age_days = round((now.timestamp() - snapshot_path.stat().st_mtime) / 86400, 2)
    extra_updated = None
    if isinstance(extra_raw, dict):
        extra_updated = parse_dt(extra_raw.get('updated_at'))
    return {
        'monitored_goods': len(top),
        'extra_goods': len(extra),
        'total_goods': len(top) + len(extra),
        'top30_snapshot_age_days': snapshot_age_days,
        'top30_snapshot_generated_at': snapshot_stamp.isoformat() if snapshot_stamp else None,
        'extra_goods_updated_at': extra_updated.isoformat() if extra_updated else None,
        'extra_goods_age_days': age_days(extra_updated, now) if extra_updated else None,
        'has_whitelist': bool(extra),
    }


def pool_stats(state, now, max_whales_per_round):
    """鲸鱼池规模与轮转周期。"""
    pool = readjson(state / 'data/whales_monitor_pool.json', {}) or {}
    snaps = readjson(state / 'data/whale_snapshots.json', {}) or {}
    last = snaps.get('last_success_scan', {}) or {}
    ages = []
    for value in last.values():
        dt = parse_dt(value)
        if dt:
            ages.append(age_days(dt, now))
    ages.sort()
    size = len(pool)
    rotation = round(size / max_whales_per_round, 2) if max_whales_per_round else None
    return {
        'size': size,
        'scanned_whales': len(last),
        'newest_scan': max(last.values()) if last else None,
        'oldest_scan': min(last.values()) if last else None,
        'median_scan_age_days': ages[len(ages) // 2] if ages else None,
        'max_whales_per_round': max_whales_per_round,
        'estimated_rotation_days': rotation,
    }


def item_freshness(state, now, top_items=20):
    """标的级覆盖新鲜度：每只鲸鱼每条记录的标的 -> 最近事件时间。"""
    snaps = readjson(state / 'data/whale_snapshots.json', {}) or {}
    per_item = {}
    for steam_id, inventory in (snaps.get('whales') or {}).items():
        for key in inventory:
            parts = key.split('\x01')
            if len(parts) < 3:
                continue
            item, good_id, when = parts[0], parts[1], parts[2]
            slot = per_item.setdefault(item, {'good_id': good_id, 'whales': set(), 'latest': None})
            slot['whales'].add(steam_id)
            dt = parse_dt(when)
            if dt and (slot['latest'] is None or dt > slot['latest']):
                slot['latest'] = dt
    rows = []
    for item, slot in per_item.items():
        rows.append({
            'item': item,
            'good_id': slot['good_id'],
            'whales': len(slot['whales']),
            'latest_event': slot['latest'].isoformat() if slot['latest'] else None,
            'age_days': age_days(slot['latest'], now) if slot['latest'] else None,
        })
    rows.sort(key=lambda r: (-r['whales'], r['item']))
    return rows[:top_items], len(rows)


def audit(root=ROOT, top_items=20):
    now = datetime.now(TZ)
    state = Path(root) / 'state/whale_monitor'
    max_whales = int(readjson(state / 'data/scan_limits.json', {}).get('max_whales_per_round', 80) or 80)
    watch = watch_list(state, now)
    pool = pool_stats(state, now, max_whales)
    items, item_count = item_freshness(state, now, top_items)
    alerts = []

    if not watch['has_whitelist']:
        alerts.append('没有显式监控白名单（state/whale_monitor/data/extra_goods.json）；'
                      '监控范围完全依赖 TOP30 快照，新品无法自动进入鲸鱼池。')
    elif watch['extra_goods_age_days'] is not None and watch['extra_goods_age_days'] > WATCH_STALE_DAYS:
        alerts.append(f"监控白名单已 {watch['extra_goods_age_days']} 天没更新。")
    if watch['top30_snapshot_age_days'] is not None and watch['top30_snapshot_age_days'] > WATCH_STALE_DAYS:
        alerts.append(f"TOP30 快照已 {watch['top30_snapshot_age_days']} 天未刷新（git checkout 会重置文件 mtime，"
                      f"进程内 age 判定永远为 0，浏览器抓取不会触发）。")

    watch_goods = {str(s.get('good_id')) for v in (readjson(state / 'data/whales_monitor_pool.json', {}) or {}).values()
                   for s in v.get('sources', []) if isinstance(s, dict)}
    covered = {r['good_id'] for r in items}
    if watch_goods and not (watch_goods & covered):
        alerts.append('监控清单里的商品在快照中一条记录都没有：可能还没跑过实采，或 good_id 不匹配。')

    if pool['estimated_rotation_days'] and pool['estimated_rotation_days'] > ROTATION_WARN_DAYS:
        alerts.append(f"鲸鱼池 {pool['size']} 只、每轮 {max_whales} 只，轮转周期约 {pool['estimated_rotation_days']} 天；"
                      f"单只鲸鱼的“最近”可能已经过去这么久。")
    for row in items:
        if row['age_days'] is not None and row['age_days'] > ITEM_STALE_DAYS:
            alerts.append(f"标的 {row['item']} 最近一次事件在 {row['age_days']} 天前（{row['whales']} 只鲸鱼有记录）。")

    status = 'ok' if not alerts else ('missing' if not watch['has_whitelist'] else 'degraded')
    return {
        'generated_at': now.isoformat(),
        'status': status,
        'watch_list': watch,
        'pool': pool,
        'items': items,
        'item_count': item_count,
        'alerts': alerts,
        'basis': '只读本地状态；CD_RECOVER 为回库事件，不是成交确认。',
    }


def render(result):
    watch, pool = result['watch_list'], result['pool']
    lines = ['# Whale 监控覆盖度自检', '', f"生成时间：{result['generated_at']}", '',
             f"状态：{result['status']}", '',
             '## 监控商品清单', '',
             f"- TOP30 快照商品：{watch['monitored_goods']} 个（快照文件已 {watch['top30_snapshot_age_days']} 天）",
             f"- 显式白名单商品：{watch['extra_goods']} 个"
             + (f"（{watch['extra_goods_age_days']} 天前更新）" if watch['extra_goods_age_days'] is not None else ''),
             f"- 合计主动监控：{watch['total_goods']} 个 good_id", '',
             '## 鲸鱼池与轮转', '',
             f"- 池规模：{pool['size']} 只；已成功扫描 {pool['scanned_whales']} 只",
             f"- 每轮扫描上限：{pool['max_whales_per_round']} 只 → 全池轮转约 {pool['estimated_rotation_days']} 天",
             f"- 单只鲸鱼末次扫描：最新 {str(pool['newest_scan'])[:16]}，最旧 {str(pool['oldest_scan'])[:16]}，"
             f"中位滞后 {pool['median_scan_age_days']} 天", '',
             '## 标的级覆盖新鲜度（前 20）', '',
             '| 标的 | good_id | 鲸鱼数 | 最近事件 | 滞后天数 |', '|---|---|---|---|---|']
    for row in result['items']:
        item = str(row['item']).replace('|', '/')
        lines.append(f"| {item} | {row['good_id']} | {row['whales']} | {str(row['latest_event'])[:16]} | {row['age_days']} |")
    if result['alerts']:
        lines += ['', '## 告警', '']
        lines += [f"- {a}" for a in result['alerts']]
    else:
        lines += ['', '无告警。']
    return '\n'.join(lines) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', action='store_true', help='输出 JSON 而不是文字报告')
    ap.add_argument('--out', default=str(ROOT / 'output/whale_coverage.json'))
    ap.add_argument('--top-items', type=int, default=20)
    args = ap.parse_args()
    result = audit(ROOT, args.top_items)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else render(result), flush=True)


if __name__ == '__main__':
    main()
