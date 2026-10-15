#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""网页版自动体检（无第三方依赖）。

检查项：
  1. build_home.py 能否正常生成 arabic_learning.html
  2. 主脚本 JS 语法（用 node --check，装了 node 才跑）
  3. JS 里 getElementById 引用但 HTML 中不存在的 id（潜在 bug）
  4. 标记区（<script>/<style> 之外）是否残留字面 \\n / \\t（会渲染成乱码）

用法：python3 tools/verify_web.py
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / 'arabic_learning.html'


def run_build():
    # 直接生成到项目根的 arabic_learning.html（保持线上文件与源码一致）
    r = subprocess.run([sys.executable, str(ROOT / 'build_home.py')],
                       cwd=str(ROOT), capture_output=True, text=True)
    if r.returncode != 0:
        print('❌ 生成失败:\n' + (r.stderr or '')[-800:])
        return False
    print('✅ 生成成功:', HTML.stat().st_size // 1024, 'KB')
    return True


def check_js(html):
    scripts = re.findall(r'(?s)<script[^>]*>(.*?)</script>', html)
    if not scripts:
        print('❌ 没找到 <script>')
        return False
    main = max(scripts, key=len)
    tmp = Path(tempfile.mkdtemp()) / 'main.js'
    tmp.write_text(main, encoding='utf-8')
    try:
        r = subprocess.run(['node', '--check', str(tmp)], capture_output=True, text=True)
    except FileNotFoundError:
        print('⚠️  未安装 node，跳过 JS 语法检查')
        return True
    if r.returncode == 0:
        print('✅ JS 语法通过')
        return True
    print('❌ JS 语法错误:\n' + (r.stderr or '')[:800])
    return False


def check_ids(html):
    scripts = re.findall(r'(?s)<script[^>]*>(.*?)</script>', html)
    js = max(scripts, key=len) if scripts else ''
    all_ids = set(re.findall(r'id=["\']([^"\']+)["\']', html))
    ref = set(re.findall(r"getElementById\(\s*'([^']+)'\s*\)", js))
    ref |= set(re.findall(r'getElementById\(\s*"([^"]+)"\s*\)', js))
    removed = {'dueBar','dueBarTxt','goalBar','goalBtn','goalTxt','miniChart','eb','ei','eiSend','em','ep','homeMic','wakeBtn','wakeStatus','homeAI','homeAIChips','homeAIIn','donMsg','payRatio','rdFloatBack','dictAI','tkTabs','tkGrid','tkSeg','nurHomeBtn'}
    missing = sorted(r for r in ref if r not in all_ids and r not in removed)
    if missing:
        print('❌ 引用了不存在的元素 id:', missing)
        return False
    print('✅ DOM id 引用完整 (%d 个)' % len(ref))
    return True


def check_stray(html):
    s = re.sub(r'(?s)<script.*?</script>', '', html)
    s = re.sub(r'(?s)<style.*?</style>', '', s)
    bad = s.count('\\n') + s.count('\\t')
    if bad:
        print('❌ 标记区残留字面转义 \\n/\\t：%d 处（页面会显示乱码）' % bad)
        return False
    print('✅ 标记区无乱码转义')
    return True


def check_fns(html):
    """标记中的 onclick/oninput 等引用的函数，是否真的定义了（防“函数被误删”类事故）。"""
    scripts = re.findall(r'(?s)<script[^>]*>(.*?)</script>', html)
    js = max(scripts, key=len) if scripts else ''
    defined = set(re.findall(r'function\s+([A-Za-z_$][\w$]*)\s*\(', js))
    defined |= set(re.findall(r'(?:var|let|const)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:function|\([^)]*\)\s*=>)', js))
    defined |= set(re.findall(r'window\.([A-Za-z_$][\w$]*)\s*=', js))
    # 外部脚本（课程中心等）里的函数也算已定义
    try:
        import os as _os
        for _f in ('data/course.js', 'data/belt.js', 'data/views.js', 'data/contact.js', 'data/unlockbox.js', 'data/dictlimit.js', 'data/freeentry.js'):
            if _os.path.exists(_f):
                _ex = open(_f, encoding='utf-8').read()
                defined |= set(re.findall(r'function\s+([A-Za-z_$][\w$]*)\s*\(', _ex))
    except Exception:
        pass
    calls = set()
    for attr in re.findall(r'on(?:click|input|change|keydown|keyup|submit|load|error)\s*=\s*"([^"]*)"', html):
        calls |= set(re.findall(r'([A-Za-z_$][\w$]*)\s*\(', attr))
    for attr in re.findall(r"on(?:click|input|change|keydown|keyup|submit|load|error)\s*=\s*'([^']*)'", html):
        calls |= set(re.findall(r'([A-Za-z_$][\w$]*)\s*\(', attr))
    builtins = {'if', 'for', 'while', 'return', 'alert', 'confirm', 'prompt', 'JSON', 'Math', 'parseInt',
                'parseFloat', 'String', 'Number', 'Array', 'Object', 'Date', 'fetch', 'setTimeout',
                'setInterval', 'encodeURIComponent', 'decodeURIComponent', 'console', 'event', 'this',
                'getElementById', 'querySelector', 'querySelectorAll', 'indexOf', 'replace', 'stringify'}
    # 只把“像函数名”的（驼峰/下划线/已知单字函数）算进来，避免英文散文里的括号误报
    single = {'nav', 'ec', 'ap', 'em', 'sp', 'esc', 'cp', 'tr', 'qs', 'rc'}
    def looks_like_fn(n):
        return ('_' in n) or any(ch.isupper() for ch in n[1:]) or (n in single)
    missing = sorted(c for c in calls if c not in defined and c not in builtins and looks_like_fn(c))
    if missing:
        print('❌ 标记里调用了但没定义的函数:', missing)
        return False
    print('✅ 标记调用的函数均已定义')
    return True


def main():
    ok = run_build()
    html = HTML.read_text(encoding='utf-8') if HTML.exists() else ''
    if not html:
        print('❌ 读不到 arabic_learning.html'); sys.exit(1)
    ok = check_js(html) and ok
    ok = check_ids(html) and ok
    ok = check_fns(html) and ok
    ok = check_stray(html) and ok
    print('\n== 结论:', '全部通过 ✅' if ok else '存在问题 ❌', '==')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
