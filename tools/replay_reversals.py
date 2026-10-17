"""Offline, read-only replay of current reversal modules (no API or signal writes)."""
import sys, copy
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from cs2 import data, features, rules, monitor, scan, config


def main():
    clean=features.clean_bars(data.usable_bars(data.load_bars(),data.load_universe()))
    feat,_=features.build_features(clean)
    rs=[r for r in rules.load_rules() if r['id'].startswith('RB')]
    dates=list(pd.to_datetime(['2026-02-09','2026-02-10']))+list(pd.date_range('2026-05-26','2026-05-31'))+list(pd.date_range('2026-08-20','2026-08-24'))
    report=['# 品类反弹与龙头识别回放','',
      '使用当前规则逐日独立判定；不是当时实盘部署重建。指定日期参与设计，全部历史结果仅为设计样本。',
      '信号日收盘确认，次日收盘模拟入场；净收益含现有手续费/滑点；没有成交量、订单簿或历史价差数据。',
      '龙头候选要求同类综合强度≥70分、3日/7日上涨且7日跑赢同类；不代表成交额龙头。', '',
      '| 日期 | 反弹形态记录 | 健康闸门放行记录 | 去重放行数 | 放行龙头数 |',
      '|---|---:|---:|---:|---:|']
    details=[]
    for day in dates:
        f=feat[feat.date<=day].copy().reset_index(drop=True)
        active=copy.deepcopy(rs)
        for r in active:r['status']='active'
        health,updates=monitor.Health(f).table(active,day)
        for r in active:
            if r['id'] in updates:r['status']=updates[r['id']][1]
        hits,_=scan.scan_rules(f,active,day)
        d=f[(f.date==day)&f.eligible&(f.flat_14<=.5)]
        shapes=[]
        for r in active:
            z=d[rules.strategy_mask(d,r)].copy();z['rule']=r['id'];z['status']=r['status'];shapes.append(z)
        z=pd.concat(shapes)
        n=len(hits);u=hits['饰品'].nunique() if n else 0
        leaders=hits.loc[hits['龙头候选']=='是','饰品'].nunique() if n else 0
        report.append(f'| {day.date()} | {len(z)} | {n} | {u} | {leaders} |')
        lines=[f'## {day.date()}', '', '| 单品 | 模块状态 | 强度分 | 龙头候选 | 当日% | 7日% | 同类上涨% |', '|---|---|---:|---|---:|---:|---:|']
        for _,a in z.sort_values('leader_score',ascending=False).head(12).iterrows():
            name=str(a['name']).replace('|',r'\|')
            lines.append(f'| {name} | {a["status"]} | {a.leader_score*100:.1f} | {"是" if a.leader_flag else "否"} | {a.r_1*100:.1f} | {a.r_7*100:.1f} | {a.peer_breadth1*100:.1f} |')
        lines.extend(['','健康度：',health.to_markdown(index=False),''])
        details.extend(lines)
        print(day.date(),len(z),n,u,flush=True)
    report.extend(['','## 全历史设计样本检验','', '| 模块 | 去重成熟样本 | 净胜率 | 中位净收益 | 跑赢全市场中位率 |','|---|---:|---:|---:|---:|'])
    h=monitor.Health(feat);last=feat.date.max()
    for r in rs:
        s=h.stats(rules.strategy_mask(feat,r),r['H'],pd.Timestamp('2026-02-01'),last-pd.Timedelta(days=r['H']+1))
        report.append(f'| {r["id"]} {r["name"]} | {s["n"]} | {s.get("win",0):.1%} | {s.get("med",0):+.1%} | {s.get("beat",0):.1%} |')
    report.extend(['','强度排名只参与候选展示，未绕过健康闸门。反弹条件没有日期或单品名称白名单。',
      '品类范围使用预先定义的武器类别；现有饰品池有覆盖偏差。未来需要固定参数后的新数据验证。','']+details)
    path=Path(config.P('output','reversal_replay_2026.md'))
    path.write_text('\n'.join(report),encoding='utf8')
    print('saved',path,flush=True)


if __name__=='__main__':main()
