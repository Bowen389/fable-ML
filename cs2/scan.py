# -*- coding: utf-8 -*-
"""市场状态 + 买点扫描 + 信号日志"""
import os
import numpy as np, pandas as pd
from . import config as C
from .rules import NICE, fmt_cond, fmt_val, cond_mask

SHOW_COLS = {'r_7': '7日%', 'r_30': '30日%', 'dd_60': '距60日高%', 'dd_60_rank': '60日回撤分位', 'dsl_30': '距30日低点天数',
             'ma7_30': 'MA7/MA30%', 'vol_ratio': '短/长波动比', 'vol_7': '7日波动%', 'ma90_dev': '偏离MA90%', 'up_14': '距14日低反弹%', 'rsi_14': 'RSI14'}
PCT_COLS = ['7日%', '30日%', '距60日高%', 'MA7/MA30%', '7日波动%', '偏离MA90%', '距14日低反弹%']
TOL = {'dsl_30': 5, 'dd_60_rank': 0.05, 'vol_ratio': 0.10, 'vol_7': 0.02, 'ma7_30': 0.02, 'up_7': 0.05, 'up_14': 0.03, 'ma90_dev': 0.05, 'pos_60': 0.02, 'logp': 0.15}


def market_snapshot(feat, date):
    row = feat[feat.date == date].iloc[0]
    s = {k: float(row[k]) for k in ['above_ma30', 'breadth7', 'mkt_r_7', 'mkt_r_14', 'mkt_r_30', 'mkt_ma30_dev', 'mkt_dd_90', 'mkt_vol_14']}
    notes = []
    a = s['above_ma30']
    if a < 0.10: notes.append(f'站上MA30占比 {a:.0%} → 极弱市场，反弹尚未确认')
    elif a < 0.35: notes.append(f'站上MA30占比 {a:.0%} → 弱势市场')
    elif a < 0.70: notes.append(f'站上MA30占比 {a:.0%} → 中性')
    else: notes.append(f'站上MA30占比 {a:.0%} → 普涨/强势')
    dd = s['mkt_dd_90']
    notes.append(f'指数距90日高点 {dd:+.1%} → 长线择时 ' + ('✓' if dd >= -0.15 else '✗'))
    if s['mkt_r_14'] < -0.20: notes.append('近期急跌，不能仅凭历史反弹叙述确认买点')
    return s, notes


def _fmt_row(sub):
    o = sub[['name', 'cat', 'close'] + list(SHOW_COLS)].rename(columns={'name': '饰品', 'cat': '品类', 'close': '价格', **SHOW_COLS})
    for c in list(SHOW_COLS.values()) + ['价格']: o[c] = o[c].astype(float)
    for c in PCT_COLS: o[c] = (o[c] * 100).round(1)
    o['价格'] = o['价格'].round(2); o['60日回撤分位'] = o['60日回撤分位'].round(2); o['短/长波动比'] = o['短/长波动比'].round(2)
    o['RSI14'] = o['RSI14'].round(0); o['距30日低点天数'] = o['距30日低点天数'].astype(int)
    o['饰品'] = o['饰品'].astype(str); o['品类'] = o['品类'].astype(str)
    return o


def scan_rules(feat, rules, date, ml_scores=None):
    """返回 (hits, near)。ml_scores: 函数 day -> DataFrame(ML分位H 列) 或 None"""
    day = feat[(feat.date == date) & feat.eligible & (feat.flat_14 <= 0.5)].copy()
    if day.empty:
        return pd.DataFrame(), pd.DataFrame()
    ml = ml_scores(day) if ml_scores is not None else None
    mrow = day.iloc[0]
    hits, near = [], []
    for r in rules:
        if r['status'] != 'active': continue
        mk_ok = all(cond_mask(day.iloc[[0]], c)[0] for c in r.get('mkt_filter', [])) if r.get('mkt_filter') else True
        mk_txt = '—' if not r.get('mkt_filter') else ('✓' if mk_ok else '✗ ' + '；'.join(f'{NICE.get(c[0], c[0])} {mrow[c[0]]:+.1%}' for c in r['mkt_filter']))
        if not mk_ok: continue
        masks = np.array([cond_mask(day, c) for c in r['conds']])
        full = masks.all(axis=0)
        if full.any():
            o = _fmt_row(day[full]); o.insert(0, '规则', f"{r['id']} {r['name']}"); o.insert(1, '状态', r['status']); o.insert(2, '建议持有', r['hold']); o['择时'] = mk_txt
            if ml is not None and len(ml.columns): o = o.join(ml.loc[day[full].index])
            o['_H'] = r['H']; o['_rid'] = r['id']; o['_mk'] = mk_ok
            hits.append(o)
        nfail = (~masks).sum(axis=0)
        for j, (f, op, t) in enumerate(r['conds']):
            cand = (nfail == 1) & (~masks[j])
            if not cand.any() or f not in TOL: continue
            x = day.loc[cand, f]
            gap = (x - t) if op == '<=' else (t - x)
            ok = gap <= TOL[f]
            if ok.any():
                o = _fmt_row(day.loc[cand][ok.values]); o.insert(0, '规则', f"{r['id']} {r['name']}")
                o.insert(1, '差的条件', [f'{fmt_cond(f, op, t)}（现 {fmt_val(f, v)}）' for v in x[ok]])
                near.append(o.head(15))
    hits = pd.concat(hits, ignore_index=True) if hits else pd.DataFrame()
    near = pd.concat(near, ignore_index=True) if near else pd.DataFrame()
    return hits, near


