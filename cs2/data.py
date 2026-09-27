# -*- coding: utf-8 -*-
"""SteamDT 开放平台取数 + 本地 K 线仓库（按月 CSV，便于 git 增量提交）"""
import os, glob, time, json
import numpy as np, pandas as pd, requests
from . import config as C

BASE_URL = 'https://open.steamdt.com'
KLINE_PATH = '/open/cs2/item/v1/kline'      # POST {marketHashName, type, platform}
KLINE_TYPE = 2                              # 文档：1=时K, 2=日K, 3=周K
BROAD_PATH = '/open/cs2/broad/v1/kline'     # POST {type}
BASE_INFO_PATH = '/open/cs2/v1/base'        # GET, 每日仅 1 次
BAR_COLS = ['name', 'date', 'open', 'close', 'high', 'low', 'fetched']
UNIVERSE_PATH = C.P('universe.csv')
ERR_PATH = C.P('data', 'fetch_errors.csv')
LOG = print


class _Limiter:
    def __init__(self, per_minute):
        self.gap = 60.0 / per_minute; self.t = 0.0
    def wait(self):
        d = self.gap - (time.time() - self.t)
        if d > 0: time.sleep(d)
        self.t = time.time()
LIMITER = _Limiter(C.RATE_PER_MINUTE)


class ApiKeyError(RuntimeError):
    pass


def api_call(method, path, body=None, retries=4):
    """返回 (data, err)。限流/网络错误自动重试；key 错误直接抛出。"""
    if not C.API_KEY:
        raise ApiKeyError('STEAMDT_API_KEY 为空：请在仓库 Settings → Secrets 添加')
    headers = {'Authorization': f'Bearer {C.API_KEY}', 'Content-Type': 'application/json'}
    last_err = ''
    for attempt in range(retries):
        LIMITER.wait()
        try:
            r = requests.request(method, BASE_URL + path, headers=headers, json=body, timeout=30)
        except requests.RequestException as e:
            last_err = f'网络错误 {e}'; time.sleep(5 * (attempt + 1)); continue
        if r.status_code == 429:
            last_err = 'HTTP 429 限流'; time.sleep(65); continue
        if r.status_code >= 500:
            last_err = f'HTTP {r.status_code}'; time.sleep(5 * (attempt + 1)); continue
        try:
            js = r.json()
        except ValueError:
            last_err = f'非 JSON 响应 HTTP {r.status_code}: {r.text[:120]}'; time.sleep(3); continue
        if js.get('success'):
            return js.get('data'), ''
        code, msg = js.get('errorCode'), str(js.get('errorMsg', ''))
        if code == 4001 or 'key' in msg.lower():
            raise ApiKeyError(f'API key 无效: {code} {msg}')
        if any(k in msg.lower() for k in ['频', '限', 'limit', 'rate', 'too many']):
            last_err = f'限流 {code} {msg}'; time.sleep(65); continue
        return None, f'{code} {msg}'
    return None, last_err


_KEYS_TS = ['time', 'updateTime', 'timestamp', 't', 'ts', 'date']
_KEYS = {'open': ['open', 'openIndex', 'o'], 'close': ['close', 'closeIndex', 'c'],
         'high': ['high', 'highIndex', 'h'], 'low': ['low', 'lowIndex', 'l']}

def parse_kline(data):
    """文档格式：每条 [更新时间, 开盘, 收盘, 最高, 最低]；兼容 dict 形式；时间戳秒/毫秒自动识别"""
    rows = []
    for rec in (data or []):
        if isinstance(rec, dict):
            ts = next((rec[k] for k in _KEYS_TS if k in rec), None)
            vals = [next((rec[k] for k in ks if k in rec), None) for ks in _KEYS.values()]
            rows.append([ts] + vals)
        elif isinstance(rec, (list, tuple)) and len(rec) >= 5:
            rows.append(list(rec[:5]))
    cols = ['date', 'open', 'close', 'high', 'low']
    if not rows:
        return pd.DataFrame(columns=cols)
    df = pd.DataFrame(rows, columns=['ts', 'open', 'close', 'high', 'low'])
    ts = pd.to_numeric(df['ts'], errors='coerce')
    if ts.notna().any() and ts.max() > 1e11:
        ts = ts // 1000
    df['date'] = pd.to_datetime(ts, unit='s', utc=True).dt.tz_convert(C.TZ).dt.normalize().dt.tz_localize(None)
    for c in ['open', 'close', 'high', 'low']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.dropna(subset=['date', 'close']).drop_duplicates('date', keep='last').sort_values('date')
    return df[cols]


# ---------------- 饰品池 ----------------
def load_universe():
    if not os.path.exists(UNIVERSE_PATH):
        raise SystemExit(f'缺少 {UNIVERSE_PATH}（name,cat 两列）')
    u = pd.read_csv(UNIVERSE_PATH, encoding='utf-8-sig')
    u.columns = [c.strip() for c in u.columns]
    u = u.rename(columns={'饰品名称': 'name', '品类': 'cat'}).dropna(subset=['name']).drop_duplicates('name')
    u['cat'] = u['cat'].fillna('other').astype(str)
    return u.reset_index(drop=True)


