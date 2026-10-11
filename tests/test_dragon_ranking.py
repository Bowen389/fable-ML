import numpy as np
import pandas as pd
from tools.research_dragon_ranking import audited_panel,evaluate


def panel():
 a=pd.DataFrame(dict(name='one',date=pd.date_range('2026-02-01',periods=40),raw_close=np.arange(40)+100.,close=np.arange(40)+100.,eligible=True,flat_14=0))
 for c in ['r_1','r_7','r_30','ma90_dev','dd_60','up_14','vol_7','peer_rs7','peer_breadth1']:a[c]=0.
 return a


def test_missing_intermediate_quote_invalidates_label_not_past_candidate():
 a=panel();a.loc[12,'raw_close']=np.nan
 f=audited_panel(a)
 assert 8 in f.index
 assert not f.loc[8,'complete7'];assert f.loc[8,'T1']==0
 assert pd.isna(f.loc[8,'truth_rank'])


def test_large_future_jump_is_flagged_not_automatically_excluded():
 a=panel();a.loc[9,'r_1']=.6
 f=audited_panel(a)
 assert f.loc[8,'jump_future15'];assert f.loc[8,'complete15']
 assert f.loc[8,'T1']==1


def test_unverifiable_selection_is_reported():
 a=panel();f=audited_panel(a);z=f[f.date=='2026-03-10']
 r=evaluate(z,np.ones(len(z)),30)
 assert r['selected']==1;assert r['verifiable']==0


def test_exclusions_apply_before_truth_ranking_and_training():
 from cs2.research_universe import EXCLUDED_WEAPONS,allowed_products
 names=pd.Series([f'{w} | Test (Factory New)' for w in EXCLUDED_WEAPONS]+['AK-47 | Test (Factory New)','Buckshot | NSWC SEAL','StatTrak™ Nova | Test','Souvenir M249 | Test'])
 allowed=allowed_products(names)
 assert not allowed.iloc[:7].any()
 assert allowed.iloc[7:9].all()
 assert not allowed.iloc[9:].any()
 a=pd.concat([panel().assign(name='Nova | Test'),panel().assign(name='AK-47 | Test')],ignore_index=True)
 f=audited_panel(a)
 assert set(f.name)=={'AK-47 | Test'}
 assert f.loc[f.date=='2026-02-09','truth_rank'].iloc[0]==1
