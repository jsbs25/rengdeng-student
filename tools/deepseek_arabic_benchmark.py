#!/usr/bin/env python3
"""Bounded, non-streaming DeepSeek Arabic latency/token benchmark.
Reads the existing server key without printing it; writes only aggregate metrics.
"""
from __future__ import annotations
import json, time, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
key = (ROOT / 'data' / 'ai_key.txt').read_text(encoding='utf-8').strip()
if not key:
    raise SystemExit('DeepSeek key is not configured')

seed = ('حلّل هذه الجملة العربية تحليلاً تعليمياً: حدّد الجذر والوزن والوظيفة النحوية، '
        'ثم قارن بإيجاز بين طريقة فهمها في سياق علم اللغة وسياق قراءة نص فقهي، مع بيان ما يحتاج إلى مراجعة المصدر الأصلي. ')
# One request per size: bounded and representative, not a batch crawl.
cases = [
    ('short', seed[:260]),
    ('medium', (seed * 7)[:1800]),
    ('long', (seed * 30)[:7000]),
]
endpoint = 'https://api.deepseek.com/chat/completions'
results = []
for label, text in cases:
    payload = {
        'model': 'deepseek-chat',
        'messages': [
            {'role': 'system', 'content': 'أنت مدرس لغة عربية دقيق. أجب بإيجاز في JSON صالح.'},
            {'role': 'user', 'content': text + '\nأعد JSON بمفاتيح: overview, root, grammar, uncertainty.'},
        ],
        'temperature': 0.1,
        'max_tokens': 420,
        'response_format': {'type': 'json_object'},
        'stream': False,
    }
    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(endpoint, data=body, method='POST', headers={
        'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key,
    })
    started = time.perf_counter()
    row = {'case': label, 'input_chars': len(text), 'request_bytes': len(body)}
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            raw = resp.read()
            row['http_status'] = int(resp.status)
        row['latency_ms'] = round((time.perf_counter() - started) * 1000)
        data = json.loads(raw.decode('utf-8'))
        usage = data.get('usage') or {}
        row.update({
            'prompt_tokens': usage.get('prompt_tokens'),
            'completion_tokens': usage.get('completion_tokens'),
            'total_tokens': usage.get('total_tokens'),
            'finish_reason': ((data.get('choices') or [{}])[0].get('finish_reason')),
            'content_chars': len(str((((data.get('choices') or [{}])[0].get('message') or {}).get('content')) or '')),
        })
    except urllib.error.HTTPError as exc:
        row['latency_ms'] = round((time.perf_counter() - started) * 1000)
        row['http_status'] = exc.code
        row['error'] = exc.read().decode('utf-8', 'replace')[:240]
    except Exception as exc:
        row['latency_ms'] = round((time.perf_counter() - started) * 1000)
        row['error'] = type(exc).__name__ + ': ' + str(exc)[:180]
    results.append(row)
    print(json.dumps(row, ensure_ascii=False))

out = {'model': 'deepseek-chat', 'endpoint_host': 'api.deepseek.com', 'cases': results}
report_dir = ROOT / 'docs'
report_dir.mkdir(exist_ok=True)
out_path = report_dir / '20261003-deepseek-arabic-benchmark.json'
out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('saved', out_path)
