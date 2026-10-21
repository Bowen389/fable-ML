"""Synthetic integration only; never a market result."""
import tempfile,json
from pathlib import Path
import pandas as pd,numpy as np
import rebound_shared_factors as r
root=Path(tempfile.mkdtemp(prefix='case-pipeline-'));(root/'research').mkdir()
u=[{'name':f'fixture{i}','cn':f'fixture{i}','id':str(i)} for i in range(20)]
(root/'firepulse_universe.json').write_text(json.dumps(u))
(root/'research/bear_rebound_cases.json').write_text(json.dumps({'events':[{'dates':[date],'cases':u[:8]} for date in ['2026-02-09','2026-05-27','2026-08-22']]}))
def fake(item,today):
    dates=pd.date_range('2023-01-01','2026-10-20');n=len(dates);rng=np.random.default_rng(int(item['id']))
    c=200*np.exp(np.cumsum(rng.normal(0,.035,n)));v=rng.integers(10,200,n)
    return pd.DataFrame({'date':dates,'open':c,'close':c,'high':c*1.02,'low':c*.98,'volume':v,**item,'family':'fixture'})
r.ROOT=root;r.OUT=root/'output'/'rebound_shared';r.CACHE=root/'cache';r.collect=fake
r.main()
x=json.loads((r.OUT/'validation.json').read_text())
assert x['historically_tradable_validation'] is False
assert x['profiles_tested']==252 and len(x['folds'])==3
assert (r.OUT/'all_profiles.csv').exists()
print('SYNTHETIC_SHARED_PIPELINE_PASS')
