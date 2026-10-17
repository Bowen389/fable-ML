import pandas as pd
from cs2.leaders import add_peer_features, reversal_rules, leader_watch
from cs2.rules import strategy_mask


def peer_day():
    n=12
    return pd.DataFrame(dict(name=[f'AK-47 | item{i}' for i in range(n)],
        cat=['gun_FN']*n, date=[pd.Timestamp('2026-08-22')]*n,
        eligible=[True]*n, flat_14=[0.]*n, r_1=[.03+i*.004 for i in range(n)],
        r_3=[.02+i*.004 for i in range(n)], r_7=[.01+i*.004 for i in range(n)],
        dd_60=[-.2]*n, dsl_30=[5.]*n, up_7=[.1]*n, ma7_dev=[.04]*n))


def test_peer_confirmation_excludes_invalid_quotes_and_future():
    a=peer_day(); b=a.copy(); b.date+=pd.Timedelta(days=1);b.r_1=-.99
    base=add_peer_features(a);full=add_peer_features(pd.concat([a,b],ignore_index=True))
    assert base.leader_score.tolist()==full.iloc[:len(a)].leader_score.tolist()
    a.loc[11,'eligible']=False;a.loc[11,'r_1']=100
    out=add_peer_features(a)
    assert out.peer_n.iloc[0]==11
    assert pd.isna(out.leader_score.iloc[11])


def test_reversal_does_not_require_ma90_or_old_bottom_and_no_date_override():
    a=add_peer_features(peer_day());r=reversal_rules('2026-10-11')[1]
    assert strategy_mask(a,r).all()
    a.peer_breadth1=.2
    assert not strategy_mask(a,r).any()


def test_relative_rank_alone_not_leader_in_falling_group():
    a=peer_day();a.r_3=-.1;a.r_7=-.1
    assert not add_peer_features(a).leader_flag.any()


def test_early_leader_can_precede_group_recovery_without_becoming_buy():
    a=peer_day();a.r_1=-.04;a.r_3=-.1;a.r_7=-.2
    a.loc[11,['r_1','r_3','r_7']]=[.12,-.01,-.05]
    out=add_peer_features(a)
    assert out.leader_early_flag.iloc[11]==1
    r=reversal_rules('2026-10-11')[1]
    watch=leader_watch(out,[r],pd.Timestamp('2026-08-22'))
    assert not watch.empty
    assert watch['扫描放行'].iloc[0]=='未通过'


def test_leader_observation_does_not_bypass_health_gate():
    a=add_peer_features(peer_day());r=reversal_rules('2026-10-11')[1];r['status']='probation'
    out=leader_watch(a,[r],pd.Timestamp('2026-08-22'))
    assert not out.empty
    assert (out['扫描放行']=='未通过').all()
