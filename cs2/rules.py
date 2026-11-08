# -*- coding: utf-8 -*-
"""规则库：条件表达、默认规则、读写 state/rules.json"""
import os, json
import numpy as np
from . import config as C

NICE = {
 'r_1': '1日涨跌幅', 'r_3': '3日涨跌幅', 'r_5': '5日涨跌幅', 'r_7': '7日涨跌幅', 'r_10': '10日涨跌幅', 'r_14': '14日涨跌幅', 'r_21': '21日涨跌幅',
 'r_30': '30日涨跌幅', 'r_45': '45日涨跌幅', 'r_60': '60日涨跌幅', 'r_90': '90日涨跌幅',
 'ma7_dev': '偏离MA7', 'ma14_dev': '偏离MA14', 'ma30_dev': '偏离MA30', 'ma60_dev': '偏离MA60', 'ma90_dev': '偏离MA90',
 'ma7_30': 'MA7/MA30-1', 'ma14_60': 'MA14/MA60-1', 'ma30_90': 'MA30/MA90-1',
 'dd_7': '距7日最高回撤', 'dd_14': '距14日最高回撤', 'dd_30': '距30日最高回撤', 'dd_60': '距60日最高回撤', 'dd_90': '距90日最高回撤',
 'up_7': '距7日最低反弹', 'up_14': '距14日最低反弹', 'up_30': '距30日最低反弹', 'up_60': '距60日最低反弹', 'up_90': '距90日最低反弹',
 'pos_7': '7日区间位置', 'pos_14': '14日区间位置', 'pos_30': '30日区间位置', 'pos_60': '60日区间位置', 'pos_90': '90日区间位置',
 'rsi_7': 'RSI7', 'rsi_14': 'RSI14', 'bb_pctb': '布林%b', 'bb_width': '布林带宽', 'vol_7': '7日波动率', 'vol_14': '14日波动率', 'vol_30': '30日波动率',
 'atr14': 'ATR14/价格', 'vol_ratio': '短/长波动比', 'streak': '连涨(+)/连跌(-)天数', 'dsh_30': '距30日高点天数', 'dsl_30': '距30日低点天数',
 'body': '当日实体', 'range': '当日振幅', 'lower_shadow': '下影线', 'upper_shadow': '上影线', 'down_days_7': '近7日下跌天数', 'down_days_14': '近14日下跌天数',
 'flat_14': '近14日无波动占比', 'logp': '价格', 'breadth7': '市场:7日上涨占比', 'above_ma30': '市场:站上MA30占比',
 'mkt_med_r7': '市场:7日涨跌中位', 'mkt_med_r30': '市场:30日涨跌中位', 'mkt_r_3': '指数3日涨跌', 'mkt_r_7': '指数7日涨跌', 'mkt_r_14': '指数14日涨跌',
 'mkt_r_30': '指数30日涨跌', 'mkt_r_60': '指数60日涨跌', 'mkt_dd_90': '指数距90日高回撤', 'mkt_up_90': '指数距90日低反弹',
 'mkt_ma30_dev': '指数偏离MA30', 'mkt_vol_14': '市场14日波动率', 'rs_7': '7日相对强弱', 'rs_30': '30日相对强弱',
 'r_30_rank': '30日涨幅分位', 'r_7_rank': '7日涨幅分位', 'dd_60_rank': '60日回撤分位', 'vol_30_rank': '30日波动率分位', 'cat_code': '品类码', 'dow': '星期',
}
RAW_UNITS = {'pos_7', 'pos_14', 'pos_30', 'pos_60', 'pos_90', 'bb_pctb', 'r_30_rank', 'r_7_rank', 'dd_60_rank', 'vol_30_rank',
             'streak', 'dsh_30', 'dsl_30', 'down_days_7', 'down_days_14', 'rsi_7', 'rsi_14', 'cat_code', 'dow', 'logp'}
NICE.update(peer_n='同类有效报价数', peer_breadth1='同类当日上涨占比', peer_med_1='同类当日涨幅中位',
            peer_code='品类编码', leader_score='同类强度分', peer_rs7='同类7日超额')
RAW_UNITS.update({'peer_n', 'peer_code'})

def fmt_cond(f, op, t):
    op = op.replace('<=', '≤').replace('>=', '≥')
    if f == 'logp': return f'价格 {op} {np.exp(t):.0f} 元'
    if f == 'cat_code': return '仅枪械' if t == 0 else f'品类码 {op} {t:g}'
    if f in RAW_UNITS: return f'{NICE.get(f, f)} {op} {t:g}'
    return f'{NICE.get(f, f)} {op} {t * 100:.1f}%'

def fmt_val(f, v):
    if f == 'logp': return f'{np.exp(v):.2f} 元'
    if f in RAW_UNITS: return f'{v:.3g}'
    return f'{v * 100:.1f}%'

