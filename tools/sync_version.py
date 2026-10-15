#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 build_home.py 里的 APP_VERSION 同步到 app/package.json 与 app/app.json。
用法：python3 tools/sync_version.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
src = (ROOT / 'build_home.py').read_text(encoding='utf-8')
m = re.search(r"APP_VERSION\s*=\s*'([^']+)'", src)
if not m:
    raise SystemExit('❌ 在 build_home.py 里找不到 APP_VERSION')
ver = m.group(1)

pkg = ROOT / 'app' / 'package.json'
d = json.loads(pkg.read_text(encoding='utf-8'))
d['version'] = ver
pkg.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

appj = ROOT / 'app' / 'app.json'
d = json.loads(appj.read_text(encoding='utf-8'))
d.setdefault('expo', {})['version'] = ver
d['version'] = ver
try:
    # versionCode 跟随版本号递增（保持单调）
    parts = [int(x) for x in re.findall(r'\d+', ver)][:3]
    while len(parts) < 3:
        parts.append(0)
    d['expo'].setdefault('android', {})['versionCode'] = parts[0] * 100 + parts[1] * 10 + parts[2]
except Exception:
    pass
appj.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

print(f'✅ 版本已同步为 {ver} → app/package.json, app/app.json (versionCode={d["expo"]["android"].get("versionCode")})')
