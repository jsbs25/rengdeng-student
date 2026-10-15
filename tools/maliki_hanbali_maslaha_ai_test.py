#!/usr/bin/env python3
"""Bounded NOUR chat-route regression for المصالح المرسلة."""
from __future__ import annotations
import argparse
import json
import sys
import time
import urllib.request
from urllib.parse import urljoin

PROMPT = (
    '请测试你对复杂法源学概念的横向解答能力。主题是 المصالح المرسلة（maslahah mursalah，'
    '无明文特定承认或否定的公共利益）。请比较马立克学派与汉百里学派：\n'
    '1）术语与方法定义；2）它们与古兰经、圣训、共识、类比和教法目的的关系；'
    '3）马立克传统中 مصالح مرسلة 的典型论证边界；4）汉百里传统如何处理相近的公共利益、'
    'سد الذرائع、必要性或政策性推理；5）明确区分两派共识、学派内部不同表述、作者原文、'
    '后世总结与模型归纳；6）列出应回到哪些真实原典或版本核验，但没有逐条核对的卷页、'
    '经文编号、圣训编号、作者原话必须写“待核验”。请用中文为主并保留阿拉伯术语，给出'
    '结构化横向比较，不要只重复问题，不要给现实个案法特瓦。'
)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='http://127.0.0.1:8129')
    args = ap.parse_args()
    body = json.dumps({
        'message': PROMPT,
        'session_id': 'qa-maliki-hanbali-20261005',
        'fast': True,
        'device_id': 'qa-local-20261005',
    }, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(
        urljoin(args.base.rstrip('/') + '/', 'api/chat/message'),
        data=body,
        headers={'Content-Type': 'application/json'},
    )
    started = time.perf_counter()
    with urllib.request.urlopen(req, timeout=180) as response:
        status = response.status
        payload = json.loads(response.read().decode('utf-8'))
    elapsed = round((time.perf_counter() - started) * 1000)
    text = str(payload.get('arabic') or payload.get('reply') or '').strip()
    checks = {
        'maliki': any(x in text for x in ('马立克', 'المالكية', 'Maliki')),
        'hanbali': any(x in text for x in ('汉百里', 'الحنابلة', 'Hanbali')),
        'maslaha': ('المصلحة' in text or 'المصالح المرسلة' in text) and ('公共利益' in text or '利益' in text),
        'evidence_layers': all(x in text for x in ('证据', '原典', '模型归纳')),
        'caveat': any(x in text for x in ('待核验', '学习性', '不是法特瓦', '不等于')),
        'not_echo_only': len(text) >= 500 and text.replace(' ', '') != PROMPT.replace(' ', ''),
    }
    result = {
        'http_status': status,
        'elapsed_ms': elapsed,
        'answer_chars': len(text),
        'checks': checks,
        'ok': status == 200 and all(checks.values()),
        'answer': text,
        'request_mode': 'NOUR /api/chat/message fast=true; single bounded request',
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['ok'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
