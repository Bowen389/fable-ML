"""Retrospective cross-event shape transfer, with explicit cohort-feature ablations."""
import concurrent.futures as futures
import json
import os
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import RobustScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.ensemble import HistGradientBoostingClassifier
from leader_research import CACHE,collect
from bear_rebound_research import feature_frame
from rebound_rank_research import enrich,daily_rank
from rebound_stage_research import add_stages,include_registered_items,clean_json
from rebound_case_learning import event_samples,metrics,case_windows
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'/'rebound_shapes'
RECIPES=('full_context_control','shape_only','volatility_scaled','shape_template')

def shape_features(d,base_cols):
    d=d.copy();new=[]
    for _,g in d.groupby('name',sort=False):
        vol=g.volatility_20.shift(3).clip(lower=.003)
        span=g.early_range.clip(lower=.05)
        for H,source in ((1,'r1'),(3,'r3'),(7,'r7'),(14,'return_14'),(30,'r30')):
            col='shape_return_z'+str(H);d.loc[g.index,col]=g[source]/(vol*np.sqrt(H));new.append(col)
        for source in ('early_drift','middle_return','wash_return','wash_support','drawdown','support_gap','trend_gap'):
            col='shape_'+source;d.loc[g.index,col]=g[source]/span;new.append(col)
        for source in ('relative_7','peer_relative_7'):
            col='shape_'+source;d.loc[g.index,col]=g[source]/(vol*np.sqrt(7));new.append(col)
    new=list(dict.fromkeys(new))
    excluded={'log_price','log_volume20','log_volume20_percentile','is_glove','is_agent','breadth','breadth_change3','m3','m7','m30'}
    pure=[x for x in base_cols if x not in excluded and not x.startswith('peer_momentum_')]
    ratio_cols=['early_vol_change','early_vol_cv','middle_volume','wash_contraction','recent_volume_step','volume_up_fraction','price_up_fraction','price_efficiency','volume_cv_5','volume_cv_10','volume_cv_20','up_down_volume','close_location']
    scaled=new+ratio_cols
    d[new]=d[new].replace([np.inf,-np.inf],np.nan)
    return d,{'full_context_control':base_cols,'shape_only':pure,'volatility_scaled':scaled,'shape_template':scaled}

def fit_recipe(train,cols,recipe):
    q=train[train.learning_label.notna()]
    if q.learning_label.nunique()<2:raise RuntimeError('Insufficient classes')
    if recipe=='shape_template':
        imputer=SimpleImputer(strategy='median',keep_empty_features=True)
        x=imputer.fit_transform(q[cols]);scaler=RobustScaler(quantile_range=(10,90));x=np.clip(scaler.fit_transform(x),-6,6)
        positive=x[q.learning_label.eq(1).to_numpy()];negative=x[q.learning_label.eq(0).to_numpy()]
        rng=np.random.default_rng(42)
        if len(negative)>1500:negative=negative[rng.choice(len(negative),1500,replace=False)]
        p=NearestNeighbors(n_neighbors=min(3,len(positive)),algorithm='brute',n_jobs=2).fit(positive)
        n=NearestNeighbors(n_neighbors=min(10,len(negative)),algorithm='brute',n_jobs=2).fit(negative)
        return {'kind':'template','imputer':imputer,'scaler':scaler,'positive':p,'negative':n}
    leaves=15 if recipe in ('full_context_control','shape_only') else 7
    model=HistGradientBoostingClassifier(max_leaf_nodes=leaves,max_iter=150,min_samples_leaf=20,l2_regularization=30,learning_rate=.04,early_stopping=False,class_weight='balanced',random_state=42)
    model.fit(q[cols],q.learning_label.astype(int))
    return model

def predict(model,z,cols):
    if isinstance(model,dict):
        x=np.clip(model['scaler'].transform(model['imputer'].transform(z[cols])),-6,6)
        a=model['positive'].kneighbors(x,return_distance=True)[0].mean(axis=1)
        b=model['negative'].kneighbors(x,return_distance=True)[0].mean(axis=1)
        return b/(a+b+1e-9)
    return model.predict_proba(z[cols])[:,1]

def score(model,z,cols):
    z=z.copy();z['raw']=predict(model,z,cols);z['rank']=daily_rank(z,z.raw)
    return z

def coverage_objective(windows,mean_ap):
    events=sorted({x['event'] for x in windows});rates=[]
    for event in events:
        q=[x for x in windows if x['event']==event and x['top_k']==30]
        rates.append(sum(x['first_top_date'] is not None for x in q)/len(q))
    return [min(rates),float(np.mean(rates)),mean_ap]

