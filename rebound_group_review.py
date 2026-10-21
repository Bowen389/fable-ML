"""Separate sector leadership from individual rank; no item-score bonuses."""
import json
import os
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'/'rebound_groups'

def group_name(name,firstgen):
    if name in firstgen:return '一代手套_略磨'
    if 'Gloves' in name or 'Wraps' in name:
        return '其他手套_略磨' if '(Minimal Wear)' in name else '手套_久经及其他'
    if not any(w in name for w in ('(Factory New)','(Minimal Wear)','(Field-Tested)')):return '探员'
    return name.split('|')[0].strip()

def group_ranks(frame,firstgen,min_items=8):
    d=frame.copy();d['group']=d.name.map(lambda n:group_name(n,firstgen))
    q=d.groupby(['date','group']).agg(items=('name','nunique'),median_score=('raw','median'),median_net7=('y7','median'),median_net14=('y14','median')).reset_index()
    q=q[q['items']>=min_items].copy()
    q['rank']=q.groupby('date').median_score.rank(ascending=False,method='min')
    q['groups_available']=q.groupby('date')['group'].transform('count')
    return q

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    source=ROOT/'output/rebound_shared/development_rows.csv.gz'
    if not source.exists():raise RuntimeError('Shared-factor experiment must finish before group review')
    cases=json.loads((ROOT/'research/bear_rebound_cases.json').read_text());firstgen={x['name'] for x in cases['events'][0]['members']}
    d=pd.read_csv(source,parse_dates=['date']);q=group_ranks(d,firstgen)
    q.sort_values(['date','rank']).to_csv(OUT/'group_rankings.csv',index=False,encoding='utf-8-sig')
    cohort=q[q['group'].eq('一代手套_略磨')].sort_values('date');cohort.to_csv(OUT/'firstgen_timeline.csv',index=False,encoding='utf-8-sig')
    meta={'source':'output/rebound_shared/development_rows.csv.gz','source_run_id':os.environ.get('GITHUB_RUN_ID'),'min_group_size':8,'members':len(firstgen),'group_score':'成员已有单品开发公式分数的中位数；不增加单品分数','production_modified':False,'independent_validation':False}
    (OUT/'manifest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
    lines=['# 板块领先与单品领先分开核对','一代略磨手套是用户指定的24款板块篮子，不预设24款都必须是单品涨幅前30。','使用同一单品开发公式分数的中位数比较板块，最少8件；没有给名单成员增加分数。','评分来自已看过这些事件的开发公式，本报告仍是描述性回放，不是独立预测验证。','报价和成交量不足造成的成员变化会在items中列出；组别使用固定划分，不是官方指数。','','| 日期 | 一代略磨成员 | 板块名次/可比较组 | 中位开发分 | 后续7日净收益中位 | 后续14日净收益中位 |','|---|---:|---:|---:|---:|---:|']
    anchor=pd.Timestamp(cases['events'][0]['dates'][0])
    for offset in (-7,-3,0,1,3,7):
        date=anchor+pd.Timedelta(days=offset);z=cohort[cohort.date.eq(date)]
        if z.empty:continue
        x=z.iloc[0];p=lambda v:'—' if pd.isna(v) else f'{v:.2%}'
        lines.append(f'| {date.date()} | {x["items"]} | {int(x["rank"])}/{int(x["groups_available"])} | {100*x["median_score"]:.1f} | {p(x["median_net7"])} | {p(x["median_net14"])} |')
    lines+=['','板块进入前列可以提示观察这一组；组内买入排序仍需检查单品相对涨幅、量能、可交易性和剩余上涨空间。板块强不等于每个成员都应当买入。']
    text='\n'.join(lines)+'\n';(OUT/'report.md').write_text(text)
    if os.environ.get('GITHUB_STEP_SUMMARY'):Path(os.environ['GITHUB_STEP_SUMMARY']).write_text(text)
    print('GROUP_REVIEW_COMPLETE',len(q),flush=True)
if __name__=='__main__':main()
