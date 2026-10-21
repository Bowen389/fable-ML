"""Independent sequential-stage rebound ranking; no identity bonuses or production writes."""
import concurrent.futures as futures
import hashlib
import json
import os
from pathlib import Path
import unicodedata
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score
from leader_research import CACHE,collect,request
from bear_rebound_research import feature_frame,net_ratio
from rebound_rank_research import enrich,COLS as BASE,daily_rank,rank_value,measure
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'/'rebound_stage'
SPECS={'stage7_global':('winner7',None),'stage21_global':('winner21',None),'stage21_recent':('winner21',540)}

def clean_json(value):
    if isinstance(value,dict):return {k:clean_json(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [clean_json(v) for v in value]
    if isinstance(value,(float,np.floating)):return float(value) if np.isfinite(value) else None
    if isinstance(value,np.integer):return int(value)
    if isinstance(value,np.bool_):return bool(value)
    return value

def norm(s):return ''.join(unicodedata.normalize('NFKC',str(s)).casefold().split())

def include_registered_items(universe,cases):
    merged={x['id']:x for x in universe if x.get('id')}
    for event in cases['events']:
        for item in event.get('members',event.get('cases',[])):
            if item.get('id'):merged[item['id']]={k:item[k] for k in ('id','name','cn')}
    return list(merged.values())

def exact_search(payload,item):
    matches=set();wanted={norm(item['name']),norm(item['cn'])}
    def walk(node):
        if isinstance(node,dict):
            if any(norm(v) in wanted for v in node.values() if isinstance(v,str)):
                identifier=str(node.get('id',''))
                if identifier.isdigit() and len(identifier)>=14:matches.add(identifier)
            for value in node.values():walk(value)
        elif isinstance(node,list):
            for value in node:walk(value)
    walk(payload)
    return next(iter(matches)) if len(matches)==1 else None

def add_stages(d):
    d=d.copy();parts=[]
    for _,g in d.groupby('name',sort=False):
        c,v=g.close,g.volume;ret=c/c.shift(1)-1;mid=(g.high+g.low)/2
        vals={
          'log_price':np.log(c),'log_volume20':np.log1p(v.rolling(20,min_periods=18).median()),
          'early_drift':c.shift(21)/c.shift(60)-1,
          'early_range':g.high.shift(21).rolling(40,min_periods=36).max()/g.low.shift(21).rolling(40,min_periods=36).min()-1,
          'early_vol_change':v.shift(21).rolling(20,min_periods=18).median()/v.shift(41).rolling(20,min_periods=18).median().replace(0,np.nan),
          'early_vol_cv':v.shift(21).rolling(30,min_periods=27).std()/v.shift(21).rolling(30,min_periods=27).mean().replace(0,np.nan),
          'middle_return':c.shift(7)/c.shift(21)-1,
          'middle_volume':v.shift(7).rolling(14,min_periods=12).mean()/v.shift(21).rolling(30,min_periods=27).median().replace(0,np.nan),
          'wash_return':c.shift(2)/c.shift(7)-1,
          'wash_support':g.low.shift(2).rolling(5).min()/g.low.shift(7).rolling(20,min_periods=18).min()-1,
          'wash_contraction':v.shift(2).rolling(5).mean()/v.shift(7).rolling(14,min_periods=12).mean().replace(0,np.nan),
          'recent_volume_step':v.rolling(3).mean()/v.shift(3).rolling(7,min_periods=6).mean().replace(0,np.nan),
          'volume_up_fraction':v.diff().gt(0).rolling(7).mean(),
          'price_up_fraction':ret.gt(0).rolling(7).mean(),
          'close_location':(c-g.low)/(g.high-g.low).replace(0,np.nan),
          'up_down_volume':v.where(ret>0,0).rolling(10).sum()/v.where(ret<=0,0).rolling(10).sum().replace(0,np.nan),
          'price_efficiency':(c/c.shift(7)-1)/ret.abs().rolling(7).sum().replace(0,np.nan),
          'observations20':c.notna().rolling(20).sum()/20,
          'positive_volume20':v.gt(0).rolling(20).mean(),
          'is_glove':float('Gloves' in g.name.iloc[0] or 'Wraps' in g.name.iloc[0]),
          'is_agent':float('|' not in g.name.iloc[0]),
        }
        for H in (3,5,10,14,21,45,60,90):
            vals['return_'+str(H)]=c/c.shift(H)-1
        for H in (5,10,20):
            vals['volatility_'+str(H)]=ret.rolling(H,min_periods=max(3,H-2)).std()
            vals['volume_cv_'+str(H)]=v.rolling(H,min_periods=max(3,H-2)).std()/v.rolling(H,min_periods=max(3,H-2)).mean().replace(0,np.nan)
        frame=pd.DataFrame(vals,index=g.index)
        for k in ('name','date','family'):frame[k]=g[k]
        parts.append(frame)
    stage=pd.concat(parts).sort_index()
    extra=[k for k in stage if k not in ('name','date','family')]
    for k in extra:d[k]=stage[k]
    for H in (3,7,14,21):
        col='r'+str(H) if H in (3,7) else 'return_'+str(H)
        eligible_value=d[col].where(d.eligible)
        median=eligible_value.groupby(d.date).transform('median')
        peer=eligible_value.groupby([d.date,d.family]).transform('median')
        n=eligible_value.groupby([d.date,d.family]).transform('count')
        d['relative_'+str(H)]=d[col]-median
        d['peer_relative_'+str(H)]=d[col]-peer.where(n>=8)
        d['peer_momentum_'+str(H)]=peer.where(n>=8)
        extra+=['relative_'+str(H),'peer_relative_'+str(H),'peer_momentum_'+str(H)]
    for k in ['early_drift','early_vol_change','middle_volume','wash_contraction','recent_volume_step','volatility_10','log_volume20']:
        col=k+'_percentile';d[col]=d[k].where(d.eligible).groupby(d.date).rank(pct=True);extra.append(col)
    d['potential21']=np.nan;d['mae21']=np.nan
    for _,g in d.groupby('name',sort=False):
        c,v=g.close,g.volume
        good=pd.concat([c.shift(-j).notna()&v.shift(-j).gt(0) for j in range(1,23)],axis=1).all(axis=1)
        future=pd.concat([net_ratio(c.shift(-(H+1))/c.shift(-1)) for H in range(7,22)],axis=1)
        d.loc[g.index,'potential21']=future.max(axis=1).where(good)
        path=pd.concat([c.shift(-j)/c.shift(-1)-1 for j in range(1,23)],axis=1)
        d.loc[g.index,'mae21']=path.min(axis=1).where(good)
    r=d.potential21.where(d.eligible).groupby(d.date).rank(ascending=False,method='first')
    d['winner21']=(r.le(30)&d.potential21.ge(.15)).astype(float).where(d.potential21.notna())
    # Every input is causal; forward returns and future extrema are labels only.
    cols=list(dict.fromkeys(BASE+extra))
    d[cols]=d[cols].replace([np.inf,-np.inf],np.nan)
    return d,cols

def split_before(d,start,recent=None):
    start=pd.Timestamp(start);calstart=start-pd.Timedelta(days=120)
    # Fixed max horizon22d embargo for every model makes comparisons use identical mature labels.
    avail=d[d.eligible&d.potential21.notna()&d.y14.notna()&(d.date+pd.Timedelta(days=22)<start)]
    train=avail[avail.date+pd.Timedelta(days=22)<calstart]
    if recent is not None:train=train[train.date>=calstart-pd.Timedelta(days=recent)]
    cal=avail[avail.date>=calstart]
    return train,cal

def train_models(d,cols,start):
    models={};audit=[]
    for key,(target,recent) in SPECS.items():
        train,cal=split_before(d,start,recent)
        if len(train)<1000 or len(cal)<500 or train[target].nunique()<2 or cal[target].nunique()<2:raise RuntimeError('Insufficient classes/history: '+key+' '+str(start))
        model=HistGradientBoostingClassifier(max_leaf_nodes=15,max_iter=100,learning_rate=.05,l2_regularization=30,min_samples_leaf=100,early_stopping=False,class_weight='balanced',random_state=42)
        model.fit(train[cols],train[target]);models[key]=model
        p=model.predict_proba(cal[cols])[:,1]
        rank=daily_rank(cal,pd.Series(p,index=cal.index))
        top=cal[rank<=30]
        ap=float(average_precision_score(cal[target],p))
        # Different targets have different base rates: compare normalized AP lift, not raw AP.
        base=float(cal[target].mean());lift=ap/base
        audit.append({'method':key,'target':target,'train_n':len(train),'cal_n':len(cal),'train_last_label':str((train.date.max()+pd.Timedelta(days=22)).date()),'cal_last_label':str((cal.date.max()+pd.Timedelta(days=22)).date()),'cal_ap':ap,'cal_base_rate':base,'cal_ap_lift':lift,'cal_top30':measure(top)})
    selected=max(audit,key=lambda x:x['cal_ap_lift'])['method']
    return models,{'start':str(pd.Timestamp(start).date()),'selected_by_cal_only':selected,'models':audit}

def window_summary(z,anchor,col,K):
    eligible=z[z[col].notna()].sort_values('date');hits=eligible[eligible[col]<=K]
    first=hits.iloc[0] if len(hits) else None
    best=eligible.loc[eligible[col].idxmin()] if len(eligible) else None
    at=eligible[eligible.date.eq(anchor)]
    price=at.close.iloc[0] if len(at) else np.nan
    return {'best_rank':rank_value(best[col]) if best is not None else None,'best_date':str(best.date.date()) if best is not None else None,'first_top_date':str(first.date.date()) if first is not None else None,'first_days_vs_anchor':int((first.date-anchor).days) if first is not None else None,'first_price_vs_anchor':float(first.close/price-1) if first is not None and pd.notna(price) else None,'first_net7':float(first.y7) if first is not None and pd.notna(first.y7) else None,'first_net14':float(first.y14) if first is not None and pd.notna(first.y14) else None,'days_evaluated':len(eligible),'days_top_k':len(hits)}

def main():
    OUT.mkdir(parents=True,exist_ok=True);CACHE.mkdir(exist_ok=True)
    cases=json.loads((ROOT/'research/bear_rebound_cases.json').read_text())
    universe=include_registered_items(json.loads((ROOT/'firepulse_universe.json').read_text()),cases);resolution=[]
    for event in cases['events']:
        for item in event.get('members',event.get('cases',[])):
            if item.get('id'):continue
            try:
                query=item['cn'].split('|')[1].split('(')[0].strip()
                payload=request('/v1/market/facade/wiki/skin_search',{'name':query,'page':1,'page_size':100,'pc':True})
                found=exact_search(payload,item)
                if found:item['id']=found;universe.append({'id':found,'name':item['name'],'cn':item['cn']})
                resolution.append({'name':item['name'],'resolved_id':found,'status':'exact_match' if found else 'no_unique_exact_wear_match'})
            except Exception as e:resolution.append({'name':item['name'],'status':'search_failed','error':str(e)})
    excluded=('Nova |','XM1014 |','MAG-7 |','Sawed-Off |','Negev |','M249 |','R8 Revolver |')
    universe=list({x['id']:x for x in universe if x.get('id') and not x['name'].startswith(excluded)}.values())
    today=pd.Timestamp.now(tz='Asia/Shanghai').tz_localize(None).normalize();frames=[];fail=[]
    with futures.ThreadPoolExecutor(max_workers=3) as ex:
        jobs={ex.submit(collect,x,today):x for x in universe}
        for i,f in enumerate(futures.as_completed(jobs),1):
            try:frames.append(f.result())
            except Exception as e:fail.append({'name':jobs[f]['name'],'error':str(e)})
            if i%100==0:print('FETCH',i,'loaded',len(frames),flush=True)
    if not frames:raise RuntimeError('No usable history')
    print('BUILD STAGE FEATURES',flush=True)
    d,cols=add_stages(enrich(feature_frame(pd.concat(frames,ignore_index=True))[0]));latest=d[d.eligible].date.max()
    windows=[('Q1','2026-01-01','2026-04-01'),('Q2','2026-04-01','2026-07-01'),('Q3','2026-07-01','2026-10-01'),('Q4_partial','2026-10-01',str((latest+pd.Timedelta(days=1)).date()))]
    chunks=[];folds=[]
    for label,lo,hi in windows:
        print('TRAIN',label,flush=True);models,audit=train_models(d,cols,lo);audit['window']=label;folds.append(audit)
        z=d[d.eligible&d.date.ge(lo)&d.date.lt(hi)].copy()
        for key,model in models.items():z[key+'_raw']=model.predict_proba(z[cols])[:,1];z[key+'_rank']=daily_rank(z,z[key+'_raw'])
        z['selected_rank']=z[audit['selected_by_cal_only']+'_rank'];z['selected_method']=audit['selected_by_cal_only'];chunks.append(z)
        print('FOLD_DONE',label,'selected',audit['selected_by_cal_only'],flush=True)
    pred=pd.concat(chunks,ignore_index=True);methods=list(SPECS)+['selected'];summaries=[]
    for label,lo,hi in windows:
        for context in ('all','bear','repair'):
            q=pred[pred.date.ge(lo)&pred.date.lt(hi)]
            if context=='bear':q=q[q.bear_context]
            if context=='repair':q=q[q.environment_ok]
            for method in methods:
                for K in (10,30):
                    z=q[q[method+'_rank']<=K];m=measure(z);truth=q[q.winner21.eq(1)]
                    m.update({'window':label,'context':context,'method':method,'top_k':K,'potential_hit':float(z.winner21.mean()) if len(z) else None,'potential_recall':float(truth[method+'_rank'].le(K).mean()) if len(truth) else None,'baseline_net14':float(q.y14.mean()) if q.y14.notna().any() else None})
                    summaries.append(m)
    case_daily=[];case_windows=[]
    for ei,event in enumerate(cases['events']):
        anchor=pd.Timestamp(event['dates'][0])
        for item in event.get('members',event.get('cases',[])):
            z=pred[pred.name.eq(item['name'])&pred.date.between(anchor-pd.Timedelta(days=7),anchor+pd.Timedelta(days=7))]
            for method in methods:
                col=method+'_rank'
                for K in (10,30):case_windows.append({'event':str(anchor.date()),'name':item['name'],'cn':item['cn'],'method':method,'top_k':K,**window_summary(z,anchor,col,K)})
                for offset in range(-7,8):
                    day=anchor+pd.Timedelta(days=offset);q=z[z.date.eq(day)];x=q.iloc[0] if len(q) else None
                    case_daily.append({'event':str(anchor.date()),'date':str(day.date()),'name':item['name'],'cn':item['cn'],'method':method,'rank':rank_value(x[col]) if x is not None else None,'pool':int(pred.date.eq(day).sum()),'net7':float(x.y7) if x is not None and pd.notna(x.y7) else None,'net14':float(x.y14) if x is not None and pd.notna(x.y14) else None,'status':'evaluated' if x is not None else 'missing_or_ineligible'})
    pd.DataFrame(case_daily).to_csv(OUT/'case_daily.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(case_windows).to_csv(OUT/'case_windows.csv',index=False,encoding='utf-8-sig')
    histcols=['date','name','close','y7','y14','mae14','potential21','winner7','winner21','bear_context','environment_ok','selected_method']+[m+'_rank' for m in methods]
    pred[histcols].to_csv(OUT/'historical_rankings.csv.gz',index=False,compression='gzip')
    print('FIT_CURRENT',flush=True);models,audit=train_models(d,cols,latest)
    current=d[d.eligible&d.date.eq(latest)].copy()
    for key,model in models.items():current[key+'_rank']=daily_rank(current,pd.Series(model.predict_proba(current[cols])[:,1],index=current.index))
    current['selected_rank']=current[audit['selected_by_cal_only']+'_rank'];current['status']='独立研究，未获买入资格'
    current.sort_values('selected_rank')[['date','name','cn','id','close','selected_rank','status']+[k+'_rank' for k in SPECS]+['early_drift','early_vol_change','middle_return','middle_volume','wash_return','wash_support','wash_contraction','recent_volume_step','relative_7','peer_momentum_7','environment_ok']].to_csv(OUT/'current_candidates.csv',index=False,encoding='utf-8-sig')
    joblib.dump({'models':models,'features':cols,'selection':audit},OUT/'models.joblib')
    result={'version':'stage-rebound-v3','asof':str(latest.date()),'items_requested':len(universe),'items_loaded':len(frames),'failures':fail,'exact_wear_resolution':resolution,'features':cols,'folds':folds,'current_fit':audit,'summaries':summaries,'fee_buy':0,'fee_sell':.01,'slippage':0,'production_modified':False,'qualified_systems':[],'manual_case_labels_used_in_training':False,'validation_status':'反复研究后的历史滚动诊断，需独立事件及前瞻验证','data_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in CACHE.glob('*.gz')}}
    (OUT/'validation.json').write_text(json.dumps(clean_json(result),ensure_ascii=False,indent=2,allow_nan=False))
    pct=lambda v:'—' if v is None else f'{v:.2%}'
    lines=['# 时序阶段反弹龙头研究 v3',f'截至{latest.date()}，加载{len(frames)}/{len(universe)}件，输入{len(cols)}项。现行评分未改。','成本：买入0、卖出1%、滑点0。次日收盘代理入场，真实日K不保证可成交。','新增蓄势（此前21至60日）、中段量价台阶（此前7至21日）、洗盘（此前2至7日）、当前放量的相对顺序；全平台量与悠悠价格分别使用。承接及会员建仓仍为代理。','比较未来7日涨幅前30目标，以及未来第7至21日收盘最大净涨幅至少15%且前30的潜力目标；后者是事后标签，绝非保证可在峰值卖出。实际收益仍列固定7/14日结果。','三个固定模型按季度训练，120日校准，22日标签隔离；近期模型只训练校准日前540日。跨目标按校准AP相对基准率的提升选择，不查看点名案例或预测季度结果选模。','人工案例只用于回放诊断，不输入身份、不加商品奖金。经过多轮已看历史结果，不能把2026年称为完全未见事件。','±7日最优名次仅是事后窗口诊断；首次入榜日期、与锚点价格差、入榜后固定收益同时保留，避免只展示涨后好看的日期。','每日商品日信号重叠，不是独立交易或组合收益。退出收益缺失按缺失保留。还没有通过完整买入验证的系统。','','| 时段 | 环境 | 模型 | 前K | 结果n | 14日净均值 | 胜率 | 潜力龙头召回 |','|---|---|---|---:|---:|---:|---:|']
    for s in summaries:lines.append(f'| {s["window"]} | {s["context"]} | {s["method"]} | {s["top_k"]} | {s["n"]} | {pct(s["mean14"])} | {pct(s["win14"])} | {pct(s["potential_recall"])} |')
    lines+=['','## 指定案例±7日覆盖','| 日期 | 模型 | 可评估/该事件案例数 | 前30覆盖 |','|---|---|---:|---:|']
    for event in cases['events']:
        date=event['dates'][0]
        for method in methods:
            z=[x for x in case_windows if x['event']==date and x['method']==method and x['top_k']==30]
            lines.append(f'| {date} | {method} | {sum(x["days_evaluated"]>0 for x in z)}/{len(z)} | {sum(x["first_top_date"] is not None for x in z)} |')
    lines+=['','逐日名次见case_daily.csv，首次入榜及最佳日期见case_windows.csv；当前研究候选不等于买入推荐。','精确磨损补采：'+json.dumps(resolution,ensure_ascii=False)]
    text='\n'.join(lines)+'\n';(OUT/'report.md').write_text(text)
    if os.environ.get('GITHUB_STEP_SUMMARY'):Path(os.environ['GITHUB_STEP_SUMMARY']).write_text(text)
    print('STAGE_RESEARCH_COMPLETE',len(current),flush=True)
if __name__=='__main__':main()
