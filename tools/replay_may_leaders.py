import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
from cs2.leaders import add_peer_features,leader_watch
from cs2.rules import load_rules
from cs2 import data,features,config
f,_=features.build_features(features.clean_bars(data.usable_bars(data.load_bars(),data.load_universe())))
rs=load_rules();dates=pd.date_range('2026-05-24','2026-05-31')
targets={'M4A4 | The Coalition (Factory New)':'合纵','USP-S | Neo-Noir (Factory New)':'USP次时代','Glock-18 | Nuclear Garden (Factory New)':'格洛克核子花园'}
lines=['# 5月24—31日关键单品与早期龙头检查','',
 '按当天归档报价识别；这些日期参与设计，不是独立验证。早期龙头是独立观察标签，未自动获得买入放行。',
 '早期标签：同类报价≥8、当日涨幅≥3%、当日强度前15%、3日强度前40%、7日强度前50%、站上MA7。不要求品类普涨或7日收益转正。','',
 '| 日期 | 单品（崭新） | 收盘元 | 当日涨幅 | 7日涨幅 | 同类中位涨幅 | 早期龙头观察 |', '|---|---|---:|---:|---:|---:|---|']
for day in dates:
 d=f[(f.date==day)&f.name.astype(str).isin(targets)]
 for _,a in d.iterrows():
  lines.append(f'| {day.date()} | {targets[str(a["name"])]} | {a.raw_close:.2f} | {a.r_1:+.1%} | {a.r_7:+.1%} | {a.peer_med_1:+.1%} | {"是" if a.leader_early_flag else "否"} |')
lines+=['','## 各日早期龙头观察（每品类前五，千元AK按当天1000—5000元展示）','']
for day in dates:
 d=f[(f.date==day)&(f.leader_early_flag>0)&f.peer_code.isin([1,2,3,4,5])].copy()
 d=d[(d.peer_code!=2)|d.close.between(1000,5000)]
 d=d.sort_values('leader_score',ascending=False).groupby('peer_group',sort=False).head(5)
 lines += [f'### {day.date()}','','| 单品 | 强度分 | 当日涨幅 | 7日涨幅 |','|---|---:|---:|---:|']
 for _,a in d.iterrows():
  name=str(a['name']).replace('|',r'\|')
  lines.append(f'| {name} | {a.leader_score*100:.1f} | {a.r_1:+.1%} | {a.r_7:+.1%} |')
 lines.append('')
print('\n'.join(lines[:30]))
p=Path(config.P('output','may_early_leaders_2026.md'));p.write_text('\n'.join(lines)+'\n')
