"""Monthly walk-forward experiments and daily observation rankings; never trade/notify."""
import sys,os,json,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np,pandas as pd
from lightgbm import LGBMRanker
from cs2 import config,data,features
from cs2.leaders import add_peer_features
from cs2.research_universe import EXCLUDED_WEAPONS
from tools.research_dragon_ranking import audited_panel,evaluate
from tools.research_seven_day import COLS

MARKET=['regime','mkt_r_7','mkt_r_30','breadth7','above_ma30','mkt_vol_14']
FAMILY=['family_code','family_r7_rank','family_r30_rank','family_ma90_rank','family_vol_rank','family_median7','family_breadth7','price_band','band_r7_rank']


def enrich(f):
 out=f.copy()
 market=out[['date','mkt_r_7','mkt_r_30','breadth7']].drop_duplicates('date')
 market['regime']=np.select([(market.mkt_r_30>0)&(market.breadth7>=.55),(market.mkt_r_30<0)&(market.breadth7<=.45)],[1,-1],default=0)
 out['regime']=out.date.map(market.set_index('date').regime)
 weapon=out.name.astype(str).str.split(' | ',n=1,regex=False).str[0]
 families={'AK-47':1,'M4A4':2,'M4A1-S':2,'AWP':3,'SSG 08':3,'G3SG1':3,'SCAR-20':3,'USP-S':4,'Glock-18':4,'P2000':4,'P250':4,'Desert Eagle':4,'Five-SeveN':4,'Tec-9':4,'CZ75-Auto':4,'Dual Berettas':4,'MAC-10':5,'MP9':5,'MP7':5,'MP5-SD':5,'UMP-45':5,'P90':5,'PP-Bizon':5,'AUG':2,'SG 553':2,'FAMAS':2,'Galil AR':2}
 out['family_code']=weapon.map(families).fillna(7).astype(int)
 out.loc[out.cat.astype(str)=='gloves_MW_FT','family_code']=6
 key=[out.date,out.family_code]
 for col,dest in [('r_7','family_r7_rank'),('r_30','family_r30_rank'),('ma90_dev','family_ma90_rank'),('vol_7','family_vol_rank')]:out[dest]=out[col].groupby(key).rank(pct=True)
 out['family_median7']=out.r_7.groupby(key).transform('median')
 out['family_breadth7']=(out.r_7>0).groupby(key).transform('mean')
 out['price_band']=pd.cut(out.close,[30,100,300,1000,3000,np.inf],labels=False,right=False).astype(float)
 out['band_r7_rank']=out.r_7.groupby([out.date,out.family_code,out.price_band]).rank(pct=True)
 return out


def training_mask(f,cutoff,rolling=False):
 mask=f.complete15&(f.date+pd.Timedelta(days=15)<cutoff)
 if rolling:mask &= f.date>=cutoff-pd.Timedelta(days=135)
 return mask


def fit_rank(f,target,cols):
 a=f.sort_values(['date','name']);med=a[cols].astype(float).median().fillna(0)
 y=np.select([(a[target]==1)&(a.truth_rank<=5),(a[target]==1)&(a.truth_rank<=10),a[target]==1],[3,2,1],default=0)
 if len(a)<1000 or np.count_nonzero(y)<30:return None
 model=LGBMRanker(objective='lambdarank',n_estimators=100,num_leaves=15,max_depth=4,min_child_samples=150,learning_rate=.04,lambdarank_truncation_level=30,random_state=389,n_jobs=2,verbosity=-1)
 model.fit(a[cols].astype(float).fillna(med),y,group=a.groupby('date',sort=False).size().to_numpy())
 return model,cols,med


def infer(bundle,a):
 model,cols,med=bundle
 return model.predict(a[cols].astype(float).fillna(med))


