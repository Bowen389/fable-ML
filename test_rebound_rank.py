import unittest
import pandas as pd
from rebound_rank_research import enrich,samples_before,COLS,rank_value
from bear_rebound_research import feature_frame
import test_bear_rebound
class RankChecks(unittest.TestCase):
    def test_predictors_do_not_see_future(self):
        raw=test_bear_rebound.Checks().raw();a=enrich(feature_frame(raw)[0]);cut=raw.date.iloc[130]
        raw.loc[raw.date>cut,['open','close','low','high','volume']]*=3
        b=enrich(feature_frame(raw)[0])
        pd.testing.assert_frame_equal(a.loc[a.date<=cut,COLS+['heuristic']],b.loc[b.date<=cut,COLS+['heuristic']])
        self.assertTrue(any(a.y14.fillna(0)!=b.y14.fillna(0)))
    def test_maturity_purge(self):
        d=pd.DataFrame({'date':pd.to_datetime(['2026-01-01','2026-01-16','2026-01-17']),'eligible':True,'y14':.1})
        q=samples_before(d,'2026-02-01')
        self.assertEqual(len(q),2)
        self.assertTrue((q.date+pd.Timedelta(days=15)<pd.Timestamp('2026-02-01')).all())
    def test_missing_rank_preserved(self):
        self.assertIsNone(rank_value(float("nan")))
        self.assertEqual(rank_value(3.),3)
    def test_no_identity_or_labels(self):
        self.assertFalse(set(COLS)&{'name','id','cn','winner7','y7','y14','mae14'})
if __name__=='__main__':unittest.main()
