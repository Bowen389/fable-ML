"""Single package entry: full traditional scan, YY demand/rank, Whale and coil reports.
Default imports existing collectors' outputs; never duplicates purchase-list calls.
"""
import argparse,csv,gzip,hashlib,io,json,math,os,sqlite3,subprocess,sys,time,unicodedata
from collections import Counter
from datetime import datetime,timedelta,timezone
from pathlib import Path
import urllib.request
from integrations.traditional import signal_types,family_count
from decision_engine import candle_features,build as build_decisions,render as render_decisions
ROOT=Path(__file__).resolve().parent
TZ=timezone(timedelta(hours=8))
START='<!-- unified-system:start -->';END='<!-- unified-system:end -->'
SOURCES={'buy':'https://raw.githubusercontent.com/huvan9527-a11y/buy-cs/main/data/steamdt_daily_1y_raw.csv',
         'quotes':'https://raw.githubusercontent.com/Bowen389/up/main/data/intraday_scores_latest.csv',
         'quote_meta':'https://raw.githubusercontent.com/Bowen389/up/main/data/intraday_latest.json',
         'demand':'https://raw.githubusercontent.com/Bowen389/up/main/data/yyyp.db'}

def now():return datetime.now(TZ)
def norm(s):return ''.join(unicodedata.normalize('NFKC',str(s)).casefold().split())
def num(x):
    try:v=float(x);return v if math.isfinite(v) else None
    except (ValueError,TypeError):return None

def readjson(p,default=None):
    try:return json.loads(Path(p).read_text(encoding='utf-8-sig'))
    except (OSError,ValueError):return default

def dump(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False));tmp.replace(p)

def writecsv(path,rows,columns=None):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    columns=columns or list(dict.fromkeys(k for r in rows for k in r)) or ['status']
    with path.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');w.writeheader()
        for r in rows:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()})

def fetch(url,path):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.download');h=hashlib.sha256();size=0
    try:
        with urllib.request.urlopen(url,timeout=120) as response,tmp.open('wb') as f:
            while True:
                b=response.read(1024*1024)
                if not b:break
                f.write(b);h.update(b);size+=len(b)
        if not size:raise ValueError('Empty source')
        tmp.replace(path)
    finally:
        if tmp.exists():tmp.unlink()
    return {'url':url,'sha256':h.hexdigest(),'bytes':size,'fetched_at':now().isoformat()}

