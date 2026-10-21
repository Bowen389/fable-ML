"""Time-purged shape memory built from historical outcomes, not manual case identities."""
import concurrent.futures as futures
import json
import os
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from leader_research import CACHE,collect
from bear_rebound_research import feature_frame
from rebound_rank_research import enrich,daily_rank,measure
from rebound_stage_research import add_stages,include_registered_items,clean_json
from rebound_case_learning import event_samples,case_windows
from rebound_shape_transfer import shape_features,fit_recipe,predict
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'/'rebound_memory'
RECIPES={'all_history':None,'recent540':540}

def prototypes_before(d,start,recent=None):
    boundary=pd.Timestamp(start)
    a=d[d.eligible&d.potential21.notna()&d.y14.notna()&(d.date+pd.Timedelta(days=22)<boundary)]
    if recent is not None:a=a[a.date>=boundary-pd.Timedelta(days=recent)]
    positive=a[a.winner21.eq(1)&(a.y7.gt(0)|a.y14.gt(0))&a.r7.le(.2)].sort_values(['name','date'])
    keep=[]
    for _,g in positive.groupby('name',sort=False):
        nextday=pd.Timestamp.min
        for idx,day in g.date.items():
            if day>=nextday:keep.append(idx);nextday=day+pd.Timedelta(days=22)
    pos=positive.loc[keep]
    if len(pos)>1200:pos=pos.sample(1200,random_state=42)
    neg=a[a.potential21.lt(.10)&a.y14.le(0)&a.r7.le(.2)]
    if len(neg)>1500:neg=neg.sample(1500,random_state=42)
    if len(pos)<30 or len(neg)<100:raise RuntimeError('Insufficient historical prototypes: '+str(start))
    q=pd.concat([pos.assign(learning_label=1),neg.assign(learning_label=0)],ignore_index=True)
    return q

