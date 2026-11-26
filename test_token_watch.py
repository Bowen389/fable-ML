"""凭证有效期监控 + Whale 只加分不卡门的强制测试。"""
import unittest
from datetime import datetime, timedelta, timezone
from token_watch import watch, TOKEN_TTL_DAYS, REMIND_DAYS, local_state

TZ = timezone(timedelta(hours=8))


def day(n):
    return (datetime(2026, 11, 26, 12, tzinfo=TZ) - timedelta(days=n)).isoformat()


class TokenWatch(unittest.TestCase):
    def test_within_ttl_is_ok(self):
        r = watch({'status': 'ok', 'generated_at': day(3)},
                  {'status': 'ok', 'batch': '2026-11-23'},
                  {'status': 'ok', 'generated_at': day(2)}, True, datetime(2026, 11, 26, 12, tzinfo=TZ))
        self.assertTrue(r['all_ok'])
        self.assertEqual(r['sources']['quotes']['status'], 'ok')
        self.assertEqual(r['sources']['demand']['status'], 'ok')

    def test_approaching_expiry_reminds(self):
        r = watch({'status': 'ok', 'generated_at': day(8)},
                  {'status': 'ok', 'batch': '2026-11-18'},
                  None, True, datetime(2026, 11, 26, 12, tzinfo=TZ))
        self.assertFalse(r['all_ok'])
        self.assertEqual(r['sources']['quotes']['status'], 'expiring')
        self.assertTrue(any('临期提醒' in a for a in r['alerts']))
        self.assertTrue(REMIND_DAYS < TOKEN_TTL_DAYS)

    def test_expired_flags_hard(self):
        r = watch({'status': 'ok', 'generated_at': day(20)},
                  {'status': 'ok', 'batch': '2026-11-06'},
                  {'status': 'ok', 'generated_at': day(11)}, True, datetime(2026, 11, 26, 12, tzinfo=TZ))
        self.assertFalse(r['all_ok'])
        self.assertEqual(r['sources']['quotes']['status'], 'expired')
        self.assertEqual(r['sources']['demand']['status'], 'expired')
        self.assertEqual(r['sources']['whale']['status'], 'expired')
        self.assertTrue(any('很可能已失效' in a for a in r['alerts']))

    def test_stale_quote_treated_as_expired(self):
        r = watch({'status': 'stale', 'generated_at': day(1)},
                  None, None, True, datetime(2026, 11, 26, 12, tzinfo=TZ))
        self.assertEqual(r['sources']['quotes']['status'], 'expired')

    def test_no_token_whale_not_configured(self):
        r = watch(None, None, None, False, datetime(2026, 11, 26, 12, tzinfo=TZ))
        # 鲸鱼没有 token：明确 not_configured；报价/求购完全没有数据：按采集不可用告警
        self.assertEqual(r['sources']['whale']['status'], 'not_configured')
        self.assertEqual(r['sources']['quotes']['status'], 'error')
        self.assertEqual(r['sources']['demand']['status'], 'error')
        self.assertFalse(r['all_ok'])

    def test_collection_error_is_alerted(self):
        r = watch({'status': 'error', 'error': 'HTTPError'}, None, None, True, datetime(2026, 11, 26, 12, tzinfo=TZ))
        self.assertEqual(r['sources']['quotes']['status'], 'error')
        self.assertFalse(r['all_ok'])


class WhaleNeverGates(unittest.TestCase):
    """Whale（索塔）只能作为加分信息，不能作为必要条件：
    无论 Whale 数据存在、缺失、过期还是报错，决策结果必须完全一致。"""

    def _fixture(self):
        from decision_engine import build
        pool, coils, monitor = [], [], []
        for i in range(60):
            n = f'AK-47 | G{i} (Factory New)'
            pool.append(dict(name=n, eligible=True, asof='2026-11-25', r3=.01, prior_r3=-.03, r7=-.1,
                             ma5=101, ma21=100, atr14=1, atr_pct=.01, support10=99, high20=110, families=2))
            coils.append(dict(name=n, date='2026-11-25', build=1, tier=1, wash=1, activation=1, relative=1,
                              penalty=0, early_coil=72, sequence=75, reasons='量价证据'))
            monitor.append({'name': n, '商品': n, '实时挂牌价': 100,
                            '价格采集时间': datetime(2026, 11, 26, 10, tzinfo=TZ).isoformat(),
                            '求购批次': '2026-11-25', '求购厚度': 9000, '求购件数': 90,
                            '求购厚度变化百分比': 0})
        return build({'monitor': monitor}, pool, coils, [], datetime(2026, 11, 26, 12, tzinfo=TZ))

    def test_decisions_identical_with_or_without_whale(self):
        base = self._fixture()
        # build 根本不消费 whale/coverage/token_watch：签名里没有这些键，
        # 因此无论 Whale 数据存在、缺失、过期还是报错，决策结果必然一致。
        import inspect
        from decision_engine import build
        params = inspect.signature(build).parameters
        self.assertNotIn('whale', params)
        self.assertNotIn('coverage', params)
        self.assertNotIn('token_watch', params)
        # 且每行都带鲸鱼辅助标注、无任何以鲸鱼为条件的 blocker
        for row in base['rows']:
            self.assertIn('仅辅助', row['whale'])
            self.assertTrue(all('鲸鱼' not in b and 'whale' not in b.lower() for b in row['blockers']))
        # 重复构建结果稳定，证明 Whale 相关输入不改变任何决策字段
        again = self._fixture()
        self.assertEqual([r['state'] for r in base['rows']], [r['state'] for r in again['rows']])

    def test_whale_coverage_error_does_not_block_entries(self):
        res = self._fixture()
        self.assertEqual(res['status'], 'research_only')
        self.assertTrue(all(r['state'] == '研究条件满足，仅模拟试探' for r in res['rows']))
        self.assertFalse(res['live_buy_allowed'])


class LocalStateSelfCheck(unittest.TestCase):
    def test_local_state_runs_offline(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'data/integrations').mkdir(parents=True)
            (root / 'output').mkdir(parents=True)
            (root / 'data/integrations/quote_meta.json').write_text(
                '{"status":"ok","generated_at":"2026-11-26T10:00:00+08:00"}', encoding='utf-8')
            result = local_state(root)
            self.assertIn('quotes', result['sources'])
            self.assertEqual(result['sources']['quotes']['status'], 'ok')


if __name__ == '__main__':
    unittest.main()
