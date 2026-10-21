"""Explain research eligibility without shrinking the independent monitoring pool."""
from collections import Counter
import json
from datetime import timedelta
import math

EXCLUDED=('Nova |','XM1014 |','MAG-7 |','Sawed-Off |','Negev |','M249 |','R8 Revolver |')

def finite(v):
    try:return math.isfinite(float(v))
    except (TypeError,ValueError):return False

def diagnose(name,error,context):
    if name.startswith(EXCLUDED):return '研究品类排除',['按既定研究规则排除品类，仍保留报价与求购监控']
    if error:
        if 'Less than 300 valid history rows' in error:return '历史不足',['不足300条有效历史日K，暂不评分']
        return '历史数据获取失败',['历史数据读取或获取失败：'+error]
    if not context or not context.get('current_exists'):return '最新日K缺失',['评分日没有真实有效日K，暂不评分']
    reasons=[]
    if not finite(context.get('close')):reasons.append('评分日价格缺失或无效')
    elif context['close']<30:reasons.append('评分日价格低于30元研究门槛')
    if context.get('history_count',0)<300:reasons.append('截至评分日不足300条有效历史日K')
    if context.get('valid90',0)<80:reasons.append('最近90自然日有效报价不足80日')
    if context.get('valid20',0)<18:reasons.append('最近20自然日有效报价不足18日')
    if not context.get('volume_ok'):
        if not finite(context.get('volume')):reasons.append('评分日成交量缺失')
        elif context['volume']<=0:reasons.append('评分日无有效成交量')
        elif not finite(context.get('rv')):reasons.append('量能窗口不足或相对量分母无效')
        else:reasons.append('量能观测跨度或窗口不满足研究要求')
    if not finite(context.get('flat_14')):reasons.append('近14日平价指标缺失')
    elif context['flat_14']>.5:reasons.append('近14日平价占比超过50%')
    if not context.get('eligible') and not reasons:reasons.append('其他历史覆盖或数据资格不满足')
    if not reasons:return '可评分',[]
    if any('低于30元' in x for x in reasons):status='低于价格门槛'
    elif any('报价不足' in x or '日K' in x or '价格缺失' in x for x in reasons):status='日K数据不足'
    elif any('成交量' in x or '量能' in x for x in reasons):status='量能条件不足'
    else:status='平价或数据条件不满足'
    return status,reasons


def write_pool_audit(universe,failures,d,latest,out):
    errors={f['name']:f['error'] for f in failures};groups={n:g for n,g in d.groupby('name',sort=False)}
    items=[]
    for item in universe:
        g=groups.get(item['name']);ctx={};last_date=None;last_close=None
        if g is not None:
            observed=g[g.close.notna()]
            if len(observed):
                last=observed.iloc[-1];last_date=str(last.date.date());last_close=float(last.close)
            same=g[g.date==latest];row=same.iloc[-1] if len(same) else None
            ctx={'current_exists':row is not None,'history_count':int(g.close.notna().sum()),
                 'valid90':int(g.loc[g.date>=latest-timedelta(days=89),'close'].notna().sum()),
                 'valid20':int(g.loc[g.date>=latest-timedelta(days=19),'close'].notna().sum())}
            if row is not None:
                for key in ['close','volume','rv','flat_14']:ctx[key]=float(row[key]) if finite(row[key]) else None
                ctx['eligible']=bool(row.eligible);ctx['volume_ok']=bool(row.volume_ok)
        status,reasons=diagnose(item['name'],errors.get(item['name']),ctx)
        items.append({'name':item['name'],'cn':item['cn'],'firepulse_id':item['id'],'asof':str(latest.date()),
            'scoring_status':status,'reasons':reasons,'last_bar_date':last_date,'last_close':last_close,'diagnostics':ctx})
    expected=int(((d.date==latest)&d.eligible&d.volume_ok&(d.flat_14<=.5)).sum())
    actual=sum(x['scoring_status']=='可评分' for x in items)
    if actual!=expected:raise AssertionError(f'Eligibility audit disagrees with actual scoring rows: {actual} vs {expected}')
    result={'version':'score-eligibility-audit-v1','asof':str(latest.date()),'research_universe_rows':len(items),
            'status_counts':dict(Counter(x['scoring_status'] for x in items)),'items':items,
            'note':'只解释评分资格；不改变独立的悠悠items.txt报价/求购监控名单，缺失分数不记0分'}
    (out/'score_pool_status.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    return result
