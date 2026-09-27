# -*- coding: utf-8 -*-
"""推送：配置了哪个 secret 就用哪个（可同时多个）。都没配就只写文件。"""
import os, json
import requests


def send(title, text, md=None):
    sent = []
    tg_token, tg_chat = os.environ.get('TG_BOT_TOKEN', ''), os.environ.get('TG_CHAT_ID', '')
    if tg_token and tg_chat:
        try:
            r = requests.post(f'https://api.telegram.org/bot{tg_token}/sendMessage',
                              json={'chat_id': tg_chat, 'text': f'{title}\n{text}'[:4000], 'disable_web_page_preview': True}, timeout=20)
            sent.append(f'telegram:{r.status_code}')
        except Exception as e:
            sent.append(f'telegram:err {e}')
    sc_key = os.environ.get('SERVERCHAN_KEY', '')          # Server酱（微信推送）https://sct.ftqq.com
    if sc_key:
        try:
            r = requests.post(f'https://sctapi.ftqq.com/{sc_key}.send', data={'title': title[:32], 'desp': (md or text)[:20000]}, timeout=20)
            sent.append(f'serverchan:{r.status_code}')
        except Exception as e:
            sent.append(f'serverchan:err {e}')
    hook = os.environ.get('WEBHOOK_URL', '')               # 企业微信/飞书/钉钉 自定义机器人 或任意 webhook
    if hook:
        try:
            if 'qyapi.weixin.qq.com' in hook:
                payload = {'msgtype': 'text', 'text': {'content': f'{title}\n{text}'[:2000]}}
            elif 'open.feishu.cn' in hook or 'open.larksuite.com' in hook:
                payload = {'msg_type': 'text', 'content': {'text': f'{title}\n{text}'}}
            elif 'oapi.dingtalk.com' in hook:
                payload = {'msgtype': 'text', 'text': {'content': f'{title}\n{text}'}}
            else:
                payload = {'title': title, 'text': text}
            r = requests.post(hook, json=payload, timeout=20)
            sent.append(f'webhook:{r.status_code}')
        except Exception as e:
            sent.append(f'webhook:err {e}')
    return sent
