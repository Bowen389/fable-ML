# -*- coding: utf-8 -*-
"""结算信号 + 规则健康度 + 状态机"""
import numpy as np, pandas as pd
from . import config as C
from .features import LAG_H
from .rules import rule_mask, save_rules
from .scan import load_signals, save_signals

HEALTH_WINDOWS = [30, 90, 180]
STATUS_RULES = dict(watch_beat=0.55, prob_beat=0.50, dis_beat=0.45, min_n=30, dis_min_n=60)


def settle_signals(clean, last):
    """按次日收盘入场、H 天后收盘出场结算；未到期的标记浮动盈亏"""
    sig = load_signals()
    if sig.empty: return sig
    px = clean.assign(name=clean['name'].astype(str)).set_index(['name', 'date'])['close']
    def look(name, d):
        try: return float(px.loc[(name, d)])
        except KeyError: return np.nan
    for i in sig.index[sig['status'] != 'closed']:
        r = sig.loc[i]
        if pd.isna(r['entry_price']) and r['entry_date'] <= last:
            sig.at[i, 'entry_price'] = look(r['name'], r['entry_date'])
        ep = sig.at[i, 'entry_price']
        if pd.isna(ep): continue
        if r['exit_date'] <= last:
            xp = look(r['name'], r['exit_date'])
            if not pd.isna(xp):
                sig.at[i, 'exit_price'] = xp; sig.at[i, 'net_ret'] = xp / ep * (1 - C.FEE) - 1; sig.at[i, 'status'] = 'closed'
        else:
            cur = look(r['name'], last)
            if not pd.isna(cur): sig.at[i, 'net_ret'] = cur / ep * (1 - C.FEE) - 1; sig.at[i, 'status'] = 'open'
    save_signals(sig)
    return sig


class Health:
    def __init__(self, feat):
        self.feat = feat
        self.daily_med = {H: feat.groupby('date')[f'fwdL_{H}'].median() for H in LAG_H}
        self.notna = {H: feat[f'fwdL_{H}'].notna().values for H in LAG_H}
        self.dates = feat['date'].values

    def stats(self, m, H, lo=None, hi=None):
        col = f'fwdL_{H}'
        sel = np.asarray(m, bool) & self.notna[H]
        if lo is not None: sel &= (self.dates >= np.datetime64(lo))
        if hi is not None: sel &= (self.dates <= np.datetime64(hi))
        d = self.feat.loc[sel, ['date', col]]
        if len(d) == 0: return dict(n=0)
        net = (1 + d[col]) * (1 - C.FEE) - 1
        exm = d[col] - d['date'].map(self.daily_med[H])
        return dict(n=int(len(d)), win=float((net > 0).mean()), med=float(net.median()), beat=float((exm > 0).mean()))

    def table(self, rules, last):
        """返回 (DataFrame, new_status dict)"""
        rows, new_status = [], {}
        allm = np.ones(len(self.feat), bool)
        for r in rules:
            H = r['H']; lab_end = last - pd.Timedelta(days=H + 1)
            m = rule_mask(self.feat, r['conds'])
            row = {'规则': f"{r['id']} {r['name']}", '状态': r['status'], 'H': H}
            st = {}
            for W in HEALTH_WINDOWS:
                s = self.stats(m, H, lab_end - pd.Timedelta(days=W), lab_end); st[W] = s
                b = self.stats(allm, H, lab_end - pd.Timedelta(days=W), lab_end)
                row[f'{W}日 n'] = s['n']
                row[f'{W}日 胜率'] = f"{s['win']:.0%}" if s['n'] else '—'
                row[f'{W}日 中位'] = f"{s['med']:+.1%}" if s['n'] else '—'
                row[f'{W}日 跑赢中位'] = f"{s['beat']:.0%}" if s['n'] else '—'
                row[f'{W}日 基准胜率'] = f"{b['win']:.0%}" if b['n'] else '—'
            oos_from = pd.Timestamp(r.get('data_end_at_creation', r.get('created'))) + pd.Timedelta(days=1)
            s = self.stats(m, H, oos_from, lab_end); st['oos'] = s
            row['OOS n'] = s['n']; row['OOS 胜率'] = f"{s['win']:.0%}" if s['n'] else '—'; row['OOS 跑赢中位'] = f"{s['beat']:.0%}" if s['n'] else '—'
            rows.append(row)
            s90, s180 = st[90], st[180]
            if s90['n'] >= STATUS_RULES['min_n']:
                if s180.get('n', 0) >= STATUS_RULES['dis_min_n'] and s180['beat'] < STATUS_RULES['dis_beat']: ns = 'disabled'
                elif s90['beat'] < STATUS_RULES['prob_beat']: ns = 'probation'
                elif s90['beat'] < STATUS_RULES['watch_beat']: ns = 'watch'
                else: ns = 'active'
                if ns != r['status']: new_status[r['id']] = (r['status'], ns, s90, s180)
        return pd.DataFrame(rows), new_status


def apply_status(rules, new_status, last):
    for r in rules:
        if r['id'] in new_status:
            old, ns, s90, _ = new_status[r['id']]
            r.setdefault('history', []).append({'date': str(last.date()), 'from': old, 'to': ns, 'beat90': round(s90['beat'], 3), 'win90': round(s90['win'], 3), 'n90': s90['n']})
            r['status'] = ns
    save_rules(rules)
