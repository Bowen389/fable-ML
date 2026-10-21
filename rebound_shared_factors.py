"""Transparent common-factor development search. Not an independent historical validation."""
import concurrent.futures as futures
import json
import os
from pathlib import Path
import numpy as np
import pandas as pd
from leader_research import CACHE,collect
from bear_rebound_research import feature_frame
from rebound_rank_research import enrich,daily_rank
from rebound_stage_research import add_stages,include_registered_items,clean_json
from rebound_case_learning import event_samples,case_windows
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'/'rebound_shared'
FACTORS=['relative_lead','relative_turn','volume_step','volatility_activation','cold_peer','early_participation']

def factor_frame(d):
    d=d.copy()
    pct=lambda col:d[col].where(d.eligible).groupby(d.date).rank(pct=True)
    d['relative_lead']=(pct('peer_relative_7')+pct('relative_7'))/2
    d['relative_turn']=pct('relative_3')
    d['volume_step']=pct('recent_volume_step')
    d['volatility_activation']=pct('volatility_10')
    d['cold_peer']=1-pct('peer_momentum_21')
    d['early_participation']=pct('early_vol_cv')
    return d

def weights_grid(total=5,parts=6):
    def rec(left,n):
        if n==1:yield [left];return
        for i in range(left+1):
            for tail in rec(left-i,n-1):yield [i]+tail
    return np.array(list(rec(total,parts)),dtype=float)/total

def rank_matrix(sample,weights):
    # Missing factor contributes no points, but coverage is exported. Not imputed to neutral.
    x=sample[FACTORS].fillna(0).to_numpy();scores=x@weights.T
    ranks=np.empty(scores.shape,dtype=np.int32)
    for _,indexes in sample.groupby('date',sort=True).groups.items():
        ix=np.asarray(list(indexes));values=scores[ix]
        order=np.argsort(-values,axis=0,kind='stable');local=np.empty_like(order)
        np.put_along_axis(local,order,np.arange(1,len(ix)+1)[:,None],axis=0)
        ranks[ix]=local
    return scores,ranks

def case_rank_minima(sample,ranks,cases):
    records=[];minimum=[]
    for ei,event in enumerate(cases['events']):
        for item in event.get('members',event.get('cases',[])):
            observed=sample.event_id.eq(ei)&sample.name.eq(item['name'])
            useful=sample.potential21.ge(.15)&(sample.y7.gt(0)|sample.y14.gt(0))
            ix=sample.index[observed&useful].to_numpy()
            records.append({'event_id':ei,'event':event['dates'][0],'name':item['name'],'cn':item['cn'],'evaluated':bool(observed.any()),'has_future_profitable_window':len(ix)>0})
            minimum.append(ranks[ix].min(axis=0) if len(ix) else np.full(ranks.shape[1],100000))
    return records,np.asarray(minimum)

def objective(records,minimum,events=None):
    if events is None:events=sorted({x['event_id'] for x in records})
    rates=[];means=[]
    for ei in events:
        ix=[i for i,x in enumerate(records) if x['event_id']==ei]
        rates.append((minimum[ix]<=30).mean(axis=0));means.append(minimum[ix].clip(max=1000).mean(axis=0))
    # Same formula for all items. Worst event first, then mean event coverage, then average best rank.
    return np.stack([np.min(rates,axis=0),np.mean(rates,axis=0),-np.mean(means,axis=0)],axis=1)

def choose(objectives):
    return max(range(len(objectives)),key=lambda i:tuple(objectives[i]))

