# -*- coding: utf-8 -*-
"""LightGBM 排序模型：目标 = 次日入场收益 − 当日全市场中位（只做当日候选间排序）"""
import os, json, time
import numpy as np, pandas as pd
from . import config as C
from .features import LAG_H, feature_cols
from .rules import rule_mask, NICE

META_PATH = C.P('state', 'ml_meta.json')
MODEL_PATH = lambda H: C.P('state', f'lgb_H{H}.txt')


def load_models(fcols_default, log=print):
    """只加载验证 RankIC ≥ ML_MIN_IC 的模型；返回 dict H -> (booster, feature list)"""
    import lightgbm as lgb
    models = {}
    if not os.path.exists(META_PATH): return models
    meta = json.load(open(META_PATH, encoding='utf-8'))
    for H in LAG_H:
        p = MODEL_PATH(H); ic = meta.get('val', {}).get(str(H), {}).get('rank_ic', 0)
        if os.path.exists(p) and ic >= C.ML_MIN_IC:
            models[H] = (lgb.Booster(model_file=p), meta.get('features', fcols_default))
        elif os.path.exists(p):
            log(f'LightGBM H={H} 验证 RankIC={ic:.3f} < {C.ML_MIN_IC}，不使用')
    if models: log(f'已加载 LightGBM 模型 H={list(models)}（训练于 {meta.get("trained")}，数据截至 {meta.get("data_end")}）')
    return models


def make_scorer(models):
    if not models: return None
    def scorer(day):
        out = {}
        for H, (m, fcols) in models.items():
            X = day.reindex(columns=fcols).astype('float32')
            p = pd.Series(m.predict(X), index=day.index)
            out[f'ML分位{H}'] = (p.rank(pct=True) * 100).round(0)
        return pd.DataFrame(out, index=day.index)
    return scorer


def _target(df, H):
    y = df[f'fwdL_{H}']
    return (y - y.groupby(df['date']).transform('median')).clip(-0.9, 1.5)


def train(feat, rules, last, val_days=90, rounds=300, log=print):
    import lightgbm as lgb
    fcols = feature_cols(feat)
    params = dict(objective='regression_l1', learning_rate=0.05, num_leaves=31, min_data_in_leaf=500, feature_fraction=0.7,
                  bagging_fraction=0.7, bagging_freq=1, lambda_l2=10, verbose=-1, num_threads=os.cpu_count() or 2)
    meta = {'trained': str(C.now_cst())[:19], 'data_end': str(last.date()), 'features': fcols, 'val': {}}
    lines = []
    for H in LAG_H:
        t0 = time.time()
        y = _target(feat, H); ok = y.notna()
        split = last - pd.Timedelta(days=val_days)
        tr = ok & (feat.date + pd.Timedelta(days=H + 1) <= split)
        te = ok & (feat.date > split)
        if tr.sum() < 5000 or te.sum() < 1000:
            log(f'  H={H} 样本不足，跳过'); continue
        m = lgb.train(params, lgb.Dataset(feat.loc[tr, fcols], y[tr]), num_boost_round=rounds)
        sub = feat.loc[te, ['date', 'name', f'fwdL_{H}']].copy(); sub['p'] = m.predict(feat.loc[te, fcols]); sub['exm'] = y[te]
        sub['net'] = (1 + sub[f'fwdL_{H}']) * (1 - C.FEE) - 1
        q = sub.groupby('date')['p'].rank(pct=True); sub['q'] = np.minimum((q * 5).astype(int), 4) + 1
        g = sub.groupby('q').agg(n=('net', 'size'), 净胜率=('net', lambda s: (s > 0).mean()), 中位净收益=('net', 'median'), 跑赢中位=('exm', lambda s: (s > 0).mean()))
        ic = sub.groupby('date').apply(lambda d: d['p'].corr(d[f'fwdL_{H}'], method='spearman') if len(d) > 20 else np.nan).mean()
        log(f'  H={H}  训练 {int(tr.sum()):,} 行（标签截止 {split.date()}），验证最近 {val_days} 天 {int(te.sum()):,} 行，日均 RankIC={ic:.3f}')
        log('  ' + g.round(3).to_string().replace('\n', '\n  '))
        for r in rules:
            if r['H'] != H: continue
            mm = rule_mask(feat, r['conds'])[te.values]
            s = sub[mm]
            if len(s) >= 40:
                hi = s[s.p >= s.p.median()]; lo = s[s.p < s.p.median()]
                log(f"  规则 {r['id']} 验证期 {len(s)} 笔：模型看好的一半 胜率 {(hi.net > 0).mean():.0%} vs 另一半 {(lo.net > 0).mean():.0%}")
        meta['val'][str(H)] = {'rank_ic': round(float(ic), 4), 'top_win': round(float(g.loc[5, '净胜率']), 3), 'bottom_win': round(float(g.loc[1, '净胜率']), 3),
                               'top_beat': round(float(g.loc[5, '跑赢中位']), 3), 'n_test': int(te.sum())}
        m_full = lgb.train(params, lgb.Dataset(feat.loc[ok, fcols], y[ok]), num_boost_round=rounds)
        m_full.save_model(MODEL_PATH(H))
        imp = pd.Series(m_full.feature_importance('gain'), index=fcols).sort_values(ascending=False)
        log(f'  重要特征: {", ".join(NICE.get(k, k) for k in imp.index[:8])} | 用时 {time.time() - t0:.0f}s')
        lines.append(f'H={H}: RankIC {ic:.3f}，第5组/第1组 跑赢中位 {g.loc[5, "跑赢中位"]:.0%}/{g.loc[1, "跑赢中位"]:.0%}，净胜率 {g.loc[5, "净胜率"]:.0%}/{g.loc[1, "净胜率"]:.0%}' + ('' if ic >= C.ML_MIN_IC else '（未达标，不启用）'))
    with open(META_PATH, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    return lines
