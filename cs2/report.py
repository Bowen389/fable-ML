# -*- coding: utf-8 -*-
"""生成 Markdown 报告（output/latest.md + GitHub Step Summary）和推送用短消息"""
import pandas as pd
import json, os
from .scan import sort_hits
from . import config as C


def md_table(df, max_rows=60):
    if df is None or len(df) == 0: return '_（无）_\n'
    df = df.head(max_rows)
    cols = [str(c) for c in df.columns]
    def cell(v):
        if isinstance(v, float):
            if pd.isna(v): return ''
            return f'{v:.4g}' if abs(v) < 1e4 else f'{v:.0f}'
        return str(v).replace('|', '\\|').replace('\n', ' ')
    lines = ['| ' + ' | '.join(cols) + ' |', '|' + '---|' * len(cols)]
    for _, row in df.iterrows():
        lines.append('| ' + ' | '.join(cell(v) for v in row.values) + ' |')
    return '\n'.join(lines) + '\n'


def build_markdown(ctx):
    """ctx: dict(last, snap, notes, hits, near, sig, health, new_status, fetch_info, n_items, broad_line, ml_note)"""
    last = ctx['last']; snap = ctx['snap']
    L = [f"# CS2 买点扫描 · {last.date()}", '']
    L.append(f"**市场状态**：站上MA30占比 {snap['above_ma30']:.1%} · 7日上涨占比 {snap['breadth7']:.1%} · 指数 7日 {snap['mkt_r_7']:+.1%} / 14日 {snap['mkt_r_14']:+.1%} / 30日 {snap['mkt_r_30']:+.1%} · 偏离MA30 {snap['mkt_ma30_dev']:+.1%} · 距90日高 {snap['mkt_dd_90']:+.1%} · 14日波动 {snap['mkt_vol_14']:.2%}")
    L.append('')
    for n in ctx['notes']: L.append(f'- {n}')
    if ctx.get('broad_line'): L.append(f"- {ctx['broad_line']}")
    if ctx.get('ml_note'): L.append(f"- {ctx['ml_note']}")
    meta_path = C.P('state', 'ml_meta.json')
    if os.path.exists(meta_path):
        with open(meta_path, encoding='utf-8') as f: meta = json.load(f)
        if meta.get('pipeline_version') != C.PIPELINE_VERSION:
            L.append('- ML旧口径已停用，等待因果清洗重训。')
        elif not any(v.get('validated', False) for v in meta.get('val', {}).values()):
            L.append('- ML已重训，所有周期未通过滚动验证或绝对净收益要求，均不启用。')
    L.append('')
    hits = ctx['hits']
    L.append(f"## 买点（{ctx['n_items']} 个饰品中）")
    if hits is None or hits.empty:
        L.append('当前没有通过报价质量、规则健康度、形态及择时条件的买点。')
    else:
        cnt = hits.groupby('规则').size()
        L.append('、'.join(f'{k}：{v}' for k, v in cnt.items()))
        L.append('')
        show = sort_hits(hits).drop(columns=[c for c in ['_H', '_rid', '_mk'] if c in hits])
        L.append(md_table(show, 80))
    near = ctx['near']
    if near is not None and not near.empty:
        L.append(f'## 接近满足（只差一个条件）{len(near)} 条')
        L.append(md_table(near.drop(columns=[c for c in ['距14日低反弹%', 'RSI14', '短/长波动比'] if c in near]), 40))
    sig = ctx['sig']
    if sig is not None and len(sig) and 'pipeline_version' in sig:
        legacy_n = int((sig.pipeline_version != C.PIPELINE_VERSION).sum())
        if legacy_n: L.append(f'旧口径记录 {legacy_n} 条保留在 signals.csv，不计入新口径战绩。')
        sig = sig[sig.pipeline_version == C.PIPELINE_VERSION]
    L.append('## 信号日志（前瞻模拟记录；非真实成交/账户收益）')
    if sig is None or sig.empty:
        L.append('尚无记录。')
    else:
        vc = sig['status'].value_counts().to_dict()
        L.append(f"累计 {len(sig)} 条：" + '，'.join(f'{k} {v}' for k, v in vc.items()))
        closed = sig[sig.status == 'closed']
        if len(closed):
            g = closed.groupby('rule_id').agg(笔数=('net_ret', 'size'), 净胜率=('net_ret', lambda s: (s > 0).mean()), 中位净收益=('net_ret', 'median'), 均值=('net_ret', 'mean')).reset_index()
            g['净胜率'] = g['净胜率'].map('{:.0%}'.format); g['中位净收益'] = g['中位净收益'].map('{:+.1%}'.format); g['均值'] = g['均值'].map('{:+.1%}'.format)
            L.append(''); L.append(md_table(g))
        op = sig[sig.status == 'open']
        if len(op):
            L.append(f"模拟未到期 {len(op)} 条，浮动净收益中位 {op.net_ret.median():+.1%}")
            o = op[['signal_date', 'rule_id', 'name', 'entry_price', 'exit_date', 'net_ret']].sort_values('exit_date').copy()
            o['signal_date'] = o['signal_date'].dt.date; o['exit_date'] = o['exit_date'].dt.date; o['net_ret'] = o['net_ret'].map('{:+.1%}'.format)
            L.append(''); L.append(md_table(o, 30))
    L.append('模拟口径：次日真实日K收盘指数入场，固定H天退出；扣手续费和双边滑点。缺报价不填造成交；跨规则同饰品不重复开仓。未模拟订单簿、交易限制和账户资金。')
    L.append('## 规则健康度（次日入场、扣费及滑点）')
    L.append('"跑赢中位" = 跑赢当日全市场中位数的比例（相对优势）；基准 = 同期随便买的胜率。判定：90 日跑赢中位 ≥55% 正常 / 50~55% watch / <50% probation / 180 日 <45% disabled；90日或有足够样本的30日中位净收益≤0则 probation，只有active且择时通过才发买点。健康度按同饰品H+1日间隔去重；仍有共同市场风险，不是账户收益。')
    L.append('')
    L.append(md_table(ctx['health']))
    ns = ctx.get('new_status') or {}
    if ns:
        L.append('**状态变更**：' + '；'.join(f"{rid}: {old} → {new}（90日 跑赢中位 {s90['beat']:.0%}，n={s90['n']}）" for rid, (old, new, s90, _) in ns.items()))
    fi = ctx.get('fetch_info') or {}
    if fi:
        L.append('')
        L.append(f"<sub>数据更新：需更新 {fi.get('todo', 0)}，成功 {fi.get('ok', 0)}，失败 {fi.get('fail', 0)}" + (f"，每饰品返回 {fi.get('hist_med')} 条" if fi.get('hist_med') else '') + ('，**已到时间上限未完成**' if fi.get('stopped') else '') + '</sub>')
    return '\n'.join(L) + '\n'


