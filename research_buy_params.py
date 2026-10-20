"""Frozen parameter grid; chronological validation; no live-rule mutations."""
import ast
import hashlib
import io
import json
import os
from pathlib import Path
import urllib.request
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
URL = 'https://raw.githubusercontent.com/huvan9527-a11y/buy-cs/main/data/steamdt_daily_1y_raw.csv'
HOLDS = (10, 14, 30)
FEE, SLIP = 0.025, 0.005


def signals(g):
    c, o, h, l = (g[k] for k in ['close', 'open', 'high', 'low'])
    def cross(a, b):
        return (a > b) & (a.shift() <= b.shift())
    lo, hi = l.rolling(9, min_periods=1).min(), h.rolling(9, min_periods=1).max()
    rsv = ((c-lo)/(hi-lo)*100).where(hi != lo, 50)
    k = rsv.ewm(alpha=1/3, adjust=False).mean()
    d = k.ewm(alpha=1/3, adjust=False).mean()
    kd = cross(k, d)
    def macd(window):
        found = pd.Series(False, index=g.index)
        for fast, slow, smooth in [(12, 26, 9), (5, 12, 4)]:
            dif = c.ewm(span=fast, adjust=False).mean()-c.ewm(span=slow, adjust=False).mean()
            found |= cross(dif, dif.ewm(span=smooth, adjust=False).mean()) & kd.rolling(window, min_periods=1).max().astype(bool)
        return found
    def ma(window):
        found = pd.Series(False, index=g.index)
        for a, b, z in [(5, 12, 21), (7, 14, 21)]:
            x, y, zz = (c.rolling(p).mean() for p in (a, b, z))
            bull = (x > y) & (y > zz)
            event = bull & ~bull.shift(fill_value=False)
            found |= bull & event.rolling(window, min_periods=1).max().astype(bool)
        return found
    def engulf(pct):
        body = (c.shift()-o.shift()).abs()
        upper = h.shift()-pd.concat([o.shift(),c.shift()],axis=1).max(axis=1)
        return (upper >= body) & (upper >= pct*c.shift()) & (c > h.shift())
    def needle(pct, position):
        found = pd.Series(False,index=g.index)
        for lag in (2,3):
            bottom = pd.concat([o.shift(lag),c.shift(lag)],axis=1).min(axis=1)
            body = (c.shift(lag)-o.shift(lag)).abs()
            lower = bottom-l.shift(lag)
            held = l.rolling(lag).min() >= bottom
            found |= ((lower >= .2*body) & (lower >= pct*c.shift(lag)) & held &
                      ((c.shift(lag)-l.shift(lag))/(h.shift(lag)-l.shift(lag)).clip(lower=1e-9) >= position) &
                      (c >= c.shift(lag)))
        return found
    out = {'双金叉_基准3日': macd(3), '双金叉_1日': macd(1), '双金叉_5日': macd(5),
           '均线合一_基准3日': ma(3), '均线合一_1日': ma(1), '均线合一_5日': ma(5),
           '上影吞没_基准1%': engulf(.01), '上影吞没_0.5%': engulf(.005), '上影吞没_2%': engulf(.02),
           '单针承接_基准2%_0.6': needle(.02,.6), '单针承接_3%_0.6': needle(.03,.6), '单针承接_2%_0.7': needle(.02,.7)}
    bases = [v for key,v in out.items() if '基准' in key]
    out['全部买点_原始并集'] = bases[0] | bases[1] | bases[2] | bases[3]
    return out


def net(gross):
    return (1+gross)*(1-SLIP)/(1+SLIP)*(1-FEE)-1


def stats(rows):
    if rows.empty:
        return {'n':0, 'items':0, 'days':0, 'win':None, 'median':None, 'mean':None, 'p10':None}
    return {'n':len(rows), 'items':rows['name'].nunique(), 'days':rows['date'].nunique(),
            'win':float((rows.net>0).mean()), 'median':float(rows.net.median()),
            'mean':float(rows.net.mean()), 'p10':float(rows.net.quantile(.1))}


def enough(s):
    return s['n']>=30 and s['items']>=10 and s['days']>=20


