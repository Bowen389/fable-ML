import unittest
from pool_audit import diagnose
class Audit(unittest.TestCase):
 def context(self,**kw):return dict(current_exists=True,close=100,history_count=400,valid90=90,valid20=20,volume_ok=True,volume=10,rv=1,flat_14=.1,eligible=True,**kw)
 def test_excluded_stays_monitored(self):self.assertEqual(diagnose('Nova | X',None,{})[0],'研究品类排除')
 def test_short_history_is_not_score_zero(self):self.assertEqual(diagnose('AK-47 | X','Less than 300 valid history rows',{})[0],'历史不足')
 def test_low_price_and_gaps_both_explained(self):
  c=self.context();c.update(close=20,valid90=70,eligible=False);status,why=diagnose('AK-47 | X',None,c)
  self.assertEqual(status,'低于价格门槛');self.assertEqual(len(why),2)
 def test_no_volume(self):
  c=self.context();c.update(volume=0,volume_ok=False);self.assertEqual(diagnose('AK-47 | X',None,c)[0],'量能条件不足')
 def test_eligible(self):self.assertEqual(diagnose('AK-47 | X',None,self.context()),('可评分',[]))
 def test_missing_bar(self):self.assertEqual(diagnose('AK-47 | X',None,{})[0],'最新日K缺失')

 def test_full_audit_agrees_with_scoring_eligibility(self):
  import pandas as pd
  from pathlib import Path
  from tempfile import TemporaryDirectory
  from pool_audit import write_pool_audit
  latest=pd.Timestamp('2026-10-20');dates=pd.date_range(end=latest,periods=400);frames=[]
  for name,price in [('AK-47 | A',100),('AK-47 | B',20)]:
   g=pd.DataFrame({'name':name,'date':dates,'close':100.,'volume':10.,'rv':1.,'flat_14':.1,'volume_ok':True,'eligible':True})
   g.loc[g.index[-1],'close']=price;g.loc[g.index[-1],'eligible']=price>=30;frames.append(g)
  universe=[{'name':n,'cn':n,'id':str(i)} for i,n in enumerate(['AK-47 | A','AK-47 | B','Nova | C','AK-47 | D'])]
  with TemporaryDirectory() as td:
   out=write_pool_audit(universe,[{'name':'AK-47 | D','error':'Less than 300 valid history rows'}],pd.concat(frames),latest,Path(td))
   self.assertEqual(out['status_counts'],{'可评分':1,'低于价格门槛':1,'研究品类排除':1,'历史不足':1})
   self.assertTrue((Path(td)/'score_pool_status.json').exists())
if __name__=='__main__':unittest.main()