# ---------------- 信号日志 ----------------
SIG_PATH = C.P('state', 'signals.csv')
SIG_COLS = ['signal_date', 'rule_id', 'name', 'cat', 'H', 'price_signal', 'mkt_ok', 'ml_pct', 'entry_date', 'entry_price', 'exit_date', 'exit_price', 'net_ret', 'status', 'logged_at', 'pipeline_version']

def load_signals():
    if os.path.exists(SIG_PATH):
        s = pd.read_csv(SIG_PATH, encoding='utf-8-sig')
        for c in ['signal_date', 'entry_date', 'exit_date']: s[c] = pd.to_datetime(s[c])
        if 'pipeline_version' not in s: s['pipeline_version'] = 'legacy-v1'
        return s
    return pd.DataFrame(columns=SIG_COLS)

def save_signals(sig):
    sig[SIG_COLS].to_csv(SIG_PATH, index=False, encoding='utf-8-sig', float_format='%.4f')

def log_signals(hits, last):
    """把本次命中追加进信号日志（按 信号日期|规则|饰品 去重），返回新增条数"""
    if hits.empty: return 0
    sig = load_signals()
    new = pd.DataFrame({'signal_date': last, 'rule_id': hits['_rid'], 'name': hits['饰品'].astype(str), 'cat': hits['品类'].astype(str), 'H': hits['_H'],
                        'price_signal': hits['价格'], 'mkt_ok': hits['_mk'],
                        'ml_pct': [row.get(f'ML分位{int(row["_H"])}', np.nan) for _, row in hits.iterrows()],
                        'entry_date': last + pd.Timedelta(days=1), 'entry_price': np.nan,
                        'exit_date': last + pd.to_timedelta(hits['_H'].astype(int) + 1, unit='D'), 'exit_price': np.nan, 'net_ret': np.nan,
                        'pipeline_version': C.PIPELINE_VERSION, 'status': 'pending', 'logged_at': str(C.now_cst())[:19]})
    key = lambda d: d['signal_date'].astype(str) + '|' + d['rule_id'].astype(str) + '|' + d['name'].astype(str)
    if len(sig): new = new[~key(new).isin(set(key(sig)))]
    # One outstanding simulated position per item, across all rules.
    if len(sig):
        busy = set(sig.loc[sig.status.isin(['pending', 'open', 'missing_exit']) & (sig.pipeline_version == C.PIPELINE_VERSION), 'name'].astype(str))
        new = new[~new.name.isin(busy)]
    new = sort_hits(new.rename(columns={'name': '饰品'}), signal_rows=True).rename(columns={'饰品': 'name'}).drop_duplicates('name')
    n_added = len(new)
    sig = pd.concat([sig, new], ignore_index=True)
    save_signals(sig)
    return n_added


def sort_hits(hits, signal_rows=False):
    if hits.empty: return hits.copy()
    out = hits.copy()
    if signal_rows:
        return out.sort_values('ml_pct', ascending=False, na_position='last', kind='stable')
    out['_score'] = [row.get(f'ML分位{int(row["_H"])}', np.nan) for _, row in out.iterrows()]
    return out.sort_values(['规则', '_score', '距60日高%', '饰品'], ascending=[True, False, True, True], na_position='last', kind='stable').drop(columns='_score')