# ---------------- K 线仓库：data/bars/YYYY-MM.csv(.gz) ----------------
BARS_DIR = C.P('data', 'bars')

def _month_path(month, current_month):
    """当前月用明文 csv（每天追加，git 增量小），历史月用 csv.gz（不再变化）"""
    return os.path.join(BARS_DIR, f'{month}.csv' if month == current_month else f'{month}.csv.gz')

def load_bars():
    files = sorted(glob.glob(os.path.join(BARS_DIR, '*.csv')) + glob.glob(os.path.join(BARS_DIR, '*.csv.gz')))
    if not files:
        return pd.DataFrame({c: pd.Series(dtype=('datetime64[ns]' if c in ('date', 'fetched') else ('str' if c == 'name' else float))) for c in BAR_COLS})
    parts = [pd.read_csv(f) for f in files]
    df = pd.concat(parts, ignore_index=True)
    df['date'] = pd.to_datetime(df['date']); df['fetched'] = pd.to_datetime(df['fetched'])
    df = df.sort_values(['name', 'date']).drop_duplicates(['name', 'date'], keep='last').reset_index(drop=True)
    return df[BAR_COLS]

def save_bars(df, months=None):
    """按月写回；months=None 时全部重写，否则只写指定月份（增量提交更小）。上个月刚过完会自动压缩成 gz。"""
    df = df.sort_values(['name', 'date']).drop_duplicates(['name', 'date'], keep='last')
    cur = C.TODAY.strftime('%Y-%m')
    mkey = df['date'].dt.strftime('%Y-%m')
    for m in sorted(mkey.unique()):
        if months is not None and m not in months: continue
        sub = df[mkey == m].copy()
        sub['date'] = sub['date'].dt.strftime('%Y-%m-%d'); sub['fetched'] = sub['fetched'].dt.strftime('%Y-%m-%d')
        path = _month_path(m, cur)
        sub[BAR_COLS].to_csv(path, index=False, float_format='%.4f')
        other = path[:-3] if path.endswith('.gz') else path + '.gz'
        if os.path.exists(other): os.remove(other)        # 月份切换：明文 → gz
    # 已经过去的月份如果还是明文 csv（当月没有新增行导致没被改写），也压缩掉
    for f in glob.glob(os.path.join(BARS_DIR, '*.csv')):
        m = os.path.basename(f)[:-4]
        if m < cur:
            pd.read_csv(f).to_csv(f + '.gz', index=False); os.remove(f)

def merge_bars(old, new):
    allb = pd.concat([old, new], ignore_index=True)
    return allb.sort_values(['name', 'date']).drop_duplicates(['name', 'date'], keep='last').reset_index(drop=True)


def only_new_rows(old, new):
    """丢掉仓库里已经是"完整 K 线"的 (name,date)：历史文件不被反复改写，git 每天只多出真正的新行"""
    if not len(old) or not len(new): return new
    complete = old[old['date'] < old['fetched']]
    key_old = pd.MultiIndex.from_frame(complete[['name', 'date']])
    key_new = pd.MultiIndex.from_frame(new[['name', 'date']])
    return new[~key_new.isin(key_old)]


def import_seed_csvs(paths):
    """把 SteamDT 导出的日 K CSV（饰品名称,品类,日期,更新时间,开盘指数,收盘指数,最高指数,最低指数）导入仓库"""
    parts = []
    for p in paths:
        d = pd.read_csv(p, encoding='utf-8-sig')
        d = d.rename(columns={'饰品名称': 'name', '日期': 'date', '开盘指数': 'open', '收盘指数': 'close', '最高指数': 'high', '最低指数': 'low'})
        d['date'] = pd.to_datetime(d['date'])
        parts.append(d[['name', 'date', 'open', 'close', 'high', 'low']])
    seed = pd.concat(parts, ignore_index=True)
    seed['fetched'] = seed['date'] + pd.Timedelta(days=1)          # 历史数据视为完整 K 线
    bars = merge_bars(seed, load_bars())                            # 已有（API）数据优先
    save_bars(bars)
    LOG(f'导入 {len(seed):,} 行，{seed.name.nunique()} 个饰品，{seed.date.min().date()} → {seed.date.max().date()}；仓库现有 {len(bars):,} 行')
    return bars


