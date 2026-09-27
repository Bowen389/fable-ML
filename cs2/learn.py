# -*- coding: utf-8 -*-
"""学习层：①重新调参（形态不变）②束搜索重新挖掘（时序外测试）"""
import time, json
import numpy as np, pandas as pd
from . import config as C
from .rules import rule_mask, rule_text, cond_mask, save_rules
from .monitor import Health


class Evaluator:
    """目标 = 次日入场收益 − 当日全市场中位（截尾），按日/按月聚合；与原研究一致"""
    def __init__(self, df, H):
        y = df[f'fwdL_{H}'].values.astype(np.float64)
        self.valid = ~np.isnan(y)
        net = (1 + np.nan_to_num(y)) * (1 - C.FEE) - 1
        self.net = np.where(self.valid, net, 0.0)
        self.win = (self.net > 0).astype(np.float64)
        med = pd.Series(y).groupby(df['date'].values).transform('median').values
        exm = np.where(self.valid, np.nan_to_num(y - med), 0.0)
        self.exm = exm; self.obj = np.clip(exm, -0.9, 1.0)
        self.date_code = pd.factorize(df['date'])[0]; self.nd = self.date_code.max() + 1
        self.item_code = pd.factorize(df['name'])[0]
        self.month_code = pd.factorize(df['date'].dt.to_period('M'))[0]; self.nm = self.month_code.max() + 1

    def stats(self, mask, min_per_day=3, full=True):
        m = mask & self.valid; n = int(m.sum())
        if n == 0: return None
        dc = self.date_code[m]
        cnt = np.bincount(dc, minlength=self.nd); s_obj = np.bincount(dc, weights=self.obj[m], minlength=self.nd)
        okd = cnt >= min_per_day; nd = int(okd.sum())
        if nd == 0: return None
        day_mean = s_obj[okd] / cnt[okd]
        mc = np.bincount(self.month_code[m], minlength=self.nm); ms = np.bincount(self.month_code[m], weights=self.obj[m], minlength=self.nm)
        okm = mc >= 40; month_mean = ms[okm] / mc[okm]
        st = dict(n=n, n_days=nd, day_pos=float((day_mean > 0).mean()), n_months=int(okm.sum()),
                  month_pos=float((month_mean > 0).mean()) if okm.sum() else 0.0,
                  month_obj=float(np.median(month_mean)) if okm.sum() else -1.0, max_month_share=float(mc.max() / n),
                  n_items=int(len(np.unique(self.item_code[m]))) if full else 10 ** 9)
        if full:
            st.update(win=float(self.win[m].mean()), med=float(np.median(self.net[m])), mean=float(np.clip(self.net[m], -0.9, 1).mean()),
                      beat=float((self.exm[m] > 0).mean()))
        return st


def make_constraints(df, max_share=0.30):
    nm = df['date'].dt.to_period('M').nunique()
    return dict(min_n=max(600, int(0.004 * len(df))), min_items=60, min_days=60, min_month_pos=0.6, min_months=min(9, max(3, nm - 1)), max_share=max_share)

def constraint_fail(st, min_n, min_items, min_days, min_month_pos, min_months, max_share):
    if st is None: return '无样本'
    bad = []
    if st['n'] < min_n: bad.append(f"样本 {st['n']}<{min_n}")
    if st['n_items'] < min_items: bad.append(f"饰品数 {st['n_items']}<{min_items}")
    if st['n_days'] < min_days: bad.append(f"天数 {st['n_days']}<{min_days}")
    if st['month_pos'] < min_month_pos: bad.append(f"正月占比 {st['month_pos']:.2f}<{min_month_pos}")
    if st['n_months'] < min_months: bad.append(f"月份数 {st['n_months']}<{min_months}")
    if st['max_month_share'] > max_share: bad.append(f"最大月占比 {st['max_month_share']:.3f}>{max_share}")
    return '；'.join(bad)

def raw_score(st):
    return -9 if st is None else st['month_obj'] + 0.05 * (st['day_pos'] - 0.5)

def score(st, **cons):
    return -9 if constraint_fail(st, **cons) else raw_score(st)


