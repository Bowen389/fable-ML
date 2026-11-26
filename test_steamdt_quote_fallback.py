"""steamdt_quote_fallback 单元测试：mock SteamDT 响应，验证兜底覆盖逻辑。"""
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import steamdt_quote_fallback as fb

TZ = timezone(timedelta(hours=8))
NOW = datetime(2026, 11, 26, 12, 0, 0, tzinfo=TZ)


def _stale_row(name='AK-47 | X-Ray (Field-Tested)', hours_old=10):
    t = (NOW - timedelta(hours=hours_old)).isoformat()
    return {'name': name, '商品': 'AK-47 | 红线', 'yyyp_id': '1',
            '实时挂牌价': 100.0, '价格采集时间': t, '当前在售数': 5,
            '求购批次': '2026-11-25', '求购厚度': 1000}


def _fresh_row(name='MAC-10 | Tatter (Factory New)'):
    t = (NOW - timedelta(hours=2)).isoformat()
    return {'name': name, '商品': 'MAC-10 | 烧尽', 'yyyp_id': '2',
            '实时挂牌价': 50.0, '价格采集时间': t, '当前在售数': 8,
            '求购批次': '2026-11-25', '求购厚度': 200}


def _steamdt_payload(names):
    """构造 /price/batch 成功响应：每个 name 含悠悠有品平台一行。"""
    data = []
    for n in names:
        data.append({'marketHashName': n, 'dataList': [
            {'platform': 'BUFF', 'sellPrice': 999.0, 'sellCount': 1, 'biddingPrice': 0, 'biddingCount': 0, 'updateTime': 1760000000},
            {'platform': '悠悠有品', 'sellPrice': 123.0, 'sellCount': 7, 'biddingPrice': 120.0, 'biddingCount': 3, 'updateTime': 1760000000},
        ]})
    return {'success': True, 'data': data, 'errorCode': 0, 'errorMsg': ''}


class TestPickYouyin(unittest.TestCase):
    def test_picks_youyin_platform(self):
        rec = fb._pick_youyin([
            {'platform': 'BUFF', 'sellPrice': 1},
            {'platform': '悠悠有品', 'sellPrice': 2},
        ])
        self.assertEqual(rec['sellPrice'], 2)

    def test_picks_youpin_english(self):
        rec = fb._pick_youyin([{'platform': 'YouPin', 'sellPrice': 5}])
        self.assertEqual(rec['sellPrice'], 5)

    def test_returns_none_when_absent(self):
        self.assertIsNone(fb._pick_youyin([{'platform': 'BUFF', 'sellPrice': 1}]))
        self.assertIsNone(fb._pick_youyin(None))


class TestTsToIso(unittest.TestCase):
    def test_seconds(self):
        iso = fb._ts_to_iso(1760000000)
        self.assertIsNotNone(iso)
        self.assertTrue(iso.startswith('2025-'))

    def test_millis(self):
        iso_s = fb._ts_to_iso(1760000000)
        iso_ms = fb._ts_to_iso(1760000000000)
        self.assertEqual(iso_s, iso_ms)

    def test_invalid(self):
        self.assertIsNone(fb._ts_to_iso(None))
        self.assertIsNone(fb._ts_to_iso('bad'))


