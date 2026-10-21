"""Causal expanding-window rebound ranking; independent of production scores."""
import concurrent.futures as futures
import json
import os
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from bear_rebound_research import feature_frame,net_ratio
from leader_research import CACHE,collect
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'/'rebound_rank'
COLS=['r1','r3','r7','r30','rv','cv','share','washv','base_drift','base_range','drawdown','rs7','breadth','breadth_change3','m3','m7','m30','support_gap','trend_gap','accumulation','uniformity','support','strength','risk']

def enrich(d):
    d=d.copy();d['support_gap']=d.close/d.low30-1;d['trend_gap']=d.close/d.ma30-1
    clip=lambda s:s.clip(0,1)
    d['accumulation']=clip(1-d.base_range/.6)*clip(1-d.base_drift.abs()/.3)
    d['uniformity']=clip(1-d.cv)*clip(1-(d.rv-1.6).abs()/1.6)*clip(1-d.share)
    d['support']=clip(1-d.support_gap/.3)*clip(1-d.washv/2)
    d['strength']=d.rs7.where(d.eligible).groupby(d.date).rank(pct=True)
    d['risk']=clip((d.r7-.15)/.3)+clip((d.rv-3)/3)+clip((-d.r3-.05)/.15)
    d['heuristic']=100*(.25*d.accumulation+.25*d.uniformity+.25*d.support+.25*d.strength)-20*d.risk
    d['y7']=np.nan;d['y14']=np.nan;d['mae14']=np.nan
    for _,g in d.groupby('name',sort=False):
        c,v=g.close,g.volume
        for H in (7,14):
            valid=pd.concat([c.shift(-j).notna()&v.shift(-j).gt(0) for j in range(1,H+2)],axis=1).all(axis=1)
            y=net_ratio(c.shift(-(H+1))/c.shift(-1)).where(valid)
            d.loc[g.index,'y'+str(H)]=y
        path=pd.concat([c.shift(-j)/c.shift(-1)-1 for j in range(1,16)],axis=1)
        d.loc[g.index,'mae14']=path.min(axis=1).where(d.loc[g.index,'y14'].notna())
    # Outcome ranks are labels ONLY; never passed to model or heuristic.
    rank=d.y7.where(d.eligible).groupby(d.date).rank(ascending=False,method='min')
    d['winner7']=(rank.le(30)&d.y7.gt(0)).astype(float).where(d.y7.notna())
    return d

def samples_before(d,boundary):
    return d[d.eligible&d.y14.notna()&(d.date+pd.Timedelta(days=15)<pd.Timestamp(boundary))]

def rank_value(value):
    return int(value) if pd.notna(value) else None

def daily_rank(d,score):
    return score.groupby(d.date).rank(ascending=False,method='min')

def measure(z):
    e=z[z.y14.notna()]
    if e.empty:return {'signals':len(z),'n':0,'mean14':None,'median14':None,'win14':None,'hit7':None,'mean_mae14':None,'days':0}
    return {'signals':len(z),'n':len(e),'mean14':float(e.y14.mean()),'median14':float(e.y14.median()),'win14':float(e.y14.gt(0).mean()),'hit7':float(e.winner7.mean()),'mean_mae14':float(e.mae14.mean()),'days':int(e.date.nunique())}

def fit_pick(d,start):
    start=pd.Timestamp(start);calstart=start-pd.Timedelta(days=120)
    available=samples_before(d,start)
    train=available[available.date+pd.Timedelta(days=15)<calstart]
    cal=available[available.date>=calstart]
    if len(train)<1000 or len(cal)<1000:raise ValueError('Insufficient train/cal data for '+str(start))
    best=None;attempts=[]
    for leaves in (7,15):
        model=HistGradientBoostingRegressor(max_leaf_nodes=leaves,max_iter=100,learning_rate=.05,l2_regularization=20,min_samples_leaf=100,early_stopping=False,random_state=42)
        # Predict downside-penalized return; the penalty and label are fixed before run.
        target=(train.y14+.3*train.mae14).clip(-.8,1.)
        model.fit(train[COLS],target)
        pred=pd.Series(model.predict(cal[COLS]),index=cal.index)
        chosen=cal[daily_rank(cal,pred)<=30]
        objective=float((chosen.y14+.3*chosen.mae14).mean())
        attempts.append({'leaves':leaves,'objective_cal_only':objective,'cal_top30':measure(chosen)})
        if best is None or objective>best[0]:best=(objective,model,leaves)
    return best[1],{'start':str(start.date()),'train_n':len(train),'cal_n':len(cal),'train_last_label':str((train.date.max()+pd.Timedelta(days=15)).date()),'cal_last_label':str((cal.date.max()+pd.Timedelta(days=15)).date()),'selected_leaves':best[2],'attempts':attempts}

