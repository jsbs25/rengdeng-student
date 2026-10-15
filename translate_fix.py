#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量补齐缺翻译的句子（AI 翻译）并重建数据"""
import json, os, re, sys, urllib.request, socket
from pathlib import Path

DIR = Path(__file__).parent

# ===== 复用 server.py 的 AI 端点探测 =====
def detect_endpoint():
    """优先 DeepSeek 官方 API（key 文件），其次本地代理"""
    key = ''
    try:
        kf = DIR / 'data' / 'ai_key.txt'
        if kf.exists():
            key = kf.read_text(encoding='utf-8').strip()
    except Exception:
        pass
    if key:
        return {'url': 'https://api.deepseek.com/chat/completions', 'key': key, 'model': 'deepseek-chat'}
    candidates = []
    try:
        cfg_path = os.path.expanduser("~/Library/Application Support/AionClaw/openclaw/state/openclaw.json")
        if os.path.exists(cfg_path):
            with open(cfg_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            prov = cfg.get('models', {}).get('providers', {}).get('aionclaw-server', {})
            base = prov.get('baseUrl', '')
            if base:
                candidates.append((base.rstrip('/') + '/chat/completions', '', 'deepseek-v4-flash'))
    except Exception:
        pass
    for url, k, m in candidates:
        try:
            host = url.split("//")[1].split("/")[0].split(":")[0]
            port = int(url.split(":")[2].split("/")[0])
            s = socket.create_connection((host, port), timeout=1.5)
            s.close()
            return {'url': url, 'key': k, 'model': m}
        except Exception:
            continue
    return {'url': 'http://127.0.0.1:65368/v1/chat/completions', 'key': '', 'model': 'deepseek-v4-flash'}

CFG = detect_endpoint()
API_URL = CFG['url']
print(f"🤖 AI 端点: {API_URL}")

def ai_translate(batch):
    """翻译一批句子，返回 {idx: {'en':..., 'cn':...}}"""
    lines = []
    for i, s in enumerate(batch):
        lines.append(f"{i}. {s['ar']}")
    prompt = (
        "请把下列阿拉伯语句子翻译成英语和中文。只返回 JSON，格式：{\"0\": {\"en\": \"...\", \"cn\": \"...\"}, ...}。\n"
        + "\n".join(lines)
    )
    body = json.dumps({"model": CFG.get('model', 'deepseek-chat'), "messages": [
        {"role": "system", "content": "你是专业阿拉伯语翻译。严格按要求的 JSON 格式输出，不要输出其他内容。"},
        {"role": "user", "content": prompt},
    ], "max_tokens": 2000, "temperature": 0.3}, ensure_ascii=False).encode("utf-8")
    hdrs = {"Content-Type": "application/json"}
    if CFG.get('key'):
        hdrs["Authorization"] = "Bearer " + CFG['key']
    req = urllib.request.Request(API_URL, data=body, headers=hdrs, method="POST")
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read())
        return data["choices"][0]["message"]["content"].strip()

def extract_json(text):
    """从 AI 回复中提取 JSON"""
    m = re.search(r'\{[\s\S]*\}', text)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None

def fix_missing(limit=None, quiet=False):
    """补齐 categorized.json 中缺翻译的句子（limit 限制每次最多翻译多少句）"""
    cat_file = DIR / 'data' / 'categorized.json'
    data = json.load(open(cat_file, encoding='utf-8'))
    missing = [it for it in data if not it.get('en', '').strip() or not it.get('cn', '').strip()]
    if limit:
        missing = missing[:limit]
    if not quiet:
        print(f"缺翻译: {len(missing)} 句")
    if not missing:
        return 0
    fixed = 0
    BATCH = 15
    for start in range(0, len(missing), BATCH):
        batch = missing[start:start + BATCH]
        try:
            reply = ai_translate(batch)
            result = extract_json(reply)
            if not result:
                if not quiet:
                    print(f"⚠️ 批次 {start} 解析失败: {reply[:100]}")
                continue
            for i, s in enumerate(batch):
                entry = result.get(str(i)) or result.get(i)
                if entry and entry.get('en') and entry.get('cn'):
                    s['en'] = entry['en'].strip()
                    s['cn'] = entry['cn'].strip()
                    fixed += 1
            if not quiet:
                print(f"批次 {start}-{start+len(batch)-1} 完成，累计 {fixed}")
        except Exception as e:
            if not quiet:
                print(f"❌ 批次 {start} 失败: {e}")
    json.dump(data, open(cat_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # 写回 data.json 时保留 cat/py（防止爬虫 recategorize 丢自定义分类）
    raw = []
    for it in data:
        r = {'ar': it.get('ar', ''), 'en': it.get('en', ''), 'cn': it.get('cn', '')}
        if it.get('cat'):
            r['cat'] = it['cat']
        if it.get('py'):
            r['py'] = it['py']
        raw.append(r)
    json.dump(raw, open(DIR / 'data' / 'data.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if not quiet:
        print(f"✅ 已修复 {fixed} 句，数据已写回")
    return fixed

def main():
    n = fix_missing()
    print(f'共修复 {n} 句')

    if not missing:
        print("✅ 无需翻译")
        return

    fixed = 0
    BATCH = 15
    for start in range(0, len(missing), BATCH):
        batch = missing[start:start + BATCH]
        try:
            reply = ai_translate(batch)
            result = extract_json(reply)
            if not result:
                print(f"⚠️ 批次 {start} 解析失败: {reply[:100]}")
                continue
            for i, s in enumerate(batch):
                entry = result.get(str(i)) or result.get(i)
                if entry and entry.get('en') and entry.get('cn'):
                    s['en'] = entry['en'].strip()
                    s['cn'] = entry['cn'].strip()
                    fixed += 1
            print(f"批次 {start}-{start+len(batch)-1} 完成，累计 {fixed}")
        except Exception as e:
            print(f"❌ 批次 {start} 失败: {e}")

    # 写回 categorized.json
    json.dump(data, open(cat_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # 同步 data.json（去掉 cat）
    raw = [{'ar': it['ar'], 'en': it['en'], 'cn': it['cn']} for it in data]
    json.dump(raw, open(DIR / 'data' / 'data.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"✅ 已修复 {fixed} 句，数据已写回")

if __name__ == '__main__':
    main()
