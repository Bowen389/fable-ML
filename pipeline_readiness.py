"""Wait for public, completed upstream publications; never request YY APIs.

SteamDT 报价兜底：当上游悠悠报价过期时，若 SteamDT 价格接口能取到悠悠有品平台的
在售价，则报价维度视为满足(不阻断)，流水线不再空等。兜底仅在 STEAMDT_API_KEY 可用时
启用；未配置时行为与原版一致(只认上游悠悠报价)。
"""
import json,os,time,urllib.request
from datetime import datetime,timedelta,timezone
from pathlib import Path
TZ=timezone(timedelta(hours=8))
SLOTS=((9,17),(15,17),(21,17))
def expected_quote_slot(current):
    slots=[current.replace(hour=h,minute=m,second=0,microsecond=0) for h,m in SLOTS]
    return max([t for t in slots if t<=current] or [(current-timedelta(days=1)).replace(hour=21,minute=17,second=0,microsecond=0)])

_QUOTE_REASONS=('等待本时段报价发布','报价超时或时间异常','报价时间缺失','报价没有有效数据')

# 热门饰品兜底样本：SteamDT 价格接口需要 Steam 官方英文 marketHashName；
# 这些是各平台长期在售的常见款，用于可用性探测(不要求在监控池内)。
POPULAR_NAMES=['AK-47 | Redline (Field-Tested)','M4A4 | Hyper Beast (Field-Tested)',
               'Desert Eagle | Light Rail (Field-Tested)','USP-S | Kill Confirmed (Field-Tested)',
               'AWP | Asiimov (Field-Tested)','Glock-18 | Fade (Field-Tested)']

def _names_from_csv(text,limit=8):
    """从 fable-ML 发布的 unified_monitor.csv 提取 name 列(标准英文 marketHashName)。"""
    if not text:return []
    names=[]
    for line in text.splitlines():
        line=line.strip()
        if not line or line.lower().startswith('name'):continue
        # name 是首列，按首个逗号切
        head=line.split(',',1)[0].strip()
        if head and head not in names:names.append(head)
        if len(names)>=limit:break
    return names

def _sample_names(quote,csv_text=None,limit=8):
    """汇总多源样本名用于 SteamDT 可用性探测：CSV(主) > 报价JSON(次) > 热门兜底。"""
    names=[]
    if csv_text:
        names=_names_from_csv(csv_text,limit)
    if len(names)<3:
        for key in ('unmapped_research_scores','monitor_universe','report_rows','score_rows'):
            v=quote.get(key)
            if isinstance(v,list):
                for r in v:
                    if isinstance(r,dict):
                        n=r.get('name') or r.get('marketHashName')
                        if n and n not in names:names.append(n)
                    elif isinstance(r,str) and r not in names:
                        names.append(r)
                    if len(names)>=limit:break
            if len(names)>=limit:break
    if len(names)<3:
        for n in POPULAR_NAMES:
            if n not in names:names.append(n)
            if len(names)>=limit:break
    return names[:limit]

def steamdt_quote_available(api_key,names,current):
    """探测 SteamDT 是否能提供悠悠有品在售价。返回 dict(available,probed,fresh,reason)。
    仅在 STEAMDT_API_KEY 可用时探测；返回 available=True 表示兜底报价可用。"""
    if not api_key:
        return {'available':False,'probed':0,'fresh':0,'reason':'无STEAMDT_API_KEY，兜底未启用'}
    if not names:
        return {'available':False,'probed':0,'fresh':0,'reason':'无可用商品名样本'}
    try:
        from steamdt_quote_fallback import fetch_steamdt_prices
        prices,err=fetch_steamdt_prices(names,api_key)
    except Exception as exc:
        return {'available':False,'probed':len(names),'fresh':0,'reason':type(exc).__name__}
    fresh=0
    for pr in prices.values():
        try:
            if pr and pr.get('sell_price') is not None and float(pr['sell_price'])>0:
                fresh+=1
        except (TypeError,ValueError):
            continue
    avail=fresh>0
    return {'available':avail,'probed':len(names),'fresh':fresh,
            'reason':'' if avail else (err or 'SteamDT 未返回悠悠在售价')}

