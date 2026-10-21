"""Publish text results atomically; preserve unrelated concurrent repository changes."""
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parent

def main():
    token=os.environ['GITHUB_TOKEN'];repo=os.environ['GITHUB_REPOSITORY']
    base='https://api.github.com/repos/'+repo
    def api(path,data=None,method=None):
        req=urllib.request.Request(base+path,data=None if data is None else json.dumps(data).encode(),method=method,
            headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=45) as r:return json.load(r)
    manifest=json.loads((ROOT/'output/process_score_validation.json').read_text())
    asof=manifest['asof'];version=manifest['version']
    paths=['output/process_score_report.md','output/process_score_validation.json','output/daily_process_scores.csv']
    extra=['output/multifactor_report.md','output/multifactor_validation.json','output/daily_multifactor_scores.csv','output/multifactor_sector_snapshot.csv','output/score_pool_status.json']
    paths += [p for p in extra if (ROOT/p).exists()]
    entries=[{'path':p,'mode':'100644','type':'blob','content':(ROOT/p).read_text(encoding='utf-8-sig')} for p in paths]
    # Immutable first score snapshot for each data day and algorithm version; latest reports may be refreshed.
    snapshot=f'output/history/process_scores_{asof}_{version}.csv'
    for attempt in range(3):
        try:
            head=api('/git/ref/heads/main')['object']['sha'];tree=api('/git/commits/'+head)['tree']['sha']
            current=list(entries)
            try:api('/contents/'+snapshot)
            except urllib.error.HTTPError as exc:
                if exc.code!=404:raise
                current.append({'path':snapshot,'mode':'100644','type':'blob','content':entries[2]['content']})
            if (ROOT/'output/multifactor_validation.json').exists():
                multi=json.loads((ROOT/'output/multifactor_validation.json').read_text())
                multi_snapshot=f'output/history/multifactor_scores_{multi["asof"]}_{multi["version"]}.csv'
                try:api('/contents/'+multi_snapshot)
                except urllib.error.HTTPError as exc:
                    if exc.code!=404:raise
                    current.append({'path':multi_snapshot,'mode':'100644','type':'blob','content':(ROOT/'output/daily_multifactor_scores.csv').read_text(encoding='utf-8-sig')})
            newtree=api('/git/trees',{'base_tree':tree,'tree':current})['sha']
            commit=api('/git/commits',{'message':f'Daily process evidence scores {asof} (research only)','tree':newtree,'parents':[head]})['sha']
            api('/git/refs/heads/main',{'sha':commit,'force':False},method='PATCH')
            print('Published',len(current),'text reports at',commit,flush=True);return
        except (urllib.error.URLError,TimeoutError):
            if attempt==2:raise
            time.sleep(5)

if __name__=='__main__':main()

