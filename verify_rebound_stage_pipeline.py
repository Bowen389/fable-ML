"""Synthetic end-to-end smoke test. These outputs are never market research results."""
import json
from pathlib import Path
import tempfile
import numpy as np
import pandas as pd
import rebound_stage_research as r

def main():
    root=Path(tempfile.mkdtemp(prefix='stage-pipeline-'));(root/'research').mkdir()
    u=[{'name':f'fixture{i}','cn':f'fixture{i}','id':str(i)} for i in range(16)]
    (root/'firepulse_universe.json').write_text(json.dumps(u))
    (root/'research/bear_rebound_cases.json').write_text(json.dumps({'events':[{'dates':['2026-05-27'],'cases':[u[0],{'name':'missing','cn':'missing | missing','id':None}]}]}))
    def fake(item,today):
        dates=pd.date_range('2023-01-01','2026-10-20');n=len(dates);rng=np.random.default_rng(int(item['id']))
        c=100*np.exp(np.cumsum(rng.normal(0,.025,n)));v=rng.integers(10,200,n)
        return pd.DataFrame({'date':dates,'open':c,'close':c,'high':c*1.02,'low':c*.98,'volume':v,**item,'family':'fixture'})
    r.ROOT=root;r.OUT=root/'output'/'rebound_stage';r.CACHE=root/'cache';r.collect=fake
    r.request=lambda *args,**kwargs:{'data':[]}
    r.main()
    result=json.loads((r.OUT/'validation.json').read_text());rows=pd.read_csv(r.OUT/'case_windows.csv')
    assert len(result['folds'])==4 and result['fee_sell']==.01
    assert rows[rows.name=='missing'].best_rank.isna().all()
    assert len(pd.read_csv(r.OUT/'case_daily.csv'))==2*15*4
    assert (r.OUT/'current_candidates.csv').exists()
    print('SYNTHETIC_PIPELINE_PASS',{'folds':len(result['folds']),'summaries':len(result['summaries']),'case_windows':len(rows)})
if __name__=='__main__':main()
