import json, tempfile, unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
import whale_coverage_audit as a

TZ = timezone(timedelta(hours=8))
REPO = Path(__file__).resolve().parent


def build_state(root, whitelist=True, goods=1, whales=2, max_whales=1, scan_age_days=1, item_age_days=1):
    state = Path(root) / 'state/whale_monitor' / 'data'
    state.mkdir(parents=True)
    (state / 'top30_latest.json').write_text(json.dumps([{'good_id': '111', 'name': 'x', 'rank': 1}] * goods))
    if whitelist:
        (state / 'extra_goods.json').write_text(json.dumps({
            'updated_at': datetime.now(TZ).isoformat(), 'goods': [{'good_id': '222', 'name': 'y'}]}))
    (state / 'scan_limits.json').write_text(json.dumps({'max_whales_per_round': max_whales}))
    pool = {f'sid{i}': {'steam_id': f'sid{i}', 'sources': [{'good_id': '111'}], 'task_id': i} for i in range(whales)}
    (state / 'whales_monitor_pool.json').write_text(json.dumps(pool))
    last = {f'sid{i}': (datetime.now(TZ) - timedelta(days=scan_age_days)).isoformat() for i in range(whales)}
    when = (datetime.now(TZ) - timedelta(days=item_age_days)).isoformat()
    (state / 'whale_snapshots.json').write_text(json.dumps({
        'whales': {f'sid{i}': {f'AK | X (崭新出厂)\x01111\x01{when}': 1} for i in range(whales)},
        'last_success_scan': last}))
    return Path(root)


class WhaleCoverageAuditTests(unittest.TestCase):
    def test_missing_whitelist_is_reported_not_ignored(self):
        with tempfile.TemporaryDirectory() as root:
            build_state(root, whitelist=False)
            result = a.audit(root)
            self.assertEqual(result['status'], 'missing')
            self.assertTrue(any('白名单' in x for x in result['alerts']))

    def test_pool_rotation_and_item_freshness_are_computed(self):
        with tempfile.TemporaryDirectory() as root:
            build_state(root, whales=6, max_whales=2, item_age_days=3)
            result = a.audit(root)
            self.assertEqual(result['pool']['size'], 6)
            self.assertEqual(result['pool']['max_whales_per_round'], 2)
            self.assertEqual(result['pool']['estimated_rotation_days'], 3.0)
            self.assertEqual(result['items'][0]['whales'], 6)
            self.assertAlmostEqual(result['items'][0]['age_days'], 3, delta=0.1)

    def test_stale_watch_list_raises_alert(self):
        with tempfile.TemporaryDirectory() as root:
            build_state(root)
            state = Path(root) / 'state/whale_monitor' / 'data'
            (state / 'extra_goods.json').write_text(json.dumps({
                'updated_at': (datetime.now(TZ) - timedelta(days=9)).isoformat(),
                'goods': [{'good_id': '222', 'name': 'y'}]}))
            result = a.audit(root)
            self.assertTrue(any('白名单' in x for x in result['alerts']))
            self.assertTrue(any('TOP30' in x for x in result['alerts']) or result['watch_list']['top30_snapshot_age_days'] is not None)

    def test_shipped_whitelist_is_valid_and_covers_focus_goods(self):
        path = REPO / 'state/whale_monitor/data/extra_goods.json'
        self.assertTrue(path.exists(), '缺少显式监控白名单')
        data = json.loads(path.read_text(encoding='utf-8'))
        goods = data['goods']
        self.assertIsInstance(goods, list)
        self.assertGreaterEqual(len(goods), 50)
        ids = [str(g['good_id']) for g in goods]
        self.assertEqual(len(ids), len(set(ids)), '白名单 good_id 重复')
        for focus in ('12248', '12304', '12196', '7136', '19252'):
            self.assertIn(focus, ids, f'重点标的 good_id {focus} 未加入监控白名单')

    def test_audit_writes_nothing_to_state(self):
        with tempfile.TemporaryDirectory() as root:
            build_state(root)
            before = {p.name: p.stat().st_mtime for p in (Path(root) / 'state/whale_monitor/data').iterdir()}
            a.audit(root)
            after = {p.name: p.stat().st_mtime for p in (Path(root) / 'state/whale_monitor/data').iterdir()}
            self.assertEqual(before, after)


class WhaleSnapshotFreshnessTests(unittest.TestCase):
    """TOP30 快照的新鲜度必须看内容时间戳，不能看 mtime（会被 git checkout 重置）。"""

    def test_generated_at_wins_over_mtime(self):
        from integrations.whale import monitor_v7 as w
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / 'top30_latest.json'
            old = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
            p.write_text(json.dumps({'generated_at': old, 'goods': [{'good_id': '1', 'name': 'a'}]}))
            self.assertAlmostEqual(w.snapshot_age_hours(p), 240, delta=2)

    def test_legacy_list_format_still_works(self):
        from integrations.whale import monitor_v7 as w
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / 'top30_latest.json'
            p.write_text(json.dumps([{'good_id': '1', 'name': 'a'}]))
            self.assertGreater(w.snapshot_age_hours(p), -1)
            self.assertEqual(w.clean_goods(json.loads(p.read_text()))[0]['good_id'], '1')

    def test_dict_format_is_readable_by_clean_goods(self):
        from integrations.whale import monitor_v7 as w
        goods = w.clean_goods({'generated_at': '2026-10-22T06:23:36+00:00', 'goods': [{'good_id': '7', 'name': 'x'}]})
        self.assertEqual(len(goods), 1)
        self.assertEqual(goods[0]['good_id'], '7')


if __name__ == '__main__':
    unittest.main()
