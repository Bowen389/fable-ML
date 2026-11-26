"""凭证有效期监控：报价/求购 token 约 10 天需更新一次，不能依赖人记。

只读本地状态判断各数据源的"最近一次成功采集"时间，换算成距今天数：
  ok        <=7 天，在有效期内
  expiring  7~10 天，临近到期，提前提醒
  expired   >10 天，很可能已失效，必须在报告顶部强提醒
  not_configured  没有配置凭据，无法采集
  error      最近一次采集报错
  unknown    找不到可用的时间戳

口径：token 是否失效以"最近成功采集时间"代理——采集成功即说明 token 当时可用；
数据停滞超过有效期，最常见原因就是 token 到期而人没记得更新。
Whale（索塔/CSQAQ）只作为加分与观察信息，永远不是入场的必要条件，不参与放行或否决。
"""
import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

TZ = timezone(timedelta(hours=8))
TOKEN_TTL_DAYS = 10          # 报价/求购 token 的有效期
REMIND_DAYS = 7              # 距到期还有几天就开始提醒

SOURCES = {
    'quotes': {'label': '报价/在售（悠悠）', 'secret': 'YP_RAW_HEADERS / 报价采集凭据'},
    'demand': {'label': '求购与大户求购排行', 'secret': 'YP_RAW_HEADERS / 求购采集凭据'},
    'whale': {'label': 'CSQAQ Whale（索塔）', 'secret': 'CSQAQ_TOKEN'},
}


def _parse(ts):
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return None
    return dt.replace(tzinfo=TZ) if dt.tzinfo is None else dt


def _age_days(ts, now):
    dt = _parse(ts)
    if dt is None:
        return None
    return round((now - dt).total_seconds() / 86400.0, 1)


def _status(age, configured, error=False):
    if error:
        return 'error'
    if not configured:
        return 'not_configured'
    if age is None:
        return 'unknown'
    if age > TOKEN_TTL_DAYS:
        return 'expired'
    if age > REMIND_DAYS:
        return 'expiring'
    return 'ok'


def _remind(source, status, age, configured=True):
    meta = SOURCES[source]
    if status == 'not_configured':
        return f"{meta['label']}：未配置凭据（{meta['secret']}），采集未执行；更新凭据后手动触发采集。"
    if status == 'error':
        return f"{meta['label']}：最近一次采集报错，token 可能已失效，请更新 {meta['secret']} 后重采。"
    if status == 'unknown':
        return f"{meta['label']}：找不到成功采集时间，无法判断 token 是否在有效期内。"
    if status == 'expired':
        return f"{meta['label']}：距上次成功采集已 {age} 天，超过 {TOKEN_TTL_DAYS} 天有效期，token 很可能已失效——请更新 {meta['secret']} 并重新采集。"
    if status == 'expiring':
        return f"{meta['label']}：距上次成功采集已 {age} 天，{TOKEN_TTL_DAYS - age} 天内将到期，请提前更新 {meta['secret']}。"
    return f"{meta['label']}：{age} 天前成功采集，在 {TOKEN_TTL_DAYS} 天有效期内。"


def watch(quotes, demand, whale, token_configured, now):
    """根据三个模块的采集结果判断各自凭证/数据的新鲜度。

    quotes/demand/whale: 模块 dict（可能为 None 或含 error）。
    token_configured: bool，各数据源凭据是否已配置。
    """
    now = now or datetime.now(TZ)
    out = {}
    alerts = []
    for source, mod in (('quotes', quotes), ('demand', demand), ('whale', whale)):
        meta = SOURCES[source]
        if mod is None or mod.get('status') == 'error':
            age = _age_days(mod.get('generated_at') or mod.get('batch'), now) if isinstance(mod, dict) else None
            configured = bool(token_configured) if source == 'whale' else True
            # 鲸鱼没有 token 就是没配置；报价/求购没有数据则按采集不可用告警
            status = 'not_configured' if (source == 'whale' and not configured) else _status(age, configured, error=True)
        else:
            if source == 'quotes':
                ts = mod.get('generated_at')
            elif source == 'demand':
                ts = mod.get('batch')
            else:
                ts = mod.get('generated_at')
            age = _age_days(ts, now)
            configured = bool(token_configured) if source == 'whale' else True
            if source == 'quotes' and mod.get('status') == 'stale':
                status = 'expired'  # 报价超过6小时即视为停滞，按过期处理
            else:
                status = _status(age, configured)
        item = {'label': meta['label'], 'status': status, 'age_days': age,
                'last_success': mod.get('generated_at') or mod.get('batch') if isinstance(mod, dict) else None,
                'reminder': _remind(source, status, age, configured)}
        out[source] = item
        if status in ('expired', 'error'):
            alerts.append(item['reminder'])
        elif status == 'expiring':
            alerts.append('【临期提醒】' + item['reminder'])
    result = {'generated_at': now.isoformat(), 'ttl_days': TOKEN_TTL_DAYS,
              'remind_days': REMIND_DAYS, 'sources': out, 'alerts': alerts,
              'all_ok': not alerts}
    return result


def local_state(root):
    """离线自检：直接读本地落盘状态，供人工/定时检查，不发请求。"""
    root = Path(root)
    quotes = demand = whale = None
    qm = root / 'data/integrations/quote_meta.json'
    if qm.is_file():
        try:
            quotes = json.loads(qm.read_text(encoding='utf-8'))
        except Exception:
            quotes = {'status': 'error'}
    db = root / 'data/integrations/yyyp.db'
    if db.is_file():
        try:
            with sqlite3.connect(db) as conn:
                row = conn.execute('SELECT MAX(run) FROM snapshot').fetchone()
            if row and row[0]:
                demand = {'status': 'ok', 'batch': row[0]}
        except Exception:
            demand = {'status': 'error'}
    wr = root / 'state/whale_monitor/reports/latest_report.json'
    if wr.is_file():
        try:
            whale = json.loads(wr.read_text(encoding='utf-8'))
        except Exception:
            whale = {'status': 'error'}
    token = bool(os.getenv('CSQAQ_TOKEN', '').strip())
    return watch(quotes, demand, whale, token, datetime.now(TZ))


if __name__ == '__main__':
    import json
    import sys
    from pathlib import Path
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent
    result = local_state(root)
    out = root / 'output/token_watch.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