def main():
    cache = Path(os.environ.get('BUY_RESEARCH_CACHE','/tmp/buy-research-source.csv'))
    if not cache.exists():
        print('Downloading buy-cs source CSV',flush=True)
        with urllib.request.urlopen(URL,timeout=90) as r:
            cache.write_bytes(r.read())
    payload = cache.read_bytes()
    source_hash = hashlib.sha256(payload).hexdigest()
    raw = pd.read_csv(io.BytesIO(payload),usecols=['marketHashName','group','date','v1','v2','v3','v4'])
    del payload
    raw = raw.rename(columns={'marketHashName':'name','v1':'open','v2':'close','v3':'high','v4':'low'})
    raw['date'] = pd.to_datetime(raw.date)
    today = pd.Timestamp.now(tz='Asia/Shanghai').tz_localize(None).normalize()
    raw = raw[(raw['group']!='knife_FN') & (raw.date<today)].drop_duplicates(['name','date'],keep='last')
    for col in ['open','close','high','low']:
        raw[col] = pd.to_numeric(raw[col],errors='coerce')
    valid = (raw[['open','close','high','low']]>0).all(axis=1)
    valid &= (raw.high>=raw[['open','close']].max(axis=1)) & (raw.low<=raw[['open','close']].min(axis=1)) & (raw.high>=raw.low)
    raw['valid'] = valid
    latest = raw.groupby('name').date.max().value_counts().idxmax()
    raw = raw[raw.date<=latest]
    split = latest-pd.Timedelta(days=90)
    events = []
    eligibility_dates = []
    # Baseline parity check uses the current upstream functions, without invoking API or notifications.
    src = urllib.request.urlopen('https://raw.githubusercontent.com/huvan9527-a11y/buy-cs/main/scanner.py',timeout=60).read().decode()
    wanted={'cross','ema','sma','signal_types','family_count'}
    nodes=[n for n in ast.parse(src).body if isinstance(n,ast.FunctionDef) and n.name in wanted]
    ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),'buy-cs-baseline','exec'),ns)
    parity=0
    for num,(name,part) in enumerate(raw.groupby('name',sort=True),1):
        part=part.sort_values('date').set_index('date')
        # Never interpolate labels or skip missing calendar days when timing exits.
        g=part.reindex(pd.date_range(part.index.min(),latest,freq='D'))
        g['valid']=g['valid'].eq(True)
        # Require 300 actual valid historical bars, matching current scanner's history threshold.
        # Also require the last 90 days to be observed, avoiding signals across stale/invalid gaps.
        eligible=(g['valid'].cumsum()>=300) & (g['valid'].rolling(90).sum()==90) & g.close.between(30,13000)
        if eligible.any(): eligibility_dates.append(g.index[eligible][0])
        if not eligible.any(): continue
        masks=signals(g)
        if parity<25 and g['valid'].all():
            expected=bool(ns['signal_types'](g[['open','close','high','low']].to_dict('records')))
            assert bool(masks['全部买点_原始并集'].iloc[-1])==expected,(name,'baseline mismatch')
            parity+=1
        for H in HOLDS:
            future=g.close.shift(-(H+1))/g.close.shift(-1)-1
            label_ok=g['valid'].shift(-1,fill_value=False) & g['valid'].shift(-(H+1),fill_value=False)
            returns=net(future)
            for rule,mask in masks.items():
                selected=np.flatnonzero((eligible & mask.fillna(False) & label_ok).to_numpy())
                # One open simulated holding per item/rule/H; no overlapping repeated samples.
                keep=[];next_allowed=-1
                for i in selected:
                    if i>=next_allowed:
                        keep.append(i);next_allowed=i+H+2
                for i in keep:
                    events.append((name,g.index[i],g.index[i]+pd.Timedelta(days=H+1),rule,H,float(returns.iloc[i])))
        if num%250==0: print('processed',num,'items',flush=True)
    ev=pd.DataFrame(events,columns=['name','date','exit_date','rule','H','net'])
    summary=[]
    for rule in signals(raw[raw.name==raw.name.iloc[0]].reset_index(drop=True)):
        for H in HOLDS:
            subset=ev[(ev.rule==rule)&(ev.H==H)]
            train=stats(subset[subset.exit_date<=split])
            val=stats(subset[(subset.date>split)&(subset.exit_date<=latest)])
            summary.append({'rule':rule,'family':rule.split('_')[0],'H':H,'train':train,'validation':val})
    selections=[]
    for family in sorted({r['family'] for r in summary}):
        candidates=[r for r in summary if r['family']==family and enough(r['train'])]
        if not candidates:
            selections.append({'family':family,'status':'训练样本不足，不选参'})
            continue
        chosen=max(candidates,key=lambda r:(r['train']['median'],r['train']['p10'],-r['H']))
        passed=chosen['train']['median']>0 and enough(chosen['validation']) and chosen['validation']['median']>0
        selections.append({'family':family,'selected_in_training':chosen['rule'],'H':chosen['H'],
                           'status':'仅列入前瞻观察，未自动应用' if passed else '验证未通过，保留原参数',
                           'train':chosen['train'],'validation':chosen['validation']})
    out=ROOT/'output';out.mkdir(exist_ok=True)
    result={'version':'buy-parameter-baseline-v1','source':URL,'sha256':source_hash,
            'data_start':str(raw.date.min().date()),'data_end':str(latest.date()),'split':str(split.date()),
            'earliest_eligible_signal':str(min(eligibility_dates).date()) if eligibility_dates else None,
            'entry':'信号次日实际日K收盘指数','exit':'入场后H个自然日实际日K收盘指数',
            'history_min_bars':300,'fee':FEE,'slippage_per_side':SLIP,'parity_items':parity,
            'grid':summary,'selections':selections,
            'notes':['单规则同商品持有期间不重复计样；不同规则仍可能共用商品及市场风险',
                     '仅当前商品清单及现存历史，有存活偏差；非历史全市场',
                     '90日验证集是会被重复查看的验证集，不是永久独立测试集',
                     '模拟收盘指数成交，不含订单簿、资金占用、账户净值或平台交易限制',
                     '未用求购与Whale做历史过滤；二者没有足够的可比历史',
                     '未修改buy-cs或fable-ML的实用规则、模型和推送']}
    (out/'buy_parameter_research.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,default=int),encoding='utf-8')
    flat=[]
    for r in summary:
        flat.append({'rule':r['rule'],'H':r['H'],**{'train_'+k:v for k,v in r['train'].items()},**{'val_'+k:v for k,v in r['validation'].items()}})
    pd.DataFrame(flat).to_csv(out/'buy_parameter_research.csv',index=False,encoding='utf-8-sig')
    pct=lambda x:'—' if x is None else f'{x:+.2%}'
    lines=['# 买点参数研究 · 固定网格基准版','',
           f'数据截止：{latest.date()}；训练退出日期≤{split.date()}；验证信号日期>{split.date()}。',
           f'入场历史要求300条有效日K；最早符合资格的信号日：{result["earliest_eligible_signal"]}。',
           f'原始并集与buy-cs核对：{parity}件通过。固定13组规则×3个持有期；手续费2.5%，双边滑点各0.5%。','',
           '## 只按训练段选择的参数','',
           '| 家族 | 训练段选择 | H | 训练样本 | 验证样本 | 验证净收益中位数 | 结论 |','|---|---|---:|---:|---:|---:|---|']
    for r in selections:
        lines.append(f'| {r["family"]} | {r.get("selected_in_training","未选择")} | {r.get("H","—")} | {r.get("train",{}).get("n","—")} | {r.get("validation",{}).get("n","—")} | {pct(r.get("validation",{}).get("median"))} | {r["status"]} |')
    lines+=['','## 各参数验证表现（仅描述，不据此反选参数）','',
            '| 规则 | H | 训练n | 验证n | 验证胜率 | 验证净中位 | 验证P10 |','|---|---:|---:|---:|---:|---:|---:|']
    for r in summary:
        t,v=r['train'],r['validation']
        lines.append(f'| {r["rule"]} | {r["H"]} | {t["n"]} | {v["n"]} | {pct(v["win"])} | {pct(v["median"])} | {pct(v["p10"])} |')
    lines+=['','## 解释与限制',
            '- 样本门槛：至少30笔、10件商品、20个信号日；只是最低研究门槛，不保证统计独立或有效。',
            '- 净收益中位数最高不等于可交易最优；不按验证段最高收益直接换参数。',
            *['- '+n for n in result['notes']],'']
    md='\n'.join(lines)
    (out/'buy_parameter_research.md').write_text(md,encoding='utf-8')
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'],'a',encoding='utf-8') as f:f.write(md)
    print(json.dumps({'data_end':result['data_end'],'earliest_eligible':result['earliest_eligible_signal'],'events':len(ev),'selections':selections},ensure_ascii=False,default=int),flush=True)


if __name__=='__main__':main()