# ---------------- 增量更新 ----------------
def refresh(universe, bars, log=LOG):
    """返回 (bars, info)。只抓"完整 K 线"没到昨天的饰品；当天抓到的当日 K 线视为临时，下次重抓覆盖。"""
    info = {'todo': 0, 'ok': 0, 'fail': 0, 'hist_med': None, 'stopped': False, 'first': ''}
    if C.DATA_SOURCE != 'api' or C.REFRESH_MODE == 'none':
        log(f'跳过 API 更新（DATA_SOURCE={C.DATA_SOURCE}, REFRESH_MODE={C.REFRESH_MODE}）'); return bars, info
    target = C.TODAY - pd.Timedelta(days=1)
    complete = bars[bars['date'] < bars['fetched']] if len(bars) else bars
    last = complete.groupby('name')['date'].max() if len(complete) else pd.Series(dtype='datetime64[ns]')
    names = universe['name'].tolist()
    todo = names if C.REFRESH_MODE == 'full' else [n for n in names if last.get(n, pd.Timestamp('2000-01-01')) < target]
    info['todo'] = len(todo)
    log(f'需要更新 {len(todo)}/{len(names)} 个饰品（约 {len(todo) / C.RATE_PER_MINUTE:.0f} 分钟，上限 {C.MAX_FETCH_MINUTES:.0f} 分钟）')
    if not todo:
        return bars, info
    t0 = time.time(); parts, errs, hist = [], [], []
    for i, n in enumerate(todo, 1):
        if (time.time() - t0) / 60 > C.MAX_FETCH_MINUTES:
            log(f'已到时间上限，剩余 {len(todo) - i + 1} 个饰品下次继续'); info['stopped'] = True; break
        try:
            data, err = api_call('POST', KLINE_PATH, {'marketHashName': n, 'type': KLINE_TYPE, 'platform': C.PLATFORM})
        except ApiKeyError as e:
            log(f'!! {e}'); info['stopped'] = True; break
        if data is None:
            errs.append({'name': n, 'err': err, 'time': str(C.now_cst())[:19]}); continue
        k = parse_kline(data)
        if k.empty:
            errs.append({'name': n, 'err': f'空数据/无法解析: {str(data)[:150]}', 'time': str(C.now_cst())[:19]}); continue
        k['name'] = n; k['fetched'] = C.TODAY; hist.append(len(k)); parts.append(k[BAR_COLS])
        if len(hist) == 1:
            gap = k['date'].diff().dt.days.median() if len(k) > 2 else 1
            info['first'] = f'{n}: {len(k)} 条，{k.date.min().date()} → {k.date.max().date()}，相邻间隔中位 {gap:.0f} 天'
            log('  首个饰品 ' + info['first'] + ('' if gap == 1 else '  ⚠️ 不是日 K？请检查 KLINE_TYPE'))
            if gap != 1: info['stopped'] = True; break
        if i % 100 == 0:
            log(f'  {i}/{len(todo)}  {(time.time() - t0) / 60:.1f} 分钟  失败 {len(errs)}')
    if parts:
        new = only_new_rows(bars, pd.concat(parts))
        info['new_rows'] = int(len(new))
        if len(new):
            bars = merge_bars(bars, new)
            save_bars(bars, months=set(new['date'].dt.strftime('%Y-%m')))
        log(f'新增/更新 K 线 {len(new):,} 行' + (f'，最新日期 {new.date.max().date()}' if len(new) else ''))
    info['ok'] = len(hist); info['fail'] = len(errs)
    if errs:
        pd.DataFrame(errs).to_csv(ERR_PATH, index=False, encoding='utf-8-sig')
        log(f'{len(errs)} 个饰品获取失败（data/fetch_errors.csv），例如: {errs[0]}')
    elif os.path.exists(ERR_PATH):
        os.remove(ERR_PATH)
    if hist:
        info['hist_med'] = int(np.median(hist))
        log(f'每个饰品返回 K 线条数：中位 {info["hist_med"]}，最少 {min(hist)}，最多 {max(hist)}')
    return bars, info


def fetch_broad(log=LOG):
    """SteamDT 官方大盘日 K（仅展示对照），存 data/broad_kline.csv"""
    path = C.P('data', 'broad_kline.csv')
    old = pd.read_csv(path, parse_dates=['date']) if os.path.exists(path) else None
    if C.DATA_SOURCE != 'api' or C.REFRESH_MODE == 'none' or not C.API_KEY:
        return old
    try:
        data, err = api_call('POST', BROAD_PATH, {'type': KLINE_TYPE})
    except ApiKeyError:
        return old
    if data is None:
        log(f'大盘 K 线获取失败: {err}'); return old
    b = parse_kline(data)
    if b.empty:
        return old
    if old is not None:
        b = pd.concat([old, b]).drop_duplicates('date', keep='last').sort_values('date')
    b.to_csv(path, index=False, float_format='%.4f')
    return b


def usable_bars(bars, universe):
    """合并品类、丢弃临时的当日 K 线"""
    df = bars.merge(universe[['name', 'cat']], on='name', how='inner')
    if C.DROP_TODAY_BAR:
        df = df[(df['date'] < df['fetched']) & (df['date'] < C.TODAY)]
    return df.drop(columns=['fetched']).reset_index(drop=True)
