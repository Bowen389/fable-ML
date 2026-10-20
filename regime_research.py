"""Bear-market states and breakout leader case study; reuses frozen raw cache."""
import gzip
import json
from pathlib import Path
import numpy as np
import pandas as pd
from leader_research import ROOT,CACHE,parse,features,masks,rows_for,statistics


def market_states(d):
    x=d.copy()
    x['new_low']=x.groupby('name',sort=False).close.transform(lambda s:s<=s.shift().rolling(20).min())
    x=x[x.eligible]
    m=x.groupby('date').agg(ret1=('r1','median'),breadth=('breadth','first'),new_lows=('new_low','mean'),volume_proxy=('rv','median'))
    m['index']=(1+m.ret1.clip(-.2,.2)).cumprod()
    for n in (3,7,30):m['r'+str(n)]=m['index']/m['index'].shift(n)-1
    m['ma20']=m['index'].rolling(20).mean();m['ma60']=m['index'].rolling(60).mean()
    m['weak']=(m['index']<m.ma60)&(m.ma60<m.ma60.shift(7))
    m['breadth_change3']=m.breadth-m.breadth.shift(3)
    m['new_low_change3']=m.new_lows-m.new_lows.shift(3)
    retreat=(m.r7>0)&(m.r3<0)&(m.breadth_change3<-.03)
    right=(m.r7>0)&(m['index']>m.ma20)&(m.breadth>=.3)
    early=m.weak&(m.r3>0)&(m.r7<=0)&(m.breadth_change3>0)
    base=m.weak&(m.r7<0)&(m.r3/3>m.r7/7)&(m.new_low_change3<=0)&(m.breadth_change3>0)
    accelerating=m.weak&(m.r3<-.03)&(m.breadth_change3<0)
    m['state']=np.select([retreat,right,early,base,accelerating,m.weak],
                        ['反弹退潮迹象','右侧反弹确认','熊市反弹初启动','熊市跌速减缓筑底迹象','熊市加速下跌','熊市持续弱势'],default='其他或资料不足')
    return m


def extra_features(d):
    chunks=[]
    for name,g in d.groupby('name',sort=False):
        g=g.copy();g['low20']=g.low.shift().rolling(20).min()
        g['hold_low3']=g.low>=g.low.shift().rolling(3).min()
        future_high=g.high.shift(-1).iloc[::-1].rolling(30,min_periods=30).max().iloc[::-1]
        future_low=g.low.shift(-1).iloc[::-1].rolling(30,min_periods=30).min().iloc[::-1]
        g['future_peak30']=future_high/g.close-1
        g['future_adverse30']=future_low/g.close.shift(-1)-1
        for n in (20,40,60):
            obs=g[g.close.notna()]
            top=obs.high.shift().rolling(n).max().reindex(g.index)
            bottom=obs.low.shift().rolling(n).min().reindex(g.index)
            width=top/bottom-1
            g['box'+str(n)]=(width<=.25)&(g.close>top)&(g.close.shift()<=top.shift())
            g['box_width'+str(n)]=width;g['break_premium'+str(n)]=g.close/top-1
        chunks.append(g)
    return pd.concat(chunks).sort_index()


def stat(e,boundary):
    r=statistics(e)
    r['mean']=None if e.empty else float(e.net.mean())
    if not e.empty:
        wins=e.loc[e.net>0,'net'];losses=e.loc[e.net<0,'net']
        r['gain_loss_ratio']=float(wins.mean()/-losses.mean()) if len(wins) and len(losses) else None
    else:r['gain_loss_ratio']=None
    # Only count labels whose full horizon was knowable at this boundary.
    for name,days in [('t1',8),('t0',15)]:
        mature=e[e.date+pd.Timedelta(days=days)<=boundary]
        r[name+'_precision']=float(mature[name].mean()) if len(mature) else None
    return r


