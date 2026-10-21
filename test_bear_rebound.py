import unittest
import numpy as np
import pandas as pd
from bear_rebound_research import feature_frame,outcome,net_ratio
class Checks(unittest.TestCase):
    def raw(self):
        n=180;c=100+np.sin(np.arange(n)/9)*10
        return pd.DataFrame({'date':pd.date_range('2025-01-01',periods=n),'open':c,'close':c,'high':c*1.02,'low':c*.98,'volume':100+np.arange(n)%7,'name':'test','cn':'test','id':'1','family':'test'})
    def test_no_future_changes(self):
        raw=self.raw();a,ma=feature_frame(raw);cut=raw.date.iloc[130]
        raw.loc[raw.date>cut,['close','open','high','low','volume']]*=3
        b,mb=feature_frame(raw)
        pd.testing.assert_frame_equal(a[a.date<=cut],b[b.date<=cut])
        for k in ma:pd.testing.assert_series_equal(ma[k][a.date<=cut],mb[k][b.date<=cut])
    def test_user_fee_convention(self):
        self.assertAlmostEqual(net_ratio(1),-.01)
        self.assertAlmostEqual(net_ratio(1.1),.089)
        self.assertAlmostEqual(net_ratio(.9),-.109)
    def test_costs_and_entry_timing(self):
        g=self.raw().set_index('date');g['close']=100.;day=g.index[20]
        x=outcome(g,day,'7');self.assertAlmostEqual(x['net'],net_ratio(1));self.assertEqual(x['exit_date'],str((day+pd.Timedelta(days=8)).date()))
        g.loc[day,'close']=1000.;self.assertAlmostEqual(outcome(g,day,'7')['net'],net_ratio(1))
    def test_missing_not_zero(self):
        g=self.raw().set_index('date');day=g.index[20];g.loc[day+pd.Timedelta(days=3),'close']=np.nan
        self.assertIsNone(outcome(g,day,'7'))
    def test_minimum_holding(self):
        g=self.raw().set_index('date');g['close']=100.;day=g.index[20];g.loc[day+pd.Timedelta(days=2):,'close']=50.
        x=outcome(g,day,'trail8');self.assertEqual(x['exit_date'],str((day+pd.Timedelta(days=8)).date()))
if __name__=='__main__':unittest.main()
