"""Causal sector phases and entries; independent development, production unchanged."""
import concurrent.futures as futures
import json,os
from pathlib import Path
import numpy as np
import pandas as pd
from leader_research import CACHE,collect
from bear_rebound_research import feature_frame,net_ratio
from rebound_rank_research import enrich,daily_rank
from rebound_stage_research import add_stages,include_registered_items,clean_json
from rebound_shared_factors import factor_frame,FACTORS
from rebound_group_review import group_name
from rebound_entry_validation import WEIGHTS,summarize
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output/rebound_gates'

def phases(d,firstgen):
    d=d.copy();d['sector']=d.name.map(lambda n:group_name(n,firstgen))
    e=d[d.eligible].copy();e['above10']=e.close.gt(e.ma10)
    q=e.groupby(['sector','date']).agg(items=('name','nunique'),r3=('r3','median'),r7=('r7','median'),breadth=('above10','mean'),rv=('rv','median')).reset_index().sort_values(['sector','date'])
    frames=[]
    for sector,g in q.groupby('sector',sort=False):
        g=g.set_index('date').asfreq('D');g['sector']=sector;change=g.breadth-g.breadth.shift(3)
        valid=g['items'].ge(8)&g['items'].shift(3).ge(8)
        repair=(g.r3.gt(0)&change.gt(0))&valid
        # Count days since observed repair onset, reset only after repair ends.
        streak=repair.groupby((~repair).cumsum()).cumsum()
        fade=valid&((g.r3.lt(0)&change.lt(0))|(g.r7.gt(.15)&change.le(0)))
        base=valid&g.r3.le(0)&g.r3.gt(g.r7*3/7)&change.ge(0)
        state=np.select([fade,repair&streak.le(3),repair&streak.gt(3),base,valid],['fading','starting','expanding','basing','falling'],default='unknown')
        g['phase']=state;g['breadth_change3']=change;g['repair_age']=streak;frames.append(g.reset_index())
    q=pd.concat(frames,ignore_index=True)
    d=d.merge(q[['date','sector','phase','items','breadth_change3','repair_age']],on=['date','sector'],how='left',validate='many_to_one')
    d['phase']=d.phase.fillna('unknown')
    return d,q

def masks(d,k=30):
    top=d.eligible&d['rank'].le(k)
    left=top&d.phase.eq('basing')&d.rv.le(1)&d.r3.ge(-.05)
    raw_launch=top&d.phase.eq('starting')&d.rv.ge(1.2)&d.r3.gt(0)
    launch=raw_launch.copy()
    for _,g in d.sort_values(['name','date']).groupby('name',sort=False):
        prior=raw_launch.loc[g.index].shift().rolling(3,min_periods=3).sum()
        launch.loc[g.index]=raw_launch.loc[g.index]&prior.eq(0)
    pull=pd.Series(False,index=d.index)
    for _,g in d.sort_values(['name','date']).groupby('name',sort=False):
        prior=launch.loc[g.index].shift().rolling(10,min_periods=10).max().eq(1)
        pull.loc[g.index]=top.loc[g.index]&prior&g.phase.isin(['starting','expanding'])&g.rv.le(1)&g.r1.lt(0)&g.close.ge(g.ma10*.98)
    return {'rank_control':top,'left_basing':left,'first_volume_start':launch,'first_pullback':pull}

