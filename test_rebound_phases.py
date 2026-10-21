import unittest
import numpy as np
import pandas as pd
from rebound_phase_research import phases,masks,trades

class PhaseTests(unittest.TestCase):
    def frame(self):
        rows=[]
        for i in range(8):
            for j,day in enumerate(pd.date_range('2026-01-01',periods=40)):
                rows.append(dict(name=f'AK-47 | X{i} (Factory New)',date=day,eligible=True,close=100+j,ma10=99,volume=10,r3=.02,r7=.04,r1=.01,rv=1.3,rank=i+1,score=90,known_event_window=False))
        return pd.DataFrame(rows)
    def test_future_does_not_change_phases_or_entries(self):
        raw=self.frame();a,_=phases(raw,set());raw.loc[raw.date.gt('2026-01-25'),'close']=1
        b,_=phases(raw,set());sel=a.date.le('2026-01-25')
        self.assertEqual(a.loc[sel,'phase'].tolist(),b.loc[sel,'phase'].tolist())
        for k in masks(a):self.assertEqual(masks(a)[k][sel].tolist(),masks(b)[k][sel].tolist())
    def test_topk_global_rank_before_filters(self):
        d,_=phases(self.frame(),set())
        for k in (3,5,30):
            for signal in masks(d,k).values():
                self.assertTrue(d.loc[signal,'rank'].le(k).all())
                self.assertLessEqual(int(signal.groupby(d.date).sum().max()),k)

    def test_multiple_sectors_with_calendar_gaps(self):
        d=self.frame();other=d.copy();other['name']=other.name.str.replace('AK-47','M4A1-S',regex=False)
        d=d[~d.date.eq('2026-01-10')];other=other[~other.date.eq('2026-01-10')]
        raw=pd.concat([d,other],ignore_index=True);out,q=phases(raw,set())
        self.assertEqual(len(out),len(raw))
        self.assertFalse(q.duplicated(['date','sector']).any())
        self.assertFalse(q.sector.isna().any())

    def test_small_group_unknown(self):
        d,q=phases(self.frame().query('rank < 8'),set());self.assertTrue(d.phase.eq('unknown').all())
    def test_exit_delayed_and_missing_not_zero(self):
        d=self.frame().query('rank == 1').copy().reset_index(drop=True);d['sector']='AK';d['phase']='starting';d['row_id']=d.index
        d.loc[d.date.eq('2026-01-04'),'phase']='fading';mask=d.index.to_series().eq(0)
        r=trades(d,mask,'sector_fade14',d.date.max())[0]
        self.assertEqual(r['exit_date'],'2026-01-05');self.assertAlmostEqual(r['net'],104/101*.99-1)
        d.loc[d.date.eq('2026-01-03'),'volume']=0
        self.assertIsNone(trades(d,mask,'sector_fade14',d.date.max())[0]['net'])
    def test_declining_breadth_after_run_fades(self):
        d=self.frame();d.loc[d.date.ge('2026-01-10'),'r7']=.2
        d.loc[d.date.ge('2026-01-10'),'close']=90
        x,_=phases(d,set());self.assertTrue(x[x.date.eq('2026-01-10')].phase.eq('fading').all())

if __name__=='__main__':unittest.main()
