import unittest
import pandas as pd
from rebound_group_review import group_name,group_ranks
class GroupChecks(unittest.TestCase):
    def test_group_assignment_does_not_boost_scores(self):
        d=pd.DataFrame({'date':pd.Timestamp('2026-02-09'),'name':['a','b','c','d'],'raw':[.1,.2,.8,.9],'y7':0.,'y14':0.})
        q=group_ranks(d,{'a','b'},min_items=2)
        self.assertAlmostEqual(float(q[q['group'].eq('一代手套_略磨')].median_score.iloc[0]),.15)
        self.assertEqual(int(q[q['group'].eq('一代手套_略磨')]['rank'].iloc[0]),2)
        self.assertEqual(group_name('★ Sport Gloves | other (Minimal Wear)',{'a'}),'其他手套_略磨')
if __name__=='__main__':unittest.main()
