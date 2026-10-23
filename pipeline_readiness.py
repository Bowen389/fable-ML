"""Wait for public, completed upstream publications; never request YY APIs."""
import json,os,time,urllib.request
from datetime import datetime,timedelta,timezone
from pathlib import Path
TZ=timezone(timedelta(hours=8))
SLOTS=((9,17),(15,17),(21,17))
def expected_quote_slot(current):
    slots=[current.replace(hour=h,minute=m,second=0,microsecond=0) for h,m in SLOTS]
    return max([t for t in slots if t<=current] or [(current-timedelta(days=1)).replace(hour=21,minute=17,second=0,microsecond=0)])
def assess(current,quote,coil):
    expected=(current.date()-timedelta(days=1)).isoformat();slot=expected_quote_slot(current);reasons=[]
    try:
        dt=datetime.fromisoformat(quote['generated_at']);dt=dt.replace(tzinfo=TZ) if dt.tzinfo is None else dt
        if dt<slot:reasons.append('等待本时段报价发布')
        if not 0<=(current-dt).total_seconds()<=21600:reasons.append('报价超时或时间异常')
    except (KeyError,ValueError,TypeError):reasons.append('报价时间缺失')
    if quote.get('status') not in ('ok','partial') or not quote.get('price_rows'):reasons.append('报价没有有效数据')
    if coil.get('status')!='ok' or coil.get('asof')!=expected:reasons.append('等待昨日完整日K蓄势评分发布')
    return dict(ready=not reasons,reasons=reasons,checked_at=current.isoformat(),expected_quote_after=slot.isoformat(),quote_generated_at=quote.get('generated_at'),expected_daily_asof=expected,coil_asof=coil.get('asof'))
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
    result=assess(datetime.now(TZ),quote,coil);result.update(upstream_sha=up,fable_sha=head,quote_run_id=quote.get('run_id'))
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
        with open(os.environ['GITHUB_ENV'],'a') as f:
            if result.get('upstream_sha'):f.write('UPSTREAM_REVISION='+result['upstream_sha']+'\n')
    print('PIPELINE_READY' if result['ready'] else 'PIPELINE_PENDING',json.dumps(result,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
