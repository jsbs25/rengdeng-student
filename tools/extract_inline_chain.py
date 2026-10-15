from pathlib import Path
import re
html = Path('arabic_learning.html').read_text(encoding='utf-8')
scripts = re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', html, flags=re.S|re.I)
for i, body in enumerate(scripts, 1):
    Path(f'/tmp/nur-chain-inline-{i}.js').write_text(body, encoding='utf-8')
print(f'extracted={len(scripts)}')
