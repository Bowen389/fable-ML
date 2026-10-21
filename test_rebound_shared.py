import unittest
import numpy as np
import pandas as pd
from rebound_shared_factors import weights_grid,rank_matrix,FACTORS
from rebound_rank_research import daily_rank
class SharedChecks(unittest.TestCase):
    def test_finite_nonnegative_grid(self):
        w=weights_grid();self.assertEqual(w.shape,(252,6));self.assertTrue((w>=0).all());np.testing.assert_allclose(w.sum(axis=1),1)
    def test_vector_ranks_match_daily_sort(self):
        rng=np.random.default_rng(5);s=pd.DataFrame(rng.random((40,6)),columns=FACTORS);s['date']=np.repeat(pd.date_range('2026-01-01',periods=2),20)
        w=weights_grid();score,rank=rank_matrix(s,w)
        for i in (0,30,251):np.testing.assert_array_equal(rank[:,i],daily_rank(s,pd.Series(score[:,i])).to_numpy())
    def test_ties_keep_exact_top_k(self):
        s=pd.DataFrame(np.ones((10,6)),columns=FACTORS);s['date']=pd.Timestamp('2026-01-01')
        _,r=rank_matrix(s,weights_grid());self.assertTrue(((r<=3).sum(axis=0)==3).all())
if __name__=='__main__':unittest.main()
