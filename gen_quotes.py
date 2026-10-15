#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成阿拉伯名人名言/谚语 40 条（阿语+中文+英文）"""
import json, re, time, urllib.request
from pathlib import Path

DIR = Path(__file__).parent
KEY = open(DIR / 'data' / 'ai_key.txt', encoding='utf-8').read().strip()
API = 'https://api.deepseek.com/chat/completions'

def call(messages, max_tokens=4000):
    body = json.dumps({"model": "deepseek-chat", "messages": messages, "max_tokens": max_tokens}, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(API, data=body, headers={
        "Content-Type": "application/json", "Authorization": "Bearer " + KEY}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:
        d = json.loads(resp.read())
        return d["choices"][0]["message"]["content"].strip()

def main():
    prompt = (
        "请提供 40 条经典阿拉伯语谚语和名人名言（如：العلم نور 知识是光）。"
        "要求：每条包含 阿拉伯语原文（带完整音符）、中文翻译、英文翻译、出处（阿拉伯谚语/具体名人）。"
        "严格按 JSON 数组格式输出：[{\"a\": \"阿语\", \"z\": \"中文\", \"e\": \"英文\", \"src\": \"出处\"}, ...]\n"
        "只输出 JSON，不要其他内容。"
    )
    reply = call([{"role": "user", "content": prompt}], max_tokens=6000)
    m = re.search(r'\[[\s\S]*\]', reply)
    if not m:
        print('❌ 解析失败:', reply[:100])
        return
    quotes = json.loads(m.group(0))
    print('生成:', len(quotes), '条')
    json.dump(quotes, open(DIR / 'data' / 'arabic_quotes.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for q in quotes[:3]:
        print(' -', q['a'][:30], '|', q['z'][:20])

if __name__ == '__main__':
    main()