def trades(d,mask,mode,latest):
    rows=[]
    for name,g in d.sort_values(['name','date']).groupby('name',sort=False):
        g=g.set_index('date');nextday=pd.Timestamp.min
        for day,x in g[g.row_id.isin(mask.index[mask])].iterrows():
            if day<nextday:continue
            # Fixed reservation independent of future outcome or chosen exit.
            nextday=day+pd.Timedelta(days=16);entry=day+pd.Timedelta(days=1);exitday=entry+pd.Timedelta(days=7 if mode=='fixed7' else 14)
            if mode=='sector_fade14':
                for t in pd.date_range(entry+pd.Timedelta(days=1),exitday-pd.Timedelta(days=1)):
                    if t in g.index and g.loc[t,'phase']=='fading':exitday=t+pd.Timedelta(days=1);break
            window=g.reindex(pd.date_range(entry,exitday));complete=window.close.notna().all() and window.volume.gt(0).all()
            net=float(net_ratio(window.close.iloc[-1]/window.close.iloc[0])) if complete else None
            rows.append({'name':name,'signal_date':str(day.date()),'entry_date':str(entry.date()),'exit_date':str(exitday.date()),'phase':x.phase,'sector':x.sector,'net':net,'status':'evaluated' if complete else 'not_mature' if exitday>latest else 'missing_quote_or_volume','known_event_window':bool(x.known_event_window)})
    return rows

def gate_evidence(d):
    d=d.copy()
    d['market_ok']=d.m3.gt(d.m7*3/7)&d.market_breadth_change3.ge(0)
    # Same-sector ranks 6..20 are followers, never current global Top3/Top5.
    sector_rank=d.score.where(d.eligible).groupby([d.date,d.sector]).rank(ascending=False,method='first')
    rear=d.eligible&sector_rank.between(6,20)&d['rank'].gt(5)
    ready=rear&d.r7.le(.15)&d.r3.gt(d.r7*3/7)&d.rv.between(.8,2.5)&d.close.ge(d.ma10*.98)
    d['rear_total']=rear.groupby([d.date,d.sector]).transform('sum')
    d['rear_ready']=ready.groupby([d.date,d.sector]).transform('sum')
    d['rear_fraction']=d.rear_ready/d.rear_total.replace(0,np.nan)
    d['relay_ok']=d.rear_total.ge(3)&d.rear_ready.ge(2)&d.rear_fraction.ge(.25)
    d['market_and_relay']=d.market_ok&d.relay_ok
    d['entry_evidence']=np.where(d.market_and_relay,'大盘跌速改善且广度未恶化；同板块后排有蓄势代理',np.where(~d.market_ok&~d.relay_ok,'大盘未修复且后排证据不足',np.where(~d.market_ok,'大盘修复条件未满足','后排蓄势证据不足')))
    return d