def main():
    OUT.mkdir(parents=True,exist_ok=True);CACHE.mkdir(exist_ok=True)
    cases=json.loads((ROOT/'research/bear_rebound_cases.json').read_text());u=include_registered_items(json.loads((ROOT/'firepulse_universe.json').read_text()),cases)
    excluded=('Nova |','XM1014 |','MAG-7 |','Sawed-Off |','Negev |','M249 |','R8 Revolver |')
    u=[x for x in u if x.get('id') and not x['name'].startswith(excluded)]
    today=pd.Timestamp.now(tz='Asia/Shanghai').tz_localize(None).normalize();frames=[];fail=[]
    with futures.ThreadPoolExecutor(max_workers=3) as ex:
        jobs={ex.submit(collect,x,today):x for x in u}
        for i,f in enumerate(futures.as_completed(jobs),1):
            try:frames.append(f.result())
            except Exception as e:fail.append({'name':jobs[f]['name'],'error':str(e)})
            if i%100==0:print('FETCH',i,'loaded',len(frames),flush=True)
    if not frames:raise RuntimeError('No history')
    d,base=add_stages(enrich(feature_frame(pd.concat(frames,ignore_index=True))[0]));d,sets=shape_features(d,base);cols=sets['volatility_scaled'];latest=d[d.eligible].date.max()
    periods=[('Q1','2026-01-01','2026-04-01'),('Q2','2026-04-01','2026-07-01'),('Q3','2026-07-01','2026-10-01'),('Q4_partial','2026-10-01',str((latest+pd.Timedelta(days=1)).date()))]
    chunks=[];audits=[];prototype_rows=[]
    for label,lo,hi in periods:
        z=d[d.eligible&d.date.ge(lo)&d.date.lt(hi)].copy()
        for recipe,recent in RECIPES.items():
            q=prototypes_before(d,lo,recent);model=fit_recipe(q,cols,'shape_template')
            p=predict(model,z,cols);z[recipe+'_raw']=p;z[recipe+'_rank']=daily_rank(z,pd.Series(p,index=z.index))
            audit={'window':label,'start':lo,'recipe':recipe,'positive_prototypes':int(q.learning_label.eq(1).sum()),'negative_prototypes':int(q.learning_label.eq(0).sum()),'latest_training_label':str((q.date.max()+pd.Timedelta(days=22)).date()),'earliest_prototype':str(q.date.min().date()),'manual_case_labels_used':False}
            audits.append(audit);prototype_rows.append(q[['date','name','learning_label']].assign(window=label,recipe=recipe));print('MEMORY_FOLD',audit,flush=True)
        z['window']=label;chunks.append(z)
    pred=pd.concat(chunks,ignore_index=True);summaries=[]
    for label,lo,hi in periods:
        for recipe in RECIPES:
            for context in ('all','bear','repair'):
                q=pred[pred.window.eq(label)]
                if context=='bear':q=q[q.bear_context]
                if context=='repair':q=q[q.environment_ok]
                for K in (10,30):
                    top=q[q[recipe+'_rank']<=K]
                    summaries.append({'window':label,'recipe':recipe,'context':context,'top_k':K,**measure(top),'baseline_net14':float(q.y14.mean()) if q.y14.notna().any() else None})
    samples=event_samples(pred,cases);windows=[]
    for recipe in RECIPES:
        q=samples.copy();q['rank']=q[recipe+'_rank'];windows+=case_windows(q,cases,'chronological_memory:'+recipe)
    pd.DataFrame(windows).to_csv(OUT/'case_windows.csv',index=False,encoding='utf-8-sig')
    pd.concat(prototype_rows,ignore_index=True).to_csv(OUT/'historical_prototypes.csv.gz',index=False,compression='gzip')
    pred[['date','name','y7','y14','potential21','mae14','window']+[r+'_rank' for r in RECIPES]].to_csv(OUT/'historical_rankings.csv.gz',index=False,compression='gzip')
    current=d[d.eligible&d.date.eq(latest)].copy();models={}
    for recipe,recent in RECIPES.items():
        q=prototypes_before(d,latest,recent);model=fit_recipe(q,cols,'shape_template');models[recipe]=model
        p=predict(model,current,cols);current[recipe+'_rank']=daily_rank(current,pd.Series(p,index=current.index))
    current['status']='历史模式记忆研究，未获买入资格'
    current.sort_values('all_history_rank')[['date','name','cn','id','close','status']+[r+'_rank' for r in RECIPES]].to_csv(OUT/'current_candidates.csv',index=False,encoding='utf-8-sig')
    joblib.dump({'models':models,'features':cols},OUT/'memory_models.joblib')
    result={'version':'historical-shape-memory-v1','asof':str(latest.date()),'loaded':len(frames),'requested':len(u),'failures':fail,'features':cols,'audits':audits,'summaries':summaries,'manual_case_labels_used_for_training':False,'training_labels_mature_before_prediction':True,'fee_buy':0,'fee_sell':.01,'slippage':0,'qualified_systems':[],'production_modified':False,'limitations':['通过历史结果自动定义赢家，筛选与特征均是研究者当前设计，仍有反复研究偏差，不代表完全未见的独立验证','固定商品池有存活偏差，历史接口数据可能修订','人工指定案例只用于研究池精确映射与事后评估，不用于原型训练标签或奖励','模板正例为未来7—21日净涨幅前30且>=15%、7或14日净收益正、信号前7日涨幅<=20%；按商品22日去重，正例最多1200，负例最多1500，固定随机种子','相似度不是盈利概率；商品日信号重叠，不是资金组合回测']}
    (OUT/'validation.json').write_text(json.dumps(clean_json(result),ensure_ascii=False,indent=2,allow_nan=False))
    lines=['# 只使用当时已成熟历史的形态记忆',f'截至{latest.date()}；加载{len(frames)}/{len(u)}件。','人工指定案例不参与训练标签。正例与失败对照来自预测季度开始前已完成22日结果的历史，未来日期不会进入原型库。','两个固定记忆范围：全部可用历史，以及最近540日；不按指定案例排名选一个范围冒充事前选择。','输入采用标准化相对形态，不输入具体商品身份、绝对价格、类别或当期大盘水平。费用仅卖出1%、买入0、零滑点。','时点隔离正确也仍有历史研究反复选型、固定池存活及数据修订偏差；需前瞻验证，无正式买入资格。','','| 事件 | 范围 | 可评估 | ±7日前30覆盖 |','|---|---|---:|---:|']
    for event in cases['events']:
        for recipe in RECIPES:
            q=[x for x in windows if x['event']==event['dates'][0] and x['method']=='chronological_memory:'+recipe and x['top_k']==30]
            lines.append(f'| {event["dates"][0]} | {recipe} | {sum(x["days_evaluated"]>0 for x in q)}/{len(q)} | {sum(x["first_top_date"] is not None for x in q)} |')
    lines+=['','## 当时可用的原型数量','| 时段 | 范围 | 正例 | 负例 | 最晚训练结果日 |','|---|---|---:|---:|---|']
    for a in audits:lines.append(f'| {a["window"]} | {a["recipe"]} | {a["positive_prototypes"]} | {a["negative_prototypes"]} | {a["latest_training_label"]} |')
    lines+=['','## 扣费后表现','| 时段 | 范围 | 环境 | 前K | 样本 | 净均值14日 | 胜率 |','|---|---|---|---:|---:|---:|---:|']
    pct=lambda x:'—' if x is None else f'{x:.2%}'
    for s in summaries:lines.append(f'| {s["window"]} | {s["recipe"]} | {s["context"]} | {s["top_k"]} | {s["n"]} | {pct(s["mean14"])} | {pct(s["win14"])} |')
    text='\n'.join(lines)+'\n';(OUT/'report.md').write_text(text)
    if os.environ.get('GITHUB_STEP_SUMMARY'):Path(os.environ['GITHUB_STEP_SUMMARY']).write_text(text)
    print('HISTORICAL_MEMORY_COMPLETE',flush=True)
if __name__=='__main__':main()
