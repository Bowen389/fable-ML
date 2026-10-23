"""Runtime boundary checks: daily paths cannot call fitting/search fallbacks."""
import ast,json,os,tempfile,types,unittest
from pathlib import Path
from unittest.mock import Mock,patch

def load_function(file,name,extra=None):
    source=Path(__file__).with_name(file).read_text()
    fn=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name==name)
    ns={'json':json,'os':os,'Path':Path,'pd':types.SimpleNamespace(DataFrame=list)}
    ns.update(extra or {})
    exec(compile(ast.Module(body=[fn],type_ignores=[]),file,'exec'),ns)
    return ns[name]

class CoreDaily(unittest.TestCase):
    def test_daily_never_fits_or_upgrades_validation(self):
        forbidden=Mock(side_effect=AssertionError('Daily fitting is forbidden'))
        fn=load_function('process_score.py','daily_model_result',{'train_and_evaluate':forbidden})
        with tempfile.TemporaryDirectory() as td,patch.dict(os.environ,{'DAILY_INFERENCE_ONLY':'1'}):
            Path(td,'process_score_validation.json').write_text(json.dumps({'asof':'2026-10-22','metrics':{'buy_validated':True}}))
            model,iso,metrics,test=fn(td,None,[],None)
            self.assertIsNone(model);self.assertIsNone(iso);self.assertFalse(metrics['buy_validated'])
            self.assertEqual(metrics['training_runs'],0);self.assertEqual(metrics['validation_asof'],'2026-10-22');forbidden.assert_not_called()
    def test_full_research_remains_explicitly_available(self):
        fitting=Mock(return_value=('model','iso',{'status':'research'},[]))
        fn=load_function('process_score.py','daily_model_result',{'train_and_evaluate':fitting})
        with patch.dict(os.environ,{'DAILY_INFERENCE_ONLY':'0'}):
            self.assertEqual(fn('.',1,2,3)[0],'model');fitting.assert_called_once_with(1,2,3)
    def test_daily_multifactor_preserves_recipe_and_freezes_date(self):
        fn=load_function('multifactor_research.py','load_daily_frozen_results',{'ENTRIES':{'I0':'traditional','I1':'left'}})
        with tempfile.TemporaryDirectory() as td:
            recipe={'H':14,'profile':'等权','gate':'市场或板块修复','threshold':65}
            Path(td,'multifactor_validation.json').write_text(json.dumps({'asof':'2026-10-22','results':[{'id':'I0','recipe':recipe,'qualified':True}]}))
            rows,date=fn(td,{'I0':None,'I1':None})
            self.assertEqual(rows[0]['recipe'],recipe);self.assertFalse(rows[0]['qualified']);self.assertTrue(rows[0]['historical_qualified'])
            self.assertIsNone(rows[1]['recipe']);self.assertEqual(date,'2026-10-22')
            # Repeated daily refreshes must not move the original validation date.
            Path(td,'multifactor_validation.json').write_text(json.dumps({'asof':'2026-10-23','validation_asof':date,'results':rows}))
            self.assertEqual(fn(td,{'I0':None})[1],'2026-10-22')
    def test_missing_frozen_research_does_not_start_search(self):
        fn=load_function('multifactor_research.py','load_daily_frozen_results')
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(RuntimeError,'no automatic parameter search'):fn(td,{})
if __name__=='__main__':unittest.main()
