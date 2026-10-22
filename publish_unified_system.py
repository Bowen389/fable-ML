"""Publish integration outputs only; merge into current remote reports atomically."""
import base64,json,os,time,urllib.request,urllib.error
from pathlib import Path
from system_report_section import merge_system_section
ROOT=Path(__file__).resolve().parent

def main():
    base='https://api.github.com/repos/'+os.environ['GITHUB_REPOSITORY'];token=os.environ['GITHUB_TOKEN']
    def api(path,data=None,method=None):
        req=urllib.request.Request(base+path,data=None if data is None else json.dumps(data).encode(),method=method,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=90) as r:return json.load(r)
    files=['decision_latest.json','decision_latest.csv','decision_latest.md','system_latest.json','system_latest.md','demand_whales.json','demand_whales.csv','traditional_pool.csv','traditional_hits.csv','unified_monitor.csv']
    entries=[{'path':'output/'+p,'mode':'100644','type':'blob','content':(ROOT/'output'/p).read_text(encoding='utf-8-sig')} for p in files]
    # Persist real Whale cursor/outbox state only; never tokens, local config, raw YY database or browser state.
    for folder in ('data','reports'):
        p=ROOT/'state/whale_monitor'/folder
        if p.exists():
            for f in p.glob('*.json'):
                entries.append({'path':str(f.relative_to(ROOT)),'mode':'100644','type':'blob','content':f.read_text()})
    for attempt in range(3):
        try:
            head=api('/git/ref/heads/main')['object']['sha'];tree=api('/git/commits/'+head)['tree']['sha'];current=list(entries)
            for p in ('output/latest.md','output/process_score_report.md','output/multifactor_report.md','output/guide_latest.md'):
                try:r=api('/contents/'+p+'?ref='+head)
                except urllib.error.HTTPError as exc:
                    if exc.code==404:continue
                    raise
                text=base64.b64decode(r['content']).decode('utf-8-sig');current.append({'path':p,'mode':'100644','type':'blob','content':merge_system_section(text,ROOT)})
            history=ROOT/'output/history'
            for f in history.glob('decision_*_decision-v1.json'):
                hp=str(f.relative_to(ROOT))
                try:api('/contents/'+hp+'?ref='+head)
                except urllib.error.HTTPError as exc:
                    if exc.code!=404:raise
                    current.append({'path':hp,'mode':'100644','type':'blob','content':f.read_text()})
            t=api('/git/trees',{'base_tree':tree,'tree':current})['sha'];c=api('/git/commits',{'tree':t,'parents':[head],'message':'Update unified CS2 system report'})['sha']
            api('/git/refs/heads/main',{'sha':c,'force':False},method='PATCH');print('UNIFIED_SYSTEM_PUBLISHED',c,flush=True);return
        except (urllib.error.URLError,TimeoutError):
            if attempt==2:raise
            time.sleep(3)
if __name__=='__main__':main()
