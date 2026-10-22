"""Freeze Top3/5 at repair onset, then wait for causal entry evidence."""
import concurrent.futures as futures
import json,os
from pathlib import Path
import numpy as np
import pandas as pd
from leader_research import CACHE,collect
from bear_rebound_research import feature_frame
from rebound_rank_research import enrich,daily_rank
from rebound_stage_research import add_stages,include_registered_items,clean_json
from rebound_shared_factors import factor_frame,FACTORS
from rebound_entry_validation import WEIGHTS,summarize
from rebound_gate_research import phases,gate_evidence,trades
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output/rebound_watch'

def watch_entries(d,ks=(3,5),life=10):
    masks={f'top{k}_{style}__{gate}':pd.Series(False,index=d.index) for k in ks for style in ('setup_now','volume_confirm','wash_reclaim') for gate in ('market','both')}
    audit=[]
    for k in ks:
        active={};expiry=pd.Timestamp.min
        for date,day in d.sort_values(['date','rank','name']).groupby('date',sort=True):
            market=bool(day.market_ok.iloc[0])
            if date>=expiry:
                active={}
                if market:
                    cohort=day[day.eligible&day['rank'].le(k)]
                    for idx,x in cohort.iterrows():
                        active[x['name']]={'setup_date':date,'setup_rank':int(x['rank']),'setup_score':float(x.score),'setup_close':float(x.close),'peak':float(x.close),'wash_date':None,'fired':set()}
                    expiry=date+pd.Timedelta(days=life)
            byname=day.set_index('name',drop=False)
            for name,state in active.items():
                if name not in byname.index:continue
                x=byname.loc[name];idx=int(x.row_id);age=(date-state['setup_date']).days
                valid=bool(x.eligible) and pd.notna(x.close) and x.volume>0
                if valid:state['peak']=max(state['peak'],float(x.close))
                dd=float(x.close/state['peak']-1) if valid else np.nan
                recovered=valid and state['wash_date'] is not None and date>state['wash_date'] and x.r1>0 and x.close>=x.ma10*.98 and dd>=-.12
                checks={'setup_now':age==0,'volume_confirm':valid and age>=1 and x.rv>=1.2 and x.r1>0 and x.close<=state['setup_close']*1.10,'wash_reclaim':recovered}
                entry_ok=valid and market and x.phase not in ('fading','unknown')
                for style,shape in checks.items():
                    for gate in ('market','both'):
                        key=f'top{k}_{style}__{gate}';passed=entry_ok and bool(shape) and (gate=='market' or bool(x.relay_ok)) and key not in state['fired']
                        if passed:masks[key].loc[idx]=True;state['fired'].add(key)
                        audit.append({'date':str(date.date()),'name':name,'top_k':k,'method':key,'setup_date':str(state['setup_date'].date()),'setup_rank':state['setup_rank'],'setup_score':state['setup_score'],'watch_age':age,'current_rank':float(x['rank']) if pd.notna(x['rank']) else None,'drawdown':dd,'wash_seen':state['wash_date'] is not None,'market_ok':market,'relay_ok':bool(x.relay_ok),'phase':x.phase,'signal':bool(passed),'reason':'证据触发' if passed else '大盘未许可' if not market else '阶段不允许' if x.phase in ('fading','unknown') else '数据不足' if not valid else '后排不足' if gate=='both' and not bool(x.relay_ok) else '形态未满足或本观察期已触发'})
                # Washout must be known on an earlier day; cannot wash and recover on same close.
                if valid and age>=1 and -.12<=dd<=-.02 and x.rv<=1:state['wash_date']=date
    return masks,pd.DataFrame(audit)

