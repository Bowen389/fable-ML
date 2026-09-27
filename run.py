# -*- coding: utf-8 -*-
"""
用法：
  python run.py scan                      # 取数 → 特征 → 扫描 → 结算 → 健康度 → 报告/推送
  python run.py learn --retune --mine --ml [--apply-retune] [--add-mined] [--mine-h 10,14,30]
  python run.py init-seed a.csv b.csv     # 把 SteamDT 导出的历史 CSV 导入 data/bars/
环境变量见 cs2/config.py；DATA_SOURCE=offline 可在没有 API key 时用本地数据跑通全流程。
"""
import sys, os, time, argparse, warnings
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
pd.set_option('display.width', 220); pd.set_option('display.max_columns', 60); pd.set_option('display.max_rows', 300)

from cs2 import config as C
from cs2 import data, features, rules as R, scan as S, monitor as M, report, notify

def log(*a):
    print(*a, flush=True)


def load_all():
    universe = data.load_universe()
    bars = data.load_bars()
    if C.DATA_SOURCE == 'api' and not C.API_KEY:
        log('⚠️ 没有 STEAMDT_API_KEY，改为 offline 模式（只用本地数据）'); C.DATA_SOURCE = 'offline'
    bars, info = data.refresh(universe, bars, log=log)
    broad = data.fetch_broad(log=log)
    use = data.usable_bars(bars, universe)
    del bars
    if use.empty:
        raise SystemExit('没有可用数据：请先 python run.py init-seed <历史CSV>，或检查 API key / universe.csv')
    log(f'可用 K 线：{len(use):,} 行，{use.name.nunique()} 个饰品，{use.date.min().date()} → {use.date.max().date()}')
    t0 = time.time()
    clean = features.clean_bars(use, log=log); del use
    feat, mk = features.build_features(clean)
    last = feat['date'].max()
    log(f'特征表 {feat.shape}，最新日期 {last.date()}，用时 {time.time() - t0:.0f}s')
    return universe, clean, feat, last, info, broad


def cmd_scan(args):
    universe, clean, feat, last, info, broad = load_all()
    rules = R.load_rules()
    snap, notes = S.market_snapshot(feat, last)
    log(f'\n===== 市场状态 @ {last.date()} =====')
    for n in notes: log(' •', n)
    broad_line = ''
    if broad is not None and len(broad) > 31:
        b = broad.set_index('date')['close']
        broad_line = f'SteamDT 官方大盘指数 {b.iloc[-1]:.2f}（{b.index[-1].date()}），7日 {b.iloc[-1] / b.iloc[-8] - 1:+.1%}，30日 {b.iloc[-1] / b.iloc[-31] - 1:+.1%}'
    # ML
    ml_note = ''
    try:
        from cs2 import ml
        models = ml.load_models(features.feature_cols(feat), log=log)
        scorer = ml.make_scorer(models)
        if models: ml_note = f'ML分位列来自 LightGBM（H={list(models)}），= 当日全市场内"跑赢中位数"预测的百分位，只用于同一规则候选间排序'
    except Exception as e:
        log('ML 模型加载失败（忽略）:', e); scorer = None
    hits, near = S.scan_rules(feat, rules, last, ml_scores=scorer)
    n_items = int((feat.date == last).sum())
    log(f'\n===== 买点扫描 @ {last.date()}（{n_items} 个饰品）=====')
    if hits.empty:
        log('没有饰品满足任何规则')
    else:
        log(hits.groupby('规则').size().to_string())
        show = hits.drop(columns=['_H', '_rid', '_mk']).sort_values(['规则', '距60日高%'])
        show.to_csv(C.P('output', 'history', f'screen_{last.date()}.csv'), index=False, encoding='utf-8-sig')
        show.to_csv(C.P('output', 'screen_latest.csv'), index=False, encoding='utf-8-sig')
        log(show.to_string(index=False))
    if not near.empty:
        log(f'\n接近满足 {len(near)} 条'); log(near.groupby('规则').size().to_string())
    n_new = S.log_signals(hits, last) if (C.SAVE_SIGNALS and not args.no_signals) else 0
    if n_new: log(f'信号日志新增 {n_new} 条')
    # 结算 + 健康度
    sig = M.settle_signals(clean, last)
    health, new_status = M.Health(feat).table(rules, last)
    log('\n===== 规则健康度 ====='); log(health.to_string(index=False))
    if new_status:
        for rid, (old, ns, s90, s180) in new_status.items():
            log(f'  → {rid}: {old} → {ns}（90日 n={s90["n"]} 跑赢中位 {s90["beat"]:.0%}）')
        if C.AUTO_UPDATE_STATUS:
            M.apply_status(rules, new_status, last); log('已更新规则状态')
    ctx = dict(last=last, snap=snap, notes=notes, hits=hits, near=near, sig=sig, health=health, new_status=new_status if C.AUTO_UPDATE_STATUS else {},
               fetch_info=info, n_items=n_items, broad_line=broad_line, ml_note=ml_note)
    md = report.build_markdown(ctx)
    with open(C.P('output', 'latest.md'), 'w', encoding='utf-8') as f: f.write(md)
    with open(C.P('output', 'history', f'report_{last.date()}.md'), 'w', encoding='utf-8') as f: f.write(md)
    short = report.build_short(ctx)
    if not args.no_notify:
        sent = notify.send(f'CS2 买点 {last.date()}', short, md=md)
        if sent: log('推送:', sent)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as f: f.write(md)
    log('\n' + short)
    log('\n报告已写入 output/latest.md')


