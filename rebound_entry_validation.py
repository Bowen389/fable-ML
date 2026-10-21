"""Frozen 40/20/40 ranking with causal first-entry/chase filters, full-period diagnostics."""
import concurrent.futures as futures
import json
import os
from pathlib import Path
import numpy as np
import pandas as pd
from leader_research import CACHE,collect
from bear_rebound_research import feature_frame,net_ratio
from rebound_rank_research import enrich,daily_rank
from rebound_stage_research import add_stages,include_registered_items,clean_json
from rebound_shared_factors import factor_frame,FACTORS
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'/'rebound_entries'
WEIGHTS=np.array([.4,.2,.4,0,0,0])

def entry_masks(d):
    top=d.eligible&d['rank'].le(30)
    first=pd.Series(False,index=d.index)
    for _,g in d.groupby('name',sort=False):
        prior_top=top.loc[g.index].shift().rolling(7,min_periods=7).sum()
        prior_quotes=(g.close.notna()&g.volume.gt(0)).shift().rolling(7,min_periods=7).sum()
        first.loc[g.index]=top.loc[g.index]&prior_top.eq(0)&prior_quotes.eq(7)
    cap=d.r7.le(.15)
    return {'top30_control':top,'first_entry_7d':first,'cap_r7_15':top&cap,'first_entry_cap15':first&cap,'first_cap_local_repair':first&cap&d.environment_ok}

def outcomes(d,H):
    result=pd.Series(np.nan,index=d.index)
    for _,g in d.groupby('name',sort=False):
        valid=pd.concat([g.close.shift(-j).notna()&g.volume.shift(-j).gt(0) for j in range(1,H+2)],axis=1).all(axis=1)
        result.loc[g.index]=net_ratio(g.close.shift(-(H+1))/g.close.shift(-1)).where(valid)
    return result

def make_trades(d,mask,H,latest):
    rows=[]
    for name,g in d[mask].sort_values(['name','date']).groupby('name',sort=False):
        nextday=pd.Timestamp.min
        for idx,x in g.iterrows():
            if x.date<nextday:continue
            nextday=x.date+pd.Timedelta(days=H+2)
            value=x['net'+str(H)]
            rows.append({'name':name,'cn':x.cn,'signal_date':str(x.date.date()),'entry_date':str((x.date+pd.Timedelta(days=1)).date()),'exit_date':str((x.date+pd.Timedelta(days=H+1)).date()),'net':float(value) if pd.notna(value) else None,'status':'evaluated' if pd.notna(value) else 'not_mature' if x.date+pd.Timedelta(days=H+1)>latest else 'missing_quote_or_volume','rank':float(x['rank']),'score':float(x.score),'r7':float(x.r7) if pd.notna(x.r7) else None,'factor_coverage':float(x.factor_coverage),'known_event_window':bool(x.known_event_window)})
    return rows

def summarize(rows):
    observed=[x for x in rows if x['net'] is not None]
    if not observed:return {'signals':len(rows),'n':0,'items':0,'mean':None,'median':None,'win':None,'p10':None}
    q=pd.DataFrame(observed)
    return {'signals':len(rows),'n':len(q),'items':int(q.name.nunique()),'mean':float(q.net.mean()),'median':float(q.net.median()),'win':float(q.net.gt(0).mean()),'p10':float(q.net.quantile(.1))}