def main():
    today=pd.Timestamp.now(tz='Asia/Shanghai').tz_localize(None).normalize()
    universe=json.loads((ROOT/'firepulse_universe.json').read_text())
    excluded=('Nova |','XM1014 |','MAG-7 |','Sawed-Off |','Negev |','M249 |','R8 Revolver |')
    frames=[]
    for item in universe:
        path=CACHE/(item['id']+'.json.gz')
        if not path.exists() or item['name'].startswith(excluded):continue
        with gzip.open(path,'rt') as f:g=parse(json.load(f),today)
        if len(g)<100:continue
        for k in ('name','cn','id'):g[k]=item[k]
        g['family']=item['name'].split('|')[0].strip();frames.append(g)
    if not frames:raise RuntimeError('No cache: download preserved leader-stage-research artifact first')
    raw=pd.concat(frames,ignore_index=True)
    print('REUSE',len(frames),'items',len(raw),'bars; no API calls',flush=True)
    d=extra_features(features(raw));latest=d[d.eligible].groupby('name').date.max().value_counts().idxmax()
    d=d[d.date<=latest];m=market_states(d);d['market_state']=d.date.map(m.state)
    split=latest-pd.Timedelta(days=90)
    early=d.market_state.isin(['熊市跌速减缓筑底迹象','熊市反弹初启动'])
    stabilizing=d.market_state.eq('熊市跌速减缓筑底迹象')
    turning=d.market_state.eq('熊市反弹初启动')
    support=(d.close/d.low20<=1.08)&d.hold_low3&(d.up_close>=.6)&(d.r1>0)&d.rv.between(.6,1.8)
    candidates={'R0_原买点无阀门':d.baseline,
                'R1_原买点只在左侧形态':d.baseline&early,
                'R2_跌速减缓低位试探':stabilizing&support&(d.r14<0),
                'R3_反弹初启低溢价':turning&(d.rs_rank>=.6)&(d.family_rank>=.7)&(d.base_gap<=.08)&d.rv.between(.8,2.5)&(d.r1>0),
                'R4_反弹退潮回避':d.baseline&~d.market_state.isin(['反弹退潮迹象','熊市加速下跌'])}
    for n in (20,40,60):
        candidates['R_平台突破'+str(n)]=d['box'+str(n)]&(d['break_premium'+str(n)]<=.03)&d.rv.between(.8,3)&(d.up_close>=.6)
    results=[]
    for rule,mask in candidates.items():
        for H in (7,14,30):
            e=rows_for(d,mask,H)
            train=stat(e[e.exit_date<=split],split)
            val=stat(e[(e.date>split)&(e.exit_date<=latest)],latest)
            folds=[]
            for offset in (270,180,90):
                lo=latest-pd.Timedelta(days=offset);hi=lo+pd.Timedelta(days=90)
                folds.append(stat(e[(e.date>lo)&(e.exit_date<=hi)],hi))
            adequate=lambda s:s['n']>=30 and s['items']>=10 and s['days']>=20
            passed=(adequate(train) and adequate(val) and train['mean']>0 and val['mean']>0 and
                    sum(adequate(x) and x['mean']>0 for x in folds)>=2)
            results.append({'rule':rule,'H':H,'training':train,'validation':val,'folds':folds,
                            'status':'仅前瞻模拟候选' if passed else '尚未通过'})
    by_state=[]
    for H in (7,14,30):
        e=rows_for(d,d.baseline,H)
        for state,g in e.groupby('market_state'):
            by_state.append({'state':state,'H':H,'all':stat(g,latest),
                             'recent':stat(g[(g.date>split)&(g.exit_date<=latest)],latest)})
    # Retrospective breakout labels, never used by entry masks or current market classification.
    breakouts=[]
    for n in (20,40,60):
        e=d[d.eligible&d.volume_ok&d['box'+str(n)]&d.future_peak30.notna()].copy()
        e['box_days']=n;e['cohort']=e.date.dt.to_period('M').astype(str)
        e['post_breakout_rank']=e.groupby('cohort').future_peak30.rank(ascending=False,method='min')
        breakouts.append(e)
    events=pd.concat(breakouts,ignore_index=True)
    targets=[('合纵','M4A4 | The Coalition (Factory New)',2025),('水栽竹','AK-47 | Hydroponic (Factory New)',2025),
             ('深红织物略磨','★ Driver Gloves | Crimson Weave (Minimal Wear)',2025),('深红织物久经','★ Driver Gloves | Crimson Weave (Field-Tested)',2025),
             ('抽象派','AK-47 | Leet Museo (Factory New)',2025),('USP次时代','USP-S | Cyrex (Factory New)',2026),
             ('格洛克核子花园','Glock-18 | Nuclear Garden (Factory New)',2026),('法玛斯机械工业','FAMAS | Mecha Industries (Factory New)',2026),
             ('M4A1闪回','M4A1-S | Flashback (Factory New)',2026)]
    cases=[];missing=[]
    cols=['date','name','cn','box_days','market_state','close','rv','base_gap','rs_rank','future_peak30','future_adverse30','post_breakout_rank']
    for label,name,year in targets:
        g=events[(events.name==name)&(events.date.dt.year==year)].sort_values('future_peak30',ascending=False).drop_duplicates('date').head(3)
        if g.empty:missing.append(label+'：该年未满足当前20/40/60日箱体定义，不能当成不存在行情')
        else:
            for row in g[cols].to_dict('records'):row['case']=label;cases.append(row)
    # Learning comparison: top-decile vs nonpositive follow-through in the same monthly cohorts.
    events['cohort_percentile']=events.groupby(['cohort','box_days']).future_peak30.rank(pct=True)
    winners=events[(events.cohort_percentile>=.9)&(events.future_peak30>0)]
    failures=events[events.net7<=0]
    descriptive={key:{'winner_median':float(winners[key].median()),'failure_median':float(failures[key].median())}
                 for key in ['rv','base_gap','rs_rank','r7','r20']}
    out=ROOT/'output';out.mkdir(exist_ok=True)
    m.to_csv(out/'market_regime_history.csv',index_label='date',encoding='utf-8-sig')
    pd.DataFrame(cases).to_csv(out/'leader_case_breakouts.csv',index=False,encoding='utf-8-sig')
    current=[]
    for rule,mask in candidates.items():
        for row in d[(d.date==latest)&d.eligible&d.volume_ok&mask][['name','cn','close','rv','base_gap','market_state']].to_dict('records'):
            row['rule']=rule;row['research_qualified']=any(x['rule']==rule and x['status']=='仅前瞻模拟候选' for x in results);current.append(row)
    pd.DataFrame(current).to_csv(out/'regime_current_candidates.csv',index=False,encoding='utf-8-sig')
    result={'version':'regime-left-entry-v2-gap-aware','asof':str(latest.date()),'split':str(split.date()),'market_latest':m.iloc[-1].to_dict(),
            'results':results,'baseline_by_state':by_state,'cases':cases,'case_missing':missing,'descriptive_winners_failures':descriptive,
            'current_candidates':current,'definitions':[
            '市场篮子为当日符合资格白名单商品收益中位数逐日链接，非官方大盘指数；有现存白名单偏差',
            '市场形态阈值先验固定，未做数据拟合；当日状态只用当日及以前的数据',
            '跌速减缓：熊市背景、7日仍跌、近3日跌速较7日减缓、新低占比不增加、站均线比例改善；不要求7日转正',
            '初启动：熊市背景、3日涨而7日仍不涨、站均线比例改善；允许在右侧确认之前观察',
            '龙头事后标签改为箱体突破后30日最高价涨幅的同月突破事件排名；不同窗口分开，标签不进入买点',
            '箱体为前20/40/60条有效K线的高低区间振幅<=25%；不是缺日补出的连续日箱体，未匹配案例不等于该行情不是龙头',
            '覆盖检查累计300根、近90日>=80根、近20日>=18根；量用33条真实观察且跨度<=45自然日，不填补缺失报价或收益标签',
            '代表案例表按事后峰值选取，仅用于解释；非样本外选股成绩。失败对照与赢家可能重叠：先跌后涨也可能出现',
            '会员成本差仍为过去20日价格中位代理，无真实会员身份或真实建仓价',
            '候选资格本轮采用扣费平均收益而非必须中位为正，适应低胜率高赔率假设；该指标变更已明确披露',
            '沿用手续费2.5%、双边各0.5%滑点；次日收盘代理入场，固定7/14/30自然日退出，不是账户净值']}
    (out/'regime_research.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,default=str))
    pct=lambda v:'—' if v is None else f'{v:+.2%}'
    lines=['# 熊市形态与左侧买点研究','',f'截至{latest.date()}；复用{len(frames)}件长期量价缓存，未重新抓取。',
           f'最新市场状态：**{m.iloc[-1]["state"]}**。','',
           '## 固定方案对照','',
           '| 方案 | H | 训练n | 训练净均值 | 验证n | 验证净均值 | 验证净中位 | 验证胜率 | 结论 |','|---|---:|---:|---:|---:|---:|---:|---:|---|']
    for x in results:
        t,v=x['training'],x['validation'];lines.append(f'| {x["rule"]} | {x["H"]} | {t["n"]} | {pct(t["mean"])} | {v["n"]} | {pct(v["mean"])} | {pct(v["median"])} | {pct(v["win"])} | {x["status"]} |')
    lines+=['','## 原买点在不同市场形态下的最近90日表现','',
            '| 市场形态 | H | 样本 | 净均值 | 净中位 |','|---|---:|---:|---:|---:|']
    for x in by_state:
        s=x['recent'];lines.append(f'| {x["state"]} | {x["H"]} | {s["n"]} | {pct(s["mean"])} | {pct(s["median"])} |')
    lines+=['','## 用户龙头案例：箱体突破后的事后观察','',
            '| 案例 | 突破日 | 箱体天数 | 当时市场形态 | 后30日最高涨幅 |','|---|---|---:|---|---:|']
    for x in cases:lines.append(f'| {x["case"]} | {x["date"].date()} | {x["box_days"]} | {x["market_state"]} | {pct(x["future_peak30"])} |')
    lines+=['',*['- '+s for s in missing],'','## 定义及适用边界',*['- '+s for s in result['definitions']],
            '',f'当日形态候选{len(current)}行，见regime_current_candidates.csv；与验证通过的系统候选分开。','']
    (out/'regime_research.md').write_text('\n'.join(lines),encoding='utf-8')
    print('REGIME_COMPLETE',json.dumps({'latest_state':m.iloc[-1]['state'],'systems':len(results),'passed':sum(x['status']=='仅前瞻模拟候选' for x in results),'cases':len(cases),'current_candidates':len(current)},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
