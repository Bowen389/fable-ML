# -*- coding: utf-8 -*-
"""离线模拟 SteamDT API：python tests/mock_api.py  （在临时副本里跑两天的增量更新，验证仓库文件变化）"""
import os, sys, json, glob, shutil, hashlib, tempfile
import pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.update(DATA_SOURCE='api', STEAMDT_API_KEY='test-key', REFRESH_MODE='auto', MAX_FETCH_MINUTES='5')
TMP = tempfile.mkdtemp(prefix='cs2test_')
os.environ['CS2_ROOT'] = TMP
shutil.copy(os.path.join(ROOT, 'universe.csv'), TMP)
shutil.copytree(os.path.join(ROOT, 'data'), os.path.join(TMP, 'data'))
import requests
from cs2 import config as C, data

# Self-contained fixtures from repository history; no private upload path.
seed = data.load_bars()
seed = seed[seed.date <= pd.Timestamp('2026-09-22')].copy()
seed['日期'] = seed.date
seed['ts'] = seed.date.dt.tz_localize('Asia/Shanghai').astype('int64') // 10**9
for path in glob.glob(os.path.join(TMP, 'data', 'bars', '*')): os.remove(path)
C.TODAY = pd.Timestamp('2026-09-23')
data.save_bars(seed[data.BAR_COLS])
by = {n: g for n, g in seed.groupby('name')}
SIM = {'today': None}

class FakeResp:
    def __init__(self, js, code=200): self._js = js; self.status_code = code; self.text = json.dumps(js)[:200]
    def json(self): return self._js

def fake_request(method, url, headers=None, json=None, timeout=None):
    assert headers['Authorization'] == 'Bearer test-key'
    if url.endswith('/open/cs2/item/v1/kline'):
        g = by.get(json['marketHashName'])
        if g is None: return FakeResp({'success': False, 'errorCode': 5000, 'errorMsg': 'item not found'})
        g = g.tail(120).copy()
        rows = [[int(t) * 1000, o, c, h, l] for t, o, c, h, l in g[['ts', 'open', 'close', 'high', 'low']].values]
        # 模拟：数据源比上传数据多出到 today 为止的 K 线（复制最后一根，价格微调）
        last_ts = int(g['ts'].max()); last_close = float(g['close'].iloc[-1])
        d = last_ts
        while True:
            d += 86400
            if pd.Timestamp(d, unit='s', tz='UTC').tz_convert('Asia/Shanghai').normalize().tz_localize(None) > SIM['today']: break
            rows.append([d * 1000, last_close, last_close * 0.99, last_close * 1.01, last_close * 0.98])
        return FakeResp({'success': True, 'data': rows, 'errorCode': 0})
    if url.endswith('/open/cs2/broad/v1/kline'):
        g = seed.groupby('日期')['close'].median().reset_index().tail(200)
        ts = (pd.to_datetime(g['日期']).dt.tz_localize('Asia/Shanghai').astype('int64') // 10**9).tolist()
        return FakeResp({'success': True, 'data': [[t, c, c, c, c] for t, c in zip(ts, g['close'])], 'errorCode': 0})
    return FakeResp({'success': False, 'errorCode': 404, 'errorMsg': 'no'}, 200)
requests.request = fake_request
data.LIMITER = data._Limiter(100000)

def snapshot():
    return {os.path.basename(f): hashlib.md5(open(f, 'rb').read()).hexdigest() for f in glob.glob(os.path.join(TMP, 'data', 'bars', '*'))}

universe = data.load_universe().head(60)
for day in ['2026-09-27', '2026-09-28', '2026-10-01']:
    SIM['today'] = pd.Timestamp(day); C.TODAY = pd.Timestamp(day)
    before = snapshot()
    bars = data.load_bars()
    bars, info = data.refresh(universe, bars, log=print)
    after = snapshot()
    changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    print(f'--- 模拟日期 {day}: info={ {k: v for k, v in info.items() if k != "first"} }')
    print(f'    变化的文件: {changed}')
    sub = bars[bars.name.isin(universe.name)]
    print(f'    仓库 {len(bars):,} 行；这 60 个饰品最新日期 {sub.date.max().date()}，fetched 取值 {sorted(sub.fetched.dt.date.astype(str).unique())[-3:]}')
    use = data.usable_bars(bars, universe)
    print(f'    usable 最新日期 {use.date.max().date()}（应为 {(C.TODAY - pd.Timedelta(days=1)).date()}）')
    assert use.date.max() == C.TODAY - pd.Timedelta(days=1)
    assert set(changed) <= {'2026-09.csv', '2026-09.csv.gz', '2026-10.csv'}, changed
b = data.fetch_broad(log=print); print('broad rows', len(b), b.date.max().date())
print('bars dir:', sorted(os.path.basename(f) for f in glob.glob(os.path.join(TMP, 'data', 'bars', '*'))))
shutil.rmtree(TMP); print('MOCK API TEST PASS')
