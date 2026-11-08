import pandas as pd
import numpy as np
from tools.research_adaptive_rank import enrich,training_mask


def example():
 return pd.DataFrame(dict(name=['AK-47 | A','AK-47 | B','USP-S | A','AK-47 | A'],cat=['gun_FN']*4,date=pd.to_datetime(['2026-05-01']*3+['2026-05-02']),mkt_r_7=[.1]*4,mkt_r_30=[.1]*4,breadth7=[.6]*4,r_7=[.1,.2,.5,100],r_30=[.2,.3,.4,100],ma90_dev=[.1,.2,.3,100],vol_7=[.01,.02,.03,100],close=[100.,200.,100.,100.]))


def test_market_family_features_ignore_future_rows_and_labels():
 a=example();f=enrich(a);old=enrich(a.iloc[:3])
 cols=['regime','family_r7_rank','family_median7','band_r7_rank']
 pd.testing.assert_frame_equal(f.loc[:2,cols],old[cols])
 assert f.loc[0,'family_r7_rank']==.5;assert f.loc[1,'family_r7_rank']==1
 assert (f.regime==1).all()
 a['net7']=[100,-100,100,-100]
 pd.testing.assert_frame_equal(enrich(a)[cols],f[cols])


def test_training_purges_entire_future_label_and_rolling_window():
 f=pd.DataFrame(dict(date=pd.to_datetime(['2026-01-01','2026-04-15','2026-04-16','2026-04-30']),complete15=[True,True,True,True]))
 mask=training_mask(f,pd.Timestamp('2026-05-01'))
 assert mask.tolist()==[True,True,False,False]
 mask=training_mask(f,pd.Timestamp('2026-07-01'),True)
 assert mask.tolist()==[False,True,True,True]
 f.loc[1,'complete15']=False
 assert not training_mask(f,pd.Timestamp('2026-05-01')).iloc[1]
