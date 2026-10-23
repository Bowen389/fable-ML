import unittest
from datetime import datetime,timezone,timedelta
from decision_engine import build,regime
NOW=datetime(2026,10,22,16,tzinfo=timezone(timedelta(hours=8)))
def fixture():
    pool=[];coils=[];quotes=[]
    for i in range(60):
        n=f'AK-47 | Test{i} (Factory New)'
        pool.append(dict(name=n,eligible=True,asof='2026-10-21',r3=.01,prior_r3=-.03,r7=-.1,ma5=101,ma21=100,atr14=1,atr_pct=.01,support10=99,high20=110,families=2))
        coils.append(dict(name=n,date='2026-10-21',build=1,tier=1,wash=1,activation=1,relative=1,penalty=0,early_coil=70,sequence=80,reasons='量价证据'))
        quotes.append({'name':n,'商品':n,'实时挂牌价':100,'价格采集时间':NOW.isoformat(),'求购批次':'2026-10-21','求购厚度':10000,'求购件数':100,'求购厚度变化百分比':0})
    return {'monitor':quotes},pool,coils
class Decisions(unittest.TestCase):
    def test_bear_repair_does_not_require_positive_7_day_return(self):
        s,p,c=fixture();x=build(s,p,c,[],NOW)
        self.assertEqual(x['market']['permission'],'研究放行');self.assertEqual(x['research_ready'],60)
        self.assertFalse(x['live_buy_allowed']);self.assertFalse(x['validated']);self.assertTrue(all(not r['live_buy_allowed'] for r in x['rows']))
    def test_missing_or_stale_data_never_releases_and_preserves_pool(self):
        s,p,c=fixture();s['monitor'][0]['价格采集时间']='2026-10-20T00:00:00+08:00';s['monitor'][1]['求购批次']='2026-10-01';c[2]['date']='2026-10-22'
        x=build(s,p,c,[],NOW);self.assertEqual(len(x['rows']),60)
        self.assertTrue(all(r['state']!='研究条件满足，仅模拟试探' for r in x['rows'][:3]));self.assertIsNone(x['rows'][2]['potential'])
    def test_missing_change_not_renormalized_or_filled(self):
        s,p,c=fixture();del s['monitor'][0]['求购厚度变化百分比'];x=build(s,p,c,[],NOW)
        a,b=x['rows'][:2];self.assertEqual(a['entry_observed_max'],90);self.assertAlmostEqual(b['entry']-a['entry'],5,places=2);self.assertTrue(a['data_notes'])
    def test_unmatched_wear_and_small_market_fail_closed(self):
        s,p,c=fixture();s['monitor'][0]['name']='AK-47 | Test0 (Minimal Wear)';x=build(s,p,c,[],NOW)
        self.assertIsNone(x['rows'][0]['potential']);self.assertEqual(regime(p[:10],'2026-10-21')['permission'],'关闭')
    def test_no_followers_blocks_trial(self):
        s,p,c=fixture()
        for r in c:r['early_coil']=0
        x=build(s,p,c,[],NOW);self.assertEqual(x['research_ready'],0)
    def test_accelerating_decline_blocks(self):
        s,p,c=fixture()
        for r in p:r['r3']=-.06;r['prior_r3']=-.02
        x=build(s,p,c,[],NOW);self.assertEqual(x['market']['state'],'下跌加速');self.assertEqual(x['research_ready'],0)
if __name__=='__main__':unittest.main()


class MissingScores(unittest.TestCase):
    def test_no_scores_is_unavailable_not_zero_opportunities(self):
        from decision_engine import render
        s,p,c=fixture()
        for r in c:r['date']='2026-10-20'
        result=build(s,p,c,[],NOW)
        self.assertEqual(result['status'],'data_unavailable')
        self.assertEqual(result['data_status'],'unavailable')
        self.assertIn('不是零买点',render(result))


class PipelineGate(unittest.TestCase):
    def test_recent_quote_cannot_override_unfinished_upstream_slot(self):
        s,p,c=fixture();s['pipeline']={'ready':False,'reasons':['等待本时段报价发布']}
        x=build(s,p,c,[],NOW)
        self.assertEqual(x['research_ready'],0)
        self.assertEqual(x['market']['permission'],'数据等待，关闭新入场')
        self.assertTrue(all('上游时序未就绪' in '；'.join(r['blockers']) for r in x['rows']))
