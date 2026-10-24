"""Audited retrospective leaders, causal daily ranking and fixed temporal evaluation."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np,pandas as pd
from lightgbm import LGBMRanker
from cs2 import config
from cs2.leaders import add_peer_features
from cs2.research_universe import EXCLUDED_WEAPONS,allowed_products
from tools.research_seven_day import labels,COLS


def audited_panel(f):
 f=f.sort_values(['name','date']).copy()
 g=f.groupby('name',observed=True,sort=False)
 # Entry, exit and every intervening daily quote must exist; never forward fill outcomes.
 f['complete7']=pd.concat([g.raw_close.shift(-k).notna() for k in range(1,9)],axis=1).all(axis=1)
 f['complete15']=pd.concat([g.raw_close.shift(-k).notna() for k in range(1,16)],axis=1).all(axis=1)
 f['past_complete7']=pd.concat([g.raw_close.shift(k).notna() for k in range(7)],axis=1).all(axis=1)
 f['jump_future15']=pd.concat([g.r_1.shift(-k).abs()>.5 for k in range(1,16)],axis=1).any(axis=1)
 for lag in [1,3,7,14]:
  for c in ['r_1','r_7','r_30','ma90_dev','dd_60','up_14','vol_7','peer_rs7','peer_breadth1']:
   f[f'{c}_lag{lag}']=g[c].shift(lag)
 f,pool=labels(f)
 f=f[pool&f.past_complete7&(f.date>=pd.Timestamp('2026-02-01'))].copy()
 # Re-rank in the audited universe; missing future quotes do not create winners.
 f['truth_rank']=np.nan
 z=f[f.complete7].assign(_name=lambda a:a.name.astype(str)).sort_values(['date','net7','_name'],ascending=[True,False,True])
 f.loc[z.index,'truth_rank']=z.groupby('date').cumcount()+1
 f['T1']=((f.truth_rank<=30)&(f.net7>0)).astype(int)
 f['T0']=((f.T1==1)&f.complete15&(f.net_next7>=.05)).astype(int)
 return f


def evaluate(a,score,k):
 z=a.assign(_score=score,_name=a.name.astype(str)).sort_values(['date','_score','_name'],ascending=[True,False,True]).groupby('date').head(k)
 valid=z[z.complete7];n=int(a.T1.sum());n0=int(a.T0.sum())
 return dict(selected=len(z),verifiable=len(valid),T1_recall=float(valid.T1.sum()/n) if n else 0,T0_recall=float(valid.T0.sum()/n0) if n0 else 0,precision=float(valid.T1.mean()),median=float(valid.net7.median()),mean=float(valid.net7.mean()),win=float((valid.net7>0).mean()))


def main():
 raw=add_peer_features(pd.read_pickle('/tmp/fable-recheck/features.pkl'))
 f=audited_panel(raw)
 end=raw.date.max();mature=f.date<=end-pd.Timedelta(days=15)
 train=mature&f.complete15&(f.date+pd.Timedelta(days=15)<pd.Timestamp('2026-05-01'))
 a=f[train].sort_values(['date','name']).copy();med=a[COLS].astype(float).median().fillna(0)
 scores={};models={}
 for target in ['T1','T0']:
  relevance=np.select([(a[target]==1)&(a.truth_rank<=5),(a[target]==1)&(a.truth_rank<=10),a[target]==1],[3,2,1],default=0)
  model=LGBMRanker(objective='lambdarank',n_estimators=120,num_leaves=15,max_depth=4,min_child_samples=100,learning_rate=.04,lambdarank_truncation_level=30,random_state=389,n_jobs=2,verbosity=-1)
  model.fit(a[COLS].astype(float).fillna(med),relevance,group=a.groupby('date',sort=False).size().to_numpy())
  scores[target]=model.predict(f[COLS].astype(float).fillna(med));f[f'{target}_rank_score']=scores[target]
  model.booster_.save_model(config.P('state',f'dragon_rank_{target}.txt'));models[target]=model
 lines=['# 真实龙头与每日排序：审计研究','',f'归档截止：{end.date()}。信号t，t+1入场、t+8退出；第二段t+8至t+15。价格>30元，两段独立扣手续费及滑点。',
 'T1：每日已取得完整8日真实报价的合格单品，第一段净收益前30且盈利；T0：T1且完整15日报价、第二段净收益≥5%。同分按名称。未来报价仅用于标签和评估。',
 '候选当时只要求既有报价资格和过去7日连续真实报价；不会用未来缺报价淘汰候选。评估同时披露可验证数，不能把未知结果算作成功。',
 '原始清洗已检查OHLC一致性、非正价格及相对过去15日报价中位数超过3倍/低于1/3的异常。未来单日绝对变化>50%只标注待核实，不直接删除真实暴涨。另做剔除后的敏感性；仅有日K，无法证实成交量、库存或可成交价格。vol_7是价格波动率，不是成交量。',
 '训练只使用2—4月、15日标签在5月1日前到期的完整样本。固定参数，不据后段调参。由于此前已经查看指定日期，后段不是完全独立测试。T1和T0模型各自最多输出30个，互为对照，不能合并成60个买点。', '', '排除武器：Nova、XM1014、MAG-7、Sawed-Off（全部霰弹枪），Negev、M249、R8 Revolver。按武器名前缀过滤，包含StatTrak/Souvenir变体。排除发生在标签排名和训练之前；一般市场指标仍来自原全市场历史数据。','', '## 样本审计','']
 lines += [f'- 因果候选样本：{len(f):,}；完整首段报价：{int(f.complete7.sum()):,}；完整两段报价：{int(f.complete15.sum()):,}。',f'- 完整到期区间真实T1：{int(f.loc[mature,"T1"].sum()):,}；真实T0：{int(f.loc[mature,"T0"].sum()):,}；T1中未来大跳价待核实：{int((mature&(f.T1==1)&f.jump_future15).sum())}。','', '## 固定时间划分对照','', '| 时段 | 方法 | 每日上限 | 真实T1覆盖 | 真实T0覆盖 | T1命中率 | 可验证/入选 | 7日净收益中位数 | 平均净收益 | 盈利比例 |','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
 result=[]
 rng=np.random.default_rng(389)
 for stage,mask in [('训练',train),('5—6月',mature&(f.date>='2026-05-01')&(f.date+pd.Timedelta(days=15)<pd.Timestamp('2026-07-01'))),('7月以后',mature&(f.date>='2026-07-01'))]:
  z=f[mask];methods={'T1排序':z.T1_rank_score,'T0排序':z.T0_rank_score,'近7日涨幅':z.r_7,'随机固定种子':rng.random(len(z))}
  for name,score in methods.items():
   for k in [5,10,30]:
    r=evaluate(z,score,k);result.append(dict(stage=stage,method=name,k=k,**r))
    lines.append(f'| {stage} | {name} | {k} | {r["T1_recall"]:.1%} | {r["T0_recall"]:.1%} | {r["precision"]:.1%} | {r["verifiable"]}/{r["selected"]} | {r["median"]:+.1%} | {r["mean"]:+.1%} | {r["win"]:.1%} |')
 lines+=['','## 同一天普通单品与龙头：启动前特征','', '以每天候选池特征中位数为参照；表内是样本特征减去同日中位数后的中位数，减少行情阶段差异。仅展示已完整到期样本；这是相关性，不是因果或独立验证。','', '| 距信号日 | 特征 | 普通单品偏离 | T1偏离 | T0偏离 |','|---|---|---:|---:|---:|']
 for lag in [0,1,3,7,14]:
  for base in ['r_1','r_7','r_30','ma90_dev','dd_60','up_14','vol_7','peer_rs7','peer_breadth1']:
   c=base if lag==0 else f'{base}_lag{lag}';v=f[c]-f.groupby('date')[c].transform('median');z=f[mature&f.complete15]
   vals=[v.loc[z.index[z.T1==0]].median(),v.loc[z.index[z.T1==1]].median(),v.loc[z.index[z.T0==1]].median()]
   lines.append(f'| {lag}日前 | {base} | {vals[0]:+.4f} | {vals[1]:+.4f} | {vals[2]:+.4f} |')
 lines+=['','## T1排序特征重要性','', '训练分裂增益仅反映模型使用程度，不等于稳定预测能力。','', '| 特征 | 增益 |','|---|---:|']
 importance=pd.Series(models['T1'].booster_.feature_importance(importance_type='gain'),index=COLS).sort_values(ascending=False)
 for c,v in importance.items():lines.append(f'| {c} | {v:.2f} |')
 lines+=['','## 未来大跳价敏感性','', '| 时段 | T1 Top30净收益中位数（剔除入选中大跳价） | 保留入选数 |','|---|---:|---:|']
 for stage,start in [('5—6月','2026-05-01'),('7月以后','2026-07-01')]:
  z=f[mature&(f.date>=start)]
  if stage=='5—6月':z=z[z.date+pd.Timedelta(days=15)<pd.Timestamp('2026-07-01')]
  pick=z.sort_values(['date','T1_rank_score'],ascending=[True,False]).groupby('date').head(30);pick=pick[~pick.jump_future15&pick.complete7]
  lines.append(f'| {stage} | {pick.net7.median():+.1%} | {len(pick)} |')
 lines+=['','## 5月24—31日指定单品','', '| 日期 | 单品 | 真实名次 | 首段净收益 | 次段净收益 | 标签 | T1预测名次 |','|---|---|---:|---:|---:|---|---:|']
 f['prediction_rank']=f.groupby('date').T1_rank_score.rank(method='first',ascending=False)
 focus=f[f.date.between('2026-05-24','2026-05-31')&f.name.astype(str).str.contains('The Coalition|USP-S \\| Neo-Noir|Glock-18 \\| Nuclear Garden')]
 for _,r in focus.sort_values(['date','name']).iterrows():
  name=str(r['name']).replace('|',r'\|');tag='T0' if r.T0 else 'T1' if r.T1 else '其他'
  lines.append(f'| {r.date.date()} | {name} | {r.truth_rank:.0f} | {r.net7:+.1%} | {r.net_next7:+.1%} | {tag} | {r.prediction_rank:.0f} |')
 lines+=['','## 最新日期预测Top30（未到期，仅预测）','',f'日期：{end.date()}。按T1模型分数降序、名称升序；不使用未来收益。','', '| 名次 | 单品 | 价格 |','|---:|---|---:|']
 latest=f[f.date==end].assign(_name=lambda z:z.name.astype(str)).sort_values(['T1_rank_score','_name'],ascending=[False,True]).head(30)
 for rank,(_,r) in enumerate(latest.iterrows(),1):
  name=str(r['name']).replace('|',r'\|')
  lines.append(f'| {rank} | {name} | {r.close:.2f} |')
 Path(config.P('output','dragon_ranking_research_2026.md')).write_text('\n'.join(lines)+'\n')
 # Complete retrospective list; all rows distinguish labels from real-time predictions.
 daily=['# 2026年2月以来逐日真实龙头','', '事后研究名单；未来收益不可当作当天买点。完整报价要求和异常标注详见排序研究报告。','']
 for day,z in f[mature&(f.T1==1)].groupby('date'):
  daily += [f'## {day.date()}','', '| 名次 | 单品 | 价格 | 首段净收益 | 次段净收益 | 等级 | 大跳价待核实 |','|---:|---|---:|---:|---:|---|---|']
  for _,r in z.sort_values('truth_rank').iterrows():
   name=str(r['name']).replace('|',r'\|');second=f'{r.net_next7:+.1%}' if r.complete15 else '报价不完整'
   daily.append(f'| {int(r.truth_rank)} | {name} | {r.close:.2f} | {r.net7:+.1%} | {second} | {"T0" if r.T0 else "T1"} | {bool(r.jump_future15)} |')
  daily.append('')
 Path(config.P('output','true_dragons_daily_2026.md')).write_text('\n'.join(daily)+'\n')
 Path(config.P('state','dragon_ranking_meta.json')).write_text(json.dumps(dict(features=COLS,medians=med.to_dict(),results=result,status='research_only',training_deadline='2026-05-01',archive_end=str(end.date()),excluded_weapons=sorted(EXCLUDED_WEAPONS)),indent=2))
 f.to_pickle('/tmp/fable-recheck/dragon-panel.pkl')
 print(json.dumps(result,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
