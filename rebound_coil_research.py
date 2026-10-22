"""Explainable, event-aligned accumulation/washout/activation scores; research only."""
import concurrent.futures as futures
import json,os
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit
from leader_research import CACHE,collect
from bear_rebound_research import feature_frame
from rebound_rank_research import enrich,daily_rank
from rebound_stage_research import include_registered_items,clean_json,window_summary
from rebound_entry_validation import make_trades,summarize,outcomes
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output/rebound_coil'
FACTORS=['build','tier','wash','activation','support','relative']
CN=['前期参与代理','量价台阶','缩量洗盘代理','持续放量','支撑与空间','相对同类领先']
PROFILES={'sequence':np.array([20,15,20,20,15,10.]),'bear_start':np.array([10,5,10,30,15,30.]),'early_coil':np.array([30,15,25,5,15,10.])}
clip=lambda s:s.clip(0,1)

def coil_features(d):
    pieces=[]
    for _,g in d.groupby('name',sort=False):
        g=g.sort_values('date');c,v=g.close,g.volume;ret=c/c.shift()-1
        choices=[]
        for base,wash,lag in ((20,5,2),(30,7,3),(45,10,3)):
            end=wash+lag
            bv=v.shift(end).rolling(base,min_periods=base).mean()
            prior=v.shift(end+base).rolling(base,min_periods=base).mean().replace(0,np.nan)
            bc=c.shift(end).rolling(base,min_periods=base).median()
            # Volume participation with no mandatory narrow-box condition.
            build=clip((bv/prior-.7)/1.0)*(.5+.5*clip(1-(c.shift(end)/c.shift(end+base)-1).abs()/.6))
            half=max(5,base//2)
            level=c.shift(end).rolling(half).median()/c.shift(end+half).rolling(half).median()-1
            tier=clip((level+.02)/.12)*clip(1-(level-.12).clip(lower=0)/.3)
            wv=v.shift(lag).rolling(wash,min_periods=wash).mean()
            low=g.low.shift(lag).rolling(wash,min_periods=wash).min()
            peak=g.high.shift(end).rolling(base,min_periods=base).max()
            dd=1-low/peak
            depth=clip(dd/.04)*clip(1-(dd-.15).clip(lower=0)/.2)
            washfactor=depth*clip(1-wv/bv.replace(0,np.nan)/1.4)
            recent=v.rolling(lag,min_periods=lag).mean()
            repeats=v.gt(bv*1.05).rolling(lag,min_periods=lag).sum()/lag
            share=v.rolling(lag).max()/v.rolling(lag).sum().replace(0,np.nan)
            activation=clip((recent/wv.replace(0,np.nan)-.8)/1.2)*repeats*clip((1-share)/.5)
            support=clip(1-(c/low-1).clip(lower=0)/.35)*clip((c/bc-.8)/.2)
            relative=clip(.5+(g.r7-g.m7)/.2)
            values=pd.DataFrame({'build':build,'tier':tier,'wash':washfactor,'activation':activation,'support':support,'relative':relative},index=g.index)
            values['coverage']=values.notna().mean(axis=1)
            values['alignment']=f'{base}/{wash}/{lag}'
            # Choose among three causal alignments by a fixed evidence rubric, never future returns.
            values['alignment_value']=values[FACTORS].fillna(0).to_numpy()@PROFILES['sequence']
            choices.append(values)
        best=np.argmax(np.column_stack([z.alignment_value for z in choices]),axis=1)
        chosen=choices[0].copy()
        for i,z in enumerate(choices):chosen.loc[best==i,z.columns]=z.loc[best==i,z.columns]
        # Isolated volume burst, upper shadow/distribution and short-term extension penalties.
        recent_share=v.rolling(3).max()/v.rolling(3).sum().replace(0,np.nan)
        location=(c-g.low)/(g.high-g.low).replace(0,np.nan)
        chosen['penalty']=10*clip((recent_share-.6)/.35)+10*clip((g.r3-.20)/.3)+10*clip((.35-location)/.35)
        chosen['penalty']=chosen.penalty.fillna(0)
        pieces.append(chosen)
    z=pd.concat(pieces).sort_index();result=d.copy()
    for col in [*FACTORS,'coverage','alignment','penalty']:result[col]=z[col]
    # Generic family median needs sufficient same-day peers; no asset-name bonus.
    peer=result.r7.where(result.eligible).groupby([result.date,result.family]).transform('median')
    count=result.r7.where(result.eligible).groupby([result.date,result.family]).transform('count')
    result['relative']=((result['relative']+clip(.5+(result.r7-peer)/.2).where(count.ge(8)))/2)
    result['coverage']=result[FACTORS].notna().mean(axis=1)
    return result

def fit_weights(d,start):
    boundary=pd.Timestamp(start)
    z=d[d.eligible&d.winner7.notna()&(d.date+pd.Timedelta(days=8)<boundary)].copy()
    if len(z)<1000 or z.winner7.nunique()<2:raise ValueError('Insufficient mature labels')
    if len(z)>60000:z=z.sample(60000,random_state=42).sort_values(['date','name'])
    X=z[FACTORS].fillna(0).to_numpy(float);y=z.winner7.to_numpy(float)
    w=np.where(y>0,.5/y.mean(),.5/(1-y.mean()));prior=PROFILES['sequence']/100
    def loss(theta):
        logits=X@theta[:-1]+theta[-1]
        reg=.02*np.sum((theta[:-1]-prior*3)**2)
        value=np.mean(w*(np.logaddexp(0,logits)-y*logits))+reg
        resid=w*(expit(logits)-y)/len(y)
        grad=np.r_[X.T@resid+.04*(theta[:-1]-prior*3),resid.sum()]
        return value,grad
    opt=minimize(loss,np.r_[prior*3,-1.],jac=True,method='L-BFGS-B',bounds=[(0,10)]*6+[(-20,20)],options={'maxiter':200})
    if not opt.success:raise RuntimeError('Weight optimization failed: '+str(opt.message))
    coef=opt.x[:-1];weights=100*coef/coef.sum() if coef.sum()>1e-8 else PROFILES['sequence'].copy()
    return weights,{'start':str(boundary.date()),'train_n':len(z),'train_last_signal':str(z.date.max().date()),'train_last_label':str((z.date.max()+pd.Timedelta(days=8)).date()),'positive_rate':float(y.mean()),'weights':dict(zip(FACTORS,weights.tolist())),'fallback':bool(coef.sum()<=1e-8),'manual_case_targets':False}

def main():
    OUT.mkdir(parents=True,exist_ok=True);CACHE.mkdir(exist_ok=True)
    cases=json.loads((ROOT/'research/bear_rebound_cases.json').read_text());u=include_registered_items(json.loads((ROOT/'firepulse_universe.json').read_text()),cases)
    u=[x for x in u if x.get('id') and not x['name'].startswith(('Nova |','XM1014 |','MAG-7 |','Sawed-Off |','Negev |','M249 |','R8 Revolver |'))]
    today=pd.Timestamp.now(tz='Asia/Shanghai').tz_localize(None).normalize();frames=[];fail=[]
    with futures.ThreadPoolExecutor(max_workers=3) as ex:
        jobs={ex.submit(collect,x,today):x for x in u}
        for i,f in enumerate(futures.as_completed(jobs),1):
            try:frames.append(f.result())
            except Exception as exc:fail.append({'name':jobs[f]['name'],'error':str(exc)})
            if i%100==0:print('FETCH',i,len(frames),flush=True)
    if not frames:raise RuntimeError('No history')
    d=coil_features(enrich(feature_frame(pd.concat(frames,ignore_index=True))[0]));latest=d[d.eligible].date.max()
    for key,w in PROFILES.items():d[key]=np.clip(d[FACTORS].fillna(0).to_numpy()@w-d.penalty,0,100)
    d['learned']=np.nan;audits=[]
    for boundary,stop in [('2026-01-01','2026-04-01'),('2026-04-01','2026-07-01'),('2026-07-01','2026-10-01'),('2026-10-01',str((latest+pd.Timedelta(days=1)).date()))]:
        print('FIT',boundary,flush=True);w,audit=fit_weights(d,boundary);audits.append(audit)
        use=d.date.ge(boundary)&d.date.lt(stop);d.loc[use,'learned']=np.clip(d.loc[use,FACTORS].fillna(0).to_numpy()@w-d.loc[use,'penalty'],0,100)
    methods=[*PROFILES,'learned']
    for method in methods:d[method+'_rank']=daily_rank(d,d[method].where(d.eligible))
    d['known_event_window']=False
    for event in cases['events']:
        anchor=pd.Timestamp(event['dates'][0]);d['known_event_window']|=d.date.between(anchor-pd.Timedelta(days=30),anchor+pd.Timedelta(days=30))
    for H in (7,14):d['net'+str(H)]=outcomes(d,H)
    allrows=[];summaries=[]
    periods=[('2026_Q1','2026-01-01','2026-03-31'),('2026_Q2','2026-04-01','2026-06-30'),('2026_Q3','2026-07-01','2026-09-30'),('recent90',str((latest-pd.Timedelta(days=90)).date()),str(latest.date()))]
    for method in methods:
        d['rank']=d[method+'_rank'];d['score']=d[method];d['factor_coverage']=d.coverage
        for K in (3,5):
            for gate in ('all','market'):
                mask=d.eligible&d['rank'].le(K)&d.date.ge('2026-01-01')
                if gate=='market':mask&=d.m3.gt(d.m7*3/7)&d.breadth_change3.ge(0)
                for H in (7,14):
                    rows=make_trades(d,mask,H,latest);allrows.extend([{**x,'method':method,'top_k':K,'gate':gate,'hold':H} for x in rows])
                    for label,lo,hi in periods:
                        z=[x for x in rows if lo<=x['signal_date']<=hi]
                        for context,sub in [('all',z),('outside_named_events',[x for x in z if not x['known_event_window']])]:summaries.append({'method':method,'top_k':K,'gate':gate,'hold':H,'period':label,'context':context,**summarize(sub)})
    pd.DataFrame(allrows).to_csv(OUT/'trades.csv.gz',index=False,compression='gzip')
    case_windows=[];case_daily=[]
    for event in cases['events']:
        anchor=pd.Timestamp(event['dates'][0])
        for item in event.get('members',event.get('cases',[])):
            z=d[d.name.eq(item['name'])&d.date.between(anchor-pd.Timedelta(days=7),anchor+pd.Timedelta(days=7))]
            for method in methods:
                for K in (3,5,30):case_windows.append({'event':str(anchor.date()),'name':item['name'],'cn':item['cn'],'method':method,'top_k':K,**window_summary(z,anchor,method+'_rank',K)})
            cols=['date','name','close','coverage','alignment','penalty',*FACTORS,*methods,*[m+'_rank' for m in methods],'y7','y14']
            case_daily.append(z[cols].assign(event=str(anchor.date())))
    pd.DataFrame(case_windows).to_csv(OUT/'case_windows.csv',index=False,encoding='utf-8-sig');pd.concat(case_daily).to_csv(OUT/'case_daily.csv',index=False,encoding='utf-8-sig')
    current=d[d.eligible&d.date.eq(latest)].copy();w,current_fit=fit_weights(d,latest);current['learned_reference']=np.clip(current[FACTORS].fillna(0).to_numpy()@w-current.penalty,0,100)
    current['learned_reference_rank']=daily_rank(current,current.learned_reference)
    def reasons(x):
        values=[(CN[i],float(x[f])*PROFILES['sequence'][i]) for i,f in enumerate(FACTORS) if pd.notna(x[f])]
        return '；'.join(f'{key}{value:.1f}分' for key,value in sorted(values,key=lambda a:-a[1])[:3])
    current['reasons']=current.apply(reasons,axis=1)
    current['shape_state']=np.select([current.activation.ge(.6)&current.wash.ge(.3)&current.build.ge(.3),current.build.ge(.5)&current.wash.ge(.25)&current.activation.lt(.6)],['蓄势后量能激活代理','蓄势观察代理'],default='局部形态，链条未完整')
    current['status']='蓄势证据研究分；未验证为买入资格或概率'
    for i,f in enumerate(FACTORS):current[f+'_points']=current[f].fillna(0)*PROFILES['sequence'][i]
    cols=['date','name','cn','id','close','sequence','sequence_rank','bear_start','bear_start_rank','early_coil','early_coil_rank','learned_reference','learned_reference_rank','coverage','alignment','penalty',*FACTORS,*[f+'_points' for f in FACTORS],'environment_ok','shape_state','reasons','status']
    current.sort_values('sequence_rank')[cols].to_csv(OUT/'current_candidates.csv',index=False,encoding='utf-8-sig')
    result={'version':'aligned-coil-v1','asof':str(latest.date()),'loaded':len(frames),'requested':len(u),'failures':fail,'profiles':{key:dict(zip(FACTORS,w.tolist())) for key,w in PROFILES.items()},'folds':audits,'current_fit':current_fit,'summaries':summaries,'qualified_systems':[],'production_modified':False,'fee_buy':0,'fee_sell':.01,'slippage':0,'limitations':['三个固定量价对齐窗口只按当时证据选取，不按未来涨幅对齐；固定窗口仍是近似过程，不证明真实建仓','分项是可解释证据强度，不等于收益概率；会员档位、真实交易身份与成本不可从日K认定','学习权重只用季度开始前已成熟8日标签，非负约束与固定正则；人工指定名单只回放，不加分','当前参考模型与季度模型分开列示，不把今天拟合模型反推历史','已经反复看过这些历史事件，季度训练不等于全新独立样本；门控及阈值仍属开发假设','只把Top3/5作为入场比较，Top30仅案例覆盖诊断；窗口最佳名次不是已知可交易入场时点','每商品固定去重后检查未来数据；持有窗口缺报价或非正成交量不记零收益','价格悠悠、成交量全平台；真实求购历史不足不倒填；逐笔平均收益不是组合收益','所有交易次日收盘代理入场，卖出1%、无滑点；当前分项高也不自动开仓']}
    (OUT/'validation.json').write_text(json.dumps(clean_json(result),ensure_ascii=False,indent=2,allow_nan=False))
    p=lambda x:'—' if x is None else f'{x:.2%}'
    lines=['# 对齐蓄势、洗盘、持续放量：独立证据评分',f'历史截至{latest.date()}，加载{len(frames)}/{len(u)}。','完整链条分项：前期参与20、台阶15、洗盘20、持续放量20、支撑空间15、相对领先10；风险最多扣30。另比较熊市启动、提前蓄势固定权重和季度因果学习非负权重。','分数未获买入资格，不能解释为越高越赚钱。32个入场方案：4评分×Top3/5×不限/大盘许可×7/14天。','','| 时段 | 范围 | 评分 | 前K | 门控 | 持有 | 结果/信号 | 净均值 | 中位 | 胜率 |','|---|---|---|---:|---|---:|---:|---:|---:|---:|']
    for s in summaries:lines.append(f'| {s["period"]} | {s["context"]} | {s["method"]} | {s["top_k"]} | {s["gate"]} | {s["hold"]} | {s["n"]}/{s["signals"]} | {p(s["mean"])} | {p(s["median"])} | {p(s["win"])} |')
    lines+=['','## 当前形态证据前五（固定完整链条分，不是买入推荐）','| 商品 | 分数 | 风险扣分 | 证据覆盖 | 主要分项 |','|---|---:|---:|---:|---|']
    for _,x in current.sort_values('sequence_rank').head(5).iterrows():lines.append(f'| {x.cn} | {x.sequence:.1f} | {x.penalty:.1f} | {x.coverage:.0%} | {x.reasons} |')
    lines+=['','## 提前蓄势观察前五（不等于允许买入）','| 商品 | 提前蓄势分 | 形态 | 风险扣分 |','|---|---:|---|---:|']
    for _,x in current.sort_values('early_coil_rank').head(5).iterrows():lines.append(f'| {x.cn} | {x.early_coil:.1f} | {x.shape_state} | {x.penalty:.1f} |')
    lines+=['','## 指定事件覆盖','| 事件 | 评分 | 前K | 有覆盖/名单数 |','|---|---|---:|---:|']
    for event in cases['events']:
        for method in methods:
            for K in (3,5,30):
                z=[x for x in case_windows if x['event']==event['dates'][0] and x['method']==method and x['top_k']==K]
                lines.append(f'| {event["dates"][0]} | {method} | {K} | {sum(x["first_top_date"] is not None for x in z)}/{len(z)} |')
    lines+=['','## 边界',*['- '+x for x in result['limitations']]];report='\n'.join(lines)+'\n';(OUT/'report.md').write_text(report)
    if os.environ.get('GITHUB_STEP_SUMMARY'):Path(os.environ['GITHUB_STEP_SUMMARY']).write_text(report)
    print('COIL_RESEARCH_COMPLETE',len(allrows),flush=True)
if __name__=='__main__':main()