def main():
    OUT.mkdir(parents=True,exist_ok=True);CACHE.mkdir(exist_ok=True)
    cases=json.loads((ROOT/'research/bear_rebound_cases.json').read_text());u=include_registered_items(json.loads((ROOT/'firepulse_universe.json').read_text()),cases)
    excluded=('Nova |','XM1014 |','MAG-7 |','Sawed-Off |','Negev |','M249 |','R8 Revolver |')
    u=[x for x in u if x.get('id') and not x['name'].startswith(excluded)]
    today=pd.Timestamp.now(tz='Asia/Shanghai').tz_localize(None).normalize();frames=[];fail=[]
    with futures.ThreadPoolExecutor(max_workers=3) as ex:
        tasks={ex.submit(collect,x,today):x for x in u}
        for i,f in enumerate(futures.as_completed(tasks),1):
            try:frames.append(f.result())
            except Exception as e:fail.append({'name':tasks[f]['name'],'error':str(e)})
            if i%100==0:print('FETCH',i,'loaded',len(frames),flush=True)
    if not frames:raise RuntimeError('No history')
    d,cols=add_stages(enrich(feature_frame(pd.concat(frames,ignore_index=True))[0]));d=factor_frame(d);latest=d[d.eligible].date.max();sample=event_samples(d,cases).reset_index(drop=True)
    weights=weights_grid();scores,ranks=rank_matrix(sample,weights);records,minimum=case_rank_minima(sample,ranks,cases);objectives=objective(records,minimum);selected=choose(objectives)
    folds=[];held_chunks=[]
    for ei,event in enumerate(cases['events']):
        selected_fold=choose(objective(records,minimum,[j for j in range(len(cases['events'])) if j!=ei]))
        z=sample[sample.event_id.eq(ei)].copy();z['rank']=ranks[z.index,selected_fold];z['raw']=scores[z.index,selected_fold]
        held_chunks.append(z)
        folds.append({'held_event':event['dates'][0],'selected_profile':int(selected_fold),'weights':dict(zip(FACTORS,weights[selected_fold].tolist()))})
    held=pd.concat(held_chunks,ignore_index=True)
    apparent=sample.copy();apparent['rank']=ranks[:,selected];apparent['raw']=scores[:,selected]
    windows=case_windows(apparent,cases,'development_selected')+case_windows(held,cases,'event_holdout_development')
    good=lambda z:z[z.potential21.ge(.15)&(z.y7.gt(0)|z.y14.gt(0))]
    useful_windows=case_windows(good(apparent),cases,'development_selected')+case_windows(good(held),cases,'event_holdout_development')
    pd.DataFrame(useful_windows).to_csv(OUT/'outcome_qualified_windows.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(windows).to_csv(OUT/'case_windows.csv',index=False,encoding='utf-8-sig')
    profiles=[]
    for i,w in enumerate(weights):profiles.append({'profile':i,**dict(zip(FACTORS,w.tolist())),'minimum_event_coverage':objectives[i,0],'mean_event_coverage':objectives[i,1],'mean_best_rank':-objectives[i,2]})
    pd.DataFrame(profiles).to_csv(OUT/'all_profiles.csv',index=False,encoding='utf-8-sig')
    savecols=['event_id','date','name','cn','rank','raw','y7','y14','potential21']+FACTORS
    apparent[savecols].to_csv(OUT/'development_rows.csv.gz',index=False,compression='gzip')
    held[savecols].to_csv(OUT/'event_holdout_rows.csv.gz',index=False,compression='gzip')
    current=d[d.eligible&d.date.eq(latest)].copy();current['score']=100*(current[FACTORS].fillna(0).to_numpy()@weights[selected]);current['rank']=daily_rank(current,current.score);current['factor_coverage']=current[FACTORS].notna().mean(axis=1);current['status']='六因子开发参考，未获买入资格'
    current.sort_values('rank')[['date','name','cn','id','close','rank','score','factor_coverage','status']+FACTORS].to_csv(OUT/'current_candidates.csv',index=False,encoding='utf-8-sig')
    metrics=[]
    for method,z in [('development_selected',apparent),('event_holdout_development',held)]:
        for ei,event in enumerate(cases['events']):
            q=z[z.event_id.eq(ei)&z['rank'].le(30)];valid=q[q.y14.notna()]
            metrics.append({'method':method,'event':event['dates'][0],'signals':len(q),'evaluated':len(valid),'mean_net14':float(valid.y14.mean()) if len(valid) else None,'median_net14':float(valid.y14.median()) if len(valid) else None,'win14':float(valid.y14.gt(0).mean()) if len(valid) else None,'potential_hit':float(q.potential21.ge(.15).mean()) if len(q) else None})
    result={'version':'common-factors-development-v1','asof':str(latest.date()),'loaded':len(frames),'requested':len(u),'failures':fail,'selected_profile':int(selected),'weights':dict(zip(FACTORS,weights[selected].tolist())),'profiles_tested':len(weights),'selection_objective':objectives[selected].tolist(),'coverage_goal':'前30且未来峰值潜力>=15%、固定7或14日净收益为正；未来结果仅用于开发目标，不用于当日过滤','folds':folds,'metrics':metrics,'fee_sell':.01,'fee_buy':0,'slippage':0,'production_modified':False,'qualified_systems':[],'historically_tradable_validation':False,'limitations':['六因子的发现已使用三个事件，因此事件留一也只是开发诊断，不能视作完全独立验证','权重网格直接按指定案例±7日排名选取，存在已知赢家与多重比较偏差','没有具体商品名称或ID加分；但缺失因子贡献0并显式显示覆盖率','最佳排名是事后窗口统计，不等于当时知道何时交易；首入榜日期与收益另列','仅研究日K代理成交与商品日统计，不是资金组合回测']}
    (OUT/'validation.json').write_text(json.dumps(clean_json(result),ensure_ascii=False,indent=2,allow_nan=False))
    lines=['# 六项共同特征：透明排序公式开发',f'截至{latest.date()}；加载{len(frames)}/{len(u)}；比较{len(weights)}组步长20%的非负权重。','**直接针对已知案例开发，含特征发现与权重选择偏差；不是独立验证或买入系统。**','六项均为当日全池分位：相对领先、相对转强、近期量能台阶、波动转活跃、弱同类背景、前期量能活跃。','选择优先提高三个事件最差的有效前30覆盖，再平均事件覆盖，再平均有效最好名次；有效要求后续潜力>=15%且7或14日净收益为正，仅用于事后开发评价，不是实时过滤。不对单个商品换公式。','首次入榜/最好日期/之后固定7与14日收益见case_windows.csv，手续费仅卖出1%、无滑点。','权重：'+json.dumps(result['weights'],ensure_ascii=False),'','| 事件 | 方法 | 可评估 | ±7日前30覆盖 | 未来结果合格的覆盖 |','|---|---|---:|---:|---:|']
    for event in cases['events']:
        for method in ('development_selected','event_holdout_development'):
            q=[x for x in windows if x['event']==event['dates'][0] and x['method']==method and x['top_k']==30]
            v=[x for x in useful_windows if x['event']==event['dates'][0] and x['method']==method and x['top_k']==30]
            lines.append(f'| {event["dates"][0]} | {method} | {sum(x["days_evaluated"]>0 for x in q)}/{len(q)} | {sum(x["first_top_date"] is not None for x in q)} | {sum(x["first_top_date"] is not None for x in v)} |')
    lines+=['','## 限制',*['- '+x for x in result['limitations']],'','生产评分未改。']
    text='\n'.join(lines)+'\n';(OUT/'report.md').write_text(text)
    if os.environ.get('GITHUB_STEP_SUMMARY'):Path(os.environ['GITHUB_STEP_SUMMARY']).write_text(text)
    print('SHARED_FACTOR_COMPLETE',result['weights'],flush=True)
if __name__=='__main__':main()
