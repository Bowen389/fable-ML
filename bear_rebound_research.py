"""Independent fixed-rule rebound study. Never writes production scores."""
import concurrent.futures as futures
import hashlib
import json
import os
from pathlib import Path
import numpy as np
import pandas as pd
from leader_research import CACHE, collect

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'/'bear_rebound'
RULES=('left_support','uniform_turn','first_pullback')

def feature_frame(raw):
    parts=[]
    for name,p in raw.groupby('name',sort=True):
        p=p.sort_values('date').set_index('date')
        g=p.reindex(pd.date_range(p.index.min(),p.index.max()))
        c,v=g.close,g.volume
        valid=c.notna()
        g['eligible']=(valid.cumsum()>=100)&(valid.rolling(60).sum()>=55)&(c>=30)&v.gt(0)
        g['r1']=c/c.shift(1)-1;g['r3']=c/c.shift(3)-1;g['r7']=c/c.shift(7)-1
        g['r30']=c/c.shift(30)-1
        g['ma10']=c.rolling(10,min_periods=9).mean()
        g['ma30']=c.rolling(30,min_periods=27).mean()
        g['rv']=v.rolling(3).mean()/v.shift(3).rolling(20).median().replace(0,np.nan)
        g['cv']=v.rolling(5).std()/v.rolling(5).mean().replace(0,np.nan)
        g['share']=v.rolling(5).max()/v.rolling(5).sum().replace(0,np.nan)
        g['washv']=v.shift(1).rolling(5).mean()/v.shift(6).rolling(20).mean().replace(0,np.nan)
        g['low10']=g.low.shift(1).rolling(10).min()
        g['low30']=g.low.shift(1).rolling(30).min()
        g['base_drift']=c.shift(10)/c.shift(40)-1
        g['base_range']=g.high.shift(10).rolling(30).max()/g.low.shift(10).rolling(30).min()-1
        g['drawdown']=c/c.shift(1).rolling(30).max()-1
        for k in ['name','cn','id','family']:g[k]=p[k].iloc[0]
        g['date']=g.index;parts.append(g.reset_index(drop=True))
    d=pd.concat(parts,ignore_index=True)
    q=d[d.eligible]
    market=q.groupby('date').agg(m3=('r3','median'),m7=('r7','median'),m30=('r30','median'),breadth=('close',lambda s:(s>d.loc[s.index,'ma30']).mean()),n=('close','size'))
    market['breadth_change3']=market.breadth-market.breadth.shift(3)
    for k in market:d[k]=d.date.map(market[k])
    d['rs7']=d.r7-d.m7
    d['repair']=(d.m3>0)&(d.breadth_change3>0)
    d['bear_context']=(d.m30<0)|(d.breadth<.35)
    # Local repair can open before the whole pool's seven-day median turns positive.
    d['environment_ok']=d.repair|((d.m3>d.m7*3/7)&(d.breadth_change3>=0))
    masks={r:pd.Series(False,index=d.index) for r in RULES}
    for _,g in d.groupby('name',sort=False):
        common=g.eligible&g.rv.between(.5,3)&g.r7.lt(.20)&g.low.ge(g.low30*.98)&g.rs7.gt(0)
        left=common&g.drawdown.le(-.08)&g.washv.lt(.9)&g.r3.gt(0)&g.close.ge(g.low10*1.02)
        uniform=common&g.rv.between(1.1,2.5)&g.cv.le(.65)&g.share.le(.4)&g.close.gt(g.ma10)&g.r3.gt(0)&g.base_drift.between(-.3,.15)&g.base_range.le(.6)
        # State machine: one first pullback after each uniform-turn episode, expires at 20d.
        pull=pd.Series(False,index=g.index);armed=None;peak=None;previous=False
        for idx,x in g.iterrows():
            trigger=bool(uniform.loc[idx])
            if armed is not None:
                peak=max(peak,x.close) if pd.notna(x.close) else peak
                age=(x.date-armed).days
                if age>20 or (pd.notna(x.close) and x.close<x.low30*.98):armed=None
                elif age>=2 and pd.notna(x.close) and -.12<=x.close/peak-1<=-.02 and x.washv<1 and x.r1>0 and x.close>=x.ma30*.95:
                    pull.loc[idx]=bool(common.loc[idx]);armed=None
            if trigger and not previous and armed is None:armed=x.date;peak=x.close
            previous=trigger
        masks['left_support'].loc[g.index]=left
        masks['uniform_turn'].loc[g.index]=uniform
        masks['first_pullback'].loc[g.index]=pull
    return d,masks

def net_ratio(ratio):return ratio*(1-.005)/(1+.005)*(1-.025)-1

