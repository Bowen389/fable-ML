import tempfile,unittest,json,gzip,csv
from pathlib import Path
from datetime import date
from learning_review import outcome,run

class Review(unittest.TestCase):
    def test_next_day_entry_and_sell_fee(self):
        bars={date(2026,1,1):(10,100),date(2026,1,2):(20,30),date(2026,1,9):(30,40)}
        self.assertAlmostEqual(outcome(bars,date(2026,1,1),7),.98)
        self.assertIsNone(outcome(bars,date(2026,1,1),14))
    def test_missing_not_zero_and_no_promotion(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'output/history';p.mkdir(parents=True)
            with (p/'process_scores_test.csv').open('w') as f:
                w=csv.DictWriter(f,fieldnames=['价格日期','算法版本','生成时间','每日参考分','name','id']);w.writeheader()
                w.writerow(dict(zip(w.fieldnames,['2026-01-01','v1','2026-01-02T10:00:00+08:00',90,'A','1'])))
            r=run(tmp,date(2026,2,1))
            self.assertFalse(r['promotion_allowed'])
            self.assertTrue(all(x['mean'] is None and x['n']==0 and x['expected']==1 for x in r['results']))
    def test_late_snapshot_excluded(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'output/history';p.mkdir(parents=True)
            (p/'process_scores_late.csv').write_text('价格日期,算法版本,生成时间,每日参考分,name,id\n2026-01-01,v1,2026-02-01T10:00:00+08:00,90,A,1\n')
            self.assertEqual(run(tmp,date(2026,3,1))['results'],[])

if __name__=='__main__':unittest.main()