def gated_entries(d):
    gates={'ungated':pd.Series(True,index=d.index),'market':d.market_ok,'relay':d.relay_ok,'both':d.market_and_relay}
    return {f'top{k}_{method}__{gate}':mask&allowed for k in (3,5) for method,mask in masks(d,k).items() for gate,allowed in gates.items()}

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
    entries=gated_entries(d);allrows=[];summaries=[]
    periods=[('2025','2025-01-01','2025-12-31'),('2026_Q1','2026-01-01','2026-03-31'),('2026_Q2','2026-04-01','2026-06-30'),('2026_Q3','2026-07-01','2026-09-30'),('recent90',str((latest-pd.Timedelta(days=90)).date()),str(latest.date()))]
    for method,mask in entries.items():
        for mode in ['fixed7','fixed14','sector_fade14']:
            rows=trades(d,mask&d.date.ge('2025-01-01'),mode,latest);allrows.extend([{**x,'method':method,'top_k':int(method.split('_')[0][3:]),'gate':method.split('__')[1],'exit':mode} for x in rows])
            for label,lo,hi in periods:
                z=[x for x in rows if lo<=x['signal_date']<=hi]
                for context,sub in [('all',z),('outside_named_events',[x for x in z if not x['known_event_window']])]:summaries.append({'method':method,'top_k':int(method.split('_')[0][3:]),'gate':method.split('__')[1],'exit':mode,'period':label,'context':context,**summarize(sub)})
    pd.DataFrame(allrows).to_csv(OUT/'trades.csv.gz',index=False,compression='gzip');q.to_csv(OUT/'sector_phases.csv.gz',index=False,compression='gzip')
    q[q.sector.eq('一代手套_略磨')&q.date.between('2026-02-01','2026-02-23')].to_csv(OUT/'feb_gloves.csv',index=False)
    current=d[d.eligible&d.date.eq(latest)].sort_values('rank').copy()
    for method,mask in entries.items():current[method]=mask.loc[current.index]
    current[['date','name','cn','close','rank','score','sector','phase','items','market_ok','rear_total','rear_ready','rear_fraction','relay_ok','market_and_relay','entry_evidence']+list(entries)].to_csv(OUT/'current_candidates.csv',index=False,encoding='utf-8-sig')
    result={'asof':str(latest.date()),'loaded':len(frames),'requested':len(u),'failures':fail,'summaries':summaries,'primary_top_k':[3,5],'gate_variants':['ungated','market','relay','both'],'qualified_systems':[],'production_modified':False,'fee_sell':.01,'fee_buy':0,'slippage':0,'limitations':['阶段阈值本轮固定；40/20/40及一代略磨篮子已看过已知事件，因此属于开发验证，不是全新独立样本','组别至少8件；使用当日可用成员，成分变动可能影响中位数，items逐日披露','阶段只用当日及过去数据；退出触发后次日收盘执行，不用当天价格假装可提前成交','洗盘和左侧均为量价代理；不是会员身份或真实建仓成本','每商品各方案统一预留16天后才允许下一信号，避免未来退出或缺数据改变样本','要求持有窗口全部真实收盘与正成交量；缺失与未成熟不记零收益','收益为相关商品逐笔收益，非组合净值；悠悠价格与全平台成交量分开理解','门控阈值是待验证假设，不由近期收益搜索选择；后排评分6至20名不是真实资金身份或确定接力','近期90天和2026各季度只报告，不按它们自动挑选最优方案']}
    (OUT/'validation.json').write_text(json.dumps(clean_json(result),ensure_ascii=False,indent=2,allow_nan=False))
    p=lambda x:'—' if x is None else f'{x:.2%}'
    lines=['# 大盘修复与后排蓄势：独立开仓门控验证',f'截至{latest.date()}，覆盖{len(frames)}/{len(u)}。现行评分未变。','阶段：下跌、蓄势、启动（修复前3天）、扩散、衰竭、数据不足。市场7日涨幅转正不是硬门槛。','板块r3>0且站上MA10比例较3天前增加视为修复；r3负但跌速减缓且广度不再恶化视为蓄势。r3和广度同时回落，或r7>15%而广度停止扩张视为衰竭。','Top3、Top5先排名再过滤，不补位。2种排名×4种入场×4种门控×3种退出共96方案。门控：不限、大盘、后排、两者同时满足。大盘：3日中位涨幅高于7日折算日速且广度不降；不要求涨幅为正。后排：同板块评分6至20名且全池排名大于5，至少3件可观察，其中至少2件且至少25%满足7日涨幅不超15%、3日跌速改善、量比0.8至2.5、价格守MA10的98%。只是蓄势代理，不预言后续上涨。所有方案每件统一16天去重，退出后次日收盘执行。','','| 时段 | 范围 | 入场 | 退出 | 结果/信号 | 净均值 | 中位 | 胜率 | P10 |','|---|---|---|---|---:|---:|---:|---:|---:|']
    for s in summaries:lines.append(f'| {s["period"]} | {s["context"]} | {s["method"]} | {s["exit"]} | {s["n"]}/{s["signals"]} | {p(s["mean"])} | {p(s["median"])} | {p(s["win"])} | {p(s["p10"])} |')
    lines+=['','## 边界',*['- '+x for x in result['limitations']]];report='\n'.join(lines)+'\n';(OUT/'report.md').write_text(report)
    if os.environ.get('GITHUB_STEP_SUMMARY'):Path(os.environ['GITHUB_STEP_SUMMARY']).write_text(report)
    print('GATE_RESEARCH_COMPLETE',len(allrows),flush=True)
if __name__=='__main__':main()
