"""Perturb future prices/volumes and verify past factors, gates and entries."""
import json
import pandas as pd
from leader_research import ROOT,features
from process_score import refresh_item,process_features
from multifactor_research import original_and_factor_features,entry_masks,PROFILES,FACTORS
from cs2.rules import load_rules

items=json.loads((ROOT/'firepulse_universe.json').read_text());today=pd.Timestamp.now(tz='Asia/Shanghai').tz_localize(None).normalize()
frames=[];used=[]
for item in items:
    try:g=refresh_item(item,today)
    except Exception:continue
    if len(g)>1000:
        item['cat']='gun_FN' if item['name'].endswith('(Factory New)') else 'gloves_MW_FT'
        frames.append(g);used.append(item)
        if len(frames)==3:break
raw=pd.concat(frames,ignore_index=True);cut=pd.Timestamp('2026-06-01')
a,_,_=original_and_factor_features(process_features(features(raw)),used)
bars=raw.copy();future=bars.date>cut
for col in ['open','close','high','low']:bars.loc[future,col]*=1.8
bars.loc[future,'volume']*=7
b,_,_=original_and_factor_features(process_features(features(bars)),used)
mask=a.date<=cut
cols=FACTORS+['score_'+p for p in PROFILES]+['market_state','market_style','market_allowed','sector_allowed','hard_risk','sector_n','sector_r3','sector_breadth','atr14','vol_ratio']
pd.testing.assert_frame_equal(a.loc[mask,cols],b.loc[mask,cols])
for eid,left in entry_masks(a,load_rules()).items():
    right=entry_masks(b,load_rules())[eid]
    pd.testing.assert_series_equal(left[mask],right[mask])
assert all(abs(sum(w)-1)<1e-12 for styles in PROFILES.values() for w in styles.values())
assert a[['score_'+p for p in PROFILES]].stack().between(0,100).all()
print('PASS: historical multifactor scores, market/sector gates and all 9 entry masks unchanged after future perturbation;',int(mask.sum()),'historical rows')
