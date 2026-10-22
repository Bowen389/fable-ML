"""Read-only integration summary, preserving independent module dates and failures."""
import json,re
from pathlib import Path
START='<!-- unified-system:start -->';END='<!-- unified-system:end -->'

def load_system(root):
    try:return json.loads((Path(root)/'output/system_latest.json').read_text(encoding='utf-8-sig'))
    except (OSError,ValueError):return None

def merge_system_section(text,root):
    text=re.sub(re.escape(START)+r'.*?'+re.escape(END),'',text,flags=re.S).strip()
    x=load_system(root)
    if not x:return text+'\n'
    s=lambda z:str(z if z is not None else '缺失').replace('|',' / ').replace('\n',' ')
    lines=[START,'## 综合决策（主结论）','',f'汇总时间：{s(x.get("generated_at"))}。原版规则、传统四类买点、蓄势、求购与Whale分别展示，不因叠加证据自动提高买入资格。','','| 模块 | 状态 | 数据日期／说明 |','|---|---|---|']
    for key,name in [('traditional','四类传统买点全扫'),('quotes','全池报价与在售'),('demand','求购与大户求购排行'),('whale','CSQAQ Whale辅助'),('coil','蓄势评分'),('original','原版规则与ML')]:
        m=x.get('modules',{}).get(key,{});lines.append('| '+name+' | '+s(m.get('status'))+' | '+s(m.get('asof') or m.get('batch') or m.get('generated_at') or m.get('reason') or m.get('error'))+' |')
    lines+=['','[查看全部模块总报告](https://github.com/Bowen389/fable-ML/blob/main/output/system_latest.md) · [815件监控与附加信号](https://github.com/Bowen389/fable-ML/blob/main/output/unified_monitor.csv) · [传统四类命中明细](https://github.com/Bowen389/fable-ML/blob/main/output/traditional_hits.csv)',
            'Whale实采不可用不等于无大户活动；悠悠挂单排行不等于Steam持仓。各模块更新时间分别标注。',END]
    d=x.get('decision',{})
    if d:
        market=d.get('market',{});brief=[f'市场：{s(market.get("state"))}；权限：{s(market.get("permission"))}；研究入场满足 {d.get("research_ready",0)} 件。尚未通过买入验证。','','| 商品 | 潜力 | 入场 | 状态 |','|---|---:|---:|---|']
        for r in d.get('top5',[]):brief.append('| '+' | '.join(s(r.get(k)) for k in ('cn','potential','entry','state'))+' |')
        brief+=['','[综合决策主报告](https://github.com/Bowen389/fable-ML/blob/main/output/decision_latest.md) · [全部商品决策](https://github.com/Bowen389/fable-ML/blob/main/output/decision_latest.csv)','','### 底层证据与覆盖']
        lines=lines[:2]+['']+brief+lines[2:]
    return '\n'.join(lines)+'\n\n'+text+'\n'
