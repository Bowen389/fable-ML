"""Causal, transparent research decision layer; no training, trading or new API calls."""
import math,statistics
from datetime import datetime,timedelta,timezone
VERSION='decision-v1';TZ=timezone(timedelta(hours=8))
def num(x):
    try:v=float(x);return v if math.isfinite(v) else None
    except (ValueError,TypeError):return None
def clip(x):return max(0,min(1,x))
def exact(rows):
    d={}
    for r in rows:d.setdefault(r['name'],[]).append(r)
    return {k:v[0] for k,v in d.items() if len(v)==1}
def candle_features(z):
    if len(z)<22:return {}
    c=[r['close'] for r in z];atr=sum(max(z[i]['high']-z[i]['low'],abs(z[i]['high']-c[i-1]),abs(z[i]['low']-c[i-1])) for i in range(len(z)-14,len(z)))/14
    return dict(r3=c[-1]/c[-4]-1,prior_r3=c[-4]/c[-7]-1,r7=c[-1]/c[-8]-1,ma5=sum(c[-5:])/5,ma21=sum(c[-21:])/21,atr14=atr,atr_pct=atr/c[-1],support10=min(r['low'] for r in z[-10:]),high20=max(r['high'] for r in z[-20:]))
def regime(rows,asof):
    z=[r for r in rows if r.get('eligible') and r['asof']==asof and r.get('r3') is not None]
    if len(z)<50:return dict(state='环境未知',permission='关闭',coverage=len(z),asof=asof)
    m=statistics.median(r['r3'] for r in z);p=statistics.median(r['prior_r3'] for r in z);b=sum(r['r3']>0 for r in z)/len(z)
    if m<-.03 and m<p:s,a='下跌加速','关闭'
    elif m>0 and b>=.5:s,a='反弹启动','研究放行'
    elif m>=p and m>=-.025:s,a='止跌蓄势','仅研究试探'
    elif p>0 and m<p:s,a='反弹衰竭','关闭'
    else:s,a='弱势震荡','仅观察'
    return dict(state=s,permission=a,coverage=len(z),asof=asof,median_r3=m,prior_median_r3=p,breadth3=b,median_r7=statistics.median(r['r7'] for r in z),basis='排刀且满足传统扫描历史/价格条件的样本；非全市场指数；不要求7日中位数为正')
def build(system,pool,coils,multifactor,current):
    asof=(current.date()-timedelta(days=1)).isoformat();market=regime(pool,asof);pc=exact(pool);cc=exact(coils);mc=exact(multifactor);groups={};rows=[]
    for p in pool:
        if p.get('eligible') and p['asof']==asof and p.get('r3') is not None:groups.setdefault(p['name'].split(' | ')[0],[]).append(p)
    for q in system['monitor']:
        name=q['name'];p=pc.get(name);c=cc.get(name);block=[];notes=[];reasons=[];potential=entry=None;parts={};ep={};support=stop=ceiling=None;triggers=[]
        if c and c.get('date')==asof:
            factors={k:num(c.get(k)) for k in ('build','tier','wash','activation','relative')};pen=num(c.get('penalty'))
            if all(v is not None for v in factors.values()) and pen is not None:
                weights=dict(build=30,tier=15,wash=20,activation=15,relative=10)
                parts={k:round(weights[k]*clip(v),3) for k,v in factors.items()};parts['risk']=round(10*clip(1-pen/30),3);potential=round(sum(parts.values()),2);reasons=c.get('reasons','').split('；')
        if potential is None:block.append('潜力因子缺失或非昨日完整日K')
        price=num(q.get('实时挂牌价'));fresh=False
        try:
            t=datetime.fromisoformat(q['价格采集时间']);t=t.replace(tzinfo=TZ) if t.tzinfo is None else t;fresh=0<=(current-t).total_seconds()<=21600
        except (ValueError,TypeError,KeyError):pass
        if not fresh or price is None or price<=0:block.append('报价缺失或超过6小时')
        if p and p['asof']==asof and p.get('atr14') is not None and price and price>0:
            support=p['support10'];atr=p['atr14'];stop=round(support-.5*atr,2);ceiling=round(min(p['ma5']+.5*atr,p['high20']),2)
            position=35*clip(1-abs((price-support)/max(atr,1e-9)-1)/3);risk=20*clip(1-p['atr_pct']/.12);pattern=20*min(p.get('families') or 0,2)/2
            depth=num(q.get('求购厚度'));qty=num(q.get('求购件数'));change=num(q.get('求购厚度变化百分比'));demand_ok=False;demand=None
            try:demand_ok=0<=(current.date()-datetime.fromisoformat(q['求购批次'][:10]).date()).days<=1
            except (ValueError,TypeError,KeyError):pass
            if demand_ok and depth is not None and qty is not None and depth>=0 and qty>=0:
                demand=15*clip(qty/100)
                if change is not None:demand+=10*clip(.5+change/40)
                else:notes.append('可比求购变化缺失：10分确认项留空')
            else:block.append('求购缺失或批次超过1天')
            ep=dict(position=round(position,2),volatility=round(risk,2),pattern=pattern,demand=None if demand is None else round(demand,2))
            if demand is not None:entry=round(position+risk+pattern+demand,2)
            if price<=support:block.append('挂牌价失守10日支撑')
            if price>ceiling:block.append('价格超过入场观察上限，等待回踩')
            if p['atr_pct']>.12:block.append('ATR波动过大')
            if not p.get('families'):block.append('无传统日K买点')
            if change is not None and change<=-20:block.append('可比求购厚度下降超过20%')
            triggers=[f'挂牌价在{round(support,2)}至{ceiling}区间并止跌确认','传统日K至少1类买点；有效求购未明显恶化']
        else:block.append('同商品日K位置或波动数据不足')
        group=name.split(' | ')[0];g=groups.get(group,[]);sector=dict(name=group,samples=len(g),state='未知');followers=0
        if len(g)>=5:
            sm=statistics.median(v['r3'] for v in g);sector.update(median_r3=sm,breadth3=sum(v['r3']>0 for v in g)/len(g),state='修复' if sm>=0 else '弱势')
            followers=sum(v['name']!=name and cc.get(v['name'],{}).get('date')==asof and (num(cc.get(v['name'],{}).get('early_coil')) or 0)>=60 for v in g)
        else:block.append('板块样本不足5')
        if market['permission'] in ('关闭','仅观察'):block.append('市场环境未放行')
        if market['permission']=='仅研究试探' and sector['state']!='修复':block.append('左侧试探缺少板块修复')
        if followers<1:block.append('同板块暂无其他提前蓄势分≥60的接力观察品')
        if potential is None:state='数据不足'
        elif potential<60:state='潜力不足，继续观察'
        elif block:state='等待条件'
        elif entry is not None and entry>=65:state='研究条件满足，仅模拟试探'
        else:state='入场证据不足'
        rows.append(dict(name=name,cn=q.get('商品'),potential=potential,entry=entry,state=state,market_permission=market['permission'],sector=sector,follower_count=followers,quote=price,quote_at=q.get('价格采集时间'),daily_asof=p.get('asof') if p else None,demand_batch=q.get('求购批次'),support=support,invalidation_price=stop,entry_ceiling=ceiling,potential_components=parts,entry_components=ep,entry_observed_max=90 if notes else 100,legacy_multifactor=mc.get(name,{}).get('多因子证据分'),coil_sequence=c.get('sequence') if c else None,reasons=reasons,triggers=triggers,blockers=block,data_notes=notes,whale='仅辅助，不计分、不因覆盖缺失扣分',live_buy_allowed=False))
    ranked=sorted([r for r in rows if r['potential'] is not None],key=lambda r:(-r['potential'],-(r['entry'] if r['entry'] is not None else -1),r['name']))
    for i,r in enumerate(ranked,1):r['potential_rank']=i
    ready=sorted([r for r in ranked if r['state']=='研究条件满足，仅模拟试探'],key=lambda r:(-r['entry'],-r['potential'],r['name']))
    return dict(version=VERSION,generated_at=current.isoformat(),asof=asof,status='research_only',validated=False,live_buy_allowed=False,market=market,monitor_rows=len(rows),scored_rows=len(ranked),research_ready=len(ready),top5=ranked[:5],entry_top5=ready[:5],rows=rows)
