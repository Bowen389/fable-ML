"""Firepulse public-data leader-stage research, fixed rules, no live orders."""
import concurrent.futures as futures
import gzip
import hashlib
import json
import os
from pathlib import Path
import threading
import time
import urllib.request
import numpy as np
import pandas as pd
from research_buy_params import signals, net

ROOT=Path(__file__).resolve().parent
CACHE=ROOT/'research_cache'
SITE='https://firepulse.com.cn'
LOCK=threading.Lock()
LAST=0.0
HORIZONS=(7,14,30)


def request(path,body):
    global LAST
    for attempt in range(4):
        with LOCK:
            delay=.4-(time.monotonic()-LAST)
            if delay>0:time.sleep(delay)
            LAST=time.monotonic()
        try:
            req=urllib.request.Request(SITE+path,data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(req,timeout=30) as r:result=json.load(r)
            if result.get('code')==200:return result
            if result.get('code') in (401,403):raise PermissionError('Public endpoint requires authorization')
            raise RuntimeError('Endpoint code '+str(result.get('code')))
        except PermissionError:raise
        except Exception:
            if attempt==3:raise
            time.sleep(5)


def parse(payload,today):
    rows=[]
    for r in payload.get('data',[]):
        if not isinstance(r,list) or len(r)<7:continue
        try:
            stamp=float(r[0]);stamp=stamp/1000 if stamp>1e12 else stamp
            day=pd.Timestamp(stamp,unit='s',tz='UTC').tz_convert('Asia/Shanghai').tz_localize(None).normalize()
            o,c,l,h,v=map(float,r[1:6])
            if day>=today or min(o,c,l,h)<=0 or v<0 or l>min(o,c) or h<max(o,c):continue
            rows.append((day,o,c,h,l,v))
        except (ValueError,TypeError,OverflowError):continue
    if not rows:return pd.DataFrame()
    return pd.DataFrame(rows,columns=['date','open','close','high','low','volume']).drop_duplicates('date',keep='last').sort_values('date')


def collect(item,today):
    path=CACHE/(item['id']+'.json.gz')
    if path.exists():
        with gzip.open(path,'rt') as f:payload=json.load(f)
    else:
        payload=request('/v1/market/facade/quote/skin_k_chart',{'id':item['id'],'type':2,'timestamp':int(time.time()),'date_range':1440,'platform':'youpin'})
        with gzip.open(path,'wt') as f:json.dump(payload,f,separators=(',',':'))
    frame=parse(payload,today)
    if len(frame)<100:raise ValueError('Less than 100 valid completed bars')
    frame['name']=item['name'];frame['cn']=item['cn'];frame['id']=item['id']
    frame['family']=item['name'].split('|')[0].strip()
    return frame


def features(frame):
    chunks=[]
    for name,part in frame.groupby('name',sort=True):
        part=part.sort_values('date').set_index('date')
        g=part.reindex(pd.date_range(part.index.min(),part.index.max()))
        c,o,h,l,v=(g[k] for k in ['close','open','high','low','volume'])
        valid=c.notna()
        g['eligible']=(valid.cumsum()>=300)&(valid.rolling(90).sum()==90)&(c>=30)
        g['ma20']=c.rolling(20).mean();g['ma60']=c.rolling(60).mean()
        for days in (1,3,7,14,20):g['r'+str(days)]=c/c.shift(days)-1
        g['break20']=c>h.shift().rolling(20).max()
        g['break5']=c>h.shift().rolling(5).max()
        g['near_high']=c/h.shift().rolling(20).max()-1
        g['base_gap']=c/c.shift().rolling(20).median()-1
        g['rv']=v.rolling(3).mean()/v.shift(3).rolling(30).median().replace(0,np.nan)
        g['pull_vol']=v.shift().rolling(3).mean()/v.shift(4).rolling(20).median().replace(0,np.nan)
        g['volume_ok']=v.rolling(33).count().eq(33)&(v>0)&(v.shift(3).rolling(30).median()>0)
        g['up_close']=(c-l)/(h-l).replace(0,np.nan)
        g['rebound']=(c>h.shift())&(g.r1>0)
        g['ma_up']=g.ma20>g.ma20.shift(5)
        g['baseline']=signals(g)['全部买点_原始并集']
        for H in HORIZONS:
            g['net'+str(H)]=net(c.shift(-(H+1))/c.shift(-1)-1).where(v.shift(-1).gt(0)&v.shift(-(H+1)).gt(0))
        g['next7']=net(c.shift(-15)/c.shift(-8)-1).where(v.shift(-8).gt(0)&v.shift(-15).gt(0))
        for col in ['name','cn','id','family']:g[col]=part[col].iloc[0]
        g['date']=g.index
        chunks.append(g.reset_index(drop=True))
    d=pd.concat(chunks,ignore_index=True)
    eligible=d[d.eligible]
    market=eligible.groupby('date').agg(breadth=('close',lambda s:float((s>d.loc[s.index,'ma20']).mean())),mkt7=('r7','median'))
    d['breadth']=d.date.map(market.breadth);d['mkt7']=d.date.map(market.mkt7)
    d['rs7']=d.r7-d.mkt7
    d['rs_rank']=d.rs7.where(d.eligible).groupby(d.date).rank(pct=True)
    d['family_rank']=d.r7.where(d.eligible).groupby([d.date,d.family]).rank(pct=True)
    d['past_leader']=d.groupby('name',sort=False).rs_rank.transform(lambda s:s.shift().rolling(10).max())
    d['t1_rank']=d.net7.where(d.eligible).groupby(d.date).rank(ascending=False,method='first')
    d['t1']=(d.t1_rank.le(30)&d.net7.gt(0)).astype(float).where(d.net7.notna())
    d['t0_rank']=d.next7.where(d.eligible).groupby(d.date).rank(ascending=False,method='first')
    d['t0']=(d.t1.eq(1)&d.t0_rank.le(30)&d.next7.gt(0)).astype(float).where(d.net7.notna()&d.next7.notna())
    return d


def masks(d):
    leader=(d.rs_rank>=.8)&(d.family_rank>=.7)
    trend=(d.close>d.ma20)&d.ma_up
    moderate=d.rv.between(1.2,3)&(d.base_gap<=.15)
    breakout=leader&d.break20&moderate&(d.up_close>=.6)
    pullback=(d.past_leader>=.85)&trend&d.near_high.between(-.1,0)&(d.pull_vol<.85)&d.rebound&d.rv.between(.8,2.5)
    restart=leader&trend&d.break5&d.rv.between(1.2,3)&d.r20.between(0,.3)&(d.base_gap<=.15)
    early=leader&trend&d.baseline&d.rv.between(1,3)&(d.base_gap<=.12)
    overheat=(d.r20>.3)&(d.rv>3)&((d.up_close<.5)|(d.r3<.03))
    market_ok=(d.breadth>=.3)&(d.mkt7>0)
    return {'B0_原买点并集':d.baseline,'L1_领先突破':breakout,'L2_龙头首次回踩代理':pullback,
            'L3_趋势再启动':restart,'L4_低成本差转强':early,
            'L5_原买点加领先及过热过滤':d.baseline&leader&~overheat&(d.base_gap<=.15),
            'L6_领先突破加市场过滤':breakout&market_ok,
            'L7_首次回踩加市场过滤':pullback&market_ok}


def rows_for(d,mask,H):
    selected=d[mask&d.eligible&d.volume_ok&d['net'+str(H)].notna()].sort_values(['name','date'])
    keep=[]
    for name,g in selected.groupby('name',sort=False):
        next_day=pd.Timestamp.min
        for row in g.itertuples():
            if row.date>=next_day:
                keep.append(row.Index);next_day=row.date+pd.Timedelta(days=H+2)
    return d.loc[keep].assign(net=d.loc[keep,'net'+str(H)],exit_date=lambda x:x.date+pd.Timedelta(days=H+1))


def statistics(g):
    if g.empty:return {'n':0,'items':0,'days':0,'median':None,'win':None,'p10':None,'t1_precision':None,'t0_precision':None}
    return {'n':len(g),'items':g.name.nunique(),'days':g.date.nunique(),'median':float(g.net.median()),'win':float((g.net>0).mean()),
            'p10':float(g.net.quantile(.1)),'t1_precision':float(g.t1.mean()),'t0_precision':float(g.t0.mean())}


def sufficient(s):return s['n']>=30 and s['items']>=10 and s['days']>=20


def main():
    CACHE.mkdir(exist_ok=True);out=ROOT/'output';out.mkdir(exist_ok=True)
    today=pd.Timestamp.now(tz='Asia/Shanghai').tz_localize(None).normalize()
    universe=json.loads((ROOT/'firepulse_universe.json').read_text())
    excluded=('Nova |','XM1014 |','MAG-7 |','Sawed-Off |','Negev |','M249 |','R8 Revolver |')
    universe=[x for x in universe if x['id'] and not x['name'].startswith(excluded)]
    limit=int(os.environ.get('RESEARCH_ITEM_LIMIT','0'))
    if limit:universe=universe[:limit]
    frames=[];failed=[];began=time.monotonic()
    print('START FIREPULSE RESEARCH',len(universe),'items; price=youpin volume=all-platform',flush=True)
    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        tasks={executor.submit(collect,item,today):item for item in universe}
        for n,f in enumerate(futures.as_completed(tasks),1):
            item=tasks[f]
            try:frames.append(f.result())
            except Exception as exc:failed.append({'name':item['name'],'error':type(exc).__name__+': '+str(exc)})
            if n%20==0 or n==len(universe):
                print(f'FETCH {n}/{len(universe)} ok={len(frames)} failed={len(failed)} elapsed={time.monotonic()-began:.0f}s',flush=True)
    if not frames:raise RuntimeError('No usable Firepulse history')
    raw=pd.concat(frames,ignore_index=True)
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in CACHE.glob('*.gz')}
    (out/'leader_data_manifest.json').write_text(json.dumps({'generated_at':pd.Timestamp.now(tz='Asia/Shanghai').isoformat(),'universe':len(universe),'success':len(frames),'failed':failed,'source':SITE,'date_start':str(raw.date.min().date()),'date_end':str(raw.date.max().date()),'hashes':hashes,'volume_basis':'全平台日成交量代理，非悠悠独立成交量'},ensure_ascii=False,indent=2))
    print('BUILD FEATURES',len(raw),'bars',flush=True)
    d=features(raw)
    latest=d[d.eligible].groupby('name').date.max().value_counts().idxmax()
    d=d[d.date<=latest].copy()
    rule_masks=masks(d);split=latest-pd.Timedelta(days=90)
    results=[];candidates=[];all_events=[]
    for rule,mask in rule_masks.items():
        for H in HORIZONS:
            e=rows_for(d,mask,H);e['rule']=rule;e['H']=H
            all_events.append(e[['name','date','exit_date','net','rule','H','t1','t0']])
            training=statistics(e[e.exit_date<=split]);validation=statistics(e[(e.date>split)&(e.exit_date<=latest)])
            folds=[]
            for offset in (270,180,90):
                lo=latest-pd.Timedelta(days=offset);hi=lo+pd.Timedelta(days=90)
                folds.append(statistics(e[(e.date>lo)&(e.exit_date<=hi)]))
            passed=(sufficient(training) and training['median']>0 and sufficient(validation) and validation['median']>0 and
                    sum(sufficient(f) and f['median']>0 for f in folds)>=2)
            results.append({'rule':rule,'H':H,'training':training,'validation':validation,'folds':folds,
                            'status':'可列入前瞻模拟候选' if passed else '未通过，保留研究'})
        now=d[(d.date==latest)&d.eligible&d.volume_ok&mask]
        for x in now.itertuples():
            candidates.append({'rule':rule,'name':x.name,'cn':x.cn,'id':x.id,'date':str(latest.date()),'close':x.close,'relative_volume':x.rv,
                               'rs_percentile':x.rs_rank,'base_price_gap':x.base_gap,'market_breadth':x.breadth,
                               'note':'形态候选；非当前可成交报价；成本差为过去20日价格中位代理，不是真实会员成本'})
    complete=len(frames)/max(len(universe),1)>=.95 and not limit
    for r in results:
        if not complete:r['status']='数据覆盖不足，仅局部研究'
    for row in candidates:
        row['research_qualified']=any(r['rule']==row['rule'] and r['status']=='可列入前瞻模拟候选' for r in results)
    pd.concat(all_events,ignore_index=True).to_csv(out/'leader_signal_samples.csv.gz',index=False,compression='gzip')
    pd.DataFrame(candidates).to_csv(out/'leader_current_candidates.csv',index=False,encoding='utf-8-sig')
    result={'version':'leader-stage-v1','asof':str(latest.date()),'split':str(split.date()),'complete_universe':complete,
            'source_platform':'youpin','volume_basis':'all-platform proxy','systems':results,'current_candidates':candidates,
            'entry':'次日实际日K收盘价代理','exit':'入场后7/14/30自然日收盘价代理','fee':.025,'slippage_each_side':.005,
            'minimum_history':300,'notes':['固定8个方案×3个持有期；不根据留出段最高收益自动改线上规则',
            '最近90日留出验证；另外展示三个90日窗口，结果不是永久独立测试',
            '每规则每商品不重叠；跨商品仍相关，不是账户回测或独立样本',
            'T1为当日可评估池中未来7日净收益前30且为正；T0为其后7日净收益也前30且为正，仅用于事后标签',
            '会员阶段是量价假设；无真实会员层级及成交记录，不能识别会员身份或真实成本',
            '成本差采用过去20日价格中位代理；首次回踩只是滚动窗口代理，未确认完整生命周期首次',
            '固定白名单有存活及筛选偏差；板块采用同武器类别相对排名，不冒充已验证的板块指数',
            '未加入求购及Whale历史过滤；未模拟实际成交、资金、平台锁定或账户最大回撤']}
    (out/'leader_research.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,default=int))
    fmt=lambda x:'—' if x is None else f'{x:+.2%}'
    lines=['# 龙头与会员传导阶段 · 多方案研究','',
           f'截至{latest.date()}；成功取数{len(frames)}/{len(universe)}件；历史{raw.date.min().date()}至{raw.date.max().date()}；留出起点{split.date()}。',
           '价格：悠悠日K；成交量：全平台代理。两者口径分别保留。','',
           '| 方案 | 持有天数 | 训练n | 训练净中位 | 验证n | 验证净胜率 | 验证净中位 | 验证P10 | 结论 |',
           '|---|---:|---:|---:|---:|---:|---:|---:|---|']
    for r in results:
        t,v=r['training'],r['validation']
        lines.append(f'| {r["rule"]} | {r["H"]} | {t["n"]} | {fmt(t["median"])} | {v["n"]} | {fmt(v["win"])} | {fmt(v["median"])} | {fmt(v["p10"])} | {r["status"]} |')
    lines+=['','## 系统候选与使用边界',
            '- 只有训练、最近验证均净中位为正，且三个窗口至少两个达标，才列为前瞻模拟候选；每段至少30笔、10件、20个信号日。',
            '- 即使达标也只进入模拟观察；不把最大历史收益称为最优，不自动改现有买点。',
            '- B0基准与新增方案都要求真实量窗口可用；其统计范围与前次纯价格回测不同，不直接相减认定改进。',
            *['- '+x for x in result['notes']],'','## 当日形态候选（不等于已验证系统）','',
            '| 方案 | 商品 | 日K价 | 相对量 | 相对强度分位 | 距20日价格中位 | 系统研究通过 |','|---|---|---:|---:|---:|---:|---|']
    for x in candidates[:100]:
        lines.append(f'| {x["rule"]} | {x["cn"].replace("|","/")} | {x["close"]:.2f} | {x["relative_volume"]:.2f} | {x["rs_percentile"]:.1%} | {x["base_price_gap"]:+.1%} | {x["research_qualified"]} |')
    lines+=['',f'完整候选{len(candidates)}行见leader_current_candidates.csv；完整样本见leader_signal_samples.csv.gz。',
            '## 数据缺口',*['- '+x['name']+'：'+x['error'] for x in failed], '']
    md='\n'.join(lines)
    (out/'leader_research.md').write_text(md,encoding='utf-8')
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'],'a',encoding='utf-8') as f:f.write(md)
    print('RESEARCH_COMPLETE',json.dumps({'systems':len(results),'passed':sum(r['status']=='可列入前瞻模拟候选' for r in results),'candidates':len(candidates),'complete_universe':complete},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
