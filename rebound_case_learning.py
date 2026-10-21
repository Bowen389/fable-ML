"""Known-case mechanism learning with event holdouts; explicitly retrospective diagnostics."""
import concurrent.futures as futures
import json
import os
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score
from leader_research import CACHE,collect
from bear_rebound_research import feature_frame
from rebound_rank_research import enrich,daily_rank,rank_value
from rebound_stage_research import add_stages,window_summary,clean_json,include_registered_items
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'/'rebound_cases'

def event_samples(d,cases):
    chunks=[]
    for ei,event in enumerate(cases['events']):
        anchor=pd.Timestamp(event['dates'][0]);names={x['name'] for x in event.get('members',event.get('cases',[]))}
        z=d[d.eligible&d.date.between(anchor-pd.Timedelta(days=7),anchor+pd.Timedelta(days=7))].copy()
        z['event_id']=ei;z['case_identity_label']=z.name.isin(names)
        # Future outcomes only construct supervised labels. All pool rows stay in prediction.
        positive=z.case_identity_label&z.potential21.ge(.15)&z.y14.gt(0)
        negative=~z.case_identity_label&z.potential21.lt(.10)&z.y14.le(0)
        z['learning_label']=np.where(positive,1,np.where(negative,0,np.nan))
        chunks.append(z)
    return pd.concat(chunks,ignore_index=True)

def fit(train,cols,leaves):
    q=train[train.learning_label.notna()]
    if q.learning_label.nunique()<2:raise RuntimeError('Need positive cases and negative controls')
    model=HistGradientBoostingClassifier(max_leaf_nodes=leaves,max_iter=150,min_samples_leaf=20,l2_regularization=20,learning_rate=.04,early_stopping=False,class_weight='balanced',random_state=42)
    model.fit(q[cols],q.learning_label.astype(int))
    return model

def score_rows(model,z,cols):
    z=z.copy();z['raw']=model.predict_proba(z[cols])[:,1]
    z['rank']=daily_rank(z,z.raw)
    return z

def metrics(z):
    labelled=z[z.learning_label.notna()]
    top=z[z['rank']<=30];mature=top[top.y14.notna()]
    return {'rows':len(z),'ap':float(average_precision_score(labelled.learning_label,labelled.raw)) if labelled.learning_label.nunique()==2 else None,'top30_rows':len(top),'top30_evaluated':len(mature),'top30_net14':float(mature.y14.mean()) if len(mature) else None,'top30_win14':float(mature.y14.gt(0).mean()) if len(mature) else None}

def case_windows(pred,cases,method):
    result=[]
    for ei,event in enumerate(cases['events']):
        anchor=pd.Timestamp(event['dates'][0])
        for item in event.get('members',event.get('cases',[])):
            z=pred[pred.event_id.eq(ei)&pred.name.eq(item['name'])]
            for K in (10,30):result.append({'event':str(anchor.date()),'name':item['name'],'cn':item['cn'],'method':method,'top_k':K,**window_summary(z,anchor,'rank',K)})
    return result

def feature_contrasts(sample,cols):
    rows=[]
    for ei,z in sample.groupby('event_id',sort=True):
        pos=z[z.learning_label.eq(1)];neg=z[z.learning_label.eq(0)]
        for col in cols:
            a=pos[col].dropna();b=neg[col].dropna()
            spread=float(b.quantile(.75)-b.quantile(.25)) if len(b) else np.nan
            am=float(a.median()) if len(a) else None;bm=float(b.median()) if len(b) else None
            rows.append({'event_id':int(ei),'feature':col,'positive_n':len(a),'negative_n':len(b),'positive_median':am,'negative_median':bm,'difference_in_negative_iqr':(am-bm)/spread if am is not None and bm is not None and spread>0 else None})
    return rows

def common_directions(rows,event_count):
    allowed=('early_','middle_','wash_','recent_','relative_','peer_','volume_up_','price_up_','price_efficiency','volatility_')
    common=[]
    for feature in sorted({x['feature'] for x in rows}):
        if not feature.startswith(allowed):continue
        q=[x for x in rows if x['feature']==feature and x['positive_n']>=5 and x['negative_n']>=10 and x['difference_in_negative_iqr'] is not None]
        if len(q)!=event_count:continue
        signs=[np.sign(x['difference_in_negative_iqr']) for x in q]
        if len(set(signs))==1 and signs[0]!=0:
            common.append({'feature':feature,'direction':'higher' if signs[0]>0 else 'lower','minimum_absolute_effect_iqr':float(min(abs(x['difference_in_negative_iqr']) for x in q))})
    return sorted(common,key=lambda x:x['minimum_absolute_effect_iqr'],reverse=True)

