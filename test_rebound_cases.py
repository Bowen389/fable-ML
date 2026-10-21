import unittest
import pandas as pd
import numpy as np
from rebound_case_learning import event_samples,fit,score_rows
class CaseChecks(unittest.TestCase):
    def test_unlabelled_winners_not_negative(self):
        d=pd.DataFrame({'date':pd.to_datetime(['2026-05-27']*4),'name':['case','winner','loser','neutral'],'eligible':True,'potential21':[.3,.4,.02,.12],'y14':[.2,.3,-.1,-.01]})
        cases={'events':[{'dates':['2026-05-27'],'cases':[{'name':'case'}]}]}
        z=event_samples(d,cases).set_index('name')
        self.assertEqual(z.loc['case','learning_label'],1)
        self.assertEqual(z.loc['loser','learning_label'],0)
        self.assertTrue(pd.isna(z.loc['winner','learning_label']))
        self.assertTrue(pd.isna(z.loc['neutral','learning_label']))
    def test_name_changes_do_not_change_prediction(self):
        rng=np.random.default_rng(3);n=200
        d=pd.DataFrame({'a':rng.normal(size=n),'b':rng.normal(size=n),'date':pd.Timestamp('2026-01-01'),'name':['fixture']*n,'learning_label':[0,1]*(n//2)})
        model=fit(d,['a','b'],7);a=score_rows(model,d,['a','b'])
        d['name']=['replacement']*n;d['learning_label']=1-d.learning_label
        b=score_rows(model,d,['a','b'])
        np.testing.assert_array_equal(a.raw,b.raw)
        np.testing.assert_array_equal(a['rank'],b['rank'])
if __name__=='__main__':unittest.main()