# ---------------- ① 重新调参 ----------------
def threshold_grid(df, f, t_now):
    if f == 'logp': return sorted(set([float(np.log(p)) for p in [3, 5, 10, 20, 50, 100, 200, 500, 2000]] + [t_now]))
    if f in ('dsl_30', 'dsh_30'): return sorted(set(list(range(10, 30)) + [t_now]))
    if f in ('rsi_7', 'rsi_14'): return sorted(set([20, 25, 30, 35, 40, 50, 60, 70] + [t_now]))
    if f in ('streak', 'cat_code', 'dow', 'down_days_7', 'down_days_14'): return [t_now]
    x = df[f].dropna()
    qs = [0.02, 0.05, 0.08, 0.1, 0.12, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.98]
    return sorted(set(np.round(x.quantile(qs).values, 4).tolist() + [t_now]))


def retune(feat, rules, last, max_steps=2, apply=False, log=print):
    """返回建议表 DataFrame；apply=True 时把通过检验的建议写回规则库"""
    cons = make_constraints(feat, max_share=0.35); t0 = time.time(); proposals = []
    health = Health(feat); recent_lo = last - pd.Timedelta(days=180)
    for r in rules:
        H = r['H']; ev = Evaluator(feat, H)
        conds = [tuple(c) for c in r['conds']]
        base_st = ev.stats(rule_mask(feat, conds)); base_sc = score(base_st, **cons)
        best, best_sc = list(conds), base_sc
        for _ in range(2):
            for j, (f, op, t) in enumerate(best):
                grid = threshold_grid(feat, f, t)
                k0 = grid.index(t) if t in grid else min(range(len(grid)), key=lambda i: abs(grid[i] - t))
                for tt in grid[max(0, k0 - max_steps): k0 + max_steps + 1]:
                    trial = list(best); trial[j] = (f, op, float(tt))
                    sc = score(ev.stats(rule_mask(feat, trial), full=False), **cons)
                    if sc > best_sc + 1e-6:
                        st_full = ev.stats(rule_mask(feat, trial)); sc = score(st_full, **cons)
                        if sc > best_sc + 1e-6: best, best_sc = trial, sc
        new_st = ev.stats(rule_mask(feat, best))
        rec_old = health.stats(rule_mask(feat, conds), H, recent_lo, last)
        rec_new = health.stats(rule_mask(feat, best), H, recent_lo, last)
        changed = [c for c in best if c not in conds]
        mo = ev.month_code; m_old = rule_mask(feat, conds) & ev.valid; m_new = rule_mask(feat, best) & ev.valid
        c_old = np.bincount(mo[m_old], minlength=ev.nm); c_new = np.bincount(mo[m_new], minlength=ev.nm)
        s_old = np.bincount(mo[m_old], weights=ev.obj[m_old], minlength=ev.nm); s_new = np.bincount(mo[m_new], weights=ev.obj[m_new], minlength=ev.nm)
        okm = (c_old >= 20) & (c_new >= 20)
        month_better = float(((s_new[okm] / c_new[okm]) >= (s_old[okm] / c_old[okm])).mean()) if okm.sum() else 0.0
        accept = (bool(changed) and raw_score(new_st) > raw_score(base_st) + 0.003 and not constraint_fail(new_st, **cons)
                  and rec_new.get('beat', 0) >= rec_old.get('beat', 0) - 0.02 and rec_new.get('n', 0) >= 30 and month_better >= 0.6)
        proposals.append({'规则': r['id'], '当前条件': rule_text(conds), '建议条件': rule_text(best) if changed else '（不变）',
                          '当前评分': round(raw_score(base_st), 4), '当前不满足的约束': constraint_fail(base_st, **cons) or '—',
                          '建议评分': round(raw_score(new_st), 4), '新优于旧的月份占比': round(month_better, 2),
                          '当前 n/胜率/跑赢中位': f"{base_st['n']}/{base_st['win']:.0%}/{base_st['beat']:.0%}" if base_st else '—',
                          '建议 n/胜率/跑赢中位': f"{new_st['n']}/{new_st['win']:.0%}/{new_st['beat']:.0%}" if new_st else '—',
                          '近180日跑赢中位 当前→建议': f"{rec_old.get('beat', float('nan')):.0%} → {rec_new.get('beat', float('nan')):.0%}",
                          '建议采纳': accept, '_conds': [list(c) for c in best]})
        log(f"  {r['id']}：评分 {raw_score(base_st):.4f} → {raw_score(new_st):.4f}  {'建议修改' if accept else '保持'}（{time.time() - t0:.0f}s）")
    prop = pd.DataFrame(proposals)
    prop.drop(columns=['_conds']).to_csv(C.P('state', f'retune_{last.date()}.csv'), index=False, encoding='utf-8-sig')
    if apply:
        n_apply = 0
        for r in rules:
            p = prop[prop['规则'] == r['id']].iloc[0]
            if p['建议采纳']:
                r.setdefault('history', []).append({'date': str(last.date()), 'retune_from': r['conds'], 'retune_to': p['_conds'], 'score': [p['当前评分'], p['建议评分']]})
                r['conds'] = p['_conds']; n_apply += 1
        save_rules(rules); log(f'已应用 {n_apply} 条调参建议')
    return prop


