#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一键启动：服务器 + 浏览器打开网页版"""
import os, subprocess, sys, time, webbrowser
from pathlib import Path

DIR = Path(__file__).parent
PORT = 8080

def is_running():
    try:
        import urllib.request
        with urllib.request.urlopen(f'http://localhost:{PORT}/', timeout=2) as r:
            return r.status == 200
    except Exception:
        return False

def main():
    print('═' * 40)
    print('  🕯  حامل المصباح · 燃灯者')
    print('  阿拉伯语学习 · 一键启动')
    print('═' * 40)

    if is_running():
        print(f'✅ 服务器已在运行: http://localhost:{PORT}')
    else:
        print('🚀 启动服务器...')
        log = open(DIR / 'server.log', 'a', encoding='utf-8')
        subprocess.Popen([sys.executable, str(DIR / 'server.py')],
                         cwd=str(DIR), stdout=log, stderr=log, start_new_session=True)
        for _ in range(15):
            time.sleep(1)
            if is_running():
                break
        if is_running():
            print(f'✅ 服务器已启动: http://localhost:{PORT}')
        else:
            print('⚠️ 服务器启动较慢，稍后访问 http://localhost:8080')

    # 打开网页版
    url = f'http://localhost:{PORT}/arabic_learning.html'
    print(f'📖 打开网页版: {url}')
    webbrowser.open(url)
    print('═' * 40)
    print('  💡 手机 App 连不上？在 App「我的 → 服务器」里')
    print('     输入本机局域网 IP（终端运行 ipconfig getifaddr en0 查看）')
    print('═' * 40)

if __name__ == '__main__':
    main()
