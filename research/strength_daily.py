"""Render historical or single-day strength rankings as Markdown."""
import argparse
import csv
from datetime import date
from statistics import median

from strength_rank import DAY, GROUP, rank_day, read_bars


def render_table(items, pool, features):
    print('| 名次 | 饰品 | 转强分 | 近3日 | 近5日 |')
    print('|---:|---|---:|---:|---:|')
    for rank, (name, score) in enumerate(items, 1):
        r3, r5, _, _ = features[name]
        label = pool[name].replace(' | ', ' ／ ')
        print(f'| {rank} | {label} | {score:.2f} | {r3:+.2%} | {r5:+.2%} |')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bars', nargs='+', required=True)
    parser.add_argument('--pool', required=True)
    parser.add_argument('--start', type=date.fromisoformat, required=True)
    parser.add_argument('--end', type=date.fromisoformat, required=True)
    args = parser.parse_args()
    if args.start > args.end:
        parser.error('--start must be on or before --end')
    bars = read_bars(args.bars)
    with open(args.pool, encoding='utf-8-sig') as handle:
        pool = {row['name']: row['cn'] for row in csv.DictReader(handle)}
    print('# 每日转强 Top20')
    print()
    print(f'报告日 {args.start} 至 {args.end}（北京时间）。按上一日及更早、且报告日已抓取的完整日 K 评分。')
    print('一代手套略磨单独排组内榜，不占全池 Top20 名额。所有品沿用研究版转强公式和原监控池中位数基准。')
    print('近 3 日和近 5 日均上涨才参与排名。组内榜列出所有达标品。历史使用当前监控池回看，结果供研究观察。')
    print()
    print('复现命令')
    print()
    print('```sh')
    print(f'python research/strength_daily.py --bars data/bars/2026-10.csv.gz data/bars/2026-11.csv --pool output/decision_latest.csv --start {args.start} --end {args.end}')
    print('```')
    signal = args.end
    while signal >= args.start:
        ranked, features = rank_day(bars, pool, signal)
        general = [(n, s) for n, s in ranked if n not in GROUP]
        gloves = [(n, s) for n, s in ranked if n in GROUP]
        observed = [features[n] for n in GROUP if n in features]
        print(f'\n## {signal}')
        print(f'\n最新完整日 K {signal - DAY}。全池有连续数据 {len(features)} 件。')
        print('\n### 转强 Top20\n')
        if general:
            render_table(general[:20], pool, features)
        else:
            print('本日无符合条件的候选。')
        print('\n### 一代手套略磨组内榜\n')
        print(f'监控覆盖 {len(GROUP & pool.keys())}/{len(GROUP)} 件，有连续数据 {len(observed)} 件，达到转强条件 {len(gloves)} 件。')
        if observed:
            print(f'近 3 日上涨 {sum(f[0] > 0 for f in observed)}/{len(observed)}，涨幅中位数 {median(f[0] for f in observed):+.2%}。'
                  f'近 5 日上涨 {sum(f[1] > 0 for f in observed)}/{len(observed)}，涨幅中位数 {median(f[1] for f in observed):+.2%}。')
        if gloves:
            print()
            render_table(gloves, pool, features)
        signal -= DAY


if __name__ == '__main__':
    main()
