"""Read-only integration baseline. Does not retrain, notify, or place orders."""
import ast
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile
from datetime import datetime, timedelta, timezone
import urllib.request

TZ = timezone(timedelta(hours=8))
ROOT = Path(__file__).resolve().parent
NAME = 'Glock-18 | Dragon Tattoo (Factory New)'


def fetch(url):
    with urllib.request.urlopen(url, timeout=90) as response:
        return response.read()


def raw(repo, path):
    return 'https://raw.githubusercontent.com/' + repo + '/main/' + path


def assess(signal, current, manual, market):
    """Missing evidence cannot become positive confirmation or an entry order."""
    result = {'status': '观察候选', 'supply_change_pct': None,
              'demand_change_pct': None, 'price_change_pct': None}
    if not signal or not current:
        result['status'] = '数据不足'
        return result
    result['price_change_pct'] = (current['price'] / signal['close'] - 1) * 100
    if manual and manual.get('on_sale'):
        result['supply_change_pct'] = (current['on_sale'] / manual['on_sale'] - 1) * 100
    result['demand_description'] = '用户报告持平；未计算精确变动率' if manual and manual.get('demand_change') == 'flat' else '未取得可比厚度'
    result['market_weak'] = market.get('above_ma30_pct', 100) < 20
    return result


