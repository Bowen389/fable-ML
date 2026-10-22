"""Daily fixed coil scores from existing cache; no fetch, training, backtest or production rank change."""
import gzip,json,os
from pathlib import Path
import numpy as np
import pandas as pd
from leader_research import parse
from rebound_coil_research import coil_features,FACTORS,CN,PROFILES
from rebound_stage_research import include_registered_items,clean_json
from coil_report_section import render_coil_section,merge_coil_section
ROOT=Path(__file__).resolve().parent
VERSION='daily-coil-v1'

def daily_inputs(raw):
    # Match historical eligibility using the full observed count, then retain only causal lookback.
    cutoff=raw.date.max()-pd.Timedelta(days=200);parts=[]
    for _,p in raw.groupby('name',sort=True):
        p=p.sort_values('date').set_index('date');g=p.reindex(pd.date_range(p.index.min(),p.index.max()))
        c,v=g.close,g.volume;valid=c.notna()
        g['eligible']=(valid.cumsum()>=100)&(valid.rolling(60).sum()>=55)&c.ge(30)&v.gt(0)
        for H in (3,7,30):g['r'+str(H)]=c/c.shift(H)-1
        g['ma30']=c.rolling(30,min_periods=27).mean()
        for col in ('name','cn','id','family'):g[col]=p[col].iloc[0]
        g['date']=g.index;parts.append(g[g.date.ge(cutoff)].reset_index(drop=True))
    d=pd.concat(parts,ignore_index=True);e=d[d.eligible]
    q=e.groupby('date').agg(m3=('r3','median'),m7=('r7','median'),breadth=('close',lambda z:z.gt(d.loc[z.index,'ma30']).mean()))
    q['breadth_change3']=q.breadth-q.breadth.shift(3)
    for col in q:d[col]=d.date.map(q[col])
    return d

def score_current(raw):
    d=coil_features(daily_inputs(raw));latest=d[d.eligible].date.max()
    if pd.isna(latest):raise ValueError('No eligible completed day')
    current=d[d.eligible&d.date.eq(latest)].copy()
    for key,w in PROFILES.items():current[key]=np.clip(current[FACTORS].fillna(0).to_numpy()@w-current.penalty,0,100)
    current['shape_state']=np.select([current.activation.ge(.6)&current.wash.ge(.3)&current.build.ge(.3),current.build.ge(.5)&current.wash.ge(.25)&current.activation.lt(.6)],['蓄势后量能激活代理','蓄势观察代理'],default='局部形态，链条未完整')
    def reason(x):
        vals=[(CN[i],float(x[f])*PROFILES['sequence'][i]) for i,f in enumerate(FACTORS) if pd.notna(x[f])]
        return '；'.join(f'{k}{v:.1f}分' for k,v in sorted(vals,key=lambda z:-z[1])[:3])
    current['reasons']=current.apply(reason,axis=1);current['market_ok']=current.m3.gt(current.m7*3/7)&current.breadth_change3.ge(0)
    current['status']='观察证据分，未通过买入验证'
    for f,w in zip(FACTORS,PROFILES['sequence']):current[f+'_points']=current[f].fillna(0)*w
    return current,latest

def write_outputs(root,raw,today,requested,failures):
    root=Path(root);out=root/'output';out.mkdir(exist_ok=True)
    current,latest=score_current(raw);now=pd.Timestamp.now(tz='Asia/Shanghai').isoformat()
    expected=today-pd.Timedelta(days=1)
    cols=['date','name','cn','id','close',*PROFILES,'shape_state','coverage','alignment','penalty',*FACTORS,*[f+'_points' for f in FACTORS],'market_ok','reasons','status']
    current=current.sort_values(['sequence','name'],ascending=[False,True]);current[cols].to_csv(out/'daily_coil_scores.csv',index=False,encoding='utf-8-sig')
    record_cols=['name','cn','close',*PROFILES,'shape_state','coverage','penalty','reasons']
    lists={key:current.sort_values([key,'name'],ascending=[False,True]).head(5)[record_cols].to_dict('records') for key in ('sequence','early_coil')}
    meta={'version':VERSION,'asof':str(latest.date()),'generated_at':now,'expected_completed_date':str(expected.date()),'status':'ok' if latest==expected else 'stale','loaded':int(raw.name.nunique()),'requested':requested,'failures':failures,'daily_rows':len(current),'market_ok':bool(current.market_ok.iloc[0]),'buy_validated':False,'production_scoring_modified':False,'new_requests':0,'training_runs':0,'price_basis':'悠悠日K','volume_basis':'全平台成交量代理','lists':lists}
    (out/'daily_coil_candidates.json').write_text(json.dumps(clean_json(meta),ensure_ascii=False,indent=2,allow_nan=False))
    section=render_coil_section(root,today=str(today.date()));(out/'daily_coil_report.md').write_text(section+'\n')
    for name in ('process_score_report.md','multifactor_report.md'):
        path=out/name
        if path.exists():path.write_text(merge_coil_section(path.read_text(),root,today=str(today.date())))
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'],'a') as f:f.write('\n'+section+'\n')
    print('DAILY_COIL_COMPLETE',json.dumps({k:meta[k] for k in ('asof','status','daily_rows','loaded','requested','new_requests','training_runs')},ensure_ascii=False),flush=True)
    return meta

def main():
    out=ROOT/'output';out.mkdir(exist_ok=True)
    today=pd.Timestamp.now(tz='Asia/Shanghai').tz_localize(None).normalize()
    try:
        cases=json.loads((ROOT/'research/bear_rebound_cases.json').read_text());u=include_registered_items(json.loads((ROOT/'firepulse_universe.json').read_text()),cases)
        u=[x for x in u if x.get('id') and not x['name'].startswith(('Nova |','XM1014 |','MAG-7 |','Sawed-Off |','Negev |','M249 |','R8 Revolver |'))]
        frames=[];failures=[]
        for item in u:
            try:
                path=ROOT/'research_cache'/(str(item['id'])+'.json.gz')
                with gzip.open(path,'rt') as f:payload=json.load(f)
                g=parse(payload,today)
                if len(g)<100:raise ValueError('Less than 100 observed bars')
                for k in ('name','cn','id'):g[k]=item[k]
                g['family']=item['name'].split('|')[0].strip();frames.append(g)
            except (OSError,ValueError,KeyError) as exc:failures.append({'name':item['name'],'error':str(exc)})
        if not frames:raise ValueError('No usable local cache; no network fallback')
        write_outputs(ROOT,pd.concat(frames,ignore_index=True),today,len(u),failures)
    except Exception as exc:
        meta={'version':VERSION,'status':'error','generated_at':pd.Timestamp.now(tz='Asia/Shanghai').isoformat(),'error':type(exc).__name__+': '+str(exc),'buy_validated':False,'lists':{}}
        (out/'daily_coil_candidates.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
        (out/'daily_coil_scores.csv').write_text('name,sequence,status\n')
        (out/'daily_coil_report.md').write_text(render_coil_section(ROOT)+'\n')
        for name in ('process_score_report.md','multifactor_report.md'):
            p=out/name
            if p.exists():p.write_text(merge_coil_section(p.read_text(),ROOT))
        raise
if __name__=='__main__':main()
