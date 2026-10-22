import csv,json,sqlite3,tempfile,unittest,hashlib,os
from pathlib import Path
from unittest.mock import patch
import unified_system as u
from system_report_section import merge_system_section
class UnifiedTests(unittest.TestCase):
    def test_four_families_deduplicate_parameter_variants(self):
        self.assertEqual(u.family_count(['双金叉 12/26/9','双金叉 5/12/4','均线合一 MA5/12/21','均线合一 MA7/14/21','上影吞没','单针承接']),4)
    def test_traditional_uses_completed_data_and_scans_all_names(self):
        from datetime import date,timedelta
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/'bars.csv';rows=[]
            for name in ['asset1','asset2']:
                for i in range(310):
                    day=date(2025,1,1)+timedelta(days=i);rows.append({'marketHashName':name,'group':'gun_FN','date':str(day),'v1':100,'v2':101,'v3':102,'v4':99})
            rows.append({**rows[-1],'date':'2025-11-07','v2':999999,'v3':999999})
            u.writecsv(p,rows)
            meta,pool,hits=u.traditional(p,'2025-11-07')
            self.assertEqual(len(pool),2);self.assertEqual(meta['asof'],'2025-11-06');self.assertTrue(all(x['price']==101 for x in pool));self.assertEqual(meta['scanned'],2)
    def test_failure_is_not_zero_and_missing_key_never_uses_demo(self):
        with tempfile.TemporaryDirectory() as root,patch.dict(os.environ,{'CSQAQ_TOKEN':'','WHALE_SELF_TEST':'1'}):
            with patch('urllib.request.urlopen',side_effect=AssertionError('must not request')):
                result=u.whale(root,collect=True)
            self.assertEqual(result['status'],'not_configured');self.assertIsNone(result['events'])
    def test_monitor_rows_preserved_and_wear_not_fuzzy_matched(self):
        monitors=[{'name':'AK | X (Factory New)','商品':'枪 | X (崭新)','yyyp_id':'1'},{'name':'AK | X (Minimal Wear)','商品':'枪 | X (略磨)','yyyp_id':'2'}]
        coils=[{'name':'AK | X (Factory New)','cn':'枪 | X (崭新)','sequence':80,'early_coil':70}]
        x=u.join_monitor(monitors,coils,[]);self.assertEqual(len(x),2);self.assertEqual(x[0]['蓄势证据分'],80);self.assertIsNone(x[1]['蓄势证据分']);self.assertIsNone(x[1]['传统买点家族数'])
    def test_demand_rank_counts_valid_orders_only_and_never_writes_db(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/'yyyp.db'
            with sqlite3.connect(p) as db:
                db.executescript('CREATE TABLE snapshot(run TEXT,tid INT,name TEXT);CREATE TABLE orders(run TEXT,tid INT,user_id INT,user_name TEXT,price REAL,qty INT,valid INT);')
                day=u.now().date().isoformat();db.execute('INSERT INTO snapshot VALUES(?,?,?)',(day,1,'test'))
                db.executemany('INSERT INTO orders VALUES(?,?,?,?,?,?,?)',[(day,1,10,'A',100,2,1),(day,1,10,'A',10000,10,0),(day,1,20,'B',50,1,1)])
            before=hashlib.sha256(p.read_bytes()).hexdigest();meta,rank=u.demand_rank(p)
            self.assertEqual(rank[0]['valid_purchase_amount'],200);self.assertEqual(rank[1]['valid_purchase_amount'],50);self.assertEqual(before,hashlib.sha256(p.read_bytes()).hexdigest())
    def test_report_merge_preserves_other_sections_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/'output';p.mkdir();(p/'system_latest.json').write_text(json.dumps({'generated_at':'date','modules':{'whale':{'status':'not_configured','reason':'missing'}}}))
            a=merge_system_section('# Old report\n<!-- daily-coil:start -->keep<!-- daily-coil:end -->',root);b=merge_system_section(a,root)
            self.assertEqual(a,b);self.assertIn('keep',b);self.assertEqual(b.count('<!-- unified-system:start -->'),1);self.assertIn('not_configured',b)
if __name__=='__main__':unittest.main()
