import unittest
import numpy as np
import pandas as pd
import test_bear_rebound
from bear_rebound_research import feature_frame
from rebound_rank_research import enrich
from rebound_stage_research import add_stages,split_before,window_summary,exact_search
class StageChecks(unittest.TestCase):
    def test_features_ignore_future(self):
        raw=test_bear_rebound.Checks().raw();a,cols=add_stages(enrich(feature_frame(raw)[0]));cut=raw.date.iloc[130]
        raw.loc[raw.date>cut,['open','close','high','low','volume']]*=3
        b,other=add_stages(enrich(feature_frame(raw)[0]))
        self.assertEqual(cols,other)
        pd.testing.assert_frame_equal(a.loc[a.date<=cut,cols],b.loc[b.date<=cut,cols])
        self.assertFalse(set(cols)&{'winner21','potential21','mae21','winner7','y7','y14','name','id','cn','family'})
    def test_purge_22_days(self):
        d=pd.DataFrame({'date':pd.to_datetime(['2025-01-01','2026-01-01','2026-01-10']),'eligible':True,'potential21':.2,'y14':.1})
        tr,cal=split_before(d,'2026-02-01')
        self.assertTrue((tr.date+pd.Timedelta(days=22)<pd.Timestamp('2025-10-04')).all())
        self.assertEqual(len(cal),1)
    def test_first_entry_and_best_are_separate(self):
        anchor=pd.Timestamp('2026-05-27')
        q=pd.DataFrame({'date':pd.date_range('2026-05-26',periods=3),'rank':[20,100,1],'close':[100.,110,130],'y7':[.1,.2,.3],'y14':[.1,.2,.3]})
        s=window_summary(q,anchor,'rank',30)
        self.assertEqual(s['first_top_date'],'2026-05-26');self.assertEqual(s['best_date'],'2026-05-28');self.assertEqual(s['days_top_k'],2)
    def test_exact_wear_only(self):
        item={'name':'Glove (Minimal Wear)','cn':'手套 (略有磨损)'}
        self.assertIsNone(exact_search({'data':[{'name':'Glove (Field-Tested)','id':'1234567890123456'}]},item))
        self.assertEqual(exact_search({'data':[{'name':item['name'],'id':'1234567890123456'}]},item),'1234567890123456')
        self.assertIsNone(exact_search({'data':[{'name':item['name'],'id':'123'}]},item))
        self.assertIsNone(exact_search({'data':[{'name':item['name'],'id':'1234567890123456'},{'name':item['name'],'id':'1234567890123457'}]},item))
if __name__=='__main__':unittest.main()
