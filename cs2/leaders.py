"""Causal peer confirmation and strength ranking; no volume/liquidity claims."""
import numpy as np
import pandas as pd


def leader_watch(feat, rules, date):
    from .rules import strategy_mask
    cols = ['饰品', '规则', '健康状态', '强度分', '同类7日超额%', '扫描放行']
    day = feat[(feat.date == date) & feat.eligible & (feat.flat_14 <= .5)]
    rows = []
    for r in rules:
        if not r['id'].startswith('RB'): continue
        for _, a in day[strategy_mask(day, r) & (day.leader_flag > 0)].iterrows():
            rows.append([str(a['name']), r['id'], r['status'], round(a.leader_score*100,1),
                         round(a.peer_rs7*100,1), '通过' if r['status']=='active' else '未通过'])
    return pd.DataFrame(rows, columns=cols).sort_values('强度分', ascending=False, kind='stable')


def add_peer_features(feat):
    out = feat.copy()
    weapon = out.name.astype(str).str.split(' | ', regex=False).str[0]
    out['peer_group'] = weapon.where(out.cat.astype(str) != 'gloves_MW_FT', '手套')
    # Fixed numeric IDs are stable when the universe changes.
    out['peer_code'] = out.peer_group.map({'手套': 1, 'AK-47': 2, 'M4A4': 3, 'USP-S': 4, 'Glock-18': 5}).fillna(0)
    ok = out.eligible & (out.flat_14 <= .5)
    key = [out.date, out.peer_group]
    out['peer_n'] = ok.groupby(key).transform('sum')
    for horizon in [1, 3, 7]:
        value = out[f'r_{horizon}'].where(ok)
        out[f'peer_med_{horizon}'] = value.groupby(key).transform('median')
        out[f'peer_rank_{horizon}'] = value.groupby(key).rank(pct=True)
    out['peer_breadth1'] = (out.r_1 > 0).where(ok).groupby(key).transform('mean')
    out['leader_score'] = .25 * out.peer_rank_1 + .35 * out.peer_rank_3 + .40 * out.peer_rank_7
    out['peer_rs7'] = out.r_7 - out.peer_med_7
    # A high rank in a falling group alone is not a leader signal.
    out['leader_flag'] = ((out.leader_score >= .70) & (out.r_3 > 0)
                          & (out.r_7 > 0) & (out.peer_rs7 > 0) & ok).astype(float)
    return out


def reversal_rules(created):
    common = [['peer_n', '>=', 8], ['peer_breadth1', '>=', .55],
              ['peer_med_1', '>=', .005], ['dd_60', '<=', -.10],
              ['dsl_30', '>=', 1], ['dsl_30', '<=', 10],
              ['r_1', '>=', .01], ['r_7', '>=', -.03],
              ['up_7', '>=', .03], ['ma7_dev', '>=', 0],
              ['up_7', '<=', .30], ['r_1', '<=', .20]]
    result = []
    for code, family in [(1, '手套'), (2, 'AK'), (3, 'M4A4'), (4, 'USP'), (5, '格洛克')]:
        result.append(dict(id=f'RB{code}', group='品类反弹', name=f'{family}近期低点后同步反弹',
                           H=14, hold='14天', status='active',
                           conds=common + [['peer_code', '>=', code], ['peer_code', '<=', code]],
                           mkt_filter=[], created=created, data_end_at_creation=created,
                           history=[], note='研究规则，指定日期参与设计；尚无独立外测。排名不代表流动性。'))
    return result
