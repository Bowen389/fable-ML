# -*- coding: utf-8 -*-
"""清洗 + 特征工程（与研究口径一致；全部特征只用 t 日及之前的数据）"""
import numpy as np, pandas as pd

CAT_CODE = {'gun_FN': 0, 'gloves_MW_FT': 1, 'agent': 2}
LABEL_H = [7, 10, 14, 30, 45, 60]
LAG_H = [10, 14, 30]


def clean_bars(df, min_days=120, max_flat=0.25, max_same=0.35, min_price=2.0, log=print):
    # Point-in-time universe: future rows must not alter past eligibility/prices.
    cols = ['open', 'close', 'high', 'low']
    df = df[['name', 'cat', 'date'] + cols].copy()
    df = df.sort_values(['name', 'date']).drop_duplicates(['name', 'date'], keep='last')
    full = []
    for name, g in df.groupby('name', sort=False, observed=True):
        g = g.set_index('date').reindex(pd.date_range(g.date.min(), g.date.max(), freq='D'))
        g['name'] = name
        g['cat'] = g['cat'].ffill()
        for col in cols:
            g[col] = pd.to_numeric(g[col], errors='coerce')
            g.loc[(g[col] <= 0) | (g[col] >= 1e6), col] = np.nan
        # Flag extreme changes against trailing observations; never interpolate.
        med = g.close.shift(1).rolling(15, min_periods=5).median()
        bad = (g.close / med > 3) | (g.close / med < 1 / 3)
        coherent = (g.high >= g[['open', 'close']].max(axis=1)) & (g.low <= g[['open', 'close']].min(axis=1))
        g['observed'] = g[cols].notna().all(axis=1) & ~bad & coherent
        g.loc[~g.observed, cols] = np.nan
        g['raw_close'] = g.close
        count = g.observed.cumsum()
        flat = ((g.high == g.low) & g.observed).cumsum() / count.replace(0, np.nan)
        same = ((g.close == g.close.shift(1)) & g.observed).cumsum() / count.replace(0, np.nan)
        price = g.close.expanding(min_periods=1).median()
        g['eligible'] = g.observed & (count >= min_days) & (flat < max_flat) & (same < max_same) & (price >= min_price)
        # Carry only for indicators, never for entry/exit labels or settlement.
        g[cols] = g[cols].ffill()
        g.index.name = 'date'
        full.append(g.reset_index())
    if not full:
        raise ValueError('没有可清洗的日K数据')
    out = pd.concat(full, ignore_index=True)
    out['name'] = out['name'].astype('category'); out['cat'] = out['cat'].astype('category')
    log(f'因果清洗：{out.name.nunique()} 个饰品，{len(out):,} 行；仅真实报价可入场/结算')
    return out


def _days_since_ext(x, w=30, mode='min', min_periods=5):
    x = np.asarray(x, float); n = len(x); out = np.full(n, np.nan)
    fill = np.inf if mode == 'min' else -np.inf
    x2 = np.where(np.isnan(x), fill, x)
    if n >= w:
        sw = np.lib.stride_tricks.sliding_window_view(x2, w)
        idx = sw.argmin(axis=1) if mode == 'min' else sw.argmax(axis=1)
        out[w - 1:] = (w - 1) - idx
    for i in range(min_periods - 1, min(w - 1, n)):
        seg = x2[:i + 1]
        j = seg.argmin() if mode == 'min' else seg.argmax()
        out[i] = i - j
    return out


def _streak(v):
    out = np.zeros(len(v)); cur = 0; prev = 0
    for i, s in enumerate(v):
        if s > 0: cur = cur + 1 if prev > 0 else 1
        elif s < 0: cur = cur - 1 if prev < 0 else -1
        else: cur = 0
        prev = s; out[i] = cur
    return out


class _F(dict):
    def __setitem__(self, k, v):
        super().__setitem__(k, v.astype('float32') if hasattr(v, 'astype') else v)