# ---------------- ② 重新挖掘 ----------------
ITEM_FEATS = ['r_1', 'r_3', 'r_5', 'r_7', 'r_10', 'r_14', 'r_21', 'r_30', 'r_60', 'r_90', 'ma7_dev', 'ma14_dev', 'ma30_dev', 'ma60_dev', 'ma90_dev',
              'ma7_30', 'ma14_60', 'ma30_90', 'dd_7', 'dd_14', 'dd_30', 'dd_60', 'dd_90', 'up_7', 'up_14', 'up_30', 'up_60', 'up_90',
              'pos_14', 'pos_30', 'pos_60', 'pos_90', 'rsi_7', 'rsi_14', 'bb_pctb', 'bb_width', 'vol_7', 'vol_14', 'vol_30', 'atr14', 'vol_ratio',
              'streak', 'dsh_30', 'dsl_30', 'body', 'range', 'lower_shadow', 'upper_shadow', 'down_days_7', 'down_days_14', 'flat_14', 'logp',
              'rs_7', 'rs_30', 'r_30_rank', 'r_7_rank', 'dd_60_rank', 'vol_30_rank']
XSEC = ['rs_7', 'rs_30', 'r_30_rank', 'r_7_rank', 'dd_60_rank', 'vol_30_rank']

def build_conditions(df, feats, qs=(0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 0.8, 0.9, 0.95)):
    conds = []
    for f in feats:
        if f == 'logp':
            for p in [5, 20, 100, 500, 2000]: conds += [(f, '<=', float(np.log(p))), (f, '>=', float(np.log(p)))]
            continue
        if f == 'streak':
            for t in [-5, -4, -3, -2, -1, 1, 2, 3]: conds += [(f, '<=', float(t)), (f, '>=', float(t))]
            continue
        if f in ('rsi_7', 'rsi_14'):
            for t in [20, 25, 30, 35, 40, 50, 60, 70, 80]: conds += [(f, '<=', float(t)), (f, '>=', float(t))]
            continue
        x = df[f].dropna()
        for t in np.unique(np.round(x.quantile(list(qs)).values, 4)): conds += [(f, '<=', float(t)), (f, '>=', float(t))]
    return conds


class MaskCache:
    def __init__(self, df, conds):
        self.N = len(df); self.packed = {c: np.packbits(cond_mask(df, c)) for c in conds}
    def get(self, c): return np.unpackbits(self.packed[c], count=self.N).astype(bool)


def beam_search(df, ev, conds, depth=3, beam=8, cons=None, log=print):
    mc = MaskCache(df, conds); results = []; frontier = [((), ev.valid.copy())]; seen = set()
    for d in range(depth):
        cand = []
        for rule, m in frontier:
            used = {c[0] for c in rule}
            for c in conds:
                if c[0] in used: continue
                nr = tuple(sorted(rule + (c,)))
                if nr in seen: continue
                seen.add(nr)
                mm = m & mc.get(c)
                sc = score(ev.stats(mm, full=False), **cons)
                if sc > -9: cand.append((sc, nr, np.packbits(mm)))
        cand.sort(key=lambda z: -z[0])
        full = []
        for sc, nr, pm in cand[:max(beam, 50)]:
            mm = np.unpackbits(pm, count=len(df)).astype(bool); st = ev.stats(mm); sc2 = score(st, **cons)
            if sc2 > -9: full.append((sc2, nr, st, mm))
        full.sort(key=lambda z: -z[0])
        results += [(sc, nr, st) for sc, nr, st, _ in full[:50]]
        frontier = [(nr, mm) for _, nr, _, mm in full[:beam]]
        log(f'    depth {d + 1}: 候选 {len(cand)}，最佳评分 {full[0][0]:.4f}' if full else f'    depth {d + 1}: 无满足约束的候选')
        if not frontier: break
    results.sort(key=lambda z: -z[0])
    return results


