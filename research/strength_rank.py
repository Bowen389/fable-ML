"""Offline daily strength study. No production integration."""
import argparse
import csv
import gzip
import json
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from statistics import mean, median

DAY = timedelta(days=1)
GEN1 = {
    'Bloodhound Gloves': ['Charred', 'Snakebite', 'Bronzed', 'Guerrilla'],
    'Sport Gloves': ['Hedge Maze', "Pandora's Box", 'Superconductor', 'Arid'],
    'Driver Gloves': ['Crimson Weave', 'Lunar Weave', 'Convoy', 'Diamondback'],
    'Hand Wraps': ['Leather', 'Spruce DDPAT', 'Slaughter', 'Badlands'],
    'Moto Gloves': ['Spearmint', 'Cool Mint', 'Boom!', 'Eclipse'],
    'Specialist Gloves': ['Crimson Kimono', 'Emerald Web', 'Foundation', 'Forest DDPAT'],
}
GROUP = {f'★ {kind} | {skin} (Minimal Wear)' for kind, skins in GEN1.items() for skin in skins}
WATCH = ('AK-47 | Phantom Disruptor (Factory New)', 'M4A1-S | Player Two (Factory New)')


def read_bars(paths):
    bars = defaultdict(dict)
    for path in paths:
        opener = gzip.open if path.endswith('.gz') else open
        with opener(path, 'rt', encoding='utf-8-sig') as handle:
            for row in csv.DictReader(handle):
                d = date.fromisoformat(row['date'])
                fetched = date.fromisoformat(row['fetched'])
                if d >= fetched:
                    continue
                try:
                    o, c, h, lo = (float(row[k]) for k in ('open', 'close', 'high', 'low'))
                except (TypeError, ValueError):
                    continue
                if min(o, c, h, lo) > 0:
                    bars[row['name']][d] = (o, c, h, lo, fetched)
    return bars


def feature(series, signal):
    history = [series.get(signal - DAY * lag) for lag in range(6, 0, -1)]
    if any(b is None or b[4] > signal for b in history):
        return None
    closes = [b[1] for b in history]
    r3, r5 = closes[-1] / closes[-4] - 1, closes[-1] / closes[0] - 1
    up = sum(a < b for a, b in zip(closes, closes[1:])) / 5
    near_high = closes[-1] / max(b[2] for b in history)
    return r3, r5, up, near_high


def rank_day(bars, pool, signal):
    features = {name: f for name in pool if (f := feature(bars[name], signal))}
    if not features:
        return [], features
    centers = [median(f[i] for f in features.values()) for i in (0, 1)]
    def clip(x):
        return max(0, min(1, x))
    scores = {}
    for name, (r3, r5, up, near_high) in features.items():
        if r3 <= 0 or r5 <= 0:
            continue
        scores[name] = (
            35 * clip((r3 - centers[0]) / .12)
            + 30 * clip((r5 - centers[1]) / .20)
            + 20 * up + 15 * clip((near_high - .90) / .10)
            - 15 * clip((r5 - .25) / .25)
        )
    return sorted(scores.items(), key=lambda item: (-item[1], item[0])), features


def evaluate(bars, names, signal, horizon):
    entry, exit_day = signal + DAY, signal + horizon * DAY
    results = []
    for name in names:
        series = bars[name]
        period = [series.get(entry + i * DAY) for i in range(horizon)]
        if not period[0] or not series.get(exit_day):
            continue
        entry_price = period[0][0]
        adverse = min(b[3] for b in period) / entry_price - 1 if all(period) else None
        results.append((series[exit_day][1] * .99 / entry_price - 1, adverse))
    return results


def summarize(rows):
    if not rows:
        return '—'
    returns = [r[0] for r in rows]
    adverse = [r[1] for r in rows if r[1] is not None]
    worst = f'{min(adverse):.2%}' if adverse else '—'
    return f'{len(returns)} | {mean(returns):+.2%} | {mean(x > 0 for x in returns):.1%} | {worst}'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bars', nargs='+', required=True)
    parser.add_argument('--pool', required=True, help='CSV whose first two columns are name and cn')
    parser.add_argument('--baseline', required=True, help='JSON mapping report date to historical potential Top5 rows')
    args = parser.parse_args()
    bars = read_bars(args.bars)
    with open(args.pool, encoding='utf-8-sig') as handle:
        pool = dict(list(row[:2]) for row in list(csv.reader(handle))[1:] if len(row) >= 2)
    chinese = {cn.replace(' | ', ' ／ ', 1): en for en, cn in pool.items()}
    baseline = json.loads(Path(args.baseline).read_text())
    dates = sorted(date.fromisoformat(d) for d, snap in baseline.items() if snap['rows'])
    cutoff = max(d for name in pool for d in bars[name])
    ranks = {signal: rank_day(bars, pool, signal) for signal in dates + [cutoff + DAY]}
    print(f'原榜与转强榜的配对信号范围 {dates[0]} 至 {dates[-1]}。完整日K截止 {cutoff}。')
    print('\n| 持有观察点 | 榜单 | 成熟信号日 | 有效笔数 | 平均净收益 | 胜率 | 最差不利变动 |')
    print('|---|---|---:|---:|---:|---:|---:|')
    for h in (8, 10, 14):
        eligible = [d for d in dates if d + h * DAY <= cutoff and ranks[d][0]]
        for kind in ('原潜力 Top5', '转强 Top5'):
            rows = []
            for d in eligible:
                selected = ([chinese[row[0]] for row in baseline[str(d)]['rows'] if row[0] in chinese]
                            if kind.startswith('原') else [name for name, _ in ranks[d][0][:5]])
                rows.extend(evaluate(bars, selected, d, h))
            print(f'| 第 {h} 天 | {kind} | {len(eligible)} | {summarize(rows)} |')
    print('\n| 饰品 | 首次进入转强 Top5 | 最新转强排名 |')
    print('|---|---|---:|')
    latest, feats = ranks[cutoff + DAY]
    first_outcomes = []
    for name in WATCH:
        first = next((str(d) for d in sorted(ranks) if name in dict(ranks[d][0][:5])), '样本内未进')
        rank = next((i for i, (n, _) in enumerate(latest, 1) if n == name), '—')
        label = pool[name].replace(' | ', ' ／ ')
        print(f'| {label} | {first} | {rank} |')
        if first != '样本内未进':
            d = date.fromisoformat(first)
            for horizon in (8, 10, 14):
                if d + horizon * DAY <= cutoff and (outcome := evaluate(bars, [name], d, horizon)):
                    first_outcomes.append(f'- {label} 首次上榜后第 {horizon} 天净收益 {outcome[0][0]:+.2%}。')
    if first_outcomes:
        print('\n' + '\n'.join(first_outcomes))
    print('\n最新转强 Top5')
    for i, (name, score) in enumerate(latest[:5], 1):
        r3, r5, _, _ = feats[name]
        print(f'{i}. {pool[name]} · {score:.2f} 分 · 3 日 {r3:+.2%} · 5 日 {r5:+.2%}')
    group = [feats[n] for n in GROUP if n in feats]
    print(f'\n一代略磨监控 {len(GROUP & pool.keys())}/{len(GROUP)} 件，{len(group)} 件有连续有效数据。')
    if group:
        print(f'3 日上涨 {sum(f[0] > 0 for f in group)}/{len(group)}，中位 {median(f[0] for f in group):+.2%}。'
              f'5 日上涨 {sum(f[1] > 0 for f in group)}/{len(group)}，中位 {median(f[1] for f in group):+.2%}。')


if __name__ == '__main__':
    main()