def load_panel(cache):
 if cache:raw=pd.read_pickle(cache)
 else:
  bars=data.usable_bars(data.load_bars(),data.load_universe())
  raw,_=features.build_features(features.clean_bars(bars))
 return enrich(audited_panel(add_peer_features(raw))),raw.date.max()


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--cache');args=parser.parse_args()
 f,end=load_panel(args.cache)
 print('PANEL',len(f),end,flush=True)
 variants={'固定基础':(COLS,False,False),'固定行情分层':(COLS+MARKET,False,True),'固定品类特征':(COLS+FAMILY,False,False),'滚动基础':(COLS,True,False),'滚动综合':(COLS+MARKET+FAMILY,True,True)}
 cutoff0=pd.Timestamp('2026-05-01');done=f.date<=end-pd.Timedelta(days=15)
 rows=[];audit=[];latest={};predictions={}
 for target in ['T1','T0']:
  for variant,(cols,rolling,experts) in variants.items():
   score=pd.Series(np.nan,index=f.index);fixed=None
   months=pd.date_range(cutoff0,end.to_period('M').start_time,freq='MS')
   for cutoff in months:
    dest=(f.date>=cutoff)&(f.date<cutoff+pd.offsets.MonthBegin())
    if not dest.any():continue
    if rolling or fixed is None:
     source=f[training_mask(f,cutoff if rolling else cutoff0,rolling)]
     pooled=fit_rank(source,target,cols)
     if pooled is None:raise ValueError('Insufficient rank training data')
     bundles={'pooled':pooled}
     if experts:
      for regime in [-1,0,1]:
       b=fit_rank(source[source.regime==regime],target,cols)
       if b is not None:bundles[str(regime)]=b
     fixed=bundles
     audit.append(dict(target=target,variant=variant,cutoff=str(cutoff.date()),last_training_signal=str(source.date.max().date()),last_training_label=str((source.date.max()+pd.Timedelta(days=15)).date()),samples=len(source),experts=list(bundles)))
    z=f[dest];s=infer(fixed['pooled'],z)
    if experts:
     for regime in [-1,0,1]:
      take=z.regime.to_numpy()==regime
      if str(regime) in fixed and take.any():s[take]=infer(fixed[str(regime)],z[take])
    score.loc[z.index]=s
    if variant=='滚动综合' and cutoff==months[-1]:latest[target]=fixed
   predictions[(target,variant)]=score
   for stage,mask in [('5—6月',done&f.date.between('2026-05-01','2026-06-30')),('7月以后',done&(f.date>='2026-07-01'))]:
    a=f[mask&score.notna()]
    for k in [5,10,30]:rows.append(dict(stage=stage,method=variant,target=target,k=k,**evaluate(a,score.loc[a.index],k)))
   print('DONE',target,variant,flush=True)
 rng=np.random.default_rng(389)
 for stage,mask in [('5—6月',done&f.date.between('2026-05-01','2026-06-30')),('7月以后',done&(f.date>='2026-07-01'))]:
  a=f[mask]
  for name,s in [('近7日涨幅',a.r_7),('随机固定种子',rng.random(len(a)))]:
   for k in [5,10,30]:rows.append(dict(stage=stage,method=name,target='基准',k=k,**evaluate(a,s,k)))
 # Live forecast uses only the current month's models and signal-day features.
 z=f[f.date==end].copy();z['score']=predictions[('T1','滚动综合')].loc[z.index];z['T0_score']=predictions[('T0','滚动综合')].loc[z.index]
 z['T0_percentile']=z.T0_score.rank(pct=True);z['_name']=z.name.astype(str)
 z=z.sort_values(['score','_name'],ascending=[False,True]).head(30)
 stale=end<config.TODAY-pd.Timedelta(days=1)
 lines=['# 自适应龙头排名 · 每日研究报告','',f'行情日期：{end.date()}；生成日期：{config.TODAY.date()}；数据状态：{"陈旧，仅历史观察" if stale else "可用"}。',
 '状态：research_only；自动买点放行数：0。每日滚动综合T1排序最多30个，T0评分只作为同一名单附加信息，不另加30个。',
 '排除全部霰弹枪、Negev、M249、R8；价格>30元。报价清洗及未来两段标签使用审计口径。vol_7是价格波动率。',
 '行情：近30日市场上涨且7日上涨广度≥55%为上涨；近30日下跌且广度≤45%为下跌；其余震荡。只使用信号日信息。每个阶段有独立训练模型，样本不足回退整体模型。',
 '品类：AK、其他步枪、狙击枪、手枪、冲锋枪、手套、其他；加入品类内强度排名及价格带相对强度。全市场真实Top30标签保持不变。',
 '滚动：每月月初重训，回看135个日历日，最后15天样本不进入训练；T1/T0分开预测。固定对照均用5月1日前到期样本。未根据后段成绩挑参数或挑当天最佳模型。',
 '历史日期已被查看，本报告是时序回放，非从未查看的独立测试。收益是日K报价模拟，不能保证成交；重复持仓不构成组合回测。', '', '## 最新观察Top30','', '| 排名 | 单品 | 价格 | 行情 | T0评分百分位 |','|---:|---|---:|---|---:|']
 for rank,(_,a) in enumerate(z.iterrows(),1):
  name=str(a['name']).replace('|',r'\|');regime={-1:'下跌',0:'震荡',1:'上涨'}[int(a.regime)]
  lines.append(f'| {rank} | {name} | {a.close:.2f} | {regime} | {a.T0_percentile:.1%} |')
 lines+=['','## 对照回放','', '| 时段 | 模型目标 | 方法 | 每日上限 | T1覆盖率 | T0覆盖率 | T1命中率 | 净收益中位数 | 平均净收益 | 盈利比例 | 可核验/入选 |','|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
 for r in rows:lines.append(f'| {r["stage"]} | {r["target"]} | {r["method"]} | {r["k"]} | {r["T1_recall"]:.1%} | {r["T0_recall"]:.1%} | {r["precision"]:.1%} | {r["median"]:+.1%} | {r["mean"]:+.1%} | {r["win"]:.1%} | {r["verifiable"]}/{r["selected"]} |')
 lines+=['','## 行情分层检查：滚动综合T1 Top30','', '| 行情 | 样本 | T1覆盖率 | 净收益中位数 | 盈利比例 |','|---|---:|---:|---:|---:|']
 score=predictions[('T1','滚动综合')]
 for regime,name in [(-1,'下跌'),(0,'震荡'),(1,'上涨')]:
  a=f[done&(f.date>='2026-05-01')&(f.regime==regime)&score.notna()]
  if len(a):
   r=evaluate(a,score.loc[a.index],30);lines.append(f'| {name} | {len(a)} | {r["T1_recall"]:.1%} | {r["median"]:+.1%} | {r["win"]:.1%} |')
 lines+=['','## 训练时间审计','', '| 目标 | 方法 | 预测月起点 | 训练最后信号日 | 训练最后标签日 | 样本 |','|---|---|---|---|---|---:|']
 for a in audit:
  assert pd.Timestamp(a['last_training_label'])<pd.Timestamp(a['cutoff'])
  lines.append(f'| {a["target"]} | {a["variant"]} | {a["cutoff"]} | {a["last_training_signal"]} | {a["last_training_label"]} | {a["samples"]} |')
 root=Path(config.P('state','adaptive_rank'));root.mkdir(exist_ok=True)
 meta=dict(status='research_only',archive_end=str(end.date()),stale=bool(stale),excluded_weapons=sorted(EXCLUDED_WEAPONS),train_audit=audit,results=rows,models={})
 for target,bundles in latest.items():
  meta['models'][target]={}
  for key,(model,cols,med) in bundles.items():
   filename=f'{target}_{key}.txt';model.booster_.save_model(str(root/filename));meta['models'][target][key]=dict(file=filename,features=cols,medians=med.to_dict())
 (root/'meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
 report='\n'.join(lines)+'\n'
 Path(config.P('output','adaptive_rank_latest.md')).write_text(report)
 Path(config.P('output','history',f'adaptive_rank_{end.date()}.md')).write_text(report)
 safe=z[['name','close','regime','score','T0_percentile']].copy();safe['name']=safe.name.astype(str)
 Path(config.P('output','adaptive_rank_latest.json')).write_text(safe.to_json(orient='records',force_ascii=False,indent=2))
 if os.environ.get('GITHUB_STEP_SUMMARY'):Path(os.environ['GITHUB_STEP_SUMMARY']).write_text(report)
 print('SAVED',len(z),json.dumps([r for r in rows if r['stage']=='7月以后' and r['k']==30],ensure_ascii=False),flush=True)

if __name__=='__main__':main()
