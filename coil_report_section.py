"""Read-only daily coil section; standard library only, no network or order permission."""
import json,re
from pathlib import Path
from datetime import datetime,timedelta,timezone,date
TZ=timezone(timedelta(hours=8))
START='<!-- daily-coil:start -->'
END='<!-- daily-coil:end -->'

def load_coil_snapshot(root):
    try:
        x=json.loads((Path(root)/'output/daily_coil_candidates.json').read_text(encoding='utf-8-sig'))
        if not isinstance(x,dict):raise ValueError('Expected object')
        return x
    except FileNotFoundError:return {'status':'missing','error':'本次日报尚未取得蓄势候选文件'}
    except (ValueError,OSError) as exc:return {'status':'error','error':'蓄势候选文件无法读取：'+type(exc).__name__}

def render_coil_section(root,report_asof=None,today=None):
    x=load_coil_snapshot(root);now=today or datetime.now(TZ).date()
    if isinstance(now,str):now=date.fromisoformat(now)
    expected=now-timedelta(days=1);safe=lambda s:str(s).replace('|',' / ').replace('\n',' ')
    lines=[START,'## 每日蓄势观察候选','', '**独立研究证据分，未通过买入系统验证；不自动开仓、不改变原有买点资格。**']
    try:asof=date.fromisoformat(x.get('asof',''))
    except (ValueError,TypeError):asof=None
    if x.get('status') in ('error','missing') or asof is None:
        lines+=['','状态：数据不足／生成失败，不能解释为零候选。原因：'+safe(x.get('error','缺少有效数据日期')),END]
        return '\n'.join(lines)
    if asof>expected:
        lines+=['','状态：数据日期异常，暂不展示候选；预计完整日为'+str(expected)+'，文件日期为'+str(asof)+'。',END]
        return '\n'.join(lines)
    stale=asof<expected or x.get('status')!='ok'
    lines+=['',f'日K日期：**{asof}**；生成时间：{safe(x.get("generated_at","未知"))}。']
    if stale:lines+=['**数据未更新至预计完整日 '+str(expected)+'；以下为旧日期观察名单，不能当作当前买点。**']
    if report_asof is not None and str(report_asof)[:10]!=str(asof):lines+=['主报告与本栏数据日期不同，请按各自日期解读。']
    lines+=[f'取数 {x.get("loaded",0)}/{x.get("requested",0)} 件；当日可评分 {x.get("daily_rows",0)} 件；仅复用每日已采集日K。',
            '市场修复代理：'+('满足，但不构成买入许可' if x.get('market_ok') is True else '未满足／数据不足，仅作观察')+'。',
            '完整链条分：前期参与20＋量价台阶15＋洗盘20＋持续放量20＋支撑空间15＋相对领先10，风险最多扣30。数据覆盖率表示字段可计算，不表示形态链条完整。']
    for key,title,score in [('sequence','完整链条证据 Top5','sequence'),('early_coil','提前蓄势观察 Top5','early_coil')]:
        lines+=['','### '+title,'','| 商品 | 分数 | 形态 | 覆盖率 | 风险扣分 | 主要理由 |','|---|---:|---|---:|---:|---|']
        lists=x.get('lists',{})
        if not isinstance(lists,dict):lists={}
        rows=lists.get(key,[])
        if not isinstance(rows,list):rows=[]
        rows=[row for row in rows if isinstance(row,dict)]
        if not rows:lines+=['本栏暂无可评分条目；请结合取数状态，不能推断没有蓄势商品。']
        for row in rows[:5]:
            def num(k,fmt):
                try:return format(float(row[k]),fmt)
                except (KeyError,TypeError,ValueError):return '缺失'
            lines.append('| '+safe(row.get('cn',row.get('name','未知')))+' | '+num(score,'.1f')+' | '+safe(row.get('shape_state','未知'))+' | '+num('coverage','.0%')+' | '+num('penalty','.1f')+' | '+safe(row.get('reasons','缺失'))+' |')
    lines+=['','价格为悠悠日K、成交量为全平台代理；建仓、洗盘和档位是量价代理，不能认定真实会员身份或成本。Whale仅辅助。',
            '研究费用：卖出1%、买入0、无滑点。该栏不重跑历史回测或拟合模型；分数不是涨幅概率。',
            '[完整分项](https://github.com/Bowen389/fable-ML/blob/main/output/daily_coil_scores.csv) · [独立验证报告](https://github.com/Bowen389/fable-ML/blob/main/output/rebound_coil/report.md)',END]
    return '\n'.join(lines)

def merge_coil_section(markdown,root,report_asof=None,today=None):
    text=re.sub(re.escape(START)+r'.*?'+re.escape(END),'',markdown,flags=re.S).rstrip()
    return text+'\n\n'+render_coil_section(root,report_asof,today)+'\n'
