"""Current-rule counterfactual daily replay; no deployment reconstruction or writes to signals."""
import sys,copy,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np,pandas as pd
from cs2 import data,features,rules,monitor,scan,config
from cs2.leaders import add_peer_features


def main():
    # Optional local feature cache is never committed; rule masks remain current.
    cache=Path('/tmp/fable-recheck/features.pkl')
    if cache.exists():f=add_peer_features(pd.read_pickle(cache))
    else:
        f,_=features.build_features(features.clean_bars(data.usable_bars(data.load_bars(),data.load_universe())))
    rs=rules.load_rules();masks={r['id']:rules.strategy_mask(f,r) for r in rs}
    lookup={id(v):k for k,v in masks.items()}
    orig=monitor.strategy_mask
    monitor.strategy_mask=lambda frame,r:masks[r['id']]
    class FastHealth(monitor.Health):
        def __init__(self):
            super().__init__(f);self.samples={};self.memo={}
            for r in rs:
                H=r['H'];col=f'fwdL_{H}'
                a=f.loc[masks[r['id']]&f.eligible&f[col].notna(),['date','name',col]].sort_values(['date','name']).copy()
                a['net']=config.net_return(a[col]);a['beat']=a[col]>a.date.map(self.daily_med[H])
                self.samples[r['id']]=a
        def stats(self,m,H,lo=None,hi=None):
            rid=lookup.get(id(m))
            if rid is None:return dict(n=0) # Baseline display only; never used by status decisions.
            key=(rid,H,str(lo),str(hi))
            if key in self.memo:return self.memo[key]
            z=self.samples[rid];z=z[(z.date>=lo)&(z.date<=hi)]
            keep=[];nxt={};gap=pd.Timedelta(days=H+1)
            for idx,name,dt in zip(z.index,z.name.astype(str),z.date):
                if dt<nxt.get(name,pd.Timestamp.min):continue
                keep.append(idx);nxt[name]=dt+gap
            z=z.loc[keep]
            s=dict(n=0) if z.empty else dict(n=len(z),n_days=z.date.nunique(),win=float((z.net>0).mean()),med=float(z.net.median()),beat=float(z.beat.mean()))
            self.memo[key]=s;return s
    h=FastHealth();last=f.loc[f.eligible,'date'].max();days=pd.date_range('2026-02-01',last)
    seq=copy.deepcopy(rs)
    for r in seq:r['status']='active'
    statechanges=[];positions={};daily=[];records=[];names_by_date={}
    bydate={d:g for d,g in f[f.date>=days[0]].groupby('date')}
    prices=f.set_index(['name','date']).raw_close
    def price(name,dt):
        try:return float(prices.loc[(name,dt)])
        except KeyError:return np.nan
    for day in days:
        _,changes=h.table(seq,day)
        for r in seq:
            if r['id'] in changes:
                old,new,*_=changes[r['id']];r['status']=new;statechanges.append([str(day.date()),r['id'],old,new])
        independent=copy.deepcopy(rs)
        for r in independent:r['status']='active'
        _,changes=h.table(independent,day)
        if str(day.date()) in ['2026-02-01','2026-05-26','2026-08-22']:
            check=copy.deepcopy(independent)
            monitor.strategy_mask=orig
            _,actual=monitor.Health(f).table(check,day)
            monitor.strategy_mask=lambda frame,r:masks[r['id']]
            assert {k:v[1] for k,v in changes.items()}=={k:v[1] for k,v in actual.items()}, str(day)
        for r in independent:
            if r['id'] in changes:r['status']=changes[r['id']][1]
        d=bydate.get(day,f.iloc[:0]);hits,_=scan.scan_rules(d,seq,day)
        ihits,_=scan.scan_rules(d,independent,day)
        # Settle/cancel positions with only quotes available up to this date.
        for name,p in list(positions.items()):
            if day>=p['entry'] and not p['entered']:
                if not np.isfinite(price(name,p['entry'])):del positions[name];continue
                p['entered']=True
            if day>=p['exit'] and np.isfinite(price(name,p['exit'])):del positions[name]
        fresh=[]
        if len(hits):
            ranked=hits.sort_values('同类强度分',ascending=False,kind='stable').drop_duplicates('饰品')
            for _,a in ranked.iterrows():
                name=a['饰品']
                if name in positions:continue
                H=int(a['_H']);positions[name]=dict(entry=day+pd.Timedelta(days=1),exit=day+pd.Timedelta(days=H+1),entered=False)
                fresh.append(name)
                records.append([str(day.date()),a['_rid'],name,float(a['价格']),H,float(a['同类强度分']),a['龙头候选']])
        scan_n=hits['饰品'].nunique() if len(hits) else 0;ind_n=ihits['饰品'].nunique() if len(ihits) else 0
        daily.append([str(day.date()),int(scan_n),len(fresh),int(ind_n)])
        names_by_date[str(day.date())]=fresh
        if day.day==1:print(day.date(),len(records),flush=True)
    monitor.strategy_mask=orig
    o=dict(start=str(days[0].date()),end=str(last.date()),daily=daily,signals=records,changes=statechanges)
    Path('/tmp/fable-recheck/daily-current.json').write_text(json.dumps(o,ensure_ascii=False))
    lines=['# 当前研究算法：2月以来逐日假设回放','',
      f'范围：{o["start"]}至{o["end"]}。使用归档数据和固定当前规则；不是当时实盘运行结果。',
      '连续口径：2月1日假设全部规则初始active，此后承接状态；新信号扣除同饰品持仓占用。规则实际建立较晚，前瞻恢复起点保留其真实创建日期，因此早期probation可能长期不恢复。',
      '独立口径：每天重新从active评估，对应此前“当前代码放行数”，仅作对照。它不能等同连续运行结果。',
      '早期龙头只观察，未计入买点。无真实订单，无仓位资金约束。当天信号次日真实日K收盘模拟入场，固定H天退出。', '',
      '| 日期 | 连续扫描去重放行 | 新增模拟信号 | 独立扫描去重放行 |','|---|---:|---:|---:|']
    lines += [f'| {d} | {n} | {a} | {i} |' for d,n,a,i in daily]
    lines += ['',f'新增模拟信号合计：{len(records)}条。','', '## 每日新增具体单品','']
    for dt,names in names_by_date.items():
        if not names:continue
        lines += [f'### {dt}','']+[f'- {name}' for name in names]+['']
    lines += ['## 逐笔信号参数','','| 信号日 | 规则 | 饰品 | 信号价 | H天 | 同类强度分 | 龙头候选 |','|---|---|---|---:|---:|---:|---|']
    for dt,rid,name,p,H,s,l in records:
        name=name.replace('|',r'\|');lines.append(f'| {dt} | {rid} | {name} | {p:.2f} | {H} | {s:.1f} | {l} |')
    lines += ['','## 连续状态变化','','| 日期 | 规则 | 原状态 | 新状态 |','|---|---|---|---|']+[f'| {d} | {r} | {a} | {b} |' for d,r,a,b in statechanges]
    Path(config.P('output','daily_current_replay_2026.md')).write_text('\n'.join(lines)+'\n')
    print('DONE',len(records),sum(x[1] for x in daily),sum(x[3] for x in daily),flush=True)


if __name__=='__main__':main()
