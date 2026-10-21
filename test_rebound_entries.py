import unittest
import numpy as np
import pandas as pd
from rebound_entry_validation import entry_masks,outcomes,make_trades
class EntryChecks(unittest.TestCase):
    def base(self):
        d=pd.DataFrame({'name':'x','cn':'x','date':pd.date_range('2026-01-01',periods=30),'close':100.,'volume':10.,'eligible':True,'rank':100.,'r7':0.,'environment_ok':True,'score':50.,'factor_coverage':1.,'known_event_window':False})
        return d
    def test_first_entry_and_unknown_quote(self):
        d=self.base();d.loc[[10,18],'rank']=1
        self.assertEqual(list(d.index[entry_masks(d)['first_entry_7d']]),[10,18])
        d.loc[8,'close']=np.nan
        self.assertEqual(list(d.index[entry_masks(d)['first_entry_7d']]),[18])
    def test_future_cannot_change_entries(self):
        d=self.base();d.loc[[10,18],'rank']=1;a=entry_masks(d)
        d.loc[20:,'close']=1000;d.loc[20:,'rank']=1;b=entry_masks(d)
        for k in a:pd.testing.assert_series_equal(a[k].iloc[:20],b[k].iloc[:20])
    def test_missing_outcome_does_not_shift_next_trade(self):
        d=self.base();d['net7']=.1;d.loc[0,'net7']=np.nan;d['rank']=1
        rows=make_trades(d,pd.Series(True,index=d.index),7,d.date.max())
        self.assertEqual([x['signal_date'] for x in rows[:2]],['2026-01-01','2026-01-10'])
        self.assertIsNone(rows[0]['net'])
    def test_cost_and_real_quote_requirement(self):
        d=self.base();n=outcomes(d,7);self.assertAlmostEqual(n.iloc[0],-.01)
        d.loc[3,'volume']=0;self.assertTrue(pd.isna(outcomes(d,7).iloc[0]))
if __name__=='__main__':unittest.main()
