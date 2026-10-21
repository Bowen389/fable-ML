"""Regime-conditioned interpretable factors and purged entry-method comparisons.
No live orders. Existing original rules remain unchanged and retain their status.
"""
import concurrent.futures as futures
import json
import os
from pathlib import Path
import numpy as np
import pandas as pd
from process_score import refresh_item,process_features,evidence_score
from leader_research import ROOT,CACHE,features,net
from cs2.features import _days_since_ext
from cs2.rules import load_rules
from pool_audit import write_pool_audit

VERSION='regime-multifactor-v1'
FACTORS=['量能','承接代理','趋势','波动风险','相对强度','过程结构']
PROFILES={
 '环境适配':{'熊市':[.15,.30,.10,.25,.10,.10],'修复':[.20,.25,.15,.20,.10,.10],'强势':[.25,.20,.20,.10,.15,.10]},
 '等权':{k:[1/6]*6 for k in ['熊市','修复','强势']},
 '防守优先':{k:[.15,.30,.10,.30,.10,.05] for k in ['熊市','修复','强势']}}
GATES=['不加环境对照','市场修复','市场或板块修复']
ENTRIES={'O_S1':'原版深跌筑底波动收敛','O_M3':'原版远离MA90止跌','O_M4':'原版低价枪械筑底','O_L1':'原版深跌MA交叉',
         'I0':'buy-cs原买点并集','I1':'偏左支撑试探','I2':'温和放量初启动','I3':'强势缩量回踩','I4':'过程结构再启动'}

def clip(x):return x.clip(0,1)