def main():
    OUT.mkdir(parents=True,exist_ok=True);CACHE.mkdir(exist_ok=True)
    today=pd.Timestamp.now(tz='Asia/Shanghai').tz_localize(None).normalize()
    u=json.loads((ROOT/'firepulse_universe.json').read_text())
    excluded=('Nova |','XM1014 |','MAG-7 |','Sawed-Off |','Negev |','M249 |','R8 Revolver |')
    u=[x for x in u if x.get('id') and not x['name'].startswith(excluded)]
    frames=[];fail=[]
    with futures.ThreadPoolExecutor(max_workers=3) as ex:
        jobs={ex.submit(collect,x,today):x for x in u}
        for i,f in enumerate(futures.as_completed(jobs),1):
            try:frames.append(f.result())
            except Exception as e:fail.append({'name':jobs[f]['name'],'error':str(e)})
            if i%100==0:print('FETCH',i,'loaded',len(frames),flush=True)
    if not frames:raise RuntimeError('No histories')
    d=enrich(feature_frame(pd.concat(frames,ignore_index=True))[0]);latest=d[d.eligible].date.max()
    splits=[('2026_Q1','2026-01-01','2026-04-01'),('2026_Q2','2026-04-01','2026-07-01'),('2026_Q3','2026-07-01','2026-10-01'),('2026_Q4_partial','2026-10-01',str((latest+pd.Timedelta(days=1)).date()))]
    predictions=[];folds=[]
    for label,lo,hi in splits:
        model,meta=fit_pick(d,lo);meta['window']=label
        z=d[d.eligible&d.date.ge(lo)&d.date.lt(hi)].copy()
        z['model_score']=model.predict(z[COLS]);z['model_rank']=daily_rank(z,z.model_score);z['heuristic_rank']=daily_rank(z,z.heuristic)
        folds.append(meta);predictions.append(z);print('FOLD',label,'selected',meta['selected_leaves'],'rows',len(z),flush=True)
    pred=pd.concat(predictions,ignore_index=True)
    summaries=[]
    for window,lo,hi in splits:
        z=pred[pred.date.ge(lo)&pred.date.lt(hi)]
        for context in ('all','bear','repair'):
            q=z if context=='all' else z[z.bear_context] if context=='bear' else z[z.environment_ok]
            # Ranks remain global; environmental filtering never renumbers candidates.
            base=q.y14.mean()
            for method,col in [('fixed_evidence','heuristic_rank'),('return_model','model_rank')]:
                for K in (10,30):
                    top=q[q[col]<=K];m=measure(top)
                    winners=q[q.winner7.eq(1)]
                    m.update({'window':window,'context':context,'method':method,'top_k':K,'baseline_mean14':None if pd.isna(base) else float(base),'winner_recall7':float(winners[col].le(K).mean()) if len(winners) else None})
                    summaries.append(m)
    cases=json.loads((ROOT/'research/bear_rebound_cases.json').read_text());case_rows=[]
    for event in cases['events']:
        anchor=pd.Timestamp(event['dates'][0])
        for item in event.get('members',event.get('cases',[])):
            z=pred[pred.name.eq(item['name'])&pred.date.between(anchor-pd.Timedelta(days=14),anchor+pd.Timedelta(days=14))]
            for method,col in [('fixed_evidence','heuristic_rank'),('return_model','model_rank')]:
                for offset in (-7,-3,0,3,7):
                    date=anchor+pd.Timedelta(days=offset);q=z[z.date.eq(date)]
                    x=q.iloc[0] if len(q) else None
                    case_rows.append({'event':str(anchor.date()),'date':str(date.date()),'name':item['name'],'cn':item['cn'],'method':method,'rank':rank_value(x[col]) if x is not None else None,'pool':int(pred.date.eq(date).sum()),'net7':float(x.y7) if x is not None and pd.notna(x.y7) else None,'net14':float(x.y14) if x is not None and pd.notna(x.y14) else None,'status':('evaluated' if pd.notna(x[col]) else 'missing_evidence') if x is not None else 'missing_or_ineligible'})
    # Fit final model only with labels complete before prediction date; research output only.
    model,meta=fit_pick(d,latest);current=d[d.eligible&d.date.eq(latest)].copy()
    current['model_score']=model.predict(current[COLS]);current['rank']=daily_rank(current,current.model_score)
    current['reference_score']=100*(1-(current['rank']-1)/max(len(current)-1,1))
    current['status']='研究候选，未获买入资格'
    current.sort_values('rank')[['date','name','cn','id','close','rank','reference_score','accumulation','uniformity','support','strength','risk','environment_ok','status']].to_csv(OUT/'current_candidates.csv',index=False,encoding='utf-8-sig')
    joblib.dump(model,OUT/'research_model.joblib')
    pd.DataFrame(case_rows).to_csv(OUT/'case_rankings.csv',index=False,encoding='utf-8-sig')
    pred[['date','name','model_rank','heuristic_rank','model_score','heuristic','y7','y14','mae14','winner7','bear_context','environment_ok']].to_csv(OUT/'historical_rankings.csv.gz',index=False,compression='gzip')
    result={'version':'independent-rebound-rank-v1','asof':str(latest.date()),'items_requested':len(u),'items_loaded':len(frames),'failures':fail,'features':COLS,'folds':folds,'current_fit':meta,'summaries':summaries,'fee_sell':.01,'fee_buy':0,'slippage':0,'qualified_systems':[],'production_modified':False,'validation_status':'历史滚动诊断；人工事件已公开，不构成未见市场事件；无自动晋级'}
    (OUT/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    pct=lambda x:'—' if x is None else f'{x:.2%}'
    lines=['# 熊市反弹龙头排序研究',f'截至{latest.date()}；数据{len(frames)}/{len(u)}件。现行评分公式未改。','卖出手续费1%，买入0，滑点0；信号后次日收盘代理入场，7/14自然日收盘退出。','模型只用显式白名单特征；按季度扩展训练，校准段120日，训练与校准标签均在各自边界前完成。两个复杂度只按校准段风险调整净收益选择。','模型预测14日净收益+0.3×14日收盘最大不利变动；正向收益训练截断100%，负向截断−80%。固定先验分作对照，不按点名商品加分。','未来7日净收益正且当日可评估池前30仅为事后龙头标签，不进入特征。排名按全池，熊市/局部修复为分组评价。','分数是当日排序映射，不是盈利概率。每日重复候选与持仓重叠；以下为商品日统计，不是独立交易或资金组合收益。','固定池有存活偏差，历史修订和已知事件构成研究局限；缺日/量无法完成标签的样本被排除，要结合信号数与可评估数判断。','无真实会员身份/成本；承接是价格量能代理，缺历史求购不倒填。两款略磨缺ID仍明确缺失。','**目前不授予正式买入资格；通过历史诊断也必须冻结模型并接受前瞻验证。**','','| 时段 | 环境 | 模型 | 前K | 信号/结果 | 14日净均值 | 同池基准 | 胜率 | 7日龙头召回 |','|---|---|---|---:|---:|---:|---:|---:|']
    for s in summaries:
        lines.append(f'| {s["window"]} | {s["context"]} | {s["method"]} | {s["top_k"]} | {s["signals"]}/{s["n"]} | {pct(s["mean14"])} | {pct(s["baseline_mean14"])} | {pct(s["win14"])} | {pct(s["winner_recall7"])} |')
    lines+=['','逐案例−7/−3/0/+3/+7日排名与收益见case_rankings.csv；每日完整排名见historical_rankings.csv.gz；当前研究候选见current_candidates.csv。']
    (OUT/'report.md').write_text('\n'.join(lines)+'\n')
    if os.environ.get('GITHUB_STEP_SUMMARY'):Path(os.environ['GITHUB_STEP_SUMMARY']).write_text('\n'.join(lines))
    print('RANK_RESEARCH_COMPLETE',len(current),flush=True)
if __name__=='__main__':main()
