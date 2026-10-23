"""Evaluate immutable daily ranks; no API calls, fitting, or trading."""
import csv,gzip,json,statistics
from datetime import date,datetime,timedelta,timezone
from pathlib import Path

def prices(payload,today):
    out={}
    for r in payload.get('data',[]):
        try:
            ts=float(r[0]);ts=ts/1000 if ts>1e12 else ts
            day=datetime.fromtimestamp(ts,timezone(timedelta(hours=8))).date()
            op,close=float(r[1]),float(r[2])
            if day<today and min(op,close)>0:out[day]=(op,close)
        except (ValueError,TypeError,IndexError,OverflowError):continue
    return out

def outcome(bars,signal,horizon):
    # Signal needs the completed daily close. Earliest proxy entry is next day's open.
    entry=signal+timedelta(days=1);exit=entry+timedelta(days=horizon)
    if entry not in bars or exit not in bars:return None
    return bars[exit][1]/bars[entry][0]*.99-1

def summarize(values):
    return dict(n=len(values),mean=statistics.mean(values) if values else None,
                median=statistics.median(values) if values else None,
                win_rate=sum(v>0 for v in values)/len(values) if values else None)

def run(root,today=None):
    root=Path(root);today=today or datetime.now(timezone(timedelta(hours=8))).date()
    groups={};details=[];cache={};snapshots=[]
    universe=root/'firepulse_universe.json'
    ids={r['name']:str(r['id']) for r in json.loads(universe.read_text())} if universe.exists() else {}
    for path in sorted((root/'output/history').glob('decision_ready_*_decision-v1.json')):
        doc=json.loads(path.read_text());generated=datetime.fromisoformat(doc['generated_at'])
        if generated.date()!=date.fromisoformat(doc['asof'])+timedelta(days=1):continue
        rows=[]
        for r in doc.get('rows',[]):
            if r.get('potential') is None:continue
            rows.append(dict(name=r['name'],id=ids.get(r['name'],''),每日参考分=r['potential'],
                价格日期=str(generated.date()),算法版本='decision-potential-'+doc['version'],
                生成时间=doc['generated_at'],entry_quote=r.get('quote')))
        if rows:snapshots.append(rows)
    # Process scores are prospectively frozen before their outcomes exist.
    for path in sorted((root/'output/history').glob('process_scores_*.csv')):
        with path.open(encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
        if rows:snapshots.append(rows)
    for rows in snapshots:
        signal=date.fromisoformat(rows[0]['价格日期'][:10]);version=rows[0]['算法版本']
        # Exclude retrospectively generated snapshots from forward evidence.
        generated=datetime.fromisoformat(rows[0]['生成时间'])
        if generated.date()>signal+timedelta(days=1):continue
        signal=generated.date() # Never use an open preceding publication.
        rows.sort(key=lambda r:(-float(r['每日参考分']),r['name']))
        for k in (3,5):
            for h in (7,14):
                key=(version,k,h);g=groups.setdefault(key,dict(expected=0,values=[],baseline=[],days=set()))
                if signal+timedelta(days=h+(0 if 'entry_quote' in rows[0] else 1))>=today:continue
                g['expected']+=min(k,len(rows));g['days'].add(str(signal))
                baseline=[]
                for i,row in enumerate(rows):
                    item=str(row['id']);p=root/'research_cache'/f'{item}.json.gz'
                    if item not in cache:
                        if p.exists():
                            with gzip.open(p,'rt') as f:cache[item]=prices(json.load(f),today)
                        else:cache[item]={}
                    if 'entry_quote' in row:
                        exitday=signal+timedelta(days=h);bar=cache[item].get(exitday);quote=row['entry_quote']
                        value=bar[1]/float(quote)*.99-1 if bar and quote and float(quote)>0 else None
                    else:value=outcome(cache[item],signal,h)
                    if value is not None:baseline.append(value)
                    if i<k:
                        details.append(dict(signal=str(signal),version=version,top=k,horizon=h,name=row['name'],net=value))
                        if value is not None:g['values'].append(value)
                if baseline:g['baseline'].append(statistics.mean(baseline))
    result=[]
    for (version,k,h),g in sorted(groups.items()):
        s=summarize(g['values']);s.update(version=version,top=k,horizon=h,expected=g['expected'],
            coverage=len(g['values'])/g['expected'] if g['expected'] else None,signal_days=len(g['days']),
            pool_day_equal_mean=statistics.mean(g['baseline']) if g['baseline'] else None)
        result.append(s)
    out=root/'output';out.mkdir(exist_ok=True)
    report=dict(asof=str(today),status='observational_only',fee='sell 1%; buy 0; no slippage',
        entry='process: next day open; decision potential: published quote',exit='entry date + 7/14 calendar days close',
        results=result,details=details,promotion_allowed=False)
    (out/'learning_review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    fmt=lambda x:'待成熟' if x is None else f'{x:.2%}'
    lines=['# 每周 Top3／Top5 前瞻检查','',f'截至 {today}；卖出费1%，不考虑滑点。',
        '过程评分：评分发布次日开盘作为入场代理；综合决策潜力榜：按时发布快照中的挂牌价作为代理。7／14自然日后收盘退出，均非实际成交。',
        '仅检查按时留存的固定版本快照；缺日不插值，不将缺失算亏损或零收益。',
        '重复持有同一商品的观察会重叠，以下不是组合收益；全池日等权均值仅作描述对照。','',
        '|版本|前几名|持有天数|有效/应有|覆盖率|信号天数|平均净收益|中位数|胜率|全池日均对照|',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in result:lines.append(f'|{r["version"]}|{r["top"]}|{r["horizon"]}|{r["n"]}/{r["expected"]}|{fmt(r["coverage"])}|{r["signal_days"]}|{fmt(r["mean"])}|{fmt(r["median"])}|{fmt(r["win_rate"])}|{fmt(r["pool_day_equal_mean"])}|')
    if not any(r['n'] for r in result):lines+=['','目前没有已成熟且价格齐全的前瞻样本，不能判断评分有效。']
    lines+=['','本报告不触发参数替换或买入放行。月度训练候选保存在独立研究产物，须在相同未参与调参的时段与旧版比较，并检查最近90日和三个滚动窗口；证据不足继续沿用旧版。']
    (out/'learning_review.md').write_text('\n'.join(lines)+'\n')
    return report

if __name__=='__main__':run(Path(__file__).resolve().parent)