def main():
    OUT.mkdir(parents=True,exist_ok=True);CACHE.mkdir(exist_ok=True)
    cases=json.loads((ROOT/'research/bear_rebound_cases.json').read_text());u=include_registered_items(json.loads((ROOT/'firepulse_universe.json').read_text()),cases)
    # Reuse exact resolved wear IDs only if previous stage manifest has them; never guess another wear.
    prior=ROOT/'output/rebound_stage/validation.json'
    if prior.exists():
        resolved={x['name']:x.get('resolved_id') for x in json.loads(prior.read_text()).get('exact_wear_resolution',[])}
        for event in cases['events']:
            for item in event.get('members',event.get('cases',[])):
                if not item.get('id') and resolved.get(item['name']):u.append({**item,'id':resolved[item['name']]})
    excluded=('Nova |','XM1014 |','MAG-7 |','Sawed-Off |','Negev |','M249 |','R8 Revolver |')
    u=list({x['id']:x for x in u if x.get('id') and not x['name'].startswith(excluded)}.values())
    frames=[];fail=[];today=pd.Timestamp.now(tz='Asia/Shanghai').tz_localize(None).normalize()
    with futures.ThreadPoolExecutor(max_workers=3) as ex:
        jobs={ex.submit(collect,x,today):x for x in u}
        for i,f in enumerate(futures.as_completed(jobs),1):
            try:frames.append(f.result())
            except Exception as e:fail.append({'name':jobs[f]['name'],'error':str(e)})
            if i%100==0:print('FETCH',i,'loaded',len(frames),flush=True)
    if not frames:raise RuntimeError('No history')
    d,cols=add_stages(enrich(feature_frame(pd.concat(frames,ignore_index=True))[0]));latest=d[d.eligible].date.max()
    sample=event_samples(d,cases);folds=[];all_predictions={};selection=[]
    contrasts=feature_contrasts(sample,cols);shared=common_directions(contrasts,len(cases['events']))
    pd.DataFrame(contrasts).to_csv(OUT/'feature_contrasts.csv',index=False,encoding='utf-8-sig')
    for leaves in (7,15):
        chunks=[];records=[]
        for ei,event in enumerate(cases['events']):
            train=sample[~sample.event_id.eq(ei)];test=sample[sample.event_id.eq(ei)]
            model=fit(train,cols,leaves);z=score_rows(model,test,cols);chunks.append(z)
            record={'held_event':event['dates'][0],'leaves':leaves,'train_positive':int(train.learning_label.eq(1).sum()),'train_negative':int(train.learning_label.eq(0).sum()),**metrics(z)};records.append(record)
            print('EVENT_HOLDOUT',record,flush=True)
        pred=pd.concat(chunks,ignore_index=True);all_predictions[leaves]=pred
        ap=np.mean([x['ap'] for x in records if x['ap'] is not None]);selection.append({'leaves':leaves,'mean_event_ap':float(ap),'folds':records})
    chosen=max(selection,key=lambda x:x['mean_event_ap'])['leaves']
    held=all_predictions[chosen];model=fit(sample,cols,chosen)
    # Apparent fit uses these same labelled cases: publish distinctly, never call it out-of-sample.
    apparent_chunks=[score_rows(model,z,cols) for _,z in sample.groupby('event_id',sort=False)]
    apparent=pd.concat(apparent_chunks,ignore_index=True)
    windows=case_windows(held,cases,'event_holdout_retrospective')+case_windows(apparent,cases,'known_case_apparent_fit')
    pd.DataFrame(windows).to_csv(OUT/'case_windows.csv',index=False,encoding='utf-8-sig')
    savecols=['event_id','date','name','cn','rank','raw','case_identity_label','learning_label','y7','y14','potential21','early_drift','early_vol_change','middle_return','middle_volume','wash_return','wash_support','wash_contraction','recent_volume_step','relative_7','peer_momentum_7']
    held[savecols].to_csv(OUT/'event_holdout_rows.csv.gz',index=False,compression='gzip')
    apparent[savecols].to_csv(OUT/'apparent_fit_rows.csv.gz',index=False,compression='gzip')
    # Rank final features at latest data using only supervised examples whose complete outcomes predate it.
    mature=sample[sample.date+pd.Timedelta(days=22)<latest]
    future_model=fit(mature,cols,chosen);current=score_rows(future_model,d[d.eligible&d.date.eq(latest)],cols)
    current['status']='案例形态研究榜；未获买入资格'
    current.sort_values('rank')[['date','name','cn','id','close','rank','status','early_drift','early_vol_change','middle_return','middle_volume','wash_return','wash_support','wash_contraction','recent_volume_step','relative_7','peer_momentum_7']].to_csv(OUT/'current_candidates.csv',index=False,encoding='utf-8-sig')
    joblib.dump({'model':future_model,'features':cols,'training_case_dates':[x['dates'] for x in cases['events']]},OUT/'case_pattern_model.joblib')
    # Keep feature paths for inspecting shared patterns and why cases were missed.
    named={x['name'] for event in cases['events'] for x in event.get('members',event.get('cases',[]))}
    feature_paths=[]
    for event in cases['events']:
        anchor=pd.Timestamp(event['dates'][0]);names={x['name'] for x in event.get('members',event.get('cases',[]))}
        z=d[d.name.isin(names)&d.date.between(anchor-pd.Timedelta(days=60),anchor+pd.Timedelta(days=21))]
        feature_paths.append(z[['date','name','cn','eligible','close','volume']+cols].assign(event=event['dates'][0]))
    pd.concat(feature_paths).to_csv(OUT/'case_feature_paths.csv.gz',index=False,compression='gzip')
    result={'version':'case-pattern-v1','asof':str(latest.date()),'loaded':len(frames),'requested':len(u),'failures':fail,'features':cols,'training_label_rule':'仅人工案例窗口且潜在涨幅>=15%且14日净收益>0为正；同期未点名且潜在涨幅<10%且14日净收益<=0为负；其余不标负','selected_leaves':chosen,'selection':selection,'common_feature_directions':shared,'event_holdout_metrics':[{'event':cases['events'][int(ei)]['dates'][0],**metrics(z)} for ei,z in held.groupby('event_id')],'apparent_fit_metrics':[{'event':cases['events'][int(ei)]['dates'][0],**metrics(z)} for ei,z in apparent.groupby('event_id')],'fee_sell':.01,'fee_buy':0,'slippage':0,'production_modified':False,'qualified_systems':[],'historically_tradable_validation':False,'limitations':['事件留一使用其他事件的训练标签；早期事件可能学到后期事件，属于回溯机制研究，不是当时可执行收益','模型复杂度也按这三个事件的平均AP选择，事件留一结果已参与开发，不能宣称最终独立测试','同一事件日共享市场变量，样本相关；案例数据有选择偏差','known_case_apparent_fit是训练案例拟合效果，不代表泛化','current_candidates只作新数据的前瞻研究记录；未完成独立事件验证']}
    (OUT/'validation.json').write_text(json.dumps(clean_json(result),ensure_ascii=False,indent=2,allow_nan=False))
    lines=['# 已知龙头形态学习：开发拟合与事件留一',f'截至{latest.date()}；加载{len(frames)}/{len(u)}；特征{len(cols)}项；复杂度{chosen}叶。','**本报告是回溯开发研究，不是历史上可交易的独立验证。**','人工案例身份仅用来构建训练标签，绝不作为模型输入；同时剔除尚未完成后续结果的训练样本。','正例要求已知案例当日之后仍有>=15%拉升潜力且14日净收益为正；同日失败商品作负例，未标注的赢家不强行当成负例。','轮流拿掉整段2月/5月/8月行情，用其余两段训练再排序该段；早期留一可能使用较晚事件，须与按时间滚动v3明确分开。','另列known_case_apparent_fit，直接反映开发模型能否记住这些形态；其效果不能当作样本外成绩。','±7日最佳名次为事后诊断，首次前30及其后收益同时保留。卖出1%、买入0、零滑点。','','| 事件 | 方法 | 可评估 | ±7日前30覆盖 |','|---|---|---:|---:|']
    for event in cases['events']:
        for method in ('event_holdout_retrospective','known_case_apparent_fit'):
            q=[x for x in windows if x['event']==event['dates'][0] and x['method']==method and x['top_k']==30]
            lines.append(f'| {event["dates"][0]} | {method} | {sum(x["days_evaluated"]>0 for x in q)}/{len(q)} | {sum(x["first_top_date"] is not None for x in q)} |')
    lines+=['','## 三段行情同方向的描述性特征','这些是已选案例与失败对照的分布差异，不是因果证明；没有同方向特征时不强行宣称手法一致。','| 特征 | 成功案例相对对照 | 三事件最小差异/IQR |','|---|---|---:|']
    for item in shared[:15]:lines.append(f'| {item["feature"]} | {item["direction"]} | {item["minimum_absolute_effect_iqr"]:.3f} |')
    lines+=['','## 研究边界',*['- '+x for x in result['limitations']],'','完整首次入榜见case_windows.csv；解释路径见case_feature_paths.csv.gz；所有同榜误报保留在逐日排名文件中。']
    text='\n'.join(lines)+'\n';(OUT/'report.md').write_text(text)
    if os.environ.get('GITHUB_STEP_SUMMARY'):Path(os.environ['GITHUB_STEP_SUMMARY']).write_text(text)
    print('CASE_LEARNING_COMPLETE',flush=True)
if __name__=='__main__':main()
