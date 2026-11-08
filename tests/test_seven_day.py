import numpy as np
import pandas as pd
from tools.research_seven_day import labels,COLS,learn,predict


def panel():
 p=np.ones(25)*100;p[8]=120;p[15]=150
 return pd.DataFrame(dict(name='item',date=pd.date_range('2026-02-01',periods=25),
 raw_close=p,close=p,eligible=True,flat_14=0))


def test_seven_day_labels_use_next_day_entry_and_separate_costs():
 f,_=labels(panel())
 assert f.loc[0,'net7']>.15
 assert f.loc[0,'net_next7']>.20
 assert f.loc[0,'T0']==1
 a=panel();a.loc[1,'raw_close']=np.nan
 f,_=labels(a)
 assert pd.isna(f.loc[0,'net7']);assert f.loc[0,'T1']==0


def test_price_filter_and_no_future_columns():
 a=panel();a.loc[0,'close']=30
 f,pool=labels(a)
 assert not pool.iloc[0];assert f.loc[0,'T0']==0
 assert not any(c.startswith(('fwd','exL','net','T0','T1')) for c in COLS)


def test_exported_rule_tree_is_predictable_without_outcome_columns():
 rng=np.random.default_rng(389);x=pd.DataFrame(rng.normal(size=(1200,len(COLS))),columns=COLS)
 y=pd.Series((x.r_1>0).astype(int));m=learn(x,y)
 s=predict(m,x)
 assert len(s)==len(x);assert np.isfinite(s).all()
 assert (s[y==1]>=m['threshold']).mean()>=.85


def test_truth_top30_and_prediction_cap_ignore_future_returns():
 from tools.research_seven_day import cap_candidates
 a=pd.concat([panel().assign(name=f'item{i:02}') for i in range(40)],ignore_index=True)
 f,_=labels(a)
 assert f.loc[f.date=='2026-02-01','T1'].sum()==30
 assert f.groupby('date').T1.sum().max()<=30
 x=f[f.date=='2026-02-01'].copy()
 x['T1_score']=np.arange(40);x['T0_score']=np.arange(40);x['peer_rs7']=0
 picked=cap_candidates(x)
 assert len(picked)==30
 assert x.loc[picked.index,'name'].tolist()==[f'item{i:02}' for i in range(39,9,-1)]
 x['net7']=-x.net7;x['T1']=0;x['T0']=0
 pd.testing.assert_frame_equal(picked,cap_candidates(x))
