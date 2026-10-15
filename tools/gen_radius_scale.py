#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""圆角收敛生成器（每日 UI 优化 · 队列第 3 项）。

扫描 arabic_learning.html 里的全部 <style>，把非 4/8/12/16 档的 border-radius
收敛到 4/8/12/16（保留 999px/99px/50% 药丸与圆形），并归一 --u-r-*/--nur-r-*/
--ap-r-*/--hig-r-* 半径 token，生成独立覆盖层 data/radius-scale.css。

纯视觉：只重写 border-radius 与半径 token，不动布局/逻辑。输出确定性。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / 'arabic_learning.html'
OUT = ROOT / 'data' / 'radius-scale.css'

SCALE = (4, 8, 12, 16)
KEEP = {'999px', '99px', '50%'}
TOKEN_PREFIX = ('--u-r-', '--nur-r-', '--ap-r-', '--hig-r-')


def map_px(tok):
    m = re.fullmatch(r'(\d+(?:\.\d+)?)px', tok)
    if not m:
        return None
    v = float(m.group(1))
    if v in SCALE:
        return tok
    if v <= 4:
        return '4px'
    if v <= 10:
        return '8px'
    if v <= 14:
        return '12px'
    return '16px'


def map_radius_value(val, force_imp=False):
    """返回映射后的 border-radius 值；无需改动返回 None。"""
    imp = force_imp or ('!important' in val)
    parts = val.replace('!important', '').strip().split()
    if not parts:
        return None
    changed = False
    out = []
    for p in parts:
        if p in KEEP or p in ('0', '0px') or p.startswith('var('):
            out.append(p)
            continue
        nv = map_px(p)
        if nv and nv != p:
            changed = True
            out.append(nv)
        else:
            out.append(p)
    if not changed:
        return None
    return ' '.join(out) + ('!important' if imp else '')


def split_top(text):
    """拆分顶层 `head{body}`，用花括号配对处理嵌套（@media 等）。"""
    items = []
    i, n = 0, len(text)
    while i < n:
        j = text.find('{', i)
        if j == -1:
            break
        head = text[i:j].strip()
        depth, k = 1, j + 1
        while k < n and depth > 0:
            if text[k] == '{':
                depth += 1
            elif text[k] == '}':
                depth -= 1
            k += 1
        items.append((head, text[j + 1:k - 1]))
        i = k
    return items


# 逐声明累积（遵循层叠：同键后出现的覆盖先出现的）
radius_map = {}   # (media, selector) -> 覆盖值 or None
# (media, selector) -> {prop: value}
token_map = {}


def walk(text, media):
    for head, body in split_top(text):
        if head.startswith('@'):
            name = head[1:].split()[0].lower() if len(head) > 1 else ''
            if name in ('media', 'supports', 'layer', 'container'):
                walk(body, (media + ' {' + head + '}') if media else head)
        elif head:
            for d in body.split(';'):
                if ':' not in d:
                    continue
                prop, val = d.split(':', 1)
                prop = prop.strip()
                val = val.strip()
                if prop.lower() == 'border-radius':
                    radius_map[(media, head)] = map_radius_value(val, force_imp=True)
                elif any(prop.startswith(p) for p in TOKEN_PREFIX):
                    nv = map_radius_value(val)
                    if nv:
                        token_map.setdefault((media, head), {})[prop] = nv


def main():
    html_txt = HTML.read_text(encoding='utf-8')
    blocks = re.findall(r'(?s)<style([^>]*)>(.*?)</style>', html_txt)
    css = '\n'.join(body for attrs, body in blocks if 'nour-radius-scale' not in attrs)
    # 外链样式表（<link>）也在层叠里，必须一并收敛（否则会被它们盖住）
    for href in re.findall(r'<link rel="stylesheet" href="([^"]+)"', html_txt):
        p = ROOT / href.split('?')[0]
        if p.exists():
            css += '\n' + p.read_text(encoding='utf-8')
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    walk(css, '')

    lines = []
    stat = {'radius': 0, 'token': 0}
    emits = {}
    for (media, sel), nv in radius_map.items():
        if nv:
            emits.setdefault((media, sel), []).append('border-radius:' + nv)
            stat['radius'] += 1
    for (media, sel), props in token_map.items():
        for prop, nv in props.items():
            emits.setdefault((media, sel), []).append(prop + ':' + nv)
            stat['token'] += 1
    for (media, sel), outs in emits.items():
        rule = sel + '{' + ';'.join(outs) + '}'
        lines.append((media + '{' + rule + '}') if media else rule)

    header = (
        '/* 圆角收敛层 radius-scale.css —— 自动生成，请勿手改（见 tools/gen_radius_scale.py）\n'
        '   队列第 3 项：全站圆角收敛到 4/8/12/16 四档（保留 999px/99px 药丸、50% 圆形）。\n'
        '   纯视觉覆盖层，只重写 border-radius 与半径 token，不改布局/逻辑。 */\n'
    )
    # inline 样式兼底（这些半径写在 HTML/JS 的 style="" 上，必须用 !important 才能覆盖）
    inline_catch = [
        '.tk-dict{border-radius:16px!important}',
        '#lockPayBox{border-radius:12px!important}',
        '#lockQr{border-radius:8px!important}',
        '#permCodeIn,#permCodeHome,#permBoxHome button,#permBox button,'
        '#permBoxHome input,#permBox input{border-radius:12px!important}',
        'button[onclick="lockContact()"],button[onclick="freeEnter()"]{border-radius:12px!important}',
    ]
    lines += inline_catch
    OUT.write_text(header + '\n'.join(lines) + '\n', encoding='utf-8')
    print('生成 %s：规则 %d 条（border-radius %d，token %d）'
          % (OUT, len(lines), stat['radius'], stat['token']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