def render(x):
    esc=lambda s:str(s).replace('|','／').replace('\n',' ')
    m=x['market'];L=['# CS2 综合决策主报告','',f'生成：{x["generated_at"]}；完整日K：{x["asof"]}；版本 {VERSION}。','','**研究观察版，尚未通过买入验证，不自动交易。**','',f'市场：**{m["state"]}**；权限：**{m["permission"]}**；同日环境样本 {m["coverage"]}。',f'监控 {x["monitor_rows"]} 件；潜力可评分 {x["scored_rows"]} 件；研究入场条件满足 {x["research_ready"]} 件。','','## 潜力Top5及入场决策','','| 商品 | 潜力分 | 入场分 | 状态 | 未满足条件 |','|---|---:|---:|---|---|']
    for r in x['top5']:L.append('| '+' | '.join(esc(v) for v in [r['cn'],r['potential'],r['entry'] if r['entry'] is not None else '缺失',r['state'],'；'.join(r['blockers']) or '无硬阻断，仍需评分门槛'])+' |')
    L+=['','## 触发与失效']
    for r in x['top5']:L+=['',f'**{esc(r["cn"])}**','- 理由：'+esc('；'.join(r['reasons'])),'- 触发：'+esc('；'.join(r['triggers']) or '补齐日K及报价'),f'- 参考支撑 {r["support"]}；入场观察上限 {r["entry_ceiling"]}；失效参考 {r["invalidation_price"]}（支撑减0.5ATR，非成交保证）。','- 数据缺口：'+esc('；'.join(r['data_notes']) or '仍为日K与每日求购代理')]
    L+=['','## 研究入场Top5','\n'.join('- '+esc(r['cn'])+'：'+str(r['entry']) for r in x['entry_top5']) or '本轮无商品满足全部研究入场条件，潜力Top5不是买入名单。','','## 公式与限制','潜力=建仓代理30+台阶15+洗盘20+持续放量15+相对强度10+风险质量10；各因子截断0～1，风险质量=截断(1−原风险扣分/30)。原ML列作对照，不重复加分。','入场=位置35+波动20+传统形态20+求购25；求购容量15分按挂单件数/100截断，可比变化10分按0.5+变化百分比/40截断。变化不可比时10分留空，不重新归一化。','位置按距离10日支撑的ATR倍数、波动按ATR/价格计算；传统家族最多计2类。市场以同日3日变化、前3日变化及上涨广度分类，不要求7日中位数为正；板块是同武器/手套家族代理。','潜力60、入场65、后排提前蓄势60、样本数与所有权重均是待验证设计假设，不声称最优。缺失数据不放行；Whale仅辅助。','悠悠挂单不是成交，会员与成本仅代理；没有逐笔盘口确认。新研究卖出费1%、无滑点；本模块本轮未生成回测收益。','','[全部815件决策](decision_latest.csv) · [决策JSON](decision_latest.json) · 下附原模块证据。','']
    return '\n'.join(L)