def cmd_learn(args):
    from cs2 import learn, ml
    universe, clean, feat, last, info, broad = load_all()
    rules = R.load_rules()
    L = [f'# 学习任务 · {last.date()}', '']
    if args.retune:
        log('\n===== ① 重新调参 =====')
        prop = learn.retune(feat, rules, last, max_steps=args.max_steps, apply=args.apply_retune, log=log)
        log(prop.drop(columns=['_conds']).to_string(index=False))
        L.append(f"## ① 重新调参（{'已应用' if args.apply_retune else '仅建议'}）"); L.append(report.md_table(prop.drop(columns=['_conds'])))
    if args.mine:
        log('\n===== ② 重新挖掘 =====')
        hs = [int(h) for h in args.mine_h.split(',')]
        res = learn.mine(feat, rules, last, hs=hs, feats=args.mine_feats, depth=args.depth, beam=args.beam, oos_days=args.oos_days, add=args.add_mined, log=log)
        for H, rows in res.items():
            tab = pd.DataFrame(rows)
            if len(tab):
                tab = tab.drop(columns=['_conds']); log(f'\nH={H}:'); log(tab.to_string(index=False))
            L.append(f"## ② 重新挖掘 H={H}（通过时序外测试的才可用；{'已加入 probation' if args.add_mined else '仅记录'}）"); L.append(report.md_table(tab))
    if args.ml:
        log('\n===== ③ LightGBM =====')
        lines = ml.train(feat, rules, last, val_days=args.val_days, rounds=args.rounds, log=log)
        L.append('## ③ LightGBM 排序模型'); L += [f'- {x}' for x in lines]
    md = '\n'.join(L) + '\n'
    with open(C.P('output', f'learn_{last.date()}.md'), 'w', encoding='utf-8') as f: f.write(md)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as f: f.write(md)
    if not args.no_notify:
        notify.send(f'CS2 学习任务 {last.date()}', md[:1800], md=md)
    log('\n学习结果已写入 output/learn_*.md 与 state/')


def cmd_init_seed(args):
    data.import_seed_csvs(args.files)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest='cmd', required=True)
    a = sp.add_parser('scan'); a.add_argument('--no-signals', action='store_true'); a.add_argument('--no-notify', action='store_true')
    b = sp.add_parser('learn')
    b.add_argument('--retune', action='store_true'); b.add_argument('--apply-retune', action='store_true'); b.add_argument('--max-steps', type=int, default=2)
    b.add_argument('--mine', action='store_true'); b.add_argument('--add-mined', action='store_true'); b.add_argument('--mine-h', default='14')
    b.add_argument('--mine-feats', default='item', choices=['item', 'pure']); b.add_argument('--depth', type=int, default=3); b.add_argument('--beam', type=int, default=8)
    b.add_argument('--oos-days', type=int, default=150)
    b.add_argument('--ml', action='store_true'); b.add_argument('--val-days', type=int, default=90); b.add_argument('--rounds', type=int, default=300)
    b.add_argument('--no-notify', action='store_true')
    c = sp.add_parser('init-seed'); c.add_argument('files', nargs='+')
    args = ap.parse_args()
    {'scan': cmd_scan, 'learn': cmd_learn, 'init-seed': cmd_init_seed}[args.cmd](args)
