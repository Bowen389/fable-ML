import unittest
import numpy as np
import pandas as pd
from rebound_coil_research import coil_features,fit_weights,FACTORS
class CoilTests(unittest.TestCase):
    def frame(self):
        rows=[]
        for i in range(9):
            rng=np.random.default_rng(i);n=210;c=100*np.exp(np.cumsum(rng.normal(0,.02,n)));v=rng.integers(20,80,n)
            for j,date in enumerate(pd.date_range('2025-01-01',periods=n)):
                rows.append(dict(name=f'item{i}',family='test',date=date,eligible=True,close=c[j],low=c[j]*.98,high=c[j]*1.02,volume=v[j],r3=.01,r7=.02,m7=.01,winner7=float((i+j)%11==0)))
        return pd.DataFrame(rows)
    def test_future_quotes_do_not_change_earlier_factors(self):
        d=self.frame();a=coil_features(d);d.loc[d.date.gt('2025-06-01'),'volume']=99999;d.loc[d.date.gt('2025-06-01'),'close']=1
        b=coil_features(d);use=a.date.le('2025-06-01');pd.testing.assert_frame_equal(a.loc[use,FACTORS+['alignment','penalty']],b.loc[use,FACTORS+['alignment','penalty']])
    def test_price_and_volume_units_do_not_change_factors(self):
        d=self.frame();a=coil_features(d);d[['close','low','high']]*=10;d['volume']*=100;b=coil_features(d)
        np.testing.assert_allclose(a[FACTORS].to_numpy(float),b[FACTORS].to_numpy(float),equal_nan=True,atol=1e-10)
    def test_mature_labels_only_and_nonnegative_weights(self):
        d=coil_features(self.frame());w,a=fit_weights(d,'2025-07-15');d.loc[d.date.ge('2025-07-07'),'winner7']=1-d.loc[d.date.ge('2025-07-07'),'winner7'];other,b=fit_weights(d,'2025-07-15')
        np.testing.assert_allclose(w,other);self.assertTrue((w>=0).all());self.assertAlmostEqual(w.sum(),100);self.assertLess(pd.Timestamp(a['train_last_label']),pd.Timestamp('2025-07-15'))
    def test_names_do_not_affect_scores(self):
        d=self.frame();a=coil_features(d);d['name']=d.name.map(lambda x:'renamed_'+x);b=coil_features(d)
        pd.testing.assert_frame_equal(a[FACTORS],b[FACTORS])
if __name__=='__main__':unittest.main()
