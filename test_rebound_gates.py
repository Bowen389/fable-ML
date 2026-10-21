import unittest
import pandas as pd
from rebound_gate_research import gate_evidence,gated_entries
class GateTests(unittest.TestCase):
    def frame(self):
        return pd.DataFrame([dict(name=f'item{i}',date=pd.Timestamp('2026-01-01'),sector='AK',eligible=True,rank=i+1,score=100-i,m3=-.01,m7=-.07,market_breadth_change3=.01,r3=-.01,r7=-.07,rv=1.1,close=100,ma10=100,phase='basing',r1=0) for i in range(12)])
    def test_bear_market_deceleration_can_pass(self):
        x=gate_evidence(self.frame());self.assertTrue(x.market_and_relay.all());self.assertTrue(x.rear_ready.eq(7).all())
    def test_no_followers_no_entry(self):
        d=self.frame();d.loc[d['rank'].gt(5),'r3']=-.1;x=gate_evidence(d)
        self.assertFalse(x.relay_ok.any());self.assertFalse(x.market_and_relay.any())
        for k,v in gated_entries(x).items():
            if k.endswith('__both'):self.assertFalse(v.any())
    def test_market_blocks_both(self):
        d=self.frame();d['market_breadth_change3']=-.01;x=gate_evidence(d)
        self.assertFalse(x.market_and_relay.any());self.assertTrue(x.relay_ok.all())
    def test_future_date_does_not_change_evidence(self):
        a=self.frame();b=a.copy();b['date']+=pd.Timedelta(days=1);b['r3']=1
        out=gate_evidence(pd.concat([a,b],ignore_index=True)).iloc[:len(a)]
        self.assertEqual(out.rear_ready.tolist(),gate_evidence(a).rear_ready.tolist())
if __name__=='__main__':unittest.main()
