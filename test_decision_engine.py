import unittest
from datetime import datetime,timezone,timedelta
from decision_engine import build,regime
NOW=datetime(2026,10,22,16,tzinfo=timezone(timedelta(hours=8)))
def fixture():
    pool=[];coils=[];quotes=[]
    for i in range(60):
        n=f'AK-47 | Test{i} (Factory New)'
        pool.append(dict(name=n,eligible=True,asof='2026-10-21',price=100,r3=-.01,prior_r3=-.03,r7=-.06,ma5=101,ma21=100,atr14=1,atr_pct=.01,support10=99,high20=110,families=2))
        coils.append(dict(name=n,date='2026-10-21',build=1,tier=1,wash=1,activation=1,relative=1,penalty=0,early_coil=70,sequence=80,reasons='量价证据'))
        quotes.append({'name':n,'商品':n,'实时挂牌价':100,'价格采集时间':NOW.isoformat(),'求购批次':'2026-10-21','求购厚度':10000,'求购件数':100,'求购厚度变化百分比':0})
    return {'monitor':quotes},pool,coils
class Decisions(unittest.TestCase):
    def test_bear_repair_does_not_require_positive_7_day_return(self):
        s,p,c=fixture()
        for r in p:r['r3']=.01;r['r7']=-.1  # 短端转正、7日仍负：熊市修复
        x=build(s,p,c,[],NOW)
        self.assertTrue(x['market']['permission'].startswith('研究放行'));self.assertEqual(x['research_ready'],60)
        self.assertFalse(x['live_buy_allowed']);self.assertFalse(x['validated']);self.assertTrue(all(not r['live_buy_allowed'] for r in x['rows']))
    def test_stale_quote_blocks(self):
        s,p,c=fixture()
        for r in p:r['r3']=-.02;r['prior_r3']=-.01;r['r7']=-.06   # 弱势震荡，非反弹
        s['monitor'][0]['价格采集时间']='2026-10-20T00:00:00+08:00'
        x=build(s,p,c,[],NOW);self.assertEqual(len(x['rows']),60)
        self.assertTrue(any('报价缺失或超过6小时' in b for b in x['rows'][0]['blockers']))
        self.assertNotEqual(x['rows'][0]['state'],'研究条件满足，仅模拟试探')

    def test_demand_is_bonus_only_when_stale(self):
        s,p,c=fixture()
        for r in p:r['r3']=.01;r['prior_r3']=-.03;r['r7']=-.1      # 反弹追认市场
        s['monitor'][1]['求购批次']='2026-10-01'                    # 求购过期
        x=build(s,p,c,[],NOW)
        # 求购过期：只留空加分、不阻断（加分项，非必要条件）
        self.assertEqual(x['rows'][1]['state'],'研究条件满足，仅模拟试探')
        self.assertIsNone(x['rows'][1]['entry_components']['demand'])
        self.assertTrue(any('求购信息缺失或批次过期' in n for n in x['rows'][1]['data_notes']))
        self.assertNotIn('求购缺失或批次超过1天',x['rows'][1]['blockers'])

    def test_demand_drop_does_not_block(self):
        s,p,c=fixture()
        for r in p:r['r3']=.01;r['prior_r3']=-.03;r['r7']=-.1      # 反弹追认市场
        s['monitor'][0]['求购厚度变化百分比']=-30
        x=build(s,p,c,[],NOW)
        self.assertEqual(x['rows'][0]['state'],'研究条件满足，仅模拟试探')
        self.assertNotIn('可比求购厚度下降超过20%',x['rows'][0]['blockers'])
        self.assertTrue(any('下降超过20%' in n for n in x['rows'][0]['data_notes']))
        self.assertEqual(x['rows'][0]['entry_components']['demand'],15.0)  # 容量15+变化0，加分不再给

    def test_rebound_mode_identifies_leaders_with_stale_quotes(self):
        """11/26-27 反弹场景：日K确认反弹后，报价断供、无传统形态的领涨单品也要能被识别。"""
        s,p,c=fixture()
        for r in p:r['r3']=.02;r['prior_r3']=-.03;r['r7']=-.05;r['families']=0
        s['monitor'][0]['价格采集时间']='2026-10-20T00:00:00+08:00'  # 报价过期
        s['monitor'][0]['求购批次']='2026-10-01'                        # 求购过期
        x=build(s,p,c,[],NOW)
        self.assertTrue(x['rebound']['confirmed'])
        self.assertEqual(x['market']['permission'],'研究放行（反弹追认）')
        r=x['rows'][0]
        self.assertEqual(r['state'],'研究条件满足，仅模拟试探')
        # 报价过期以日K收盘价兜底、求购加分留空，均不阻断
        self.assertNotIn('报价缺失或超过6小时',r['blockers'])
        self.assertNotIn('价格超过入场观察上限，等待回踩',r['blockers'])
        self.assertIsNone(r['entry_components']['demand'])
        self.assertAlmostEqual(r['quote'],100,places=2)
        # 动量加分已计入潜力
        self.assertIn('rebound_momentum',r['potential_components'])
        self.assertTrue(any('反弹追认模式' in n for n in r['data_notes']))

    def test_rebound_not_confirmed_when_declining(self):
        s,p,c=fixture()
        for r in p:r['r3']=-.02;r['prior_r3']=-.01;r['r7']=-.06
        x=build(s,p,c,[],NOW)
        self.assertFalse(x['rebound']['confirmed'])
        self.assertEqual(x['market']['permission'],'仅观察')
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
