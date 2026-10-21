import unittest
import numpy as np
import pandas as pd
from rebound_historical_memory import prototypes_before
class MemoryChecks(unittest.TestCase):
    def data(self):
        dates=pd.date_range('2024-01-01',periods=365);p=np.arange(len(dates))%5==0
        return pd.concat([pd.DataFrame({'name':f'item{i}','date':dates,'eligible':True,'winner21':p.astype(float),'potential21':np.where(p,.3,.02),'y14':np.where(p,.15,-.1),'y7':np.where(p,.05,-.05),'r7':.01}) for i in range(8)],ignore_index=True)
    def test_prototypes_purged_and_future_independent(self):
        d=self.data();start=pd.Timestamp('2025-01-01');a=prototypes_before(d,start)
        self.assertTrue((a.date+pd.Timedelta(days=22)<start).all())
        d.loc[d.date+pd.Timedelta(days=22)>=start,['winner21','potential21','y14','y7']]=1000
        b=prototypes_before(d,start);pd.testing.assert_frame_equal(a,b)
    def test_nonoverlapping_positive_prototypes(self):
        q=prototypes_before(self.data(),'2025-01-01');p=q[q.learning_label.eq(1)]
        for _,g in p.groupby('name'):
            self.assertTrue(g.sort_values('date').date.diff().dropna().dt.days.ge(22).all())
if __name__=='__main__':unittest.main()
