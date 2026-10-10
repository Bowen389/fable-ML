import tempfile
from pathlib import Path
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
from cs2 import features, scan, monitor, config as C, ml


def bars(n=170):
    dates = pd.date_range('2025-01-01', periods=n)
    price = 10 + np.arange(n) * .03 + np.sin(np.arange(n)) * .05
    return pd.DataFrame(dict(name='item', cat='gun_FN', date=dates, open=price, close=price, high=price+.1, low=price-.1))


def test_future_append_does_not_rewrite_history():
    raw = bars(); raw.loc[25, 'close'] = np.nan
    short = features.clean_bars(raw.iloc[:145], log=lambda x: None)
    long = features.clean_bars(raw, log=lambda x: None)
    assert_frame_equal(short, long[long.date <= short.date.max()].reset_index(drop=True))
    a, _ = features.build_features(short); b, _ = features.build_features(long)
    cols = ['date', 'eligible', 'observed'] + features.feature_cols(a)
    assert_frame_equal(a[cols], b.loc[b.date <= a.date.max(), cols].reset_index(drop=True))
    assert np.isnan(short.loc[25, 'raw_close'])
    assert not short.loc[25, 'observed']
    assert not short.loc[118, 'eligible']


def test_missing_quote_invalidates_forward_label():
    raw = bars(); raw.loc[150, 'close'] = np.nan
    feat, _ = features.build_features(features.clean_bars(raw, log=lambda x: None))
    assert np.isnan(feat.loc[149, 'fwdL_10'])
    assert 'eligible' not in features.feature_cols(feat)
    assert 'raw_close' not in features.feature_cols(feat)


def test_market_filter_and_probation_do_not_emit():
    feat, _ = features.build_features(features.clean_bars(bars(), log=lambda x: None))
    r = dict(id='T', name='T', H=10, hold='10天', status='active', conds=[['logp', '>=', 0]], mkt_filter=[['mkt_r_7', '<=', -1]])
    hits, _ = scan.scan_rules(feat, [r], feat.date.max())
    assert hits.empty
    r['mkt_filter'] = []; r['status'] = 'probation'
    assert scan.scan_rules(feat, [r], feat.date.max())[0].empty


def test_ml_sort_uses_matching_horizon():
    hits = pd.DataFrame({'规则':['R','R'], '饰品':['a','b'], '_H':[14,14], '距60日高%':[-90,-10], 'ML分位14':[5,95]})
    assert scan.sort_hits(hits)['饰品'].tolist() == ['b','a']


def test_settlement_never_fills_missing_quote(monkeypatch):
    raw = bars(); raw.loc[150, 'close'] = np.nan
    clean = features.clean_bars(raw, log=lambda x: None)
    sig = pd.DataFrame([dict(name='item', entry_date=raw.date[150], exit_date=raw.date[160], entry_price=np.nan, status='pending', net_ret=np.nan, pipeline_version=C.PIPELINE_VERSION)])
    monkeypatch.setattr(monitor, 'load_signals', lambda: sig.copy())
    monkeypatch.setattr(monitor, 'save_signals', lambda x: None)
    out = monitor.settle_signals(clean, raw.date[165])
    assert out.status[0] == 'cancelled'; assert np.isnan(out.entry_price[0])


def test_manual_disable_stays_disabled():
    feat, _ = features.build_features(features.clean_bars(bars(240), log=lambda x: None))
    rule = dict(id='T', name='T', H=10, status='disabled', conds=[['logp','>=',0]], created='2025-01-01')
    _, updates = monitor.Health(feat).table([rule], feat.date.max())
    assert 'T' not in updates


def test_duplicate_item_not_logged_twice(monkeypatch):
    hits = pd.DataFrame({'规则':['A','B'], '饰品':['item','item'], '品类':['gun_FN']*2, '价格':[10,10], '_H':[10,14], '_rid':['A','B'], '_mk':[True,True]})
    saved=[]
    monkeypatch.setattr(scan, 'load_signals', lambda: pd.DataFrame(columns=scan.SIG_COLS))
    monkeypatch.setattr(scan, 'save_signals', saved.append)
    assert scan.log_signals(hits, pd.Timestamp('2025-01-01')) == 1
    monkeypatch.setattr(scan, 'load_signals', lambda: saved[0])
    assert scan.log_signals(hits, pd.Timestamp('2025-01-02')) == 0


def test_legacy_model_rejected(monkeypatch, tmp_path):
    meta=tmp_path/'meta.json'; meta.write_text('{}')
    monkeypatch.setattr(ml, 'META_PATH', str(meta))
    assert ml.load_models([], log=lambda x: None) == {}
