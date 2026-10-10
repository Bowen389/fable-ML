# -*- coding: utf-8 -*-
"""全部配置来自环境变量（GitHub Actions 里用 secrets / env 注入），本地运行可直接 export"""
import os
import pandas as pd

ROOT = os.environ.get('CS2_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)

API_KEY = os.environ.get('STEAMDT_API_KEY', '').strip()
DATA_SOURCE = os.environ.get('DATA_SOURCE', 'api')            # api / offline（只用本地已有数据）
PLATFORM = os.environ.get('PLATFORM', 'ALL')                   # ALL/BUFF/YOUPIN/C5/STEAM/HALOSKINS
REFRESH_MODE = os.environ.get('REFRESH_MODE', 'auto')          # auto / full / none
MAX_FETCH_MINUTES = float(os.environ.get('MAX_FETCH_MINUTES', '40'))
RATE_PER_MINUTE = int(os.environ.get('RATE_PER_MINUTE', '110'))
FEE = float(os.environ.get('FEE', '0.025'))
SLIPPAGE = float(os.environ.get('SLIPPAGE', '0.005'))
PIPELINE_VERSION = 'causal-v2'
def net_return(gross):
    return (1 + gross) * (1 - SLIPPAGE) / (1 + SLIPPAGE) * (1 - FEE) - 1
DROP_TODAY_BAR = os.environ.get('DROP_TODAY_BAR', '1') == '1'
SAVE_SIGNALS = os.environ.get('SAVE_SIGNALS', '1') == '1'
AUTO_UPDATE_STATUS = os.environ.get('AUTO_UPDATE_STATUS', '1') == '1'
ML_MIN_IC = float(os.environ.get('ML_MIN_IC', '0.05'))

TZ = 'Asia/Shanghai'
def now_cst():
    return pd.Timestamp.now(tz=TZ).tz_localize(None)
TODAY = now_cst().normalize()

for d in ['data/bars', 'state', 'output/history', 'seed']:
    os.makedirs(P(d), exist_ok=True)