def build_features(df):
    """返回 (feat, mk)。标签 fwd_H(当日入场) / fwdL_H(次日入场，规则评估口径)"""
    df = df.sort_values(['name', 'date']).reset_index(drop=True)
    key = df['name']
    c, o, h, l = df['close'], df['open'], df['high'], df['low']
    F = _F()
    def gshift(s, k): return s.groupby(key, observed=True).shift(k)
    def groll(s, k, fn, mp=None):
        mp = mp or max(2, k // 2)
        r = s.groupby(key, observed=True).rolling(k, min_periods=mp)
        return getattr(r, fn)().reset_index(level=0, drop=True)
    lr1 = np.log(c).groupby(key, observed=True).diff(); F['lr1'] = lr1
    for k in [1, 3, 5, 7, 10, 14, 21, 30, 45, 60, 90]:
        F[f'r_{k}'] = c / gshift(c, k) - 1
    for k in [7, 14, 30, 60, 90]:
        F[f'ma{k}_dev'] = c / groll(c, k, 'mean') - 1
    F['ma7_30'] = groll(c, 7, 'mean') / groll(c, 30, 'mean') - 1
    F['ma14_60'] = groll(c, 14, 'mean') / groll(c, 60, 'mean') - 1
    F['ma30_90'] = groll(c, 30, 'mean') / groll(c, 90, 'mean') - 1
    for k in [7, 14, 30, 60, 90]:
        hi = groll(h, k, 'max'); lo = groll(l, k, 'min')
        F[f'dd_{k}'] = c / hi - 1
        F[f'up_{k}'] = c / lo - 1
        F[f'pos_{k}'] = (c - lo) / (hi - lo).replace(0, np.nan)
    d = c.groupby(key, observed=True).diff()
    for k in [7, 14]:
        gain = groll(d.clip(lower=0), k, 'mean'); loss = groll((-d).clip(lower=0), k, 'mean')
        rsi = 100 - 100 / (1 + gain / loss.replace(0, np.nan))
        F[f'rsi_{k}'] = rsi.fillna(100 * (gain > 0))
    ma20 = groll(c, 20, 'mean'); sd20 = groll(c, 20, 'std')
    F['bb_pctb'] = 0.5 + (c - ma20) / (4 * sd20).replace(0, np.nan)
    F['bb_width'] = 4 * sd20 / ma20
    for k in [7, 14, 30]:
        F[f'vol_{k}'] = groll(lr1, k, 'std')
    tr = pd.concat([h - l, (h - gshift(c, 1)).abs(), (l - gshift(c, 1)).abs()], axis=1).max(axis=1)
    F['atr14'] = groll(tr, 14, 'mean') / c
    F['vol_ratio'] = F['vol_7'] / F['vol_30'].replace(0, np.nan)
    sign = np.sign(d).fillna(0)
    F['streak'] = sign.groupby(key, observed=True).transform(lambda s: pd.Series(_streak(s.values), index=s.index))
    F['dsh_30'] = c.groupby(key, observed=True).transform(lambda s: pd.Series(_days_since_ext(s.values, 30, 'max'), index=s.index))
    F['dsl_30'] = c.groupby(key, observed=True).transform(lambda s: pd.Series(_days_since_ext(s.values, 30, 'min'), index=s.index))
    F['body'] = (c - o) / o
    F['range'] = (h - l) / c
    F['lower_shadow'] = (np.minimum(o, c) - l) / c
    F['upper_shadow'] = (h - np.maximum(o, c)) / c
    F['down_days_7'] = groll((d < 0).astype(float), 7, 'sum')
    F['down_days_14'] = groll((d < 0).astype(float), 14, 'sum')
    F['flat_14'] = groll((h == l).astype(float), 14, 'mean')
    F['logp'] = np.log(c)
    F['cat_code'] = df['cat'].astype(str).map(CAT_CODE).fillna(3).astype('float32')
    F['dow'] = df['date'].dt.dayofweek
    feat = pd.DataFrame(F); del F
    out = pd.concat([df[['name', 'cat', 'date', 'close', 'raw_close', 'observed', 'eligible']], feat], axis=1); del feat
    mk = out[out.eligible].assign(lrc=lambda d: d['lr1'].clip(-0.2, 0.2)).groupby('date').agg(
        mkt_lr=('lrc', 'mean'), breadth7=('r_7', lambda s: (s > 0).mean()),
        above_ma30=('ma30_dev', lambda s: (s > 0).mean()), mkt_med_r7=('r_7', 'median'), mkt_med_r30=('r_30', 'median'),
        n_items=('name', 'size'))
    mk['mkt_idx'] = np.exp(mk['mkt_lr'].fillna(0).cumsum())
    for k in [3, 7, 14, 30, 60]:
        mk[f'mkt_r_{k}'] = mk['mkt_idx'] / mk['mkt_idx'].shift(k) - 1
    mk['mkt_dd_90'] = mk['mkt_idx'] / mk['mkt_idx'].rolling(90, min_periods=20).max() - 1
    mk['mkt_up_90'] = mk['mkt_idx'] / mk['mkt_idx'].rolling(90, min_periods=20).min() - 1
    mk['mkt_ma30_dev'] = mk['mkt_idx'] / mk['mkt_idx'].rolling(30, min_periods=10).mean() - 1
    mk['mkt_vol_14'] = mk['mkt_lr'].rolling(14, min_periods=7).std()
    mkt = mk.drop(columns=['mkt_lr', 'n_items']).astype('float32')
    for col in mkt.columns:
        out[col] = out['date'].map(mkt[col]).astype('float32')
    out['rs_7'] = out['r_7'] - out['mkt_med_r7']; out['rs_30'] = out['r_30'] - out['mkt_med_r30']
    for col in ['r_30', 'r_7', 'dd_60', 'vol_30']:
        out[f'{col}_rank'] = out[col].where(out.eligible).groupby(out.date).rank(pct=True).astype('float32')
    g = out.groupby('name', sort=False, observed=True)['raw_close']
    for H in LABEL_H:
        out[f'fwd_{H}'] = (g.shift(-H) / out['raw_close'] - 1).astype('float32')
    for H in LAG_H:
        out[f'fwdL_{H}'] = (g.shift(-(H + 1)) / g.shift(-1) - 1).where(out.eligible).astype('float32')
    mi = mk['mkt_idx']
    for H in LAG_H:
        out[f'ex_{H}'] = (out[f'fwd_{H}'] - out['date'].map(mi.shift(-H) / mi - 1)).astype('float32')
        out[f'exL_{H}'] = (out[f'fwdL_{H}'] - out['date'].map(mi.shift(-(H + 1)) / mi.shift(-1) - 1)).astype('float32')
    return out, mk


def feature_cols(feat):
    return [c for c in feat.columns if c not in ('name', 'cat', 'date', 'close', 'mkt_idx', 'raw_close', 'observed', 'eligible')
            and not c.startswith(('fwd', 'ex_', 'exL_', 'mkt_fwd'))]
