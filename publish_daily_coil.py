"""Publish only coil outputs and merge into reports read at the current remote head."""
import base64,json,os,time
from pathlib import Path
import urllib.request,urllib.error
from coil_report_section import merge_coil_section
ROOT=Path(__file__).resolve().parent

def remote_text(api,path,head):
    remote=api('/contents/'+path+'?ref='+head)
    if remote.get('encoding')!='base64' or not remote.get('content'):
        sha=remote.get('sha')
        if not sha:raise ValueError('Remote file has no blob SHA: '+path)
        remote=api('/git/blobs/'+sha)
    if remote.get('encoding')!='base64' or not remote.get('content'):
        raise ValueError('Remote file content unavailable: '+path)
    return base64.b64decode(remote['content'],validate=False).decode('utf-8-sig')

def main():
    token=os.environ['GITHUB_TOKEN'];repo=os.environ['GITHUB_REPOSITORY'];base='https://api.github.com/repos/'+repo
    def api(path,data=None,method=None):
        req=urllib.request.Request(base+path,data=None if data is None else json.dumps(data).encode(),method=method,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=45) as r:return json.load(r)
    meta=json.loads((ROOT/'output/daily_coil_candidates.json').read_text())
    outputs=['output/daily_coil_candidates.json','output/daily_coil_scores.csv','output/daily_coil_report.md']
    entries=[{'path':p,'type':'blob','mode':'100644','content':(ROOT/p).read_text(encoding='utf-8-sig')} for p in outputs]
    for attempt in range(3):
        try:
            head=api('/git/ref/heads/main')['object']['sha'];tree=api('/git/commits/'+head)['tree']['sha'];current=list(entries)
            for p in ('output/latest.md','output/process_score_report.md','output/multifactor_report.md','output/guide_latest.md'):
                try:text=remote_text(api,p,head)
                except urllib.error.HTTPError as exc:
                    if exc.code==404:continue
                    raise
                current.append({'path':p,'type':'blob','mode':'100644','content':merge_coil_section(text,ROOT)})
            try:
                guide_text=remote_text(api,'output/guide_latest.json',head)
            except urllib.error.HTTPError as exc:
                if exc.code!=404:raise
            else:
                guide=json.loads(guide_text)
                guide['coil_candidates']=meta
                current.append({'path':'output/guide_latest.json','type':'blob','mode':'100644','content':json.dumps(guide,ensure_ascii=False,indent=2)})
            if meta.get('status')=='ok':
                frozen=f'output/history/coil_scores_{meta["asof"]}_{meta["version"]}.csv'
                try:api('/contents/'+frozen)
                except urllib.error.HTTPError as exc:
                    if exc.code!=404:raise
                    current.append({'path':frozen,'type':'blob','mode':'100644','content':(ROOT/'output/daily_coil_scores.csv').read_text(encoding='utf-8-sig')})
            newtree=api('/git/trees',{'base_tree':tree,'tree':current})['sha']
            commit=api('/git/commits',{'tree':newtree,'parents':[head],'message':'Daily accumulation watch candidates '+str(meta.get('asof','error'))+' ('+meta['status']+')'})['sha']
            api('/git/refs/heads/main',{'sha':commit,'force':False},method='PATCH')
            print('DAILY_COIL_PUBLISHED',commit,meta['status'],len(current),flush=True);return
        except (urllib.error.URLError,TimeoutError):
            if attempt==2:raise
            time.sleep(3)
if __name__=='__main__':main()
