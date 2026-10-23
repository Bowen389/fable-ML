"""Daily process evidence score and independently evaluated supervised ranking."""
import concurrent.futures as futures
import gzip
import hashlib
import json
import os
from pathlib import Path
import time
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import average_precision_score, brier_score_loss
import joblib
from leader_research import ROOT,CACHE,parse,request,features,net
from regime_research import market_states

FUTURE_FEATURES=['net7','net14','net30','t1','t0','t1_rank','t0_rank','next7']


def refresh_item(item,today):
    path=CACHE/(item['id']+'.json.gz')
    payload=None
    if path.exists():
        with gzip.open(path,'rt') as f:payload=json.load(f)
    old=parse(payload or {},today)
    refresh=os.environ.get('REFRESH_PUBLIC_DATA')=='1'
    if refresh and (old.empty or old.date.max()<today-pd.Timedelta(days=1)):
        span=1440 if old.empty or (today-old.date.max()).days>50 else 60
        recent=request('/v1/market/facade/quote/skin_k_chart',{'id':item['id'],'type':2,'timestamp':int(time.time()),'date_range':span,'platform':'youpin'})
        rows={str(r[0]):r for r in (payload or {}).get('data',[]) if isinstance(r,list) and r}
        rows.update({str(r[0]):r for r in recent.get('data',[]) if isinstance(r,list) and r})
        payload={'code':200,'data':sorted(rows.values(),key=lambda r:float(r[0]))}
        with gzip.open(path,'wt') as f:json.dump(payload,f,separators=(',',':'))
    if payload is None:raise ValueError('No preserved cache; enable REFRESH_PUBLIC_DATA to fetch')
    g=parse(payload,today)
    if len(g)<300:raise ValueError('Less than 300 valid history rows')
    for key in ['name','cn','id']:g[key]=item[key]
    g['family']=item['name'].split('|')[0].strip()
    return g


def process_features(d):
    pieces=[]
    for name,g in d.groupby('name',sort=False):
        g=g.copy();obs=g[g.close.notna()].copy();c=obs.close;v=obs.volume
        vals={
            'early_range40':obs.high.shift(21).rolling(40).max()/obs.low.shift(21).rolling(40).min()-1,
            'early_drift40':c.shift(21)/c.shift(60)-1,
            'second_wave_return':c.shift(7)/c.shift(21)-1,
            'second_wave_volume':v.shift(7).rolling(14).mean()/v.shift(21).rolling(30).mean().replace(0,np.nan),
            'wash_drawdown':obs.low.shift().rolling(10).min()/obs.high.shift(11).rolling(20).max()-1,
            'wash_volume_ratio':v.shift().rolling(5).mean()/v.shift(6).rolling(20).mean().replace(0,np.nan),
            'volume_cv7':v.rolling(7).std()/v.rolling(7).mean().replace(0,np.nan),
            'volume_max_share7':v.rolling(7).max()/v.rolling(7).sum().replace(0,np.nan),
            'volume_rising_days7':v.diff().gt(0).rolling(7).mean(),
            'volume_acceleration':v.rolling(3).mean()/v.rolling(7).mean().replace(0,np.nan),
            'early_cost_gap':c/c.shift(21).rolling(40).median()-1,
            'price_efficiency7':obs.r7/obs.rv.clip(lower=.1),
            'support_recovery':(c-obs.low.shift().rolling(10).min())/(obs.high.shift().rolling(20).max()-obs.low.shift().rolling(10).min()).replace(0,np.nan),
            'prior_low7':obs.low.shift().rolling(7).min()}
        for key,val in vals.items():g[key]=val.reindex(g.index)
        # Future target: +20% net reached before -10%, with exits considered only from day 7 onward.
        # Full 31-day observed-price window required; no label interpolation and uniform label maturity.
        entry=g.close.shift(-1)
        complete=g.close.shift(-1).iloc[::-1].rolling(31,min_periods=31).count().iloc[::-1].eq(31)&g.volume.shift(-1).gt(0)&g.volume.shift(-31).gt(0)
        outcome=net(g.close.shift(-31)/entry-1).to_numpy()
        hit=np.zeros(len(g),dtype=float);decided=np.zeros(len(g),dtype=bool)
        for k in range(7,31):
            ret=net(g.close.shift(-(k+1))/entry-1).to_numpy()
            can_exit=g.volume.shift(-(k+1)).gt(0).to_numpy()
            up=(ret>=.2)&can_exit&~decided
            down=(ret<=-.1)&can_exit&~decided
            outcome[up|down]=ret[up|down];hit[up]=1;decided|=up|down
        g['big_rise_label']=pd.Series(hit,index=g.index).where(complete)
        g['barrier_net']=pd.Series(outcome,index=g.index).where(complete)
        g['label_maturity']=g.date+pd.Timedelta(days=31)
        pieces.append(g)
    return pd.concat(pieces).sort_index()