def build_short(ctx, max_len=1800):
    last = ctx['last']; snap = ctx['snap']; hits = ctx['hits']
    L = [f"CS2 买点扫描 {last.date()}",
         f"站上MA30 {snap['above_ma30']:.0%} | 指数14日 {snap['mkt_r_14']:+.1%} | 距90日高 {snap['mkt_dd_90']:+.1%}"]
    L += [n.split('→')[-1].strip() for n in ctx['notes'][:2]]
    if hits is None or hits.empty:
        L.append('买点：无')
    else:
        cnt = hits.groupby('_rid').size()
        L.append('买点：' + '，'.join(f'{k} {v} 个' for k, v in cnt.items()))
        for rid, sub in hits.groupby('_rid'):
            names = sort_hits(sub)['饰品'].head(5).tolist()
            L.append(f'[{rid}] ' + '；'.join(n.replace(' (Factory New)', ' FN') for n in names) + ('…' if len(sub) > 5 else ''))
    ns = ctx.get('new_status') or {}
    if ns: L.append('规则状态变更：' + '，'.join(f'{k} {v[0]}→{v[1]}' for k, v in ns.items()))
    sig = ctx['sig']
    if sig is not None and len(sig) and 'pipeline_version' in sig:
        legacy_n = int((sig.pipeline_version != C.PIPELINE_VERSION).sum())
        if legacy_n: L.append(f'旧口径记录 {legacy_n} 条保留在 signals.csv，不计入新口径战绩。')
        sig = sig[sig.pipeline_version == C.PIPELINE_VERSION]
    if sig is not None and len(sig):
        closed = sig[sig.status == 'closed']
        if len(closed): L.append(f"已结算 {len(closed)} 笔：胜率 {(closed.net_ret > 0).mean():.0%}，中位 {closed.net_ret.median():+.1%}")
    txt = '\n'.join(L)
    return txt[:max_len]
