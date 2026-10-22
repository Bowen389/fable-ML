import base64,io,json,tempfile,unittest,urllib.error
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
import daily_coil_scores as daily
from rebound_coil_research import coil_features,FACTORS,PROFILES
from bear_rebound_research import feature_frame
from coil_report_section import merge_coil_section,START,END
import publish_daily_coil as publisher

class DailyCoilTests(unittest.TestCase):
    def raw(self):
        parts=[]
        for i in range(9):
            rng=np.random.default_rng(i);dates=pd.date_range('2025-01-01',periods=300);c=200*np.exp(np.cumsum(rng.normal(0,.015,len(dates))))
            parts.append(pd.DataFrame({'date':dates,'name':f'item{i}','cn':f'测试 | {i}','id':str(i),'family':'test','close':c,'open':c,'high':c*1.02,'low':c*.98,'volume':rng.integers(20,80,len(dates))}))
        return pd.concat(parts,ignore_index=True)
    def snapshot(self,root,asof='2026-10-21',status='ok'):
        row={'cn':'测试 | 商品','sequence':70,'early_coil':60,'shape_state':'蓄势观察代理','coverage':1,'penalty':0,'reasons':'参与20；洗盘15'}
        p=Path(root)/'output';p.mkdir(exist_ok=True);(p/'daily_coil_candidates.json').write_text(json.dumps({'version':'daily-coil-v1','asof':asof,'status':status,'buy_validated':True,'lists':{'sequence':[row],'early_coil':[row]}}))
    def test_daily_scores_equal_full_research_factors(self):
        raw=self.raw();full=coil_features(feature_frame(raw)[0]);current,latest=daily.score_current(raw)
        a=full[full.eligible&full.date.eq(latest)].set_index('name').sort_index();b=current.set_index('name').sort_index()
        np.testing.assert_allclose(a[FACTORS].to_numpy(),b[FACTORS].to_numpy(),equal_nan=True,atol=1e-10)
        np.testing.assert_allclose(np.clip(a[FACTORS].fillna(0).to_numpy()@PROFILES['sequence']-a.penalty,0,100),b.sequence,atol=1e-10)
    def test_original_history_count_survives_lookback_trim(self):
        raw=self.raw().query("name == 'item0'").copy();raw.loc[raw.index[120:240],['close','open','high','low','volume']]=np.nan
        d=daily.daily_inputs(raw);self.assertTrue(bool(d.iloc[-1].eligible))
    def test_report_merge_is_idempotent_and_does_not_grant_buy_permission(self):
        with tempfile.TemporaryDirectory() as root:
            self.snapshot(root);a=merge_coil_section('# 原有买点\n保持原文\n',root,today='2026-10-22');b=merge_coil_section(a,root,today='2026-10-22')
            self.assertEqual(a,b);self.assertEqual(a.count(START),1);self.assertIn('保持原文',a);self.assertIn('未通过买入系统验证',a);self.assertIn('测试  /  商品',a)
    def test_stale_and_future_dates_are_not_current_signals(self):
        with tempfile.TemporaryDirectory() as root:
            self.snapshot(root,asof='2026-10-20');a=merge_coil_section('',root,today='2026-10-22');self.assertIn('旧日期观察名单',a)
            self.snapshot(root,asof='2026-10-22');b=merge_coil_section('',root,today='2026-10-22');self.assertIn('日期异常',b);self.assertNotIn('测试',b)
    def test_failure_replaces_old_candidates_and_raises(self):
        with tempfile.TemporaryDirectory() as root:
            self.snapshot(root)
            with patch.object(daily,'ROOT',Path(root)):
                with self.assertRaises(FileNotFoundError):daily.main()
            x=json.loads((Path(root)/'output/daily_coil_candidates.json').read_text());self.assertEqual(x['status'],'error');self.assertEqual(x['lists'],{})
            self.assertIn('不能解释为零候选',merge_coil_section('',root,today='2026-10-22'))
    def test_publisher_retries_using_new_remote_report_and_preserves_snapshot(self):
        with tempfile.TemporaryDirectory() as root:
            self.snapshot(root);out=Path(root)/'output';(out/'daily_coil_scores.csv').write_text('newscore');(out/'daily_coil_report.md').write_text('section');(out/'latest.md').write_text('STALE CHECKOUT')
            heads=[0];updates=[0];trees=[]
            def fake(req,timeout=45):
                path=req.full_url.split('/repos/test/repo')[1];method=req.get_method();data=json.loads(req.data) if req.data else None
                if path=='/git/ref/heads/main':heads[0]+=1;value={'object':{'sha':'h'+str(heads[0])}}
                elif path.startswith('/git/commits/h'):value={'tree':{'sha':'tree'}}
                elif path.startswith('/contents/output/latest.md?ref='):value={'encoding':'base64','content':base64.b64encode(('REMOTE '+path[-2:]).encode()).decode()}
                elif path.startswith('/contents/output/history/'):value={'sha':'existing-snapshot'}
                elif path.startswith('/contents/'):raise urllib.error.HTTPError(req.full_url,404,'missing',{},None)
                elif path=='/git/trees':trees.append(data['tree']);value={'sha':'newtree'}
                elif path=='/git/commits':value={'sha':'newcommit'}
                elif path=='/git/refs/heads/main':
                    updates[0]+=1
                    if updates[0]==1:raise urllib.error.HTTPError(req.full_url,409,'head moved',{},None)
                    value={'ok':True}
                else:raise AssertionError(path)
                return io.BytesIO(json.dumps(value).encode())
            with patch.object(publisher,'ROOT',Path(root)),patch.dict('os.environ',{'GITHUB_TOKEN':'dummy','GITHUB_REPOSITORY':'test/repo'}),patch('urllib.request.urlopen',side_effect=fake),patch('time.sleep'):
                publisher.main()
            self.assertEqual(heads[0],2)
            latest=next(x['content'] for x in trees[-1] if x['path']=='output/latest.md')
            self.assertIn('REMOTE h2',latest);self.assertNotIn('STALE CHECKOUT',latest)
            self.assertFalse(any(x['path'].startswith('output/history/') for x in trees[-1]))
    def test_daily_outputs_are_dated_and_do_not_fit_models(self):
        with tempfile.TemporaryDirectory() as root:
            raw=self.raw();day=raw.date.max()+pd.Timedelta(days=1)
            with patch('scipy.optimize.minimize',side_effect=AssertionError('No training allowed')),patch('urllib.request.urlopen',side_effect=AssertionError('No requests allowed')):
                meta=daily.write_outputs(root,raw,day,9,[])
            self.assertEqual(meta['status'],'ok');self.assertEqual(meta['new_requests'],0);self.assertEqual(meta['training_runs'],0)
            self.assertEqual(len(meta['lists']['sequence']),5);self.assertFalse(meta['buy_validated'])
if __name__=='__main__':unittest.main()
