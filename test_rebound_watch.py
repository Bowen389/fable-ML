import unittest
import pandas as pd
from rebound_watch_research import watch_entries
class WatchTests(unittest.TestCase):
    def frame(self):
        rows=[]
        for j,date in enumerate(pd.date_range('2026-01-01',periods=14)):
            for i in range(6):
                c=100 if j==0 else 96 if j==1 else 98 if j==2 else 101
                rows.append(dict(name=f'item{i}',date=date,eligible=True,rank=i+1 if j==0 else 20+i,score=100-i,close=c,volume=10,r1=-.04 if j==1 else .02,rv=.8 if j==1 else 1.3,ma10=98,market_ok=True,relay_ok=True,phase='starting'))
        d=pd.DataFrame(rows);d['row_id']=d.index;return d
    def test_frozen_top3_can_recover_outside_current_top3(self):
        d=self.frame();m,a=watch_entries(d,ks=(3,));z=a[a.method.eq('top3_wash_reclaim__market')&a.signal]
        self.assertEqual(len(z),3);self.assertTrue(z.current_rank.gt(3).all());self.assertTrue(z.watch_age.eq(2).all());self.assertTrue(z.setup_rank.le(3).all())
    def test_no_same_day_wash_and_recovery(self):
        d=self.frame();d.loc[d.date.eq('2026-01-02'),'r1']=.01
        m,a=watch_entries(d,ks=(3,));self.assertFalse(a[a.date.eq('2026-01-02')&a.method.str.contains('wash_reclaim')].signal.any())
    def test_market_and_relay_refusal(self):
        d=self.frame();d.loc[d.date.eq('2026-01-03'),'market_ok']=False;d['relay_ok']=False
        m,a=watch_entries(d,ks=(3,));self.assertFalse(a[a.date.eq('2026-01-03')].signal.any());self.assertFalse(a[a.method.str.endswith('__both')].signal.any())
    def test_future_does_not_change_past_watchlist(self):
        d=self.frame();m,a=watch_entries(d,ks=(3,));d.loc[d.date.gt('2026-01-05'),'rank']=1
        n,b=watch_entries(d,ks=(3,));pd.testing.assert_frame_equal(a[a.date.le('2026-01-05')].reset_index(drop=True),b[b.date.le('2026-01-05')].reset_index(drop=True))
    def test_no_replacement_with_unselected_items(self):
        d=self.frame();_,a=watch_entries(d,ks=(3,));self.assertEqual(set(a.name),{'item0','item1','item2'})
if __name__=='__main__':unittest.main()