def main():
    OUT.mkdir(parents=True,exist_ok=True);CACHE.mkdir(exist_ok=True)
    cases=json.loads((ROOT/'research/bear_rebound_cases.json').read_text());u=include_registered_items(json.loads((ROOT/'firepulse_universe.json').read_text()),cases)
    excluded=('Nova |','XM1014 |','MAG-7 |','Sawed-Off |','Negev |','M249 |','R8 Revolver |')
    u=[x for x in u if x.get('id') and not x['name'].startswith(excluded)];today=pd.Timestamp.now(tz='Asia/Shanghai').tz_localize(None).normalize();frames=[];fail=[]
    with futures.ThreadPoolExecutor(max_workers=3) as ex:
        jobs={ex.submit(collect,x,today):x for x in u}
        for i,f in enumerate(futures.as_completed(jobs),1):
            try:frames.append(f.result())
            except Exception as e:fail.append({'name':jobs[f]['name'],'error':str(e)})
            if i%100==0:print('FETCH',i,'loaded',len(frames),flush=True)
    if not frames:raise RuntimeError('No history')
    d,_=add_stages(enrich(feature_frame(pd.concat(frames,ignore_index=True))[0]));d=factor_frame(d);latest=d[d.eligible].date.max()
    d['score']=100*(d[FACTORS].fillna(0).to_numpy()@WEIGHTS);d['factor_coverage']=d[FACTORS[:3]].notna().mean(axis=1)
    d['rank']=daily_rank(d,d.score.where(d.eligible));d['known_event_window']=False
    for event in cases['events']:
        anchor=pd.Timestamp(event['dates'][0]);d['known_event_window']|=d.date.between(anchor-pd.Timedelta(days=30),anchor+pd.Timedelta(days=30))
    masks=entry_masks(d)
    for H in (7,10,14):d['net'+str(H)]=outcomes(d,H)
    trades=[];summaries=[]
    periods=[('2025','2025-01-01','2025-12-31'),('2026_Q1','2026-01-01','2026-03-31'),('2026_Q2','2026-04-01','2026-06-30'),('2026_Q3','2026-07-01','2026-09-30'),('2026_to_date','2026-01-01',str(latest.date())),('recent90',str((latest-pd.Timedelta(days=90)).date()),str(latest.date()))]
    for method,mask in masks.items():
        for H in (7,10,14):
            rows=make_trades(d,mask&d.date.ge('2025-01-01'),H,latest)
            trades.extend([{**x,'method':method,'holding_days':H} for x in rows])
            for label,lo,hi in periods:
                z=[x for x in rows if lo<=x['signal_date']<=hi]
                for context,sub in [('all',z),('outside_named_events',[x for x in z if not x['known_event_window']])]:
                    summaries.append({'method':method,'holding_days':H,'period':label,'context':context,**summarize(sub)})
    pd.DataFrame(trades).to_csv(OUT/'trades.csv.gz',index=False,compression='gzip')
    current=d[d.eligible&d.date.eq(latest)].copy();current['status']='独立入场验证，未获买入资格'
    for method,mask in masks.items():current[method]=mask.loc[current.index]
    current.sort_values('rank')[['date','name','cn','id','close','rank','score','factor_coverage','r7','environment_ok','status']+list(masks)].to_csv(OUT/'current_candidates.csv',index=False,encoding='utf-8-sig')
    result={'version':'frozen-rank-entry-v1','asof':str(latest.date()),'loaded':len(frames),'requested':len(u),'failures':fail,'weights':dict(zip(FACTORS,WEIGHTS.tolist())),'policies_fixed_before_this_run':True,'summaries':summaries,'fee_buy':0,'fee_sell':.01,'slippage':0,'production_modified':False,'qualified_systems':[],'limitations':['40/20/40是此前已看三个事件后开发得到，完整时段及排除事件段都不等于真正未见样本','首次入榜只是此前7个自然日均不在前30且报价完整的代理，不是生命周期首次','每方法每商品按计划H+2日去重；先保留信号再检查未来报价，缺数据不记零收益','全部退出窗口要求真实收盘及正成交量；未成熟与缺数据分别保留','信号按季度归属，退出可跨季度，但必须在asof已有真实结果','仍是逐商品回测，跨商品相关；没有资金、仓位或账户净值模拟','缺失因子贡献0且显示覆盖率；价格悠悠、成交量全平台，缺历史求购不倒填','费用卖出1%、无滑点；次日及退出日收盘为代理，不保证成交']}
    (OUT/'validation.json').write_text(json.dumps(clean_json(result),ensure_ascii=False,indent=2,allow_nan=False))
    pct=lambda x:'—' if x is None else f'{x:.2%}'
    lines=['# 固定40/20/40公式：完整时段与首次入榜检验',f'截至{latest.date()}；加载{len(frames)}/{len(u)}件。','五个固定入场×7/10/14日持有，共15个方案。本轮不按收益自动改权重或升级生产。','首次入榜：前7日无前30且有真实报价；短期涨幅上限为7日15%；局部修复沿用已有因果环境规则，不要求全池7日涨幅为正。','已知事件前后30日另作排除诊断，仍不能冒充从未看过的独立数据。','','| 时段 | 范围 | 入场 | 持有 | 信号/结果 | 净均值 | 中位 | 胜率 | P10 |','|---|---|---|---:|---:|---:|---:|---:|']
    for s in summaries:lines.append(f'| {s["period"]} | {s["context"]} | {s["method"]} | {s["holding_days"]} | {s["signals"]}/{s["n"]} | {pct(s["mean"])} | {pct(s["median"])} | {pct(s["win"])} | {pct(s["p10"])} |')
    lines+=['','## 边界',*['- '+x for x in result['limitations']]]
    text='\n'.join(lines)+'\n';(OUT/'report.md').write_text(text)
    if os.environ.get('GITHUB_STEP_SUMMARY'):Path(os.environ['GITHUB_STEP_SUMMARY']).write_text(text)
    print('ENTRY_VALIDATION_COMPLETE',len(trades),flush=True)
if __name__=='__main__':main()
