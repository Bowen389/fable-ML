import unittest
from datetime import datetime,timezone,timedelta
from pipeline_readiness import assess,expected_quote_slot,steamdt_quote_available,_sample_names
TZ=timezone(timedelta(hours=8))

def _stale_quote():
    # 报价停留在旧日期，必然触发"等待本时段报价发布/报价超时"
    return dict(generated_at='2026-10-30T15:29:33+08:00',status='partial',price_rows=785)

def _ok_coil(asof='2026-11-25'):
    return dict(status='ok',asof=asof)

class TimingTests(unittest.TestCase):
    def test_old_but_recent_quote_does_not_pass_new_slot(self):
        t=datetime(2026,10,23,16,7,tzinfo=TZ)
        result=assess(t,dict(generated_at='2026-10-23T12:00:00+08:00',status='partial',price_rows=802),dict(status='ok',asof='2026-10-22'))
        self.assertFalse(result['ready']);self.assertIn('等待本时段报价发布',result['reasons'])
    def test_new_quotes_still_wait_for_same_day_score(self):
        t=datetime(2026,10,23,10,47,tzinfo=TZ)
        q=dict(generated_at='2026-10-23T10:00:00+08:00',status='partial',price_rows=802)
        self.assertFalse(assess(t,q,dict(status='ok',asof='2026-10-21'))['ready'])
        self.assertTrue(assess(t,q,dict(status='ok',asof='2026-10-22'))['ready'])
    def test_midnight_and_future_times(self):
        t=datetime(2026,10,23,0,30,tzinfo=TZ)
        self.assertEqual(expected_quote_slot(t).isoformat(),'2026-10-22T21:17:00+08:00')
        self.assertFalse(assess(t,dict(generated_at='2026-10-24T10:00:00+08:00',status='ok',price_rows=1),dict(status='ok',asof='2026-10-22'))['ready'])

class SteamDTFallbackTests(unittest.TestCase):
    t=datetime(2026,11,26,12,0,tzinfo=TZ)

    def test_stale_quote_no_fallback_blocks(self):
        # 兜底未启用：行为与原版一致，报价过期仍阻断
        r=assess(self.t,_stale_quote(),_ok_coil())
        self.assertFalse(r['ready'])
        self.assertIn('等待本时段报价发布',r['reasons'])
        self.assertNotIn('steamdt_fallback',r)

    def test_stale_quote_fallback_available_passes(self):
        # 上游报价过期，但 SteamDT 兜底可用：报价维度按满足处理，ready
        sd={'available':True,'probed':6,'fresh':3,'reason':''}
        r=assess(self.t,_stale_quote(),_ok_coil(),steamdt=sd)
        self.assertTrue(r['ready'])
        self.assertEqual(r['reasons'],[])
        self.assertTrue(any('SteamDT兜底' in n for n in r['notes']))
        self.assertEqual(r['steamdt_fallback']['available'],True)

    def test_stale_quote_fallback_unavailable_blocks(self):
        # 兜底不可用：报价过期仍阻断，并记录兜底不可用
        sd={'available':False,'probed':6,'fresh':0,'reason':'SteamDT 未返回悠悠在售价'}
        r=assess(self.t,_stale_quote(),_ok_coil(),steamdt=sd)
        self.assertFalse(r['ready'])
        self.assertIn('等待本时段报价发布',r['reasons'])
        self.assertTrue(any('SteamDT兜底不可用' in n for n in r['notes']))

    def test_fallback_available_coil_not_ready_still_blocks(self):
        # 兜底报价可用，但日K蓄势未发布：仍阻断(日K维度)
        sd={'available':True,'probed':6,'fresh':3,'reason':''}
        r=assess(self.t,_stale_quote(),dict(status='ok',asof='2026-11-24'),steamdt=sd)
        self.assertFalse(r['ready'])
        self.assertIn('等待昨日完整日K蓄势评分发布',r['reasons'])

    def test_fresh_quote_fallback_not_needed(self):
        # 上游报价新鲜：兜底不介入，正常放行
        q=dict(generated_at='2026-11-26T11:00:00+08:00',status='partial',price_rows=785)
        sd={'available':True,'probed':6,'fresh':3,'reason':''}
        r=assess(self.t,q,_ok_coil(),steamdt=sd)
        self.assertTrue(r['ready'])
        self.assertEqual(r['reasons'],[])

    def test_steamdt_available_no_key(self):
        r=steamdt_quote_available('',['AK-47 | Redline (Field-Tested)'],self.t)
        self.assertFalse(r['available'])
        self.assertIn('STEAMDT_API_KEY',r['reason'])

    def test_steamdt_available_no_names(self):
        r=steamdt_quote_available('KEY',[],self.t)
        self.assertFalse(r['available'])
        self.assertIn('样本',r['reason'])

    def test_sample_names_extraction(self):
        quote={'monitor_items':[{'name':'AK-47 | Redline (Field-Tested)'},{'name':'M4A4 | 合纵'}]}
        names=_sample_names(quote,limit=2)
        self.assertEqual(names,['AK-47 | Redline (Field-Tested)','M4A4 | 合纵'])

    def test_sample_names_empty(self):
        self.assertEqual(_sample_names({},limit=3),[])

if __name__=='__main__':
    unittest.main()
