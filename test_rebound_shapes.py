import unittest
import numpy as np
import pandas as pd
import test_bear_rebound
from bear_rebound_research import feature_frame
from rebound_rank_research import enrich
from rebound_stage_research import add_stages
from rebound_shape_transfer import shape_features,coverage_objective,fit_recipe,predict
class ShapeChecks(unittest.TestCase):
    def test_price_scale_invariance(self):
        raw=test_bear_rebound.Checks().raw();a,base=add_stages(enrich(feature_frame(raw)[0]));a,sets=shape_features(a,base)
        raw[['open','close','high','low']]*=10
        b,base=add_stages(enrich(feature_frame(raw)[0]));b,_=shape_features(b,base)
        np.testing.assert_allclose(a[sets['volatility_scaled']].to_numpy(),b[sets['volatility_scaled']].to_numpy(),rtol=1e-8,atol=1e-8,equal_nan=True)
        for forbidden in ['log_price','log_volume20','is_glove','is_agent','breadth','m7']:
            self.assertNotIn(forbidden,sets['shape_only'])
            self.assertNotIn(forbidden,sets['volatility_scaled'])
    def test_minimum_event_coverage_precedes_one_good_event(self):
        def rows(rates):
            return [{'event':str(i),'top_k':30,'first_top_date':'yes' if j<k else None} for i,k in enumerate(rates) for j in range(10)]
        self.assertGreater(coverage_objective(rows([3,3,3]),.1),coverage_objective(rows([0,10,10]),.9))
    def test_template_ignores_query_labels(self):
        d=pd.DataFrame({'a':np.linspace(-2,2,100),'b':np.sin(np.arange(100)),'learning_label':[0]*50+[1]*50})
        model=fit_recipe(d,['a','b'],'shape_template');x=predict(model,d,['a','b'])
        d['learning_label']=1-d.learning_label;d['name']='irrelevant'
        np.testing.assert_array_equal(x,predict(model,d,['a','b']))
if __name__=='__main__':unittest.main()
