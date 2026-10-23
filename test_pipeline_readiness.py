import unittest
from datetime import datetime,timezone,timedelta
from pipeline_readiness import assess,expected_quote_slot
TZ=timezone(timedelta(hours=8))
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
