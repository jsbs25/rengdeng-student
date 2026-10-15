#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量生成高频词词义（DeepSeek 官方 API，分批）→ data/vocab_meanings.json"""
import json, re, time, urllib.request
from pathlib import Path

DIR = Path(__file__).parent
KEY = open(DIR / 'data' / 'ai_key.txt', encoding='utf-8').read().strip()
API = 'https://api.deepseek.com/chat/completions'

def call(messages, max_tokens=4000):
    body = json.dumps({"model": "deepseek-chat", "messages": messages, "max_tokens": max_tokens}, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(API, data=body, headers={
        "Content-Type": "application/json", "Authorization": "Bearer " + KEY}, method="POST")
    with urllib.request.urlopen(req, timeout=90) as resp:
        d = json.loads(resp.read())
        return d["choices"][0]["message"]["content"].strip()

def main():
    words = json.load(open('/tmp/top_words.json', encoding='utf-8'))
    out = {}
    BATCH = 40
    for i in range(0, len(words), BATCH):
        batch = words[i:i+BATCH]
        prompt = (
            "请为下列阿拉伯语高频词提供简洁的中文释义（2-6字）和英文释义。"
            "严格按 JSON 格式输出：{\"词\": {\"cn\": \"中文\", \"en\": \"English\"}, ...}\n"
            "只输出 JSON，不要其他内容。\n\n词表：" + json.dumps(batch, ensure_ascii=False)
        )
        try:
            reply = call([{"role": "user", "content": prompt}])
            m = re.search(r'\{[\s\S]*\}', reply)
            if m:
                parsed = json.loads(m.group(0))
                for w in batch:
                    if w in parsed and parsed[w].get('cn'):
                        out[w] = parsed[w]
            print(f'批次 {i}-{i+len(batch)} 完成，累计 {len(out)}', flush=True)
        except Exception as e:
            print(f'批次 {i} 失败: {str(e)[:80]}', flush=True)
        time.sleep(1)

    json.dump(out, open(DIR / 'data' / 'vocab_meanings.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'✅ 完成: {len(out)}/{len(words)} 个词有释义')

if __name__ == '__main__':
    main()
