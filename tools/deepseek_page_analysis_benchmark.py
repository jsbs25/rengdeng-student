#!/usr/bin/env python3
"""Bounded benchmark for the actual NOUR page-analysis request.

Default: two non-streaming requests to the current page model (deepseek-flash),
using the same JSON mode, thinking=disabled and max_tokens=1150 as server.py.
It records aggregate metrics only; no key or model response is written.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
KEY = (ROOT / 'data' / 'ai_key.txt').read_text(encoding='utf-8').strip()
ENDPOINT = 'https://api.deepseek.com/chat/completions'


def page_prompt(text: str) -> str:
    # Reuse the production prompt builder so the benchmark measures the real
    # page-analysis contract rather than a short toy prompt.
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink):
        import server
    meta = {'id': 'fiqh-quduri', 't': 'مختصر القدوري', 'a': 'أبو الحسين القدوري',
            'c': '法学', 'c_ar': 'فقه', 'discipline': '法学',
            'fiqh_schools': ['hanafi'], 'fiqh_school_labels': ['哈乃斐学派'],
            'fiqh_school_evidence': {'hanafi': ['القدوري']},
            'fiqh_school_inference': '书目元数据推断；不是作者自证或教法裁决',
            'source': 'Shamela local metadata', 'access': '按需读取'}
    return server._page_analysis_prompt({
        'book_title': 'مختصر القدوري · 复杂语法与法学阅读样本',
        'book_kind': 'fiqh', 'page_number': 1, 'page_total': 1,
        'text': text, 'book_meta': meta, 'fiqh_school': 'hanafi',
        'response_language': 'zh-CN',
    })


SEED = ('إذا تعلّق الحكم بوصفٍ مشتقٍّ من معنى في اللفظ، وجب التفريق بين دلالة السياق، '
        'وتركيب الجملة، وعموم العبارة وخصوصها؛ ولا يصح نقل الحكم من موضع إلى آخر إلا بعد '
        'مراجعة النص والقرينة ووجه الاستدلال، مع بيان ما هو منصوص وما هو تفسير وما هو مجرد احتمال. ')


def parse_json(content: str) -> bool:
    s = str(content or '').strip()
    if s.startswith('```'):
        s = s.replace('```json', '', 1).replace('```', '').strip()
    try:
        return isinstance(json.loads(s), dict)
    except Exception:
        a, b = s.find('{'), s.rfind('}')
        if a >= 0 and b > a:
            try:
                return isinstance(json.loads(s[a:b + 1]), dict)
            except Exception:
                return False
        return False


def run(model: str, label: str, text: str) -> dict:
    prompt = page_prompt(text)
    payload = {'model': model, 'messages': [{'role': 'user', 'content': prompt}],
               'temperature': 0.15, 'max_tokens': 1150,
               'response_format': {'type': 'json_object'}, 'thinking': {'type': 'disabled'},
               'stream': False}
    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(ENDPOINT, data=body, method='POST', headers={
        'Content-Type': 'application/json', 'Authorization': 'Bearer ' + KEY,
    })
    started = time.perf_counter()
    row = {'case': label, 'model': model, 'input_chars': len(text),
           'prompt_chars': len(prompt), 'request_bytes': len(body)}
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            raw = resp.read()
            row['http_status'] = int(resp.status)
        row['latency_ms'] = round((time.perf_counter() - started) * 1000)
        data = json.loads(raw.decode('utf-8'))
        usage = data.get('usage') or {}
        message = ((data.get('choices') or [{}])[0].get('message') or {})
        content = message.get('content') or message.get('reasoning_content') or ''
        row.update({'prompt_tokens': usage.get('prompt_tokens'),
                    'completion_tokens': usage.get('completion_tokens'),
                    'total_tokens': usage.get('total_tokens'),
                    'finish_reason': ((data.get('choices') or [{}])[0].get('finish_reason')),
                    'json_parse_ok': parse_json(content),
                    'repair_requests': 0})
    except urllib.error.HTTPError as exc:
        row['latency_ms'] = round((time.perf_counter() - started) * 1000)
        row['http_status'] = exc.code
        row['error_type'] = 'HTTPError'
        row['error_excerpt'] = exc.read().decode('utf-8', 'replace')[:180]
    except Exception as exc:
        row['latency_ms'] = round((time.perf_counter() - started) * 1000)
        row['error_type'] = type(exc).__name__
        row['error_excerpt'] = str(exc)[:180]
    return row


def main() -> None:
    if not KEY:
        raise SystemExit('DeepSeek key is not configured')
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', default=os.environ.get('NUR_PAGE_AI_MODEL', 'deepseek-flash'))
    args = ap.parse_args()
    cases = [('short-grammar-fiqh', (SEED * 8)[:1100]), ('long-grammar-fiqh', (SEED * 48)[:6500])]
    rows = []
    for label, text in cases:
        row = run(args.model, label, text)
        rows.append(row)
        print(json.dumps({k: v for k, v in row.items() if k not in ('error_excerpt',)}, ensure_ascii=False))
    report = {'model': args.model, 'endpoint_host': 'api.deepseek.com',
              'production_profile': {'json_mode': True, 'thinking': 'disabled', 'timeout_s': 75, 'max_tokens': 1150, 'page_text_cap_chars': 6500},
              'cases': rows, 'notes': ['两次请求均为非流式、有界样本；不是长期 SLA。', '输入使用生产页级提示与代表性阿拉伯语语法/法学样本，不写入模型返回正文。', '缓存命中不会产生新 token；生产 JSON 修复路径才会额外重试，本文基准未触发修复请求。']}
    path = ROOT / 'docs' / '20261003-deepseek-page-analysis-performance.json'
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('saved', path)


if __name__ == '__main__':
    main()