def assess(current,quote,coil,steamdt=None):
    expected=(current.date()-timedelta(days=1)).isoformat();slot=expected_quote_slot(current);notes=[]
    quote_reasons=[]
    try:
        dt=datetime.fromisoformat(quote['generated_at']);dt=dt.replace(tzinfo=TZ) if dt.tzinfo is None else dt
        if dt<slot:quote_reasons.append('等待本时段报价发布')
        if not 0<=(current-dt).total_seconds()<=21600:quote_reasons.append('报价超时或时间异常')
    except (KeyError,ValueError,TypeError):quote_reasons.append('报价时间缺失')
    if quote.get('status') not in ('ok','partial') or not quote.get('price_rows'):quote_reasons.append('报价没有有效数据')
    fallback_ok=bool(steamdt and steamdt.get('available'))
    if quote_reasons and fallback_ok:
        # 上游报价过期但 SteamDT 兜底报价可用：报价维度按满足处理，仅记录说明，不阻断。
        notes.append('上游悠悠报价过期，SteamDT兜底报价可用，报价维度按兜底满足')
    elif quote_reasons:
        notes.append('上游悠悠报价过期'+('，SteamDT兜底不可用' if steamdt is not None else ''))
    reasons=[] if fallback_ok else list(quote_reasons)
    if coil.get('status')!='ok' or coil.get('asof')!=expected:reasons.append('等待昨日完整日K蓄势评分发布')
    result=dict(ready=not reasons,reasons=reasons,notes=notes,checked_at=current.isoformat(),
        expected_quote_after=slot.isoformat(),quote_generated_at=quote.get('generated_at'),
        expected_daily_asof=expected,coil_asof=coil.get('asof'))
    if steamdt:result['steamdt_fallback']=steamdt
    return result
def fetch(url):
    req=urllib.request.Request(url,headers={'Accept':'application/vnd.github+json','User-Agent':'fable-pipeline-readiness'})
    token=os.environ.get('GITHUB_TOKEN')
    if token and url.startswith('https://api.github.com/'):req.add_header('Authorization','Bearer '+token)
    with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)
def inspect():
    # Pin files to the same upstream commit: metadata, quote CSV and demand DB cannot race across publications.
    up=fetch('https://api.github.com/repos/Bowen389/up/git/ref/heads/main')['object']['sha']
    quote=fetch('https://raw.githubusercontent.com/Bowen389/up/'+up+'/data/intraday_latest.json')
    head=fetch('https://api.github.com/repos/Bowen389/fable-ML/git/ref/heads/main')['object']['sha']
    coil=fetch('https://raw.githubusercontent.com/Bowen389/fable-ML/'+head+'/output/daily_coil_candidates.json')
    # 从 fable-ML 已发布的 unified_monitor.csv 取真实英文 marketHashName 作为 SteamDT 探测样本
    try:
        csv_text=fetch('https://raw.githubusercontent.com/Bowen389/fable-ML/'+head+'/output/unified_monitor.csv')
    except Exception:
        csv_text=''
    current=datetime.now(TZ)
    steamdt=steamdt_quote_available(os.environ.get('STEAMDT_API_KEY','').strip(),_sample_names(quote,csv_text),current)
    result=assess(current,quote,coil,steamdt);result.update(upstream_sha=up,fable_sha=head,quote_run_id=quote.get('run_id'))
    return result
def main():
    limit=int(os.environ.get('PIPELINE_WAIT_SECONDS','1800'));deadline=time.monotonic()+limit
    while True:
        try:result=inspect()
        except Exception as exc:result=dict(ready=False,reasons=['上游状态读取失败：'+type(exc).__name__],checked_at=datetime.now(TZ).isoformat())
        if result['ready'] or time.monotonic()>=deadline:break
        print('PIPELINE_WAIT',json.dumps(result,ensure_ascii=False),flush=True);time.sleep(min(30,max(0,deadline-time.monotonic())))
    p=Path('data/integrations/pipeline_readiness.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,ensure_ascii=False,indent=2))
    if os.getenv('GITHUB_ENV'):
        with open(os.getenv('GITHUB_ENV'),'a') as f:
            if result.get('upstream_sha'):f.write('UPSTREAM_REVISION='+result['upstream_sha']+'\n')
    print('PIPELINE_READY' if result['ready'] else 'PIPELINE_PENDING',json.dumps(result,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