def readrows(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def traditional(path,today):
    groups={};invalid=0
    with Path(path).open(encoding='utf-8-sig',newline='') as f:
        for r in csv.DictReader(f):
            try:
                name=r['marketHashName'];day=r['date'][:10]
                datetime.fromisoformat(day)
                if day>=today or r.get('group')=='knife_FN':continue
                o,c,h,l=[float(r[k]) for k in ('v1','v2','v3','v4')]
                if not all(math.isfinite(x) and x>0 for x in (o,c,h,l)) or l>min(o,c) or h<max(o,c):raise ValueError('OHLC')
                groups.setdefault(name,{})[day]={'date':day,'open':o,'close':c,'high':h,'low':l,'group':r.get('group')}
            except (KeyError,ValueError,TypeError):invalid+=1
    if not groups:raise ValueError('No completed valid candles')
    counts=Counter(max(z) for z in groups.values());asof=counts.most_common(1)[0][0];expected=(datetime.fromisoformat(today)-timedelta(days=1)).date().isoformat()
    rows=[];hits=[]
    for name,byday in sorted(groups.items()):
        z=[byday[k] for k in sorted(byday)];last=z[-1];types=[]
        eligible=len(z)>=300 and last['date']==asof and 30<=last['close']<=13000
        if eligible:types=signal_types(z)
        row={'name':name,'group':last['group'],'asof':last['date'],'price':last['close'],'bars':len(z),'eligible':eligible,'families':family_count(types) if eligible else None,'types':types,'status':'scanned' if eligible else 'history_or_price_or_date_ineligible'}
        row.update(candle_features(z))
        rows.append(row)
        if types:hits.append(row)
    hits.sort(key=lambda r:(-r['families'],r['name']))
    return {'status':'ok' if asof==expected else 'stale','asof':asof,'expected_completed_date':expected,'pool':len(groups),'scanned':sum(x['eligible'] for x in rows),'hits':len(hits),'invalid_rows':invalid,'latest_date_counts':dict(counts),'families':['双金叉','均线合一','上影吞没','单针承接'],'formula':'vendored exact buy-cs families; unfinished day excluded'},rows,hits

def demand_rank(path):
    uri=Path(path).resolve().as_uri()+'?mode=ro'
    with sqlite3.connect(uri,uri=True) as db:
        batch=db.execute('SELECT MAX(run) FROM snapshot').fetchone()[0]
        if not batch:raise ValueError('No demand snapshots')
        batches=[r[0] for r in db.execute('SELECT DISTINCT run FROM snapshot ORDER BY run DESC LIMIT 2')];previous=batches[1] if len(batches)>1 else None
        covered=db.execute('SELECT COUNT(*) FROM snapshot WHERE run=?',(batch,)).fetchone()[0]
        old={str(r[0]):r[1] for r in db.execute('SELECT user_id,SUM(price*qty) FROM orders WHERE run=? AND valid=1 GROUP BY user_id',(previous,))} if previous else {}
        ranks=[]
        for uid,uname,total,items in db.execute('SELECT user_id,MAX(user_name),SUM(price*qty),COUNT(DISTINCT tid) FROM orders WHERE run=? AND valid=1 GROUP BY user_id ORDER BY SUM(price*qty) DESC,user_id LIMIT 100',(batch,)):
            details=[{'tid':tid,'name':name,'amount':amount} for tid,name,amount in db.execute('SELECT o.tid,MAX(s.name),SUM(o.price*o.qty) FROM orders o LEFT JOIN snapshot s ON o.run=s.run AND o.tid=s.tid WHERE o.run=? AND o.user_id=? AND o.valid=1 GROUP BY o.tid ORDER BY SUM(o.price*o.qty) DESC LIMIT 10',(batch,uid))]
            ranks.append({'user_id':str(uid),'user_name':uname,'valid_purchase_amount':total,'items':items,'change_vs_previous':total-old.get(str(uid),0) if previous else None,'batch':batch,'details':details})
        total=db.execute('SELECT COUNT(DISTINCT user_id) FROM orders WHERE run=? AND valid=1',(batch,)).fetchone()[0]
    day=batch[:10];age=(now().date()-datetime.fromisoformat(day).date()).days
    return {'status':'ok' if age<=1 else 'stale','batch':batch,'previous_batch':previous,'monitored_items_with_snapshot':covered,'users':total,'shown':len(ranks),'basis':'有效求购挂单总金额；不是成交或持仓；悠悠user_id不等于Steam ID'},ranks

def whale(root,collect=False):
    state=Path(root)/'state/whale_monitor';report=state/'reports/latest_report.json';eventsfile=state/'reports/new_cd_items.json'
    if collect:
        if not os.getenv('CSQAQ_TOKEN','').strip():return {'status':'not_configured','reason':'fable-ML 未配置 CSQAQ_TOKEN；Whale代码已纳入，未进行实采','events':None}
        os.environ['WHALE_ROOT']=str(state);os.environ['WHALE_SELF_TEST']='0';os.environ['WHALE_RUN_FOREVER']='0'
        os.environ.setdefault('WHALE_MAX_WHALES_PER_ROUND','30');os.environ.setdefault('WHALE_MAX_RUN_SECONDS','600');os.environ.setdefault('WHALE_FIRST_SCAN_REPORT_HISTORY','0')
        from integrations.whale import monitor_v7 as w
        cfg=w.Config.from_env();client=w.CSQAQClient(os.environ['CSQAQ_TOKEN'],cfg);client.bind_ip();w.run_once(cfg,client)
    result=readjson(report)
    if not result:
        return {'status':'not_configured' if not os.getenv('CSQAQ_TOKEN') else 'not_collected','reason':'尚无可读取的Whale实采报告；不能当作零事件','events':None}
    e=readjson(eventsfile,{});events=e.get('events')
    if not isinstance(events,list):raise ValueError('Whale events missing or invalid')
    scan=result.get('scan',{});partial=bool(scan.get('failed') or scan.get('coverage_risk') or scan.get('processed',0)<scan.get('pool_size',0))
    dt=datetime.fromisoformat(result['generated_at']);dt=dt.replace(tzinfo=TZ) if dt.tzinfo is None else dt
    age=(now()-dt).total_seconds()/3600
    return {'status':'stale' if age>36 else 'partial' if partial else 'ok','generated_at':result['generated_at'],'age_hours':age,'scan':scan,'new_event_rows':result.get('new_event_rows'),'frequency':result.get('frequency'),'events':events,'basis':'仅相对上次成功扫描新增CD_RECOVER；首扫默认建基线，非真实买入认定'}

def join_monitor(monitor,coils,hits):
    byname={};bycn={};trad={r['name']:r for r in hits}
    for x in coils:byname.setdefault(norm(x['name']),[]).append(x);bycn.setdefault(norm(x.get('cn','')),[]).append(x)
    out=[]
    for r in monitor:
        row=dict(r);m=byname.get(norm(r['name']),[]) or bycn.get(norm(r.get('商品','')),[])
        x=m[0] if len(m)==1 else None;t=trad.get(r['name']) or (trad.get(x['name']) if x else None)
        row.update({'蓄势证据分':x.get('sequence') if x else None,'提前蓄势分':x.get('early_coil') if x else None,'蓄势形态':x.get('shape_state') if x else None,'传统买点家族数':t['families'] if t else None,'传统买点':t['types'] if t else None,'匹配状态':'exact_unique' if x else 'unmapped_or_ambiguous','综合说明':'各证据分列，不增加原评分，不构成买入指令'})
        out.append(row)
    if len(out)!=len(monitor):raise AssertionError('Monitor pool lost rows')
    return out

def safe(s):return str(s if s is not None else '缺失').replace('|',' / ').replace('\n',' ')
def table(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','|'+'---|'*len(headers),*['| '+' | '.join(safe(x) for x in r)+' |' for r in rows]])

def render(x):
    m=x['modules'];lines=['# CS2 一体化总报告','',f'生成时间：{x["generated_at"]}','', '**原版规则、四类传统买点、蓄势分、求购与Whale分列展示；不自动下单。**','',table(['模块','状态','数据日期／覆盖'],[[k,v.get('status'),v.get('asof') or v.get('batch') or v.get('generated_at') or v.get('reason') or v.get('error')] for k,v in m.items()])]
    t=m['traditional'];lines+=['','## 四类传统买点（全量扫描）',f'数据日 {t.get("asof","缺失")}；研究池 {t.get("pool","缺失")} 件；实际扫描 {t.get("scanned","缺失")} 件；命中 {t.get("hits","缺失")} 件。双金叉、均线合一、上影吞没、单针承接；参数组合不重复算独立家族。']
    if t.get('status')=='stale':lines+=['**上游日K未更新，以下为旧日期结果。**']
    lines+=[table(['商品','日K价','家族数','形态'],[[r['name'],r['price'],r['families'],'＋'.join(r['types'])] for r in x['traditional_hits'][:30]]),'完整扫描与命中：output/traditional_pool.csv、output/traditional_hits.csv；全量结果未合并到单一Glock样本。',
            '','## 悠悠求购、在售与报价',f'全监控表保留 {len(x["monitor"])} 件；来源报价覆盖 {m["quotes"].get("price_rows","缺失")}；报价更新时间 {m["quotes"].get("generated_at","缺失")}；求购批次 {m["demand"].get("batch","缺失")}。','报价、求购和日K日期独立显示；本总报告复用现有采集结果，求购请求数为0。',table(['商品','挂牌价','在售','求购厚度','求购批次','蓄势分'],[[r.get('商品'),r.get('实时挂牌价'),r.get('当前在售数'),r.get('求购厚度'),r.get('求购批次'),r.get('蓄势证据分')] for r in sorted(x['monitor'],key=lambda z:-(num(z.get('蓄势证据分')) or -1))[:15]]),
            '','## 悠悠大户求购排行（不是Whale持仓）',m['demand'].get('basis','数据不可用'),table(['用户','有效求购总额','较上批次变化','商品数'],[[r['user_name'],round(r['valid_purchase_amount'],2),None if r['change_vs_previous'] is None else round(r['change_vs_previous'],2),r['items']] for r in x['demand_rank'][:20]]),'完整Top100及商品明细：output/demand_whales.json、output/demand_whales.csv。',
            '','## 蓄势观察候选', '高分仅表示量价证据符合设计，尚未通过买入系统验证。']
    for key,title in [('sequence','完整链条Top5'),('early_coil','提前蓄势Top5')]:
        z=x['coil'].get('lists',{}).get(key,[]);lines+=['',title,table(['商品','分数','形态','理由'],[[r.get('cn'),round(r[key],1),r.get('shape_state'),r.get('reasons')] for r in z])]
    w=m['whale'];lines+=['','## CSQAQ Whale（辅助）',f'状态：{w.get("status")}；{w.get("reason") or w.get("basis","")}。']
    if w.get('events') is not None:lines +=[f'报告时间 {w.get("generated_at")}；新增 {w.get("new_event_rows")} 条。',table(['鲸鱼','事件时间','商品','数量'],[[e.get('steam_name'),e.get('time'),e.get('item'),e.get('quantity')] for e in w['events'][:30]])]
    else:lines+=['尚未取得实采事件；不是“没有大户活动”，也不使用演示数据。']
    lines+=['','## 原版ML与规则扫描',f'原版规则候选 {len(x["original_hits"])} 条；数据日期 {m["original"].get("asof","缺失")}。',table(['规则','商品','价格'],[[r.get('规则'),r.get('饰品'),r.get('价格')] for r in x['original_hits'][:20]]),'原规则状态和资格保持独立，详见 output/latest.md、output/process_score_report.md、output/multifactor_report.md。',
            '','## 使用口径','- 悠悠user_id与Steam ID是不同身份，不能合并为同一人；挂单金额、真实成交、持仓与CD事件不可互换。','- 商品只做精确、唯一的名称/磨损匹配；未映射保留为空，不按相似名称强配。','- 数据失败、过期与零事件区分；Whale不参与加分或否决。','- 新研究费用卖出1%、无滑点；原版历史统计仍以其报告单独标注为准。']
    return '\n'.join(lines)+'\n'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['report','collect-demand','collect-quotes','collect-traditional'],nargs='?',default='report');ap.add_argument('--offline',action='store_true');ap.add_argument('--collect-whale',action='store_true');args=ap.parse_args()
    raw=ROOT/'data/integrations';out=ROOT/'output';raw.mkdir(parents=True,exist_ok=True);out.mkdir(exist_ok=True)
    if args.command.startswith('collect-'):
        name={'collect-demand':'monitor.py','collect-quotes':'intraday_guide.py','collect-traditional':'../buycs_scanner.py'}[args.command]
        env=dict(os.environ);env['YYYP_DATA']=str(raw);env['RAW_FILE']=str(raw/'traditional.csv');env['ITEMS_FILE']=str(ROOT/'integrations/upstream_selected_items.csv')
        script=ROOT/'integrations/up'/name
        code=subprocess.call([sys.executable,str(script.resolve())],env=env)
        if code==0 and args.command=='collect-quotes':
            import shutil
            shutil.copyfile(raw/'intraday_scores_latest.csv',raw/'quotes.csv');shutil.copyfile(raw/'intraday_latest.json',raw/'quote_meta.json')
        raise SystemExit(code)
    modules={};sources={};paths={k:raw/({'buy':'traditional.csv','quotes':'quotes.csv','quote_meta':'quote_meta.json','demand':'yyyp.db'}[k]) for k in SOURCES}
    for key,url in SOURCES.items():
        try:
            if not args.offline:sources[key]=fetch(url,paths[key])
            elif not paths[key].exists():raise FileNotFoundError(key)
        except Exception as exc:modules[key]={'status':'error','error':type(exc).__name__}
    hits=[];pool=[];monitor=[];ranks=[]
    if 'buy' not in modules:
        try:modules['traditional'],pool,hits=traditional(paths['buy'],now().date().isoformat())
        except Exception as exc:modules['traditional']={'status':'error','error':type(exc).__name__}
    else:modules['traditional']=modules.pop('buy')
    try:
        if 'quotes' in modules:raise ValueError('Quote source unavailable')
        monitor=readrows(paths['quotes']);meta=readjson(paths['quote_meta'],{}) if 'quote_meta' not in modules else {}
        if not monitor or 'yyyp_id' not in monitor[0]:raise ValueError('Quote CSV schema')
        modules['quotes']={k:v for k,v in meta.items() if k in ('status','generated_at','price_rows','price_missing_rows','monitor_items','score_dates','demand_batches')}
        modules['quotes'].setdefault('status','partial');modules['quotes']['rows']=len(monitor)
        if meta.get('generated_at'):
            dt=datetime.fromisoformat(meta['generated_at']);dt=dt.replace(tzinfo=TZ) if dt.tzinfo is None else dt
            modules['quotes']['age_hours']=(now()-dt).total_seconds()/3600
            if modules['quotes']['age_hours']>18:modules['quotes']['status']='stale'
    except Exception as exc:modules['quotes']={'status':'error','error':type(exc).__name__}
    try:
        if 'demand' in modules:raise ValueError('Demand source unavailable')
        modules['demand'],ranks=demand_rank(paths['demand'])
    except Exception as exc:modules['demand']={'status':'error','error':type(exc).__name__}
    try:modules['whale']=whale(ROOT,args.collect_whale)
    except Exception as exc:modules['whale']={'status':'error','reason':type(exc).__name__+'；请查看采集日志，未当作零事件','events':None}
    coil=readjson(out/'daily_coil_candidates.json',{});modules['coil']={'status':coil.get('status','missing'),'asof':coil.get('asof'),'daily_rows':coil.get('daily_rows')}
    originals=readrows(out/'screen_latest.csv') if (out/'screen_latest.csv').exists() else []
    latest=(out/'latest.md').read_text() if (out/'latest.md').exists() else ''
    import re
    match=re.search(r'CS2 买点扫描 · (\d{4}-\d{2}-\d{2})',latest);modules['original']={'status':'available' if latest else 'missing','asof':match[1] if match else None}
    coils=readrows(out/'daily_coil_scores.csv') if (out/'daily_coil_scores.csv').exists() else []
    monitor=join_monitor(monitor,coils,hits)
    result={'version':'unified-system-v1','generated_at':now().isoformat(),'status':'partial' if any(m.get('status') not in ('ok','success','available') for m in modules.values()) else 'ok','modules':modules,'sources':sources,'traditional_hits':hits,'demand_rank':ranks,'monitor':monitor,'coil':coil,'original_hits':originals,'purchase_list_requests':0}
    multi=readrows(out/'daily_multifactor_scores.csv') if (out/'daily_multifactor_scores.csv').exists() else []
    decision=build_decisions(result,pool,coils,multi,now());result['decision']={k:v for k,v in decision.items() if k!='rows'}
    dump(out/'decision_latest.json',decision);writecsv(out/'decision_latest.csv',decision['rows']);(out/'decision_latest.md').write_text(render_decisions(decision))
    history=out/'history'/('decision_'+now().date().isoformat()+'_'+decision['version']+'.json')
    if not history.exists():dump(history,decision)
    dump(out/'system_latest.json',result);(out/'system_latest.md').write_text(render_decisions(decision)+'\n---\n\n'+render(result));dump(out/'demand_whales.json',{'meta':modules['demand'],'rank':ranks});writecsv(out/'demand_whales.csv',ranks);writecsv(out/'traditional_pool.csv',pool);writecsv(out/'traditional_hits.csv',hits);writecsv(out/'unified_monitor.csv',monitor)
    if os.environ.get('GITHUB_STEP_SUMMARY'):Path(os.environ['GITHUB_STEP_SUMMARY']).write_text(render_decisions(decision))
    print('UNIFIED_SYSTEM_COMPLETE',json.dumps({'status':result['status'],'modules':{k:v.get('status') for k,v in modules.items()},'monitored':len(monitor),'traditional_hits':len(hits)},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