def outcome(g,day,policy):
    entryday=day+pd.Timedelta(days=1)
    H=int(policy) if policy in ('7','14','30') else 30
    window=g.reindex(pd.date_range(entryday,entryday+pd.Timedelta(days=H)))
    # Full real close/volume window; no interpolation, no future-validity gate on signals.
    if len(window)!=H+1 or window.close.isna().any() or not window.volume.gt(0).all():return None
    entry=window.close.iloc[0];exitpos=H;reason='fixed'
    if policy not in ('7','14','30'):
        peak=entry
        for j in range(1,H+1):
            price=window.close.iloc[j];peak=max(peak,price)
            if j<7:continue
            ret=net_ratio(price/entry)
            if ret<=-.10:exitpos=j;reason='stop';break
            if policy=='take15' and ret>=.15:exitpos=j;reason='take_profit';break
            if policy=='trail8' and price/peak-1<=-.08:exitpos=j;reason='trailing';break
    path=window.close.iloc[:exitpos+1]
    # Trigger close is also execution close: descriptive optimistic fill assumption.
    return {'net':float(net_ratio(path.iloc[-1]/entry)),'mae_close':float((path/entry-1).min()),'mfe_close':float((path/entry-1).max()),'exit_date':str(path.index[-1].date()),'exit_reason':reason,'entry_price':float(entry)}

def stats(rows):
    if not rows:return {'n':0,'mean':None,'median':None,'win':None,'p10':None,'mean_mae':None,'items':0}
    a=pd.DataFrame(rows)
    return {'n':len(a),'mean':float(a.net.mean()),'median':float(a.net.median()),'win':float(a.net.gt(0).mean()),'p10':float(a.net.quantile(.1)),'mean_mae':float(a.mae_close.mean()),'items':int(a.name.nunique())}

