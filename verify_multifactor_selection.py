import numpy as np,pandas as pd
from multifactor_research import select_recipe,PROFILES,qualify
rng=np.random.default_rng(7);dates=pd.date_range('2025-10-01','2026-06-01')
d=pd.DataFrame([(f'item{i}',date) for i in range(20) for date in dates],columns=['name','date'])
d['eligible']=True;d['volume_ok']=True;d['flat_14']=0.;d['market_allowed']=True;d['sector_allowed']=True;d['hard_risk']=False
for p in PROFILES:d['score_'+p]=rng.uniform(40,90,len(d))
for H in (7,14,30):d['retH'+str(H)]=rng.normal(.02,.05,len(d))
cut=pd.Timestamp('2026-03-01');mask=pd.Series(True,index=d.index)
a,_=select_recipe(d,mask,cut)
z=d.copy()
for H in (7,14,30):z.loc[z.date+pd.Timedelta(days=H+1)>cut,'retH'+str(H)]=1000
b,_=select_recipe(z,mask,cut)
assert a is not None and a==b,(a,b)
s={'n':100,'items':30,'days':30,'mean':.1,'median':.05}
w=[dict(s) for _ in range(3)]
assert qualify(s,w,'市场修复')
assert not qualify(s,w,'不加环境对照')
assert not qualify({**s,'mean':-.01},w,'市场修复')
assert not qualify(s,[{**s,'n':0},s,s],'市场修复')
print('PASS: recipe selection uses only labels mature at its boundary; ungated, losing and insufficient-window systems cannot qualify')