class TestOverlay(unittest.TestCase):
    def _run(self, rows, payload, api_key='KEY'):
        with patch.object(fb, '_post', return_value=(payload, '')), \
             patch.dict('os.environ', {'STEAMDT_API_KEY': api_key}, clear=False):
            return fb.overlay_stale_quotes(rows, api_key=api_key, now=NOW)

    def test_stale_row_overlaid(self):
        rows = [_stale_row()]
        new_rows, stats = self._run(rows, _steamdt_payload(['AK-47 | X-Ray (Field-Tested)']))
        self.assertEqual(stats['overlaid'], 1)
        r = new_rows[0]
        self.assertEqual(r['实时挂牌价'], 123.0)      # 悠悠有品 sellPrice
        self.assertEqual(r['当前在售数'], 7)          # 悠悠有品 sellCount
        self.assertIn('SteamDT', r['报价来源'])
        self.assertIn('兜底', r['价格状态'])
        self.assertIn('兜底说明', r)
        # 求购等其它字段不动
        self.assertEqual(r['求购批次'], '2026-11-25')
        self.assertEqual(r['求购厚度'], 1000)

    def test_fresh_row_kept(self):
        rows = [_fresh_row()]
        new_rows, stats = self._run(rows, _steamdt_payload([]))
        self.assertEqual(stats['kept_fresh'], 1)
        self.assertEqual(stats['overlaid'], 0)
        self.assertEqual(new_rows[0]['实时挂牌价'], 50.0)  # 未被替换
        self.assertNotIn('兜底说明', new_rows[0])

    def test_mixed_stale_fresh(self):
        rows = [_stale_row(), _fresh_row()]
        new_rows, stats = self._run(rows, _steamdt_payload(['AK-47 | X-Ray (Field-Tested)']))
        self.assertEqual(stats['overlaid'], 1)
        self.assertEqual(stats['kept_fresh'], 1)
        self.assertEqual(new_rows[0]['实时挂牌价'], 123.0)
        self.assertEqual(new_rows[1]['实时挂牌价'], 50.0)

    def test_steamdt_miss_keeps_original(self):
        rows = [_stale_row()]
        # SteamDT 成功返回但无该品
        new_rows, stats = self._run(rows, _steamdt_payload([]))
        self.assertEqual(stats['steamdt_miss'], 1)
        self.assertEqual(stats['overlaid'], 0)
        self.assertEqual(new_rows[0]['实时挂牌价'], 100.0)  # 保留原值

    def test_no_api_key_skips(self):
        rows = [_stale_row()]
        new_rows, stats = fb.overlay_stale_quotes(rows, api_key='', now=NOW)
        self.assertTrue(stats['no_key'])
        self.assertEqual(new_rows[0]['实时挂牌价'], 100.0)  # 不动

    def test_missing_quote_time_treated_stale(self):
        row = _stale_row()
        row['价格采集时间'] = None  # 缺失
        new_rows, stats = self._run([row], _steamdt_payload(['AK-47 | X-Ray (Field-Tested)']))
        self.assertEqual(stats['stale'], 1)
        self.assertEqual(stats['overlaid'], 1)

    def test_api_error_keeps_original(self):
        rows = [_stale_row()]
        with patch.object(fb, '_post', return_value=(None, 'HTTP 500')), \
             patch.dict('os.environ', {'STEAMDT_API_KEY': 'KEY'}, clear=False):
            new_rows, stats = fb.overlay_stale_quotes(rows, api_key='KEY', now=NOW)
        self.assertIn('error', stats)
        self.assertEqual(new_rows[0]['实时挂牌价'], 100.0)  # 失败不覆盖

    def test_rate_limit_retries_then_succeeds(self):
        # 首次限流、重试后成功：应完成覆盖
        rows = [_stale_row()]
        rate_limited = {'success': False, 'data': None, 'errorMsg': '当前接口请求已达到上限'}
        success = _steamdt_payload(['AK-47 | X-Ray (Field-Tested)'])
        side = [(rate_limited, ''), (success, '')]
        with patch.object(fb, '_post', side_effect=side), \
             patch.object(fb.time, 'sleep', return_value=None), \
             patch.dict('os.environ', {'STEAMDT_API_KEY': 'KEY'}, clear=False):
            new_rows, stats = fb.overlay_stale_quotes(rows, api_key='KEY', now=NOW)
        self.assertEqual(stats['overlaid'], 1)
        self.assertEqual(new_rows[0]['实时挂牌价'], 123.0)

    def test_rate_limit_exhausted_skips_batch(self):
        # 持续限流：跳过该批，保留原值不覆盖
        rows = [_stale_row()]
        rate_limited = {'success': False, 'data': None, 'errorMsg': '当前接口请求已达到上限'}
        with patch.object(fb, '_post', return_value=(rate_limited, '')), \
             patch.object(fb.time, 'sleep', return_value=None), \
             patch.dict('os.environ', {'STEAMDT_API_KEY': 'KEY'}, clear=False):
            new_rows, stats = fb.overlay_stale_quotes(rows, api_key='KEY', now=NOW)
        self.assertEqual(stats['overlaid'], 0)
        self.assertEqual(new_rows[0]['实时挂牌价'], 100.0)  # 保留原值


if __name__ == '__main__':
    unittest.main()