def evidence_score(d):
    clip=lambda x:x.clip(0,1)
    s=pd.DataFrame(index=d.index)
    s['前期建仓代理']=20*clip(1-d.early_range40/.5)*clip(1-d.early_drift40.abs()/.3)
    s['第二轮量价台阶']=15*clip(d.second_wave_return/.08)*clip((.3-d.second_wave_return)/.15)*clip(d.second_wave_volume/.8)*clip((3-d.second_wave_volume)/1.5)
    s['洗盘承接代理']=20*clip((-d.wash_drawdown-.02)/.05)*clip((d.wash_drawdown+.25)/.1)*clip((1.1-d.wash_volume_ratio)/.4)*clip(d.support_recovery)
    s['均匀放量']=20*clip((d.rv-.6)/.6)*clip((3.5-d.rv)/1.5)*clip((.9-d.volume_cv7)/.5)*clip((.5-d.volume_max_share7)/.25)
    s['价格空间']=15*clip((.3-d.early_cost_gap)/.25)*clip((d.early_cost_gap+.15)/.15)
    s['相对强度']=10*clip(d.rs_rank)
    s['风险扣分']=np.where((d.rv>4)|(d.volume_max_share7>.5),10,0)+np.where(d.r7>.3,10,0)+np.where(d.close<d.prior_low7,10,0)
    s['证据覆盖率']=s.iloc[:,:6].notna().mean(axis=1)
    s['证据分']=(s.iloc[:,:6].fillna(0).sum(axis=1)-s['风险扣分']).clip(0,100)
    return s


def daily_top(frame,score,column='big_rise_label'):
    z=frame.copy();z['_score']=score
    rank=z.groupby('date')['_score'].rank(pct=True,method='average')
    return z[rank>=.9]


def measures(g):
    return {'n':len(g),'days':g.date.nunique(),'items':g.name.nunique(),
            'hit_rate':float(g.big_rise_label.mean()) if len(g) else None,
            'barrier_mean_net':float(g.barrier_net.mean()) if len(g) else None,
            'fixed30_mean_net':float(g.net30.mean()) if len(g) else None}


def bootstrap_daily_difference(all_rows,top):
    a=all_rows.groupby('date').big_rise_label.mean()
    t=top.groupby('date').big_rise_label.mean()
    diff=(t-a).dropna().to_numpy()
    if len(diff)<20:return [None,None]
    # Consecutive 7-day blocks reduce the fiction that nearby signals are independent.
    blocks=[diff[i:i+7] for i in range(0,len(diff),7)]
    rng=np.random.default_rng(42);vals=[]
    for _ in range(500):
        chosen=rng.integers(0,len(blocks),len(blocks));vals.append(np.concatenate([blocks[i] for i in chosen]).mean())
    return [float(x) for x in np.quantile(vals,[.025,.975])]