def main():
    now = datetime.now(TZ)
    evidence = json.loads((ROOT / 'guide_observations.json').read_text())
    assert evidence['item'] == NAME and evidence['yyyp_id'] == 43712
    sources, errors = {}, []
    def obtain(label, url):
        payload = fetch(url)
        sources[label] = {'url': url, 'sha256': hashlib.sha256(payload).hexdigest()}
        return payload

    # Stream the full source CSV, retaining only the exact wear/quality variant.
    url = raw('huvan9527-a11y/buy-cs', 'data/steamdt_daily_1y_raw.csv')
    digest = hashlib.sha256()
    with urllib.request.urlopen(url, timeout=90) as response:
        payload = response.read()
    digest.update(payload)
    sources['buy_bars'] = {'url': url, 'sha256': digest.hexdigest()}
    bars = []
    for row in csv.DictReader(io.StringIO(payload.decode('utf-8-sig'))):
        if row['marketHashName'] == NAME:
            bars.append({'date': row['date'], **{key: float(row[value]) for key, value in
                         [('open', 'v1'), ('close', 'v2'), ('high', 'v3'), ('low', 'v4')]}})
    del payload
    # Exclude the unfinished current day even if the upstream CSV contains it.
    bars = sorted((r for r in bars if r['date'] < now.date().isoformat()), key=lambda r: r['date'])
    if not bars:
        raise RuntimeError('No completed candles for exact marketHashName')
    code = obtain('buy_rules', raw('huvan9527-a11y/buy-cs', 'scanner.py')).decode()
    wanted = {'cross', 'ema', 'sma', 'signal_types', 'family_count'}
    nodes = [n for n in ast.parse(code).body if isinstance(n, ast.FunctionDef) and n.name in wanted]
    if {n.name for n in nodes} != wanted:
        raise RuntimeError('Upstream signal function interface changed')
    ns = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), 'upstream-buy-rules', 'exec'), ns)
    types = ns['signal_types'](bars)
    signal = {**bars[-1], 'types': types, 'families': ns['family_count'](types)}

    market_md = obtain('fable_report', raw('Bowen389/fable-ML', 'output/latest.md')).decode()
    meta = json.loads(obtain('fable_model', raw('Bowen389/fable-ML', 'state/ml_meta.json')))
    date_match = re.search(r'CS2 买点扫描 · (\d{4}-\d{2}-\d{2})', market_md)
    breadth = re.search(r'站上MA30占比 ([\d.]+)%', market_md)
    market = {'date': date_match.group(1) if date_match else None,
              'above_ma30_pct': float(breadth.group(1)) if breadth else None,
              'ml_validation': {h: bool(v.get('validated')) for h, v in meta.get('val', {}).items()},
              'note': '原有规则的通过/未通过不等于buy-cs形态的验证结论；不产生未经验证的ML评分'}
    if market['above_ma30_pct'] is None:
        market.pop('above_ma30_pct')

    observations = [r for r in evidence['observations'] if r['kind'] != 'manual_approximate']
    try:
        db_bytes = obtain('up_database', raw('Bowen389/up', 'data/yyyp.db'))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'source.db'
            path.write_bytes(db_bytes)
            with sqlite3.connect(f'file:{path}?mode=ro', uri=True) as db:
                row = db.execute('SELECT run,name,min_price,on_sale,depth,depth_qty FROM snapshot WHERE tid=? ORDER BY run DESC LIMIT 1', (43712,)).fetchone()
            if row:
                observations.append({'at': row[0], 'name': row[1], 'price': row[2],
                                     'on_sale': row[3], 'depth': row[4], 'depth_qty': row[5],
                                     'kind': 'repository_snapshot', 'source': sources['up_database']['url'],
                                     'note': 'run仅精确到日期或分钟，并非逐笔行情时间；厚度阈值沿用up配置'})
    except Exception as exc:
        errors.append('正式求购数据库读取失败：' + type(exc).__name__)

    def observation_time(row):
        text = row['at']
        dt = datetime.fromisoformat(text)
        return dt.replace(tzinfo=TZ) if dt.tzinfo is None else dt
    current = max(observations, key=observation_time) if observations else None
    manual = next((r for r in evidence['observations'] if r['kind'] == 'manual_approximate'), None)
    # Only compare the manually supplied previous-day observation to its matching day.
    comparable_manual = manual if current and manual and observation_time(current).date() == datetime.fromisoformat(manual['at']).date() + timedelta(days=1) else None
    result = assess(signal, current, comparable_manual, market)
    signal_age = (now.date() - datetime.fromisoformat(signal['date']).date()).days
    current_age = (now - observation_time(current)).total_seconds() / 3600 if current else None
    if not types:
        result['status'] = '最新完整日无技术买点'
    if signal_age > 1 or current_age is None or current_age > 24:
        result['status'] = '数据过期，等待更新'
    if not market.get('date') or (now.date() - datetime.fromisoformat(market['date']).date()).days > 1:
        errors.append('市场报告缺失日期或已过期；不作当前市场确认')
    report = {'version': 'guide-baseline-v1', 'generated_at': now.isoformat(),
              'item': NAME, 'mapping': {'yyyp_id': 43712, 'csqaq_id': 1114},
              'signal': signal, 'current_supply': current, 'manual_comparison': comparable_manual,
              'supply_age_hours': current_age, 'market': market, 'assessment': result,
              'whale': {'role': '辅助', 'status': '未接入本轮报告；不参与打分或否决'},
              'errors': errors, 'sources': sources,
              'limitations': ['未验证策略收益，不给胜率或最优参数结论', '在售减少不等于成交',
                              '求购厚度是阈值内挂单金额，不是成交量', '不同采集时间及价格口径不能算实际收益',
                              '519为最低挂牌价，不保证可成交；本报告不自动下单']}
    out = ROOT / 'output'
    out.mkdir(exist_ok=True)
    (out / 'guide_latest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    fmt = lambda v: '缺失' if v is None else f'{v:+.2f}%'
    lines = ['# 统一交易指导 · 基准版', '', f'商品：{NAME}', f'生成时间：{now.isoformat(timespec="seconds")}', '',
             '| 项目 | 证据 |', '|---|---|',
             f'| 技术买点 | {signal["date"]}；{signal["families"]}类：{"＋".join(types) or "无"}；日K收盘指数 {signal["close"]:.2f} |',
             f'| 求购快照 | {current["at"] if current else "缺失"}；底价 {current["price"] if current else "缺失"}；在售 {current["on_sale"] if current else "缺失"}；厚度 {current["depth"] if current else "缺失"} |',
             f'| 快照来源 | {current["kind"] if current else "缺失"}；日志厚度可能有取整 |',
             f'| 价格差异 | 相对技术信号日收盘指数 {fmt(result.get("price_change_pct"))}；非实际交易收益 |',
             f'| 在售变化 | {fmt(result.get("supply_change_pct"))}；仅在日期可比时采用用户提供的昨日同期约350件 |',
             f'| 求购变化 | {result.get("demand_description", "缺失")} |',
             f'| 市场背景 | {market.get("date")}；站上MA30比例 {market.get("above_ma30_pct", "缺失")}% |',
             f'| ML启用资格 | {market["ml_validation"]}；仅展示资格，不伪造评分 |',
             '| Whale | 辅助信息，本轮未接入，不设硬门槛 |', '',
             '**当前分类：' + result['status'] + '**', '',
             '技术信号、供需及市场环境分别展示。基准版不把指标个数当胜率，不宣称供需共振。', '',
             '## 数据限制', *['- ' + x for x in report['limitations']], *['- ' + x for x in errors], '',
             '## 来源', *[f'- {key}: {value["url"]}' for key, value in sources.items()],
             '- 单品实时采样：https://github.com/Bowen389/up/actions/runs/39430760444',
             '- 昨日同期350件及求购持平：用户提供的近似观察，非自动采集。', '']
    markdown = '\n'.join(lines)
    (out / 'guide_latest.md').write_text(markdown, encoding='utf-8')
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as handle:
            handle.write(markdown)
    print(json.dumps({'status': result['status'], 'signal_date': signal['date'], 'supply_at': current['at'] if current else None, 'errors': errors}, ensure_ascii=False))


if __name__ == '__main__':
    main()