def main():
    CACHE.mkdir(exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    universe=json.loads((ROOT/'firepulse_universe.json').read_text())
    cases=json.loads((ROOT/'research/bear_rebound_cases.json').read_text())
    excluded=('Nova |','XM1014 |','MAG-7 |','Sawed-Off |','Negev |','M249 |','R8 Revolver |')
    universe=[x for x in universe if x.get('id') and not x['name'].startswith(excluded)]
    today=pd.Timestamp.now(tz='Asia/Shanghai').tz_localize(None).normalize()
    frames=[];failed=[]
    with futures.ThreadPoolExecutor(max_workers=3) as ex:
        jobs={ex.submit(collect,x,today):x for x in universe}
        for i,f in enumerate(futures.as_completed(jobs),1):
            try:frames.append(f.result())
            except Exception as err:failed.append({'name':jobs[f]['name'],'error':str(err)})
            if i%50==0:print('FETCH',i,'/',len(universe),'loaded',len(frames),flush=True)
    if not frames:raise RuntimeError('No usable history')
    raw=pd.concat(frames,ignore_index=True);d,masks=feature_frame(raw)
    latest=raw.date.max();events=[];case_rows=[];coverage=[]
    byname={n:g.set_index('date').sort_index() for n,g in d.groupby('name')}
    for event in cases['events']:
        anchor=pd.Timestamp(event['dates'][0])
        for item in event.get('members',event.get('cases',[])):
            g=byname.get(item['name'])
            coverage.append({'name':item['name'],'event':str(anchor.date()),'mapped':bool(item.get('id')),'loaded':g is not None,'event_close_available':bool(g is not None and anchor in g.index and pd.notna(g.loc[anchor,'close']))})
            if g is None:continue
            baseline=g.loc[anchor,'close'] if anchor in g.index else np.nan
            for rule,mask in masks.items():
                z=d[mask&d.name.eq(item['name'])&d.date.between(anchor-pd.Timedelta(days=14),anchor+pd.Timedelta(days=14))]
                first=z.iloc[0] if len(z) else None
                case_rows.append({'event':str(anchor.date()),'name':item['name'],'cn':item['cn'],'rule':rule,'first_signal':str(first.date.date()) if first is not None else None,'signal_days_vs_anchor':int((first.date-anchor).days) if first is not None else None,'anchor_close':None if pd.isna(baseline) else float(baseline),'signal_vs_anchor_price':float(first.close/baseline-1) if first is not None and pd.notna(baseline) else None,'net7':outcome(g,first.date,'7') if first is not None else None,'net14':outcome(g,first.date,'14') if first is not None else None})
    for rule,mask in masks.items():
        for gate in ('ungated','local_repair'):
            selected=d[mask&(d.environment_ok if gate=='local_repair' else True)&d.date.ge('2025-01-01')]
            for policy in ('7','14','30','take15','trail8'):
                for name,sg in selected.groupby('name'):
                    nextday=pd.Timestamp.min;g=byname[name]
                    for x in sg.sort_values('date').itertuples():
                        if x.date<nextday:continue
                        # Reserve the maximum holding period BEFORE checking future data availability.
                        nextday=x.date+pd.Timedelta(days=(int(policy) if policy.isdigit() else 30)+2)
                        result=outcome(g,x.date,policy)
                        events.append({'name':name,'date':str(x.date.date()),'rule':rule,'gate':gate,'policy':policy,'bear_context':bool(x.bear_context),'evaluated':result is not None,**(result or {})})
    summaries=[]
    windows=[('development_2025','2025-01-01','2025-12-31'),('2026_Q1','2026-01-01','2026-03-31'),('2026_Q2','2026-04-01','2026-06-30'),('2026_Q3','2026-07-01','2026-09-30'),('recent90',str((latest-pd.Timedelta(days=90)).date()),str(latest.date()))]
    for rule in RULES:
        for gate in ('ungated','local_repair'):
            for policy in ('7','14','30','take15','trail8'):
                for label,lo,hi in windows:
                    signals=[x for x in events if x['rule']==rule and x['gate']==gate and x['policy']==policy and lo<=x['date']<=hi]
                    mature=[x for x in signals if x['evaluated'] and x['exit_date']<=hi]
                    summaries.append({'rule':rule,'gate':gate,'policy':policy,'window':label,'signals':len(signals),'evaluated':len(mature),'all':stats(mature),'bear':stats([x for x in mature if x['bear_context']])})
    pd.DataFrame(events).to_csv(OUT/'trades.csv.gz',index=False,compression='gzip')
    pd.DataFrame(case_rows).to_json(OUT/'case_detection.json',orient='records',force_ascii=False,indent=2)
    manifest={'asof':str(latest.date()),'requested':len(universe),'loaded':len(frames),'failed':failed,'case_coverage':coverage,'hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in CACHE.glob('*.gz')},'fee':.025,'slippage_each_side':.005,'minimum_exit_days':7,'price':'youpin','volume':'all-platform proxy','production_score_modified':False}
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    report={'fixed_before_run':True,'parameter_search':False,'qualified_systems':[],'qualification_status':'研究诊断，未设自动晋级；须独立事件及前瞻验证','summaries':summaries}
    (OUT/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    pct=lambda x:'—' if x is None else f'{x:.2%}'
    lines=['# 熊市反弹独立回测',f'截至{latest.date()}；取数{len(frames)}/{len(universe)}；案例精确加载{sum(x["loaded"] for x in coverage)}/{len(coverage)}。','现行评分公式未改。三规则×两环境×五退出，共30个固定方案，无收益最优自动选择。','价格为悠悠日K，成交量为全平台代理；次日收盘代理入场，手续费2.5%，双边各0.5%滑点。','最早第7日退出；动态退出按触发收盘成交，存在乐观执行假设。MAE按收盘价，不代表盘中最大回撤。','仅逐商品去重，不是资金组合净值；固定池有存活偏差。开发与2026事件诊断不冒充独立验证。','100根历史门槛为独立早期研究要求，不改生产300根门槛；缺日不补价，退出窗口要求真实报价和正成交量。','缺失历史求购、会员档位与Whale不倒填。组内未触发也保留；三个事件在±14日内诊断首次信号，不能当作自动事件发现。','','| 规则 | 环境 | 退出 | 时段 | 信号/可评估 | 熊市n | 熊市净均值 | 熊市净中位 | 熊市胜率 | 熊市P10 |','|---|---|---|---|---:|---:|---:|---:|---:|---:|']
    for s in summaries:
        b=s['bear'];lines.append(f'| {s["rule"]} | {s["gate"]} | {s["policy"]} | {s["window"]} | {s["signals"]}/{s["evaluated"]} | {b["n"]} | {pct(b["mean"])} | {pct(b["median"])} | {pct(b["win"])} | {pct(b["p10"])} |')
    lines+=['','## 案例覆盖缺口',*[f'- {x["name"]}：mapped={x["mapped"]}, loaded={x["loaded"]}, event_close={x["event_close_available"]}' for x in coverage if not x['loaded'] or not x['event_close_available']],'','完整逐笔、案例触发及覆盖见同目录文件；未通过系统验证，不输出正式买入资格。']
    text='\n'.join(lines)+'\n';(OUT/'report.md').write_text(text)
    if os.environ.get('GITHUB_STEP_SUMMARY'):Path(os.environ['GITHUB_STEP_SUMMARY']).write_text(text)
    print('BEAR_REBOUND_COMPLETE',len(events),'signals',flush=True)

if __name__=='__main__':main()