def mine(feat, rules, last, hs=(14,), feats='item', depth=3, beam=8, oos_days=150, add=False, log=print):
    """束搜索 + 时序外测试；返回 {H: rows}。add=True 时把通过的候选加入规则库（probation）"""
    feats_use = ITEM_FEATS if feats == 'item' else [f for f in ITEM_FEATS if f not in XSEC]
    split = last - pd.Timedelta(days=oos_days)
    health = Health(feat); mined_all = {}
    exist_masks = {r['id']: rule_mask(feat, r['conds']) for r in rules}
    allm = np.ones(len(feat), bool)
    for H in hs:
        t0 = time.time()
        train = feat[feat.date + pd.Timedelta(days=H + 1) <= split].reset_index(drop=True)
        cons = make_constraints(train)
        conds = build_conditions(train, feats_use)
        log(f'  H={H}：训练期 ≤ {split.date()}（{len(train):,} 行），候选条件 {len(conds)}')
        ev = Evaluator(train, H)
        res = beam_search(train, ev, conds, depth=depth, beam=beam, cons=cons, log=log)
        seen_f, rows = set(), []
        base_oos = health.stats(allm, H, split + pd.Timedelta(days=1), last)
        for sc, nr, st in res:
            fs = tuple(sorted(c[0] for c in nr))
            if fs in seen_f: continue
            seen_f.add(fs)
            m_all = rule_mask(feat, nr)
            oos = health.stats(m_all, H, split + pd.Timedelta(days=1), last)
            overlap = max([(m_all & em).sum() / max(1, (m_all | em).sum()) for em in exist_masks.values()] + [0])
            passed = oos.get('n', 0) >= 100 and oos.get('beat', 0) >= 0.55 and oos.get('win', 0) >= 0.45
            rows.append({'规则': rule_text(nr), '评分': round(sc, 4), '训练 n': st['n'], '训练胜率': round(st['win'], 3), '训练跑赢中位': round(st['beat'], 3),
                         '月份数': st['n_months'], '正月占比': round(st['month_pos'], 2), '最大月占比': round(st['max_month_share'], 2),
                         'OOS n': oos.get('n', 0), 'OOS胜率': round(oos.get('win', float('nan')), 3), 'OOS中位': round(oos.get('med', float('nan')), 3),
                         'OOS跑赢中位': round(oos.get('beat', float('nan')), 3), '同期基准胜率': round(base_oos.get('win', float('nan')), 3),
                         '与现有规则最大重叠': round(overlap, 2), '通过': bool(passed), '_conds': [list(c) for c in nr]})
            if len(rows) >= 15: break
        log(f'  H={H} 完成，{len(rows)} 个候选，通过 {sum(r["通过"] for r in rows)} 个，用时 {(time.time() - t0) / 60:.1f} 分钟')
        mined_all[H] = rows
    with open(C.P('state', f'mined_{last.date()}.json'), 'w', encoding='utf-8') as f:
        json.dump({'split': str(split.date()), 'feats': feats, 'results': {str(k): v for k, v in mined_all.items()}}, f, ensure_ascii=False, indent=1)
    if add:
        added = 0
        for H, rows in mined_all.items():
            for k, row in enumerate([x for x in rows if x['通过'] and x['与现有规则最大重叠'] < 0.6][:2], 1):
                rid = f'X{H}-{last.strftime("%m%d")}-{k}'
                rules.append({'id': rid, 'group': {10: '短线', 14: '中线', 30: '长线'}.get(H, '中线'), 'name': '自动挖掘', 'H': H, 'hold': f'{H}天', 'status': 'probation',
                              'conds': row['_conds'], 'mkt_filter': [], 'ref': {'win': row['训练胜率'], 'beat': row['训练跑赢中位'], 'test_win': row['OOS胜率'], 'test_med': row['OOS中位']},
                              'note': f'自动挖掘于 {last.date()}，OOS {row["OOS n"]} 笔 胜率 {row["OOS胜率"]:.0%} 跑赢中位 {row["OOS跑赢中位"]:.0%}',
                              'created': str(last.date()), 'data_end_at_creation': str(last.date()), 'history': []})
                added += 1
        save_rules(rules); log(f'已加入 {added} 条新规则（probation）')
    return mined_all