def train_and_evaluate(d,cols,latest):
    first=latest-pd.Timedelta(days=270);second=latest-pd.Timedelta(days=90)
    usable=d[d.eligible&d.volume_ok&d.big_rise_label.notna()].copy()
    # Fixed per-item weekday offsets, independent of outcomes, reduce overlapping training rows.
    offset=usable.name.map(lambda s:int(hashlib.sha256(s.encode()).hexdigest()[:8],16)%7)
    stagger=(usable.date.astype('int64')//86400000000000)%7==offset
    train=usable[(usable.label_maturity<=first)&stagger]
    cal=usable[(usable.date>first)&(usable.label_maturity<=second)]
    test=usable[(usable.date>second)&(usable.label_maturity<=latest)].copy()
    if min(len(train),len(cal),len(test))<200 or train.big_rise_label.nunique()<2 or cal.big_rise_label.nunique()<2:
        return None,None,{'status':'模型样本不足','train_n':len(train),'cal_n':len(cal),'test_n':len(test)},test
    X=lambda f:f[cols].replace([np.inf,-np.inf],np.nan).to_numpy(dtype=np.float32)
    weights=1/train.groupby('date').date.transform('size').to_numpy();weights*=len(weights)/weights.sum()
    trials=[];models=[]
    for leaves in (7,15,31):
        model=HistGradientBoostingClassifier(max_leaf_nodes=leaves,max_iter=120,learning_rate=.05,l2_regularization=5,
                                            min_samples_leaf=80,early_stopping=False,random_state=42)
        model.fit(X(train),train.big_rise_label.astype(int),sample_weight=weights)
        pred=model.predict_proba(X(cal))[:,1]
        ap=float(average_precision_score(cal.big_rise_label,pred))
        trials.append({'leaves':leaves,'cal_average_precision':ap,'cal_top':measures(daily_top(cal,pred))})
        models.append(model)
        print('MODEL',leaves,'cal AP',round(ap,5),flush=True)
    best=int(np.argmax([x['cal_average_precision'] for x in trials]));model=models[best]
    iso=IsotonicRegression(out_of_bounds='clip').fit(model.predict_proba(X(cal))[:,1],cal.big_rise_label)
    raw=model.predict_proba(X(test))[:,1];prob=iso.predict(raw)
    top=daily_top(test,raw);base=measures(test);high=measures(top)
    ci=bootstrap_daily_difference(test,top)
    lift=high['hit_rate']/base['hit_rate'] if base['hit_rate'] and high['hit_rate'] is not None else None
    predictive=bool(ci[0] is not None and ci[0]>0 and lift is not None and lift>=1.5 and len(top)>=200 and high['days']>=30)
    buy_validated=bool(predictive and high['barrier_mean_net']>0 and high['fixed30_mean_net']>0)
    metrics={'status':'通过前瞻观察资格' if buy_validated else '未验证为买入系统','predictive_rank_validated':predictive,
             'buy_validated':buy_validated,'train_n':len(train),'cal_n':len(cal),'test_n':len(test),
             'train_maturity_cutoff':str(first.date()),'cal_maturity_cutoff':str(second.date()),
             'trials':trials,'selected_leaves':trials[best]['leaves'],'test_base':base,'test_top_decile':high,
             'test_lift':lift,'daily_block_lift_difference_ci95':ci,
             'test_brier':float(brier_score_loss(test.big_rise_label,prob))}
    test['model_raw']=raw;test['model_calibrated']=prob
    regressors=[];reg_trials=[]
    for leaves in (7,15,31):
        reg=HistGradientBoostingRegressor(max_leaf_nodes=leaves,max_iter=120,learning_rate=.05,l2_regularization=5,
                                         min_samples_leaf=80,early_stopping=False,random_state=42)
        reg.fit(X(train),train.barrier_net,sample_weight=weights)
        score=reg.predict(X(cal));m=measures(daily_top(cal,score))
        reg_trials.append({'leaves':leaves,'cal_top':m});regressors.append(reg)
        print('RETURN_MODEL',leaves,'cal mean',m['barrier_mean_net'],flush=True)
    chosen=int(np.argmax([x['cal_top']['barrier_mean_net'] if x['cal_top']['barrier_mean_net'] is not None else -1e9 for x in reg_trials]))
    reg=regressors[chosen];return_pred=reg.predict(X(test));test['return_model_raw']=return_pred
    rt=measures(daily_top(test,return_pred))
    metrics['return_model']={'selected_leaves':reg_trials[chosen]['leaves'],'trials':reg_trials,'test_top_decile':rt,
        'buy_validated':bool(rt['n']>=200 and rt['days']>=30 and rt['barrier_mean_net'] is not None and rt['barrier_mean_net']>0 and rt['fixed30_mean_net']>0)}
    # Fixed trained models; these three date blocks are stability diagnostics, not rolling refits.
    windows=[]
    for dates in np.array_split(np.sort(test.date.unique()),3):
        z=test[test.date.isin(dates)]
        windows.append({'start':str(pd.Timestamp(dates[0]).date()),'end':str(pd.Timestamp(dates[-1]).date()),
            'base':measures(z),'rise_top':measures(daily_top(z,z.model_raw)),
            'return_top':measures(daily_top(z,z.return_model_raw))})
    metrics['frozen_model_three_windows']=windows
    joblib.dump({'model':reg,'feature_columns':cols,'metrics':metrics['return_model']},ROOT/'output'/'process_return_model.joblib')
    return model,iso,metrics,test


def daily_model_result(out,d,cols,latest):
    if os.environ.get('DAILY_INFERENCE_ONLY')!='1':
        return train_and_evaluate(d,cols,latest)
    path=Path(out)/'process_score_validation.json'
    frozen=json.loads(path.read_text()) if path.exists() else {}
    old=frozen.get('validation_asof') or frozen.get('asof')
    metrics=dict(frozen.get('metrics',{}))
    metrics.update(buy_validated=False,status='固定公式日常证据分；历史验证冻结于'+str(old),training_runs=0,validation_asof=old)
    return None,None,metrics,pd.DataFrame()

def main():
    CACHE.mkdir(exist_ok=True);out=ROOT/'output';out.mkdir(exist_ok=True)
    today=pd.Timestamp.now(tz='Asia/Shanghai').tz_localize(None).normalize()
    universe=json.loads((ROOT/'firepulse_universe.json').read_text())
    excluded=('Nova |','XM1014 |','MAG-7 |','Sawed-Off |','Negev |','M249 |','R8 Revolver |')
    universe=[x for x in universe if not x['name'].startswith(excluded)]
    frames=[];failures=[]
    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        fs={executor.submit(refresh_item,item,today):item for item in universe}
        for n,f in enumerate(futures.as_completed(fs),1):
            try:frames.append(f.result())
            except Exception as exc:failures.append({'name':fs[f]['name'],'error':type(exc).__name__+': '+str(exc)})
            if n%50==0 or n==len(fs):print('DATA',n,'/',len(fs),'success',len(frames),flush=True)
    if not frames:raise RuntimeError('No data for process-score research')
    raw=pd.concat(frames,ignore_index=True)
    print('BUILD PROCESS FEATURES',len(raw),'bars',flush=True)
    d=process_features(features(raw))
    latest=d[d.eligible].groupby('name').date.max().value_counts().idxmax();d=d[d.date<=latest].copy()
    market=market_states(d);d['market_state']=d.date.map(market.state)
    scores=evidence_score(d)
    for c in scores:d[c]=scores[c]
    cols=['r1','r3','r7','r14','r20','rv','base_gap','rs7','rs_rank','family_rank','breadth','mkt7','up_close',
          'early_range40','early_drift40','second_wave_return','second_wave_volume','wash_drawdown','wash_volume_ratio',
          'volume_cv7','volume_max_share7','volume_rising_days7','volume_acceleration','early_cost_gap','price_efficiency7','support_recovery']
    assert not set(cols)&set(FUTURE_FEATURES+['big_rise_label','barrier_net','label_maturity'])
    model,iso,metrics,test=daily_model_result(out,d,cols,latest)
    current=d[(d.date==latest)&d.eligible&d.volume_ok].copy()
    current['模型排序分位']=np.nan
    current['收益模型排序分位']=np.nan
    if model is not None:
        p=model.predict_proba(current[cols].replace([np.inf,-np.inf],np.nan).to_numpy(dtype=np.float32))[:,1]
        current['模型排序分位']=pd.Series(p,index=current.index).rank(pct=True)*100
        joblib.dump({'model':model,'calibrator':iso,'feature_columns':cols,'metrics':metrics},out/'process_rank_model.joblib')
        return_model=joblib.load(out/'process_return_model.joblib')['model']
        rp=return_model.predict(current[cols].replace([np.inf,-np.inf],np.nan).to_numpy(dtype=np.float32))
        current['收益模型排序分位']=pd.Series(rp,index=current.index).rank(pct=True)*100
    current['评分类型']='模型排序分'  if metrics.get('buy_validated') else '待验证证据分'
    current['每日参考分']=current['模型排序分位'] if metrics.get('buy_validated') else current['证据分']
    current['系统状态']=metrics['status']
    current['价格日期']=str(latest.date())
    current['生成时间']=pd.Timestamp.now(tz='Asia/Shanghai').isoformat()
    current['算法版本']='leader-process-score-v1'
    components=['前期建仓代理','第二轮量价台阶','洗盘承接代理','均匀放量','价格空间','相对强度']
    current['主要理由']=current.apply(lambda r:'；'.join(f'{k} {r[k]:.1f}' for k in sorted(components,key=lambda k:0 if pd.isna(r[k]) else r[k],reverse=True)[:3]),axis=1)
    current['风险提示']=current.apply(lambda r:'；'.join(x for x in [
        '市场：'+str(r.market_state),'距早期价格代理 '+f'{r.early_cost_gap:+.1%}',
        '量峰值集中' if r.volume_max_share7>.5 else '',
        '近期涨幅偏大' if r.r7>.3 else '',
        '分数未验证为收益排序' if not metrics.get('buy_validated') else '仅前瞻观察，非收益保证'] if x),axis=1)
    current=current.sort_values(['每日参考分','证据覆盖率','name'],ascending=[False,False,True])
    output_cols=['name','cn','id','价格日期','生成时间','算法版本','close','每日参考分','评分类型','系统状态','模型排序分位','收益模型排序分位','证据分','证据覆盖率',*components,'风险扣分','rv','volume_cv7','volume_max_share7','early_cost_gap','market_state','主要理由','风险提示']
    current[output_cols].to_csv(out/'daily_process_scores.csv',index=False,encoding='utf-8-sig')
    bands=[]
    if len(test):
        test=test.copy();test['证据分']=d.loc[test.index,'证据分']
        test['band']=pd.cut(test['证据分'],[-.01,20,40,60,80,100],labels=['0–20','20–40','40–60','60–80','80–100'])
        for band,g in test.groupby('band',observed=False):bands.append({'band':str(band),**measures(g)})
        test[['name','date','big_rise_label','barrier_net','net30','证据分']+[c for c in ['model_raw','model_calibrated','return_model_raw'] if c in test]].to_csv(out/'process_score_holdout.csv.gz',index=False,compression='gzip')
    manifest={'version':'leader-process-score-v1','asof':str(latest.date()),'generated_at':pd.Timestamp.now(tz='Asia/Shanghai').isoformat(),
              'training_runs':0 if os.environ.get('DAILY_INFERENCE_ONLY')=='1' else 1,'validation_asof':metrics.get('validation_asof',str(latest.date())),'daily_mode':os.environ.get('DAILY_INFERENCE_ONLY')=='1',
              'source':'Firepulse public interface','price_basis':'youpin daily OHLC','volume_basis':'all-platform proxy',
              'items_requested':len(universe),'items_loaded':len(frames),'failures':failures,'feature_columns':cols,
              'metrics':metrics,'evidence_score_bands':bands,'daily_rows':len(current),'historical_rows':len(raw),'earliest_price_date':str(raw.date.min().date()),
              'expected_completed_date':str((today-pd.Timedelta(days=1)).date()),'data_stale':bool(latest<today-pd.Timedelta(days=1)),
              'target':'次日收盘代理入场；第7至30自然日净收盘收益先达到+20%再达到-10%；完整31日真实报价窗口',
              'limitations':['六项证据权重为先验设计，尚未因果识别真实建仓或会员档位；阶段窗口部分重叠，并非已验证的严格建仓时序',
              '全池样本按商品日计数，信号与持仓可能重叠，不是独立交易数或组合收益',
              '最近90日仅59个信号日具备完整31日结果，其余日期只能前瞻观察；三个子窗口为冻结模型诊断，非滚动重训',
              '模型只在校准段选参数，随后一次留出验证；重跑任务会重复查看历史留出段，仍需前瞻观察',
              '七日分块自助法处理部分时间相关性，仍不构成独立市场事件或账户回测',
              '固定白名单及历史修订可能带来存活偏差，不掌握真实会员身份或建仓成本',
              '手续费2.5%、双边各0.5%滑点；最早第7日退出是研究假设，未模拟平台全部限制或真实成交',
              '当前证据分并未呈现大涨率随分数单调上升，不能解释为买入优先级；高模型分也可能高风险',
              '分数不等于大涨概率；模型未通过买入资格时只输出待验证证据分，不宣称越高越赚钱',
              'Whale仅辅助；本轮缺乏求购和在售的完整历史，不倒填、不伪造这些证据',
              '日K收盘是历史价格代理，当前买入还需核对实时在售价与求购承接']}
    (out/'process_score_validation.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2,default=int))
    pct=lambda v:'—' if v is None else f'{v:.2%}'
    lines=['# 龙头过程评分 · 每日参考与验证报告','',f'截至{latest.date()}；数据{len(frames)}/{len(universe)}件；每日评分{len(current)}件。',
           '**系统状态：'+metrics['status']+'**','',
           '## 过程证据分（0–100）','',
           '| 项目 | 最高分 |','|---|---:|','| 前期建仓代理 | 20 |','| 第二轮量价台阶 | 15 |','| 洗盘承接代理 | 20 |','| 均匀放量 | 20 |','| 价格空间 | 15 |','| 相对强度 | 10 |',
           '','风险扣分最多30分；缺失证据不给分。所有分项由当日及以前数据计算。',
           '## 独立时段模型验证（每日模式沿用历史结果）','',f'- 本轮训练次数：{manifest["training_runs"]}；历史验证截至：{manifest["validation_asof"]}；本轮不重新认证买入资格。',f'- 标签：{manifest["target"]}',f'- 参数选择：{metrics.get("selected_leaves","样本不足")}叶节点；只按校准段平均精确率选择。',
           f'- 训练/校准/留出样本：{metrics.get("train_n")}/{metrics.get("cal_n")}/{metrics.get("test_n")}',
           f'- 留出全池大涨标签率：{pct(metrics.get("test_base",{}).get("hit_rate"))}',
           f'- 留出每日模型前10%大涨标签率：{pct(metrics.get("test_top_decile",{}).get("hit_rate"))}',
           f'- 前10%止盈/止损代理平均净收益：{pct(metrics.get("test_top_decile",{}).get("barrier_mean_net"))}',
           f'- 前10%固定30日平均净收益：{pct(metrics.get("test_top_decile",{}).get("fixed30_mean_net"))}',
           f'- 排序资格通过：{metrics.get("predictive_rank_validated",False)}；买入系统资格通过：{metrics.get("buy_validated",False)}。',
           f'- 收益模型前10%止盈/止损代理净均值：{pct(metrics.get("return_model",{}).get("test_top_decile",{}).get("barrier_mean_net"))}；买入资格：{metrics.get("return_model",{}).get("buy_validated",False)}。',
           '','## 证据分在留出段的实际表现','',
           '| 分数段 | 样本 | 大涨标签率 | 止盈/止损代理净均值 | 固定30日净均值 |','|---|---:|---:|---:|---:|']
    for b in bands:lines.append(f'| {b["band"]} | {b["n"]} | {pct(b["hit_rate"])} | {pct(b["barrier_mean_net"])} | {pct(b["fixed30_mean_net"])} |')
    lines+=['','## 当日形态证据前20（证据分未通过收益排序验证）','',
            '| 商品 | 参考分 | 证据覆盖 | 日K价 | 主要理由 |','|---|---:|---:|---:|---|']
    for _,r in current.head(20).iterrows():lines.append(f'| {r.cn.replace("|","/")} | {r["每日参考分"]:.1f} | {r["证据覆盖率"]:.0%} | {r.close:.2f} | {r["主要理由"]} |')
    lines+=['','## 适用边界',*['- '+x for x in manifest['limitations']],
            '','完整分项、扣分、风险和价格日期见daily_process_scores.csv。']
    md='\n'.join(lines)
    (out/'process_score_report.md').write_text(md,encoding='utf-8')
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'],'a',encoding='utf-8') as f:f.write(md)
    print('PROCESS_SCORE_COMPLETE',json.dumps({'daily_rows':len(current),'historical_rows':len(raw),'earliest_price_date':str(raw.date.min().date()),
              'expected_completed_date':str((today-pd.Timedelta(days=1)).date()),'data_stale':bool(latest<today-pd.Timedelta(days=1)),'metrics':metrics},ensure_ascii=False,default=int),flush=True)


if __name__=='__main__':main()