def rule_text(conds):
    return ' 且 '.join(fmt_cond(*c) for c in conds)

def cond_mask(df, c):
    f, op, t = c; x = df[f].values
    return (x <= t) if op == '<=' else (x >= t)

def eligible_mask(df):
    return df['eligible'].fillna(False).to_numpy(bool) if 'eligible' in df else np.ones(len(df), bool)

def strategy_mask(df, rule):
    return rule_mask(df, rule['conds']) & rule_mask(df, rule.get('mkt_filter', []))

def rule_mask(df, conds):
    m = eligible_mask(df)
    for c in conds: m &= cond_mask(df, c)
    return m


RULES_PATH = C.P('state', 'rules.json')
DEFAULT_RULES = [
 {'id': 'S1', 'group': '短线', 'name': '深跌筑底+波动收敛', 'H': 10, 'hold': '10~14天', 'status': 'active',
  'conds': [['dd_60_rank', '<=', 0.20], ['dsl_30', '>=', 25], ['vol_ratio', '<=', 0.30]], 'mkt_filter': [],
  'ref': {'win': 0.593, 'med': 0.041, 'beat': 0.662, 'test_win': 0.391, 'test_med': -0.034},
  'note': '持 14 天 (62%/+6.5%) 好于持 10 天；止损 -10%，止盈 +10~15%'},
 {'id': 'M3', 'group': '中线', 'name': '远离MA90+止跌(抗熊市)', 'H': 14, 'hold': '14天', 'status': 'active',
  'conds': [['ma90_dev', '<=', -0.379], ['pos_60', '>=', 0.03], ['up_14', '<=', 0.092]], 'mkt_filter': [],
  'ref': {'win': 0.569, 'med': 0.036, 'beat': 0.645, 'test_win': 0.57, 'test_med': 0.034},
  'note': '唯一在 2026-05~09 熊市里净收益仍为正的规则；收益薄，信号多时分散小仓位'},
 {'id': 'M4', 'group': '中线', 'name': '深跌筑底+缩量+枪械5~100元', 'H': 14, 'hold': '14天', 'status': 'active',
  'conds': [['dd_60_rank', '<=', 0.10], ['dsl_30', '>=', 25], ['vol_7', '<=', 0.074], ['cat_code', '<=', 0], ['logp', '>=', float(np.log(5))], ['logp', '<=', float(np.log(100))]],
  'mkt_filter': [], 'ref': {'win': 0.608, 'med': 0.071, 'beat': 0.675, 'test_win': 0.49, 'test_med': -0.002},
  'note': '数字最好但含人工过滤，实盘打折看；持 30 天也可 (60%/+9.5%)'},
 {'id': 'L1', 'group': '长线', 'name': '深跌+MA7上穿MA30', 'H': 30, 'hold': '30~45天', 'status': 'active',
  'conds': [['dd_60_rank', '<=', 0.10], ['ma7_30', '>=', 0.024], ['up_7', '<=', 0.335]], 'mkt_filter': [['mkt_dd_90', '>=', -0.15]],
  'ref': {'win': 0.60, 'med': 0.097, 'beat': 0.66, 'test_win': 0.35, 'test_med': -0.105},
  'note': '只在择时满足(指数距90日高点<15%)时用，满足时 65%/+15.3%；否则熊市里 35%/-10.5%。分批止盈 +20~30%，止损 -15~-20%'},
 {'id': 'L3', 'group': '长线', 'name': '深跌筑底+低价≤20元', 'H': 30, 'hold': '30~60天', 'status': 'active',
  'conds': [['dd_60_rank', '<=', 0.10], ['dsl_30', '>=', 21], ['logp', '<=', float(np.log(20))]], 'mkt_filter': [],
  'ref': {'win': 0.576, 'med': 0.085, 'beat': 0.66, 'test_win': 0.45, 'test_med': -0.042},
  'note': '低价饰品买卖价差比例大，实际收益再打折'},
]

def load_rules():
    if not os.path.exists(RULES_PATH):
        rules = []
        for r in DEFAULT_RULES:
            r = dict(r); r['created'] = str(C.TODAY.date()); r['data_end_at_creation'] = '2026-09-22'; r['history'] = []
            rules.append(r)
        from .leaders import reversal_rules
        rules.extend(reversal_rules(str(C.TODAY.date())))
        save_rules(rules)
        print('已初始化规则库 state/rules.json')
    with open(RULES_PATH, encoding='utf-8') as f:
        return json.load(f)['rules']

def save_rules(rules):
    with open(RULES_PATH, 'w', encoding='utf-8') as f:
        json.dump({'updated': str(C.now_cst())[:19], 'fee': C.FEE, 'rules': rules}, f, ensure_ascii=False, indent=1)