def main():
    OUT.mkdir(parents=True,exist_ok=True);CACHE.mkdir(exist_ok=True)
    cases=json.loads((ROOT/'research/bear_rebound_cases.json').read_text());firstgen={x['name'] for x in cases['events'][0]['members']}
    u=include_registered_items(json.loads((ROOT/'firepulse_universe.json').read_text()),cases)
    u=[x for x in u if x.get('id') and not x['name'].startswith(('Nova |','XM1014 |','MAG-7 |','Sawed-Off |','Negev |','M249 |','R8 Revolver |'))]
    today=pd.Timestamp.now(tz='Asia/Shanghai').tz_localize(None).normalize();frames=[];fail=[]
    with futures.ThreadPoolExecutor(max_workers=3) as ex:
        jobs={ex.submit(collect,x,today):x for x in u}
        for i,f in enumerate(futures.as_completed(jobs),1):
            try:frames.append(f.result())
            except Exception as exc:fail.append({'name':jobs[f]['name'],'error':str(exc)})
            if i%100==0:print('FETCH',i,len(frames),flush=True)
    if not frames:raise RuntimeError('No history')
    d,_=add_stages(enrich(feature_frame(pd.concat(frames,ignore_index=True))[0]));d=factor_frame(d)
    d['score']=100*(d[FACTORS].fillna(0).to_numpy()@WEIGHTS);d['rank']=daily_rank(d,d.score.where(d.eligible))
    d=d.rename(columns={'breadth_change3':'market_breadth_change3'});d,q=phases(d,firstgen);d=gate_evidence(d);d['row_id']=d.index;latest=d[d.eligible].date.max();d['known_event_window']=False
    for event in cases['events']:
        anchor=pd.Timestamp(event['dates'][0]);d['known_event_window']|=d.date.between(anchor-pd.Timedelta(days=30),anchor+pd.Timedelta(days=30))
    entries,audit=watch_entries(d);audit.to_csv(OUT/'watch_audit.csv.gz',index=False,compression='gzip');allrows=[];summaries=[]
    periods=[('2025','2025-01-01','2025-12-31'),('2026_Q1','2026-01-01','2026-03-31'),('2026_Q2','2026-04-01','2026-06-30'),('2026_Q3','2026-07-01','2026-09-30'),('recent90',str((latest-pd.Timedelta(days=90)).date()),str(latest.date()))]
    for method,mask in entries.items():
        evidence=audit[audit.method.eq(method)&audit.signal].set_index(['date','name'])
        for mode in ('fixed7','sector_fade14'):
            rows=trades(d,mask&d.date.ge('2025-01-01'),mode,latest)
            for x in rows:
                x.update(evidence.loc[(x['signal_date'],x['name']),['setup_date','setup_rank','watch_age','current_rank']].to_dict())
            allrows.extend([{**x,'method':method,'exit':mode} for x in rows])
            for label,lo,hi in periods:
                z=[x for x in rows if lo<=x['signal_date']<=hi]
                for context,sub in [('all',z),('outside_named_events',[x for x in z if not x['known_event_window']])]:summaries.append({'method':method,'exit':mode,'period':label,'context':context,**summarize(sub)})
    pd.DataFrame(allrows).to_csv(OUT/'trades.csv.gz',index=False,compression='gzip')
    audit[audit.date.eq(str(latest.date()))].to_csv(OUT/'current_watch.csv',index=False,encoding='utf-8-sig')
    labels=[]
    for event in cases['events']:
        anchor=pd.Timestamp(event['dates'][0]);members={x['name'] for x in event.get('members',event.get('cases',[]))}
        labels.extend([{**x,'event':str(anchor.date())} for x in allrows if x['name'] in members and abs((pd.Timestamp(x['signal_date'])-anchor).days)<=7])
    pd.DataFrame(labels,columns=['event',*pd.DataFrame(allrows).columns]).to_csv(OUT/'named_case_entries.csv',index=False)
    result={'version':'frozen-watch-v1','asof':str(latest.date()),'loaded':len(frames),'requested':len(u),'failures':fail,'summaries':summaries,'qualified_systems':[],'production_modified':False,'fee_buy':0,'fee_sell':.01,'slippage':0,'watch_days':10,'limitations':['固定40/20/40来自已见案例；本轮是开发验证，不是全新独立样本','修复首次出现且无有效观察篮子时冻结当日全池Top3/5，10自然日内不补位；期满且大盘仍许可才重建','观察期内商品可以跌出前三/前五，入场仍来自当初冻结名单；每种形态每期最多触发一次','大盘不许可或板块衰竭/未知时禁止新信号；洗盘只用早于回升日的量价代理','持仓不是实盘账户，沿用每商品16日去重；不同方法独立比较，不能累加收益','全部持有窗口要求真实报价和正成交量，缺失与未成熟不记零','日K缓存实际日期以asof为准，不把今天运行称为今天实时行情；价格悠悠，成交量全平台','卖出1%，无滑点，次日收盘代理入场，衰竭退出也延迟至次日收盘']}
    (OUT/'validation.json').write_text(json.dumps(clean_json(result),ensure_ascii=False,indent=2,allow_nan=False))
    p=lambda x:'—' if x is None else f'{x:.2%}'
    lines=['# 冻结Top3/5后等待入场：独立研究',f'历史截至{latest.date()}，加载{len(frames)}/{len(u)}。','先入观察名单，后寻找入场证据；不要求洗盘后回升当天仍在全池Top3/5。','修复日冻结名单10天，不补位；比较当日信号、后续放量确认、缩量回踩后隔日回升，分别使用大盘或大盘+后排许可，固定7天或衰竭次日退出（最长14天），共24方案。','','| 时段 | 范围 | 入场及门控 | 退出 | 结果/信号 | 净均值 | 中位 | 胜率 | P10 |','|---|---|---|---|---:|---:|---:|---:|---:|']
    for s in summaries:lines.append(f'| {s["period"]} | {s["context"]} | {s["method"]} | {s["exit"]} | {s["n"]}/{s["signals"]} | {p(s["mean"])} | {p(s["median"])} | {p(s["win"])} | {p(s["p10"])} |')
    lines+=['','## 边界',*['- '+x for x in result['limitations']]];report='\n'.join(lines)+'\n';(OUT/'report.md').write_text(report)
    if os.environ.get('GITHUB_STEP_SUMMARY'):Path(os.environ['GITHUB_STEP_SUMMARY']).write_text(report)
    print('WATCH_RESEARCH_COMPLETE',len(allrows),flush=True)
if __name__=='__main__':main()
