"""Check that changing future prices cannot change past process features or scores."""
import json
import pandas as pd
import numpy as np
from process_score import refresh_item,features,process_features,evidence_score
from leader_research import ROOT

items=json.loads((ROOT/'firepulse_universe.json').read_text())
today=pd.Timestamp.now(tz='Asia/Shanghai').tz_localize(None).normalize()
frames=[]
for item in items:
    try:g=refresh_item(item,today)
    except Exception:continue
    if len(g)>1000:
        frames.append(g)
        if len(frames)==3:break
raw=pd.concat(frames,ignore_index=True);cut=pd.Timestamp('2026-06-01')
a=process_features(features(raw));perturbed=raw.copy();future=perturbed.date>cut
for c in ['open','close','high','low']:perturbed.loc[future,c]*=1.8
perturbed.loc[future,'volume']*=7
b=process_features(features(perturbed))
cols=['early_range40','early_drift40','second_wave_return','second_wave_volume','wash_drawdown','wash_volume_ratio',
      'volume_cv7','volume_max_share7','volume_rising_days7','volume_acceleration','early_cost_gap','price_efficiency7','support_recovery',
      'r1','r3','r7','r14','r20','rv','base_gap','rs7','rs_rank','family_rank','breadth','mkt7','up_close']
mask=a.date<=cut
pd.testing.assert_frame_equal(a.loc[mask,cols],b.loc[mask,cols])
pd.testing.assert_frame_equal(evidence_score(a).loc[mask],evidence_score(b).loc[mask])
assert a.loc[(a.date>cut-pd.Timedelta(days=31))&(a.date<=cut),'big_rise_label'].notna().any()
print('PASS: future price/volume perturbation leaves historical predictors and scores unchanged;',int(mask.sum()),'rows,',len(cols),'features')