def main():
    OUT.mkdir(parents=True,exist_ok=True);CACHE.mkdir(exist_ok=True)
    cases=json.loads((ROOT/'research/bear_rebound_cases.json').read_text())
    u=include_registered_items(json.loads((ROOT/'firepulse_universe.json').read_text()),cases)
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
    d,base=add_stages(enrich(feature_frame(pd.concat(frames,ignore_index=True))[0]));d,feature_sets=shape_features(d,base);latest=d[d.eligible].date.max();sample=event_samples(d,cases)
    windows=[];selection=[];predictions=[];apparent_predictions=[];models={}
    for recipe in RECIPES:
        cols=feature_sets[recipe];chunks=[];records=[]
        for ei,event in enumerate(cases['events']):
            train=sample[~sample.event_id.eq(ei)];test=sample[sample.event_id.eq(ei)]
            model=fit_recipe(train,cols,recipe);z=score(model,test,cols);chunks.append(z)
            record={'event':event['dates'][0],**metrics(z)};records.append(record)
            print('HOLDOUT',recipe,record,flush=True)
        held=pd.concat(chunks,ignore_index=True);held['recipe']=recipe;predictions.append(held)
        w=case_windows(held,cases,'event_holdout:'+recipe);windows+=w
        mean_ap=float(np.mean([x['ap'] for x in records if x['ap'] is not None]))
        selection.append({'recipe':recipe,'features':len(cols),'objective':coverage_objective(w,mean_ap),'folds':records})
        model=fit_recipe(sample,cols,recipe);models[recipe]=model
        chunks=[score(model,z,cols) for _,z in sample.groupby('event_id',sort=False)]
        apparent=pd.concat(chunks,ignore_index=True);apparent['recipe']=recipe;apparent_predictions.append(apparent)
        windows+=case_windows(apparent,cases,'apparent_fit:'+recipe)
    chosen=max(selection,key=lambda x:x['objective'])['recipe']
    pd.DataFrame(windows).to_csv(OUT/'case_windows.csv',index=False,encoding='utf-8-sig')
    savecols=['recipe','event_id','date','name','cn','rank','raw','learning_label','y7','y14','potential21']
    pd.concat(predictions)[savecols].to_csv(OUT/'event_holdout_rows.csv.gz',index=False,compression='gzip')
    pd.concat(apparent_predictions)[savecols].to_csv(OUT/'apparent_fit_rows.csv.gz',index=False,compression='gzip')
    current=d[d.eligible&d.date.eq(latest)].copy()
    for recipe in RECIPES:
        mature=sample[sample.date+pd.Timedelta(days=22)<latest]
        models[recipe]=fit_recipe(mature,feature_sets[recipe],recipe)
        current[recipe+'_rank']=daily_rank(current,pd.Series(predict(models[recipe],current,feature_sets[recipe]),index=current.index))
    current['selected_rank']=current[chosen+'_rank'];current['status']='跨事件形态研究，未获买入资格'
    current.sort_values('selected_rank')[['date','name','cn','id','close','selected_rank','status']+[x+'_rank' for x in RECIPES]].to_csv(OUT/'current_candidates.csv',index=False,encoding='utf-8-sig')
    joblib.dump({'models':models,'features':feature_sets,'selected':chosen},OUT/'shape_models.joblib')
    result={'version':'shape-transfer-v1','asof':str(latest.date()),'loaded':len(frames),'requested':len(u),'failures':fail,'feature_sets':feature_sets,'selection':selection,'selected':chosen,'selection_rule':'先最大化三个事件最差前30覆盖率，再平均事件覆盖率，最后平均AP；选择使用了事件留一结果，因此只是开发选模','fee_sell':.01,'fee_buy':0,'slippage':0,'historically_tradable_validation':False,'qualified_systems':[],'production_modified':False}
    (OUT/'validation.json').write_text(json.dumps(clean_json(result),ensure_ascii=False,indent=2,allow_nan=False))
    lines=['# 去除行情与价格档位的形态迁移实验',f'截至{latest.date()}；加载{len(frames)}/{len(u)}；按开发目标选中{chosen}。','**这是回溯开发实验；事件留一可能使用较晚行情，且选模使用了这些结果，不是历史可执行或最终独立验证。**','四组对照：全背景控制；去除绝对价格、绝对量、手套/探员类别、大盘背景和同类整体动量；进一步按自身历史波动与前期区间标准化；标准化形态的正负案例近邻模板。','人工案例身份只构造训练标签，不输入模型。所有单日特征不使用该日之后数据。','选模按三事件最差前30覆盖、平均事件覆盖、AP依次比较，不能对每件商品事后换一个模型。','模板以训练样本拟合缺失值和缩放，仅用训练负例确定固定随机子样本；分数不是概率。','成本为买入0、卖出1%、零滑点。±7日最好名次是事后诊断，首次入榜日期和后续收益同时保留。','','| 事件 | 模型 | 方法 | 可评估 | 前30覆盖 |','|---|---|---|---:|---:|']
    for event in cases['events']:
        for recipe in RECIPES:
            for method in ('event_holdout','apparent_fit'):
                q=[x for x in windows if x['event']==event['dates'][0] and x['method']==method+':'+recipe and x['top_k']==30]
                lines.append(f'| {event["dates"][0]} | {recipe} | {method} | {sum(x["days_evaluated"]>0 for x in q)}/{len(q)} | {sum(x["first_top_date"] is not None for x in q)} |')
    lines+=['','训练拟合覆盖不代表泛化；跨事件有改善也仍需冻结后的独立行情验证。生产评分保持不变。']
    text='\n'.join(lines)+'\n';(OUT/'report.md').write_text(text)
    if os.environ.get('GITHUB_STEP_SUMMARY'):Path(os.environ['GITHUB_STEP_SUMMARY']).write_text(text)
    print('SHAPE_TRANSFER_COMPLETE',chosen,flush=True)
if __name__=='__main__':main()