def original_and_factor_features(d,universe):
    catmap={x['name']:x['cat'] for x in universe}
    parts=[]
    for name,g in d.groupby('name',sort=False):
        g=g.copy();c=g.close;h=g.high;l=g.low;v=g.volume
        obs=c.notna();ci=c.ffill();hi=h.ffill();li=l.ffill()
        ret=np.log(ci).diff();ma=lambda n:ci.rolling(n,min_periods=max(2,n//2)).mean()
        g['ma7']=ma(7);g['ma30']=ma(30);g['ma90']=ma(90)
        g['ma30_slope']=g.ma30/g.ma30.shift(5)-1
        g['ma7_30']=g.ma7/g.ma30-1;g['ma90_dev']=c/g.ma90-1
        high60=hi.rolling(60,min_periods=30).max();low60=li.rolling(60,min_periods=30).min()
        low14=li.rolling(14,min_periods=7).min();low7=li.rolling(7,min_periods=3).min()
        g['dd_60']=c/high60-1;g['pos_60']=(c-low60)/(high60-low60).replace(0,np.nan)
        g['up_14']=c/low14-1;g['up_7']=c/low7-1
        g['dsl_30']=_days_since_ext(ci.to_numpy(),30,'min')
        g['vol_7']=ret.rolling(7,min_periods=3).std();g['vol_30']=ret.rolling(30,min_periods=15).std()
        g['vol_ratio']=g.vol_7/g.vol_30.replace(0,np.nan)
        tr=pd.concat([hi-li,(hi-ci.shift()).abs(),(li-ci.shift()).abs()],axis=1).max(axis=1)
        g['atr14']=tr.rolling(14,min_periods=7).mean()/c
        g['r30']=c/ci.shift(30)-1
        g['ma30_dev']=c/g.ma30-1
        g['retlog']=ret.where(obs)
        g['priorlow3']=l.shift().rolling(3,min_periods=3).min()
        g['hold_low3']=l>=g.priorlow3
        g['support_rebound']=c>c.shift()
        g['cat']=catmap.get(name,'unknown')
        g['flat_14']=(h==l).astype(float).where(obs).rolling(14,min_periods=7).mean()
        # Label exists only with actual, positive-volume entry and exit quotes.
        for H in (7,10,14,30):
            g['retH'+str(H)]=net(c.shift(-(H+1))/c.shift(-1)-1).where(v.shift(-1).gt(0)&v.shift(-(H+1)).gt(0))
        parts.append(g)
    d=pd.concat(parts).sort_index()
    eligible=d[d.eligible]
    m=eligible.groupby('date').agg(retlog=('retlog',lambda s:s.clip(-.2,.2).mean()),
        above_ma30=('ma30_dev',lambda s:(s>0).mean()),breadth7=('r7',lambda s:(s>0).mean()),n=('name','size'))
    m['index']=np.exp(m.retlog.fillna(0).cumsum())
    for H in (3,7,14,30):m['r'+str(H)]=m['index']/m['index'].shift(H)-1
    m['dd90']=m['index']/m['index'].rolling(90,min_periods=20).max()-1
    m['ma30dev']=m['index']/m['index'].rolling(30,min_periods=10).mean()-1
    m['breadth_change3']=m.above_ma30-m.above_ma30.shift(3)
    risk=(m.r3<-.06)&(m.breadth_change3<-.04)
    tide=(m.r7>0)&(m.r3<0)&(m.breadth_change3<-.03)
    strong=(m.above_ma30>=.7)&(m.r30>0)&(m.ma30dev>0)
    repair=(m.r3>0)&(m.breadth_change3>0)
    base=(m.r7<=0)&(m.r3/3>m.r7/7)&(m.breadth_change3>=0)
    weak=(m.above_ma30<.35)|(m.dd90<-.15)|(m.r30<-.05)
    m['state']=np.select([risk,tide,strong,repair,base,weak],['加速下跌','反弹退潮','强势扩散','反弹修复','跌速减缓','弱势延续'],default='震荡或未确认')
    m['style']=np.select([strong,repair|base],['强势','修复'],default='熊市')
    m['allowed']=(strong|repair|base)&~risk&~tide
    for col in ['above_ma30','dd90','ma30dev','r3','r7','r30','breadth_change3','state','style','allowed']:
        d['market_'+col]=d.date.map(m[col])
    # Preserve original drawdown ranks on this explicitly different, Firepulse-priced research pool.
    d['dd_60_rank']=d.dd_60.where(d.eligible).groupby(d.date).rank(pct=True)
    # Weapon/glove families; sparse groups fall back to original broad category.
    sectors=[]
    for scope in ['family','cat']:
        q=eligible.groupby([scope,'date']).agg(n=('name','size'),retlog=('retlog',lambda s:s.clip(-.2,.2).mean()),
            breadth=('ma30_dev',lambda s:(s>0).mean()))
        q=q.sort_index();q['index']=q.groupby(level=0).retlog.transform(lambda s:np.exp(s.fillna(0).cumsum()))
        for H in (3,7):q['r'+str(H)]=q['index']/q.groupby(level=0)['index'].shift(H)-1
        q['breadth_change3']=q.breadth-q.groupby(level=0).breadth.shift(3)
        q['scope']=scope;sectors.append(q.reset_index().rename(columns={scope:'sector'}))
        idx=pd.MultiIndex.from_arrays([d[scope],d.date])
        for col in ['n','breadth','r3','r7','breadth_change3']:d[scope+'_'+col]=q[col].reindex(idx).to_numpy()
    use_family=d.family_n>=8
    d['sector_name']=d.family.where(use_family,d.cat)
    d['sector_scope']=np.where(use_family,'同武器/手套家族','原版大类')
    for col in ['n','breadth','r3','r7','breadth_change3']:
        d['sector_'+col]=d['family_'+col].where(use_family,d['cat_'+col])
    d['sector_valid']=np.where(use_family,d.sector_n>=8,d.sector_n>=20)
    d['sector_allowed']=d.sector_valid&(d.sector_r3>0)&(d.sector_breadth>=.4)&(d.sector_breadth_change3>0)
    d['hard_risk']=d.market_state.isin(['加速下跌','反弹退潮'])
    # Each score lies in [0,1]. Missing evidence remains missing, then contributes 0, never a neutral bonus.
    d['量能']=.50*clip((d.rv-.6)/.6)*clip((3.5-d.rv)/1.5)+.30*clip((.9-d.volume_cv7)/.5)+.20*clip((.5-d.volume_max_share7)/.25)
    downvol=clip((1.1-d.wash_volume_ratio)/.6)
    d['承接代理']=.30*clip(d.support_recovery)+.25*d.hold_low3.where(d.close.notna()).astype(float)+.25*clip(d.up_close)+.20*downvol
    # Slightly left-side entries are not forced to recover MA30; they can earn partial trend-repair evidence.
    d['趋势']=.35*clip((d.close/d.ma7-1+.03)/.06)+.30*clip((d.ma7_30+.06)/.12)+.35*clip((d.ma30_slope+.03)/.06)
    d['波动风险']=.55*clip((.15-d.atr14)/.12)+.45*clip((1.4-d.vol_ratio)/.8)
    d['相对强度']=.65*clip(d.rs_rank)+.35*clip(d.family_rank)
    ev=evidence_score(d)
    d['过程结构']=(ev['前期建仓代理'].fillna(0)+ev['第二轮量价台阶'].fillna(0)+ev['洗盘承接代理'].fillna(0))/55
    d['factor_coverage']=d[FACTORS].notna().mean(axis=1)
    d['penalty']=np.where(d.r7>.3,10,0)+np.where((d.rv>4)|(d.volume_max_share7>.5),10,0)+np.where(d.close<d.prior_low7,15,0)
    for profile,styles in PROFILES.items():
        total=pd.Series(0.,index=d.index)
        for style,weights in styles.items():
            z=d.market_style.eq(style)
            total.loc[z]=(d.loc[z,FACTORS].fillna(0).to_numpy()*np.array(weights)).sum(axis=1)*100
        d['score_'+profile]=(total-d.penalty).clip(0,100)
    return d,m,pd.concat(sectors,ignore_index=True)


def entry_masks(d,rules):
    m={}
    for r in rules:
        if r['id'] not in ('S1','M3','M4','L1'):continue
        result=pd.Series(True,index=d.index)
        for f,op,t in r['conds']:
            if f=='cat_code':x=d.cat.map({'gun_FN':0,'gloves_MW_FT':1,'agent':2}).fillna(3)
            elif f=='logp':x=np.log(d.close)
            else:x=d[f]
            result&=(x<=t if op=='<=' else x>=t)
        for f,op,t in r.get('mkt_filter',[]):
            # Original index rule reproduced on Firepulse basket, not claimed identical to SteamDT index.
            x=d['market_dd90'] if f=='mkt_dd_90' else d[f]
            result&=(x<=t if op=='<=' else x>=t)
        m['O_'+r['id']]=result
    m['I0']=d.baseline
    m['I1']=(d.ma90_dev<=-.2)&(d.up_14<=.15)&d.hold_low3&d.support_rebound&(d.rv<=2.5)
    m['I2']=d.hold_low3&(d.r3>0)&d.r7.between(-.1,.12)&d.rv.between(.8,2.5)&(d.volume_cv7<=.9)&(d.up_close>=.5)
    m['I3']=(d.past_leader>=.8)&(d.close>=d.ma20)&d.near_high.between(-.15,.02)&(d.wash_volume_ratio<=1)&d.support_rebound
    ev=evidence_score(d)
    m['I4']=(ev['前期建仓代理']>=4)&(ev['第二轮量价台阶']>=3)&(ev['洗盘承接代理']>=3)&(ev['均匀放量']>=8)&d.support_rebound
    return m


def gate_mask(d,gate):
    if gate=='不加环境对照':return pd.Series(True,index=d.index)
    if gate=='市场修复':return d.market_allowed.eq(True)&~d.hard_risk
    return (d.market_allowed.eq(True)|d.sector_allowed.eq(True))&~d.hard_risk


def dedup(g,H):
    if g.empty:return g
    keep=[]
    for _,p in g.sort_values(['name','date']).groupby('name',sort=False):
        nextday=pd.Timestamp.min
        for idx,day in p.date.items():
            if day>=nextday:keep.append(idx);nextday=day+pd.Timedelta(days=H+2)
    return g.loc[keep]


def stats(g,H):
    y=g['retH'+str(H)].dropna();z=g.loc[y.index]
    return {'n':len(y),'items':z.name.nunique(),'days':z.date.nunique(),
        'mean':float(y.mean()) if len(y) else None,'median':float(y.median()) if len(y) else None,
        'win':float(y.gt(0).mean()) if len(y) else None,'p10':float(y.quantile(.1)) if len(y) else None}


def select_recipe(d,entrymask,end,start=None):
    best=None;control=None;trials=0
    for H in (7,14,30):
        base=d[entrymask&d.eligible&d.volume_ok&(d.flat_14<=.5)&d['retH'+str(H)].notna()&(d.date+pd.Timedelta(days=H+1)<=end)]
        if start is not None:base=base[base.date>start]
        for profile in PROFILES:
            for gate in GATES:
                gated=base[gate_mask(base,gate)]
                for threshold in (55,65):
                    trials+=1;g=dedup(gated[gated['score_'+profile]>=threshold],H);s=stats(g,H)
                    if s['n']<30 or s['days']<15 or s['items']<10:continue
                    # Net returns, not relative outperformance, drive calibration selection.
                    objective=s['mean']+.25*min(s['p10'],0)
                    candidate={'H':H,'profile':profile,'gate':gate,'threshold':threshold,'objective':objective,'calibration':s}
                    if gate=='不加环境对照':
                        if control is None or objective>control['objective']:control=candidate
                    elif best is None or objective>best['objective']:best=candidate
    if best is not None:
        best['selection_role']='有环境的候选';best['ungated_calibration_control']=control
    elif control is not None:control['selection_role']='仅无环境对照，受限方案样本不足'
    return (best if best is not None else control),trials


def evaluate(d,mask,recipe,start,end,signal_end=None):
    H=recipe['H'];g=d[mask&d.eligible&d.volume_ok&(d.flat_14<=.5)&gate_mask(d,recipe['gate'])&
        (d['score_'+recipe['profile']]>=recipe['threshold'])&(d.date>start)&(d.date+pd.Timedelta(days=H+1)<=end)&d['retH'+str(H)].notna()]
    if signal_end is not None:g=g[g.date<=signal_end]
    return dedup(g,H)


def qualify(s,windows,gate):
    return bool(gate!='不加环境对照' and s['n']>=30 and s['items']>=10 and s['days']>=15 and s['mean'] is not None and s['mean']>0 and s['median']>0
        and len(windows)==3 and all(w['n']>=10 and w['days']>=5 and w['mean'] is not None and w['mean']>0 for w in windows))


def main():
    out=ROOT/'output';out.mkdir(exist_ok=True)
    today=pd.Timestamp.now(tz='Asia/Shanghai').tz_localize(None).normalize()
    universe=json.loads((ROOT/'firepulse_universe.json').read_text())
    full_universe=list(universe)
    excluded=('Nova |','XM1014 |','MAG-7 |','Sawed-Off |','Negev |','M249 |','R8 Revolver |')
    universe=[x for x in universe if not x['name'].startswith(excluded)]
    cats=pd.read_csv(ROOT/'universe.csv');catmap=dict(zip(cats.name.astype(str),cats.cat.astype(str)))
    for x in universe:
        x['cat']=catmap.get(x['name'],'gloves_MW_FT' if 'Gloves' in x['name'] or 'Hand Wraps' in x['name'] else ('gun_FN' if x['name'].endswith('(Factory New)') else 'agent'))
    # Raw refresh is owned by process_score.py in the daily pipeline; this step never re-fetches or combines prices.
    os.environ['REFRESH_PUBLIC_DATA']='0'
    frames=[];failed=[]
    with futures.ThreadPoolExecutor(max_workers=3) as ex:
        fs={ex.submit(refresh_item,x,today):x for x in universe}
        for f in futures.as_completed(fs):
            try:frames.append(f.result())
            except Exception as e:failed.append({'name':fs[f]['name'],'error':str(e)})
    if not frames:raise RuntimeError('No preserved research data')
    raw=pd.concat(frames,ignore_index=True);print('MULTIFACTOR_DATA',len(frames),len(raw),flush=True)
    d=process_features(features(raw));d,m,sectors=original_and_factor_features(d,universe)
    latest=d[d.eligible].groupby('name').date.max().value_counts().idxmax();d=d[d.date<=latest].copy()
    pool_audit=write_pool_audit(full_universe,failed,d,latest,out)
    rules=load_rules();masks=entry_masks(d,rules)
    split=latest-pd.Timedelta(days=90);development_end=latest-pd.Timedelta(days=270)
    rolling_edges=pd.date_range(latest-pd.Timedelta(days=121),latest-pd.Timedelta(days=31),periods=4)
    results=[];total_trials=0;rows=[]
    # Each method is selected on earlier calibration data, then frozen for the last-90-day check.
    for eid,mask in masks.items():
        recipe,trials=select_recipe(d,mask,split,development_end);total_trials+=trials
        if recipe is None:
            results.append({'id':eid,'name':ENTRIES[eid],'status':'校准样本不足','qualified':False});continue
        held=evaluate(d,mask,recipe,split,latest);s=stats(held,recipe['H'])
        windows=[];rolling=[]
        frozen_edges=pd.date_range(split,latest-pd.Timedelta(days=recipe['H']+1),periods=4)
        for start,end in zip(frozen_edges[:-1],frozen_edges[1:]):
            windows.append({'start':str(start.date()),'end':str(end.date()),**stats(evaluate(d,mask,recipe,start,latest,signal_end=end),recipe['H'])})
        for start,end in zip(rolling_edges[:-1],rolling_edges[1:]):
            # Genuine forward selection; later outcomes are for scoring only, never available at start.
            rp,rt=select_recipe(d,mask,start,start-pd.Timedelta(days=180));total_trials+=rt
            rolling.append({'start':str(start.date()),'end':str(end.date()),'recipe':rp,
                'result':None if rp is None else stats(evaluate(d,mask,rp,start,latest,signal_end=end),rp['H'])})
        q=qualify(s,[w['result'] for w in rolling if w['result'] is not None],recipe['gate'])
        # Require the same frozen recipe to survive the three subwindows, too; otherwise adaptive gains cannot certify it.
        q=q and all(w['n']>=10 and w['mean'] is not None and w['mean']>0 for w in windows)
        result={'id':eid,'name':ENTRIES[eid],'recipe':recipe,'test':s,'frozen_windows':windows,'rolling_windows':rolling,
                'qualified':q,'status':'允许前瞻模拟候选' if q else '未通过买入验证',
                'development':stats(evaluate(d,mask,recipe,pd.Timestamp('2000-01-01'),development_end),recipe['H'])}
        rawH={'O_S1':10,'O_M3':14,'O_M4':14,'O_L1':30}.get(eid,14)
        rawcontrol=d[mask&d.eligible&d.volume_ok&(d.flat_14<=.5)&(d.date>split)&(d.date+pd.Timedelta(days=rawH+1)<=latest)&d['retH'+str(rawH)].notna()]
        result['raw_entry_control']={'H':rawH,**stats(dedup(rawcontrol,rawH),rawH)}
        # Compare score bands inside the same entry/environment; do not mix all-regime samples into a fake monotone score.
        base=d[mask&d.eligible&d.volume_ok&gate_mask(d,recipe['gate'])&(d.date>split)&
            (d.date+pd.Timedelta(days=recipe['H']+1)<=latest)&d['retH'+str(recipe['H'])].notna()]
        bands=[]
        for low,high in [(0,40),(40,55),(55,65),(65,80),(80,101)]:
            z=dedup(base[base['score_'+recipe['profile']].between(low,high,inclusive='left')],recipe['H'])
            bands.append({'band':f'{low}–{min(high,100)}',**stats(z,recipe['H'])})
        result['score_bands']=bands
        nonempty=[b for b in bands if b['n']>=20]
        monotone=len(nonempty)>=3 and all(b['mean']>=a['mean'] for a,b in zip(nonempty[:-1],nonempty[1:]))
        result['score_monotonicity_observed']=bool(monotone)
        result['qualified']=bool(result['qualified'] and monotone)
        result['status']='允许前瞻模拟候选' if result['qualified'] else '未通过买入验证'
        results.append(result);print('ENTRY',eid,json.dumps({'recipe':recipe,'test':s,'qualified':result['qualified']},ensure_ascii=False,default=int),flush=True)
    current=d[(d.date==latest)&d.eligible&d.volume_ok&(d.flat_14<=.5)].copy()
    byid={r['id']:r for r in results};now=pd.Timestamp.now(tz='Asia/Shanghai').isoformat()
    for idx,r in current.iterrows():
        hits=[eid for eid,mask in masks.items() if bool(mask.loc[idx])]
        choices=[]
        for eid in hits:
            res=byid[eid];rp=res.get('recipe')
            if rp:
                env=bool(gate_mask(current.loc[[idx]],rp['gate']).iloc[0]);score=float(r['score_'+rp['profile']])
                choices.append((bool(res['qualified']) and env and score>=rp['threshold'],env,score,eid,rp))
        chosen=max(choices,key=lambda a:(a[0],a[1],a[2])) if choices else None
        if chosen:
            buy,env,score,eid,rp=chosen;entry=ENTRIES[eid];profile=rp['profile'];threshold=rp['threshold'];gate=rp['gate'];H=rp['H']
        else:
            buy=False;env=bool(gate_mask(current.loc[[idx]],'市场或板块修复').iloc[0]);score=float(r['score_环境适配']);eid='';entry='未命中入场形态';profile='环境适配';threshold=None;gate='市场或板块修复';H=None
        # An ungated calibration winner is a control, never an actionable environment permission.
        if gate=='不加环境对照':env=False;buy=False
        missing=[]
        if not env:missing.append('市场/板块未放行或仅为无门控对照')
        if chosen is None:missing.append('无入场触发')
        if threshold is not None and score<threshold:missing.append(f'低于本规则{threshold}分门槛')
        if chosen is not None and not byid[eid]['qualified']:missing.append('该入场与评分未通过完整验证')
        if chosen is None:missing.append('没有已通过验证的入场方案')
        weights=PROFILES[profile][r.market_style]
        contributions={f:float(0 if pd.isna(r[f]) else r[f])*w*100 for f,w in zip(FACTORS,weights)}
        why='；'.join(f'{f}贡献{contributions[f]:.1f}分' for f in sorted(contributions,key=contributions.get,reverse=True)[:3])
        row={'name':r['name'],'cn':r.cn,'价格日期':str(latest.date()),'生成时间':now,'算法版本':VERSION,'日K价':r.close,
            '多因子证据分':score,'评分类型':'已验证前瞻模拟分' if chosen is not None and byid[eid]['qualified'] else '研究证据分','行动':'允许前瞻模拟观察' if buy else '等待/研究观察','入场方式':entry,'触发的全部方式':'；'.join(ENTRIES[x] for x in hits),
            '评分方案':profile,'门槛':threshold,'参考持有日':H,'市场状态':r.market_state,'环境权重类别':r.market_style,
            '板块代理':r.sector_name,'板块口径':r.sector_scope,'板块样本':r.sector_n,'板块近3日':r.sector_r3,
            '板块广度':r.sector_breadth,'环境放行':env,'环境规则':gate,'证据覆盖率':r.factor_coverage,
            **{f+'贡献':v for f,v in contributions.items()},'风险扣分':r.penalty,'主要证据':why,'未满足条件':'；'.join(missing),
            '实时承接状态':'未接入完整实时盘口，当前承接为日K代理','会员证据':'无身份真值，仅量价过程代理'}
        rows.append(row)
    scores=pd.DataFrame(rows).sort_values(['环境放行','多因子证据分'],ascending=[False,False])
    scores.to_csv(out/'daily_multifactor_scores.csv',index=False,encoding='utf-8-sig')
    sectors[sectors.date.eq(latest)].to_csv(out/'multifactor_sector_snapshot.csv',index=False,encoding='utf-8-sig')
    manifest={'version':VERSION,'generated_at':now,'asof':str(latest.date()),'items_requested':len(universe),'items_loaded':len(frames),
        'rows':len(raw),'daily_rows':len(scores),'scoring_pool_status_counts':pool_audit['status_counts'],'failures':failed,'source':'Firepulse YOUPIN prices; global all-platform volume proxy',
        'calibration_start':str(development_end.date()),'validation_start':str(split.date()),'profiles':PROFILES,'entry_methods':ENTRIES,
        'rolling_signal_start':str(rolling_edges[0].date()),'rolling_signal_end':str(rolling_edges[-1].date()),
        'total_search_combinations_including_rolling':total_trials,'results':results,'qualified_systems':[r['id'] for r in results if r['qualified']],
        'daily_allowed_rows':int(scores['行动'].eq('允许前瞻模拟观察').sum()),'original_rule_status':{r['id']:r['status'] for r in rules},
        'limitations':['原版规则条件在Firepulse研究池重算，未沿用SteamDT历史收益、旧模型或官方指数；历史规则含已看过验证段的人为经验，并非全新盲测',
            '权重与门控候选为先验设计，参数只用各验证开始前成熟标签挑选；多方案筛选仍有过拟合风险，需新增数据前瞻验证',
            '板块为武器/手套家族或原版枪械/手套/探员大类代理，含当前商品；非官方板块、收藏品系列或会员群体，稀疏组回退大类',
            '承接、建仓、会员档位及成本只有日K代理，没有真实会员身份、历史求购或在售盘口真值',
            '悠悠价格、全平台成交量分别使用；缺日仅在原版技术指标中向前延续，不用于买卖标签或模拟结算',
            '每个入场方案内部同商品按H+2自然日去重，跨方案为独立对照；无资金分配、账户收益或保证成交，固定持有期可能违反实际平台限制',
            '手续费2.5%、双边各0.5%滑点；次日收盘代理买入，H日后收盘代理退出；7/14/30日均为研究方案',
            '原版S1/M3/M4/L1仍保持probation，L3因价格≤20元与本池≥30元冲突而不参与，未自动复活旧规则',
            '高分仅表示公式证据齐；必须同时通过入场、环境、阈值、历史资格和分组单调性检验才给前瞻模拟候选；不宣称成功概率',
            'Whale仅辅助；固定研究池、历史修订和相关样本导致的偏差仍然存在']}
    (out/'multifactor_validation.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2,default=int))
    pct=lambda x:'—' if x is None else f'{x:.2%}'
    lines=['# 市场与板块条件下的多因子评分研究','',f'截至{latest.date()}；{len(frames)}/{len(universe)}件数据，{len(scores)}件每日评分。',
        f'通过完整检验的系统：{", ".join(manifest["qualified_systems"]) or "无"}；当前允许前瞻模拟观察：{manifest["daily_allowed_rows"]}件。',
        '','## 原版审计','',
        '复用原版短/中/长周期规则、MA30市场广度分档、90日指数回撤、短长波动比和ATR思想。原版五规则当前均为probation；本研究不改变其状态。原LightGBM只做收益排序，不能把它的分位视为成功概率。',
        '','## 公式与权重','',
        'S = clip(100 × Σ[环境对应权重 × 因子(0–1)] − 风险扣分, 0, 100)。环境和入场资格单独展示，不通过时保留分数并标为等待。',
        '','| 环境适配权重 | 量能 | 承接代理 | 趋势 | 波动风险 | 相对强度 | 过程结构 |','|---|---:|---:|---:|---:|---:|---:|',
        '| 熊市 | 15% | 30% | 10% | 25% | 10% | 10% |','| 修复 | 20% | 25% | 15% | 20% | 10% | 10% |',
        '| 强势 | 25% | 20% | 20% | 10% | 15% | 10% |',
        '','另比较等权与防守优先；每种方案比较不加环境、市场修复、市场或板块修复，以及55/65分门槛和7/14/30日持有。所有方案先在校准段选择，最后90日检验。',
        f'训练/开发标签截止{development_end.date()}，校准结束{split.date()}；共计{total_trials}个参数组合（含三轮滚动选择，非独立实验数量）。',
        '','## 入场比较（每种入场方式的校准优选，不按最后验证结果倒选）','',
        '| 入场 | H | 权重/门控/门槛 | 开发样本/均值 | 校准样本/均值 | 最近90日样本 | 均值 | 中位 | 胜率 | 完整通过 |',
        '|---|---:|---|---|---|---:|---:|---:|---:|---|']
    for r in results:
        p=r.get('recipe');s=r.get('test',{});dev=r.get('development',{})
        if p:lines.append(f'| {r["id"]} {r["name"]} | {p["H"]} | {p["profile"]}/{p["gate"]}/{p["threshold"]} | {dev.get("n",0)}/{pct(dev.get("mean"))} | {p["calibration"]["n"]}/{pct(p["calibration"]["mean"])} | {s["n"]} | {pct(s["mean"])} | {pct(s["median"])} | {pct(s["win"])} | {r["qualified"]} |')
        else:lines.append(f'| {r["id"]} {r["name"]} | — | 校准样本不足 | — | — | 0 | — | — | — | False |')
    lines+=['','## 三轮真正滚动验证','',
        '每轮重新选择权重、门控、门槛及持有期，只可用当轮开始前已成熟结果。滚动信号窗口为截至日前121日至31日的三个30日区间，结果可在窗口结束后成熟，但不得晚于报告日；与最近90自然日检验分开展示。冻结方案另按本方案已成熟信号日期分三段。缺结果记样本不足，不当作零收益。',
        '','| 入场 | 窗口 | 本轮选择 | 样本 | 净均值 |','|---|---|---|---:|---:|']
    for r in results:
        for w in r.get('rolling_windows',[]):
            p=w['recipe'];s=w['result']
            lines.append(f'| {r["id"]} | {w["start"]}至{w["end"]} | '+('样本不足 | 0 | — |' if p is None else f'{p["H"]}日/{p["profile"]}/{p["gate"]}/{p["threshold"]} | {s["n"]} | {pct(s["mean"])} |'))
    lines+=['','## 每日证据前15（等待不等于买点）','',
        '| 商品 | 分数 | 环境放行 | 入场 | 行动 | 未满足条件 |','|---|---:|---|---|---|---|']
    for _,r in scores.head(15).iterrows():lines.append(f'| {r.cn.replace("|","/")} | {r["多因子证据分"]:.1f} | {r["环境放行"]} | {r["入场方式"]} | {r["行动"]} | {r["未满足条件"]} |')
    lines+=['','## 限制与口径',*['- '+x for x in manifest['limitations']],
        '','因子精确计算见multifactor_research.py；各规则分数段、冻结窗口、滚动窗口、失败清单见multifactor_validation.json。']
    md='\n'.join(lines);(out/'multifactor_report.md').write_text(md)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'],'a') as f:f.write('\n\n'+md)
    print('MULTIFACTOR_COMPLETE',json.dumps({k:manifest[k] for k in ['asof','daily_rows','qualified_systems','daily_allowed_rows','total_search_combinations_including_rolling']},ensure_ascii=False),flush=True)

if __name__=='__main__':main()

