"""Learn shallow causal rule trees for 7-day profit labels. No live buys or notifications."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np,pandas as pd
from sklearn.tree import DecisionTreeClassifier
from lightgbm import LGBMClassifier
from cs2 import data,features,config
from cs2.leaders import add_peer_features
from cs2.research_universe import allowed_products,EXCLUDED_WEAPONS

COLS=['r_1','r_3','r_7','r_14','r_30','ma7_dev','ma30_dev','ma90_dev','dd_60',
 'dsl_30','up_7','up_14','pos_60','vol_ratio','vol_7','rsi_14','peer_breadth1',
 'peer_med_1','peer_med_7','peer_rank_1','peer_rank_3','peer_rank_7','peer_rs7','cat_code']


def labels(f):
 g=f.groupby('name',observed=True,sort=False).raw_close
 out=f.copy()
 out['net7']=config.net_return(g.shift(-8)/g.shift(-1)-1)
 out['net_next7']=config.net_return(g.shift(-15)/g.shift(-8)-1)
 pool=out.eligible&(out.flat_14<=.5)&(out.close>30)&allowed_products(out.name)
 ordered=out.loc[pool&out.net7.notna()].assign(_name=lambda a:a.name.astype(str)).sort_values(['date','net7','_name'],ascending=[True,False,True])
 rank=ordered.groupby('date').cumcount()+1
 out['T1']=0
 out.loc[ordered.index,'T1']=((rank<=30)&(ordered.net7>0)).astype(int)
 out['T0']=(out.T1.astype(bool)&(out.net_next7>=.05)).astype(int)
 return out,pool


def cap_candidates(f,n=30):
 """Rank with causal model scores only; outcomes never enter selection."""
 a=f.copy()
 a['potential_score']=.6*a.groupby('date').T1_score.rank(pct=True)+.4*a.groupby('date').T0_score.rank(pct=True)
 a['_name']=a.name.astype(str)
 a=a.sort_values(['date','potential_score','peer_rs7','_name'],ascending=[True,False,False,True],na_position='last')
 a['candidate_rank']=a.groupby('date').cumcount()+1
 return a.loc[a.candidate_rank<=n,['potential_score','candidate_rank']]


def learn(x,y):
 med=x.median().fillna(0);a=x.fillna(med)
 tree=DecisionTreeClassifier(max_depth=4,min_samples_leaf=300,class_weight='balanced',random_state=389)
 tree.fit(a,y);leaves=tree.apply(a)
 rates=pd.DataFrame({'leaf':leaves,'y':y.to_numpy()}).groupby('leaf').y.mean()
 score=pd.Series(leaves).map(rates).to_numpy()
 # Broad coverage: retain at least 95% of TRAIN positives; no validation tuning.
 threshold=float(np.quantile(score[y.to_numpy()==1],.05,method='lower'))
 t=tree.tree_
 model=dict(features=COLS,medians=med.to_dict(),threshold=threshold,
  nodes=[dict(left=int(t.children_left[i]),right=int(t.children_right[i]),feature=int(t.feature[i]),
              threshold=float(t.threshold[i]),rate=float(rates.get(i,0))) for i in range(t.node_count)])
 return model


def predict(model,x):
 a=x[model['features']].fillna(pd.Series(model['medians'])).to_numpy();scores=np.zeros(len(a))
 for j,row in enumerate(a):
  i=0
  while model['nodes'][i]['left']!=-1:
   n=model['nodes'][i];i=n['left'] if row[n['feature']]<=n['threshold'] else n['right']
  scores[j]=model['nodes'][i]['rate']
 return scores


def leaf_rules(m):
 rows=[]
 def walk(i,path):
  n=m['nodes'][i]
  if n['left']==-1:
   if n['rate']>=m['threshold']:rows.append((' 且 '.join(path),n['rate']))
   return
  name=m['features'][n['feature']];v=n['threshold']
  walk(n['left'],path+[f'{name}≤{v:.4f}']);walk(n['right'],path+[f'{name}>{v:.4f}'])
 walk(0,[]);return rows


def main():
 cache=Path('/tmp/fable-recheck/features.pkl')
 if cache.exists():f=add_peer_features(pd.read_pickle(cache))
 else:f,_=features.build_features(features.clean_bars(data.usable_bars(data.load_bars(),data.load_universe())))
 f,pool=labels(f);f=f[pool&(f.date>=pd.Timestamp('2026-02-01'))].copy()
 mature=f.net7.notna()&f.net_next7.notna()
 train=mature&(f.date+pd.Timedelta(days=15)<pd.Timestamp('2026-05-01'))
 stages={'训练':train,'5—6月验证':mature&(f.date>=pd.Timestamp('2026-05-01'))&(f.date+pd.Timedelta(days=15)<pd.Timestamp('2026-07-01')),
  '7月以后时序检验':mature&(f.date>=pd.Timestamp('2026-07-01'))}
 models={};lines=['# 30元以上：7日利润T1 / 连续两段7日利润T0研究','',
 '信号日t，次日收盘入场t+1，t+8退出；第二段t+8入场、t+15退出。每段均扣现有手续费和双边滑点。',
 'T1：同日30元以上合格单品中，第一段净收益同日前30且>0；T0：T1且第二段净收益≥5%。这是事后研究标签，不是当日可知的身份。',
 '仅用2—4月且15日标签在5月1日前到期的样本学习；宽候选阈值以训练T1/T0召回率至少95%设定。5—6月和7月以后不调参。此前已查看部分日期，因此后段也不能声称完全独立外测。',
 '排除全部霰弹枪（Nova、XM1014、MAG-7、Sawed-Off）、Negev、M249、R8 Revolver，再排名及训练。',
 '树深最多4、每叶至少300条样本；叶内条件取交集，各选中叶取并集。没有目标单品/日期白名单。', '',
 '| 标签 | 时段 | 样本 | 真目标 | 召回率 | 候选占比 | 候选命中率 | 候选7日中位净收益 |',
 '|---|---|---:|---:|---:|---:|---:|---:|']
 metrics=[]
 comparison=[]
 for target in ['T1','T0']:
  model=learn(f.loc[train,COLS],f.loc[train,target]);models[target]=model
  f[f'{target}_score']=predict(model,f);f[f'{target}_candidate']=f[f'{target}_score']>=model['threshold']
  for stage,mask in stages.items():
   a=f[mask];sel=a[a[f'{target}_candidate']];tp=int(sel[target].sum());n=int(a[target].sum())
   row=[target,stage,len(a),n,tp/n if n else 0,len(sel)/len(a),tp/len(sel) if len(sel) else 0,float(sel.net7.median())]
   metrics.append(row);lines.append(f'| {target} | {stage} | {len(a)} | {n} | {row[4]:.1%} | {row[5]:.1%} | {row[6]:.1%} | {row[7]:+.1%} |')
  print(target,metrics[-3:],flush=True)
  # A richer alternative uses the identical train split and causal columns.
  med=f.loc[train,COLS].astype(float).median().fillna(0)
  booster=LGBMClassifier(n_estimators=120,num_leaves=15,max_depth=4,min_child_samples=300,
                        learning_rate=.04,class_weight='balanced',random_state=389,verbosity=-1,n_jobs=2)
  booster.fit(f.loc[train,COLS].astype(float).fillna(med),f.loc[train,target])
  score=booster.predict_proba(f[COLS].astype(float).fillna(med))[:,1]
  threshold=float(np.quantile(score[train.to_numpy()&(f[target].to_numpy()==1)],.05))
  f[f'{target}_boost_score']=score;f[f'{target}_boost_candidate']=score>=threshold
  booster.booster_.save_model(config.P('state',f'seven_day_{target}_research.txt'))
  models[target+'_boost_meta']=dict(features=COLS,medians=med.to_dict(),threshold=threshold,status='research_only')
  for stage,mask in stages.items():
   a=f[mask];sel=a[a[f'{target}_boost_candidate']];n=int(a[target].sum());tp=int(sel[target].sum())
   comparison.append([target,stage,tp/n if n else 0,len(sel)/len(a),tp/len(sel) if len(sel) else 0,float(sel.net7.median())])
  print('BOOST',target,comparison[-3:],flush=True)
 lines+=['','## 相同时间划分：增强树对照（未按后段调参）','','| 标签 | 时段 | 召回率 | 候选占比 | 候选命中率 | 候选7日中位净收益 |','|---|---|---:|---:|---:|---:|']
 for t,s,rec,share,prec,net in comparison:lines.append(f'| {t} | {s} | {rec:.1%} | {share:.1%} | {prec:.1%} | {net:+.1%} |')
 # Interpretable structural comparison; informed by already inspected cases.
 f['structural_candidate']=((f.dd_60<=-.30)&(f.up_14>=.03))|((f.r_30>=0)&(f.ma90_dev>=0)&(f.up_14>=.03))
 lines+=['','## 双结构观察规则（受指定案例启发，非独立验证）','',
  '报价合格且价格>30元，并满足以下之一：①距60日高回撤≥30%，距14日低点反弹≥3%；②近30日涨幅≥0、价格不低于MA90、距14日低点反弹≥3%。不要求当日上涨或品类普涨。',
  '这是宽观察条件，不是自动买入；第二条描述中期相对强势，不能用于预先给8月22日定性。','',
  '| 目标 | 时段 | 召回率 | 候选占比 | 命中率 | 候选7日中位净收益 |','|---|---|---:|---:|---:|---:|']
 structural=[]
 for target in ['T1','T0']:
  for stage,mask in stages.items():
   a=f[mask];z=a[a.structural_candidate];tp=int(z[target].sum());n=int(a[target].sum())
   row=[target,stage,tp/n if n else 0,len(z)/len(a),tp/len(z) if len(z) else 0,float(z.net7.median())];structural.append(row)
   lines.append(f'| {target} | {stage} | {row[2]:.1%} | {row[3]:.1%} | {row[4]:.1%} | {row[5]:+.1%} |')
 print('STRUCTURAL',structural,flush=True)
 picked=cap_candidates(f)
 f['potential_score']=picked.potential_score.reindex(f.index)
 f['candidate_rank']=picked.candidate_rank.reindex(f.index)
 f['T1_proposed']=f.index.isin(picked.index)
 f['T0_proposed']=f.T1_proposed&f.T0_candidate
 assert f.groupby('date').T1_proposed.sum().max()<=30
 lines+=['','## 新设计：每日最多30个候选（非自动买点）','']
 lines+=['','候选排序：0.6×当日T1浅树评分百分位 + 0.4×当日T0浅树评分百分位；同分依次按当日peer_rs7降序、名称升序。只取前30名；T0潜力是这30名中达到T0训练阈值的子集。未来收益不参与排序，双结构仅作对照。','']
 lines+=['| 标签 | 时段 | 大涨目标覆盖率 | 候选占比 | 命中率 | 候选7日中位净收益 |','|---|---|---:|---:|---:|---:|']
 combined=[]
 for target in ['T1','T0']:
  for stage,mask in stages.items():
   a=f[mask];z=a[a[f'{target}_proposed']];tp=int(z[target].sum());n=int(a[target].sum())
   row=[target,stage,tp/n if n else 0,len(z)/len(a),tp/len(z) if len(z) else 0,float(z.net7.median())];combined.append(row)
   lines.append(f'| {target} | {stage} | {row[2]:.1%} | {row[3]:.1%} | {row[4]:.1%} | {row[5]:+.1%} |')
 print('COMBINED',combined,flush=True)
 lines+=['','## 目标单品启动前特征（中位数，全部已到期样本）','','| 特征 | 全体 | T1 | T0 |','|---|---:|---:|---:|']
 for col in COLS:
  z=f[mature];v=[float(z[col].median()),float(z.loc[z.T1==1,col].median()),float(z.loc[z.T0==1,col].median())]
  lines.append(f'| {col} | {v[0]:.4f} | {v[1]:.4f} | {v[2]:.4f} |')
 for target in ['T1','T0']:
  m=models[target]
  lines += ['',f'## {target}候选规则','',f'共同前提：报价合格、flat_14≤0.5、信号日收盘价>30元。训练评分阈值：{m["threshold"]:.4f}。','']
  for cond,rate in leaf_rules(m):lines.append(f'- {cond}；训练目标比例{rate:.1%}。')
 lines+=['','## T0第二段阈值敏感性','','| 第二段净收益下限 | 目标样本数 |','|---|---:|']
 for cut in [0,.03,.05,.10]:lines.append(f'| {cut:.0%} | {int((mature&(f.T1==1)&(f.net_next7>=cut)).sum())} |')
 lines+=['','## 重点单品事后标签与Top30覆盖','','| 日期 | 饰品 | 第一段净收益 | 第二段净收益 | 真实标签 | 当时T1候选 | 当时T0候选 |','|---|---|---:|---:|---|---|---|']
 targets=['The Coalition','USP-S | Neo-Noir','Glock-18 | Nuclear Garden']
 focus=f[f.date.between('2026-05-24','2026-05-31')&f.name.astype(str).apply(lambda n:any(k in n for k in targets))]
 for _,a in focus.iterrows():
  name=str(a['name']).replace('|',r'\|');label='T0' if a.T0 else 'T1' if a.T1 else '其他'
  lines.append(f'| {a.date.date()} | {name} | {a.net7:+.1%} | {a.net_next7:+.1%} | {label} | {bool(a.T1_proposed)} | {bool(a.T0_proposed)} |')
 lines+=['','## 每日候选与事后目标数量','','| 日期 | T1候选 | T0候选 | 已到期真实T1 | 已到期真实T0 |','|---|---:|---:|---:|---:|']
 for day,a in f.groupby('date'):
  done=a.net7.notna()&a.net_next7.notna()
  lines.append(f'| {day.date()} | {int(a.T1_proposed.sum())} | {int(a.T0_proposed.sum())} | {int(a.loc[done,"T1"].sum())} | {int(a.loc[done,"T0"].sum())} |')
 lines+=['','## 最新日期候选Top30','','| 排名 | 饰品 | 潜力评分 | T0潜力 |','|---|---|---:|---|']
 latest=f[f.date==f.date.max()]
 for _,a in latest[latest.T1_proposed].sort_values('candidate_rank').iterrows():
  name=str(a['name']).replace('|',r'\|')
  lines.append(f'| {int(a.candidate_rank)} | {name} | {a.potential_score:.4f} | {bool(a.T0_proposed)} |')
 models['meta']=dict(excluded_weapons=sorted(EXCLUDED_WEAPONS),price_min_exclusive=30,signal_to_entry_days=1,first_hold=7,second_hold=7,T1_daily_top_n=30,candidate_daily_max=30,ranking_weights=dict(T1=.6,T0=.4),ranking_tiebreak=['peer_rs7_desc','name_asc'],T0_second_net_min=.05,train_label_deadline='2026-05-01',status='research_only')
 models['structural']=dict(conds_or=[[['dd_60','<=',-.30],['up_14','>=',.03]],[['r_30','>=',0],['ma90_dev','>=',0],['up_14','>=',.03]]],status='research_only')
 Path(config.P('state','seven_day_research.json')).write_text(json.dumps(models,ensure_ascii=False,indent=2))
 Path(config.P('output','seven_day_research_2026.md')).write_text('\n'.join(lines)+'\n')
 f.to_pickle('/tmp/fable-recheck/seven-labels.pkl')
 Path('/tmp/fable-recheck/seven-metrics.json').write_text(json.dumps(metrics))
 print('DONE',len(f),int(f.T1.sum()),int(f.T0.sum()),flush=True)


if __name__=='__main__':main()
