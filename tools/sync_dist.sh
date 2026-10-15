#!/bin/bash
# 生成可静态部署的 dist/（Cloudflare Pages / Netlify 备用站）
cd "$(dirname "$0")/.." || exit 1
SRV="root@152.239.115.147"
KEY="$HOME/.ssh/id_ed25519"
rm -rf dist
mkdir -p dist/data/library dist/data/hadith dist/assets/fonts
cp arabic_learning.html dist/index.html
cp data/*.js dist/data/ 2>/dev/null
cp data/*.json dist/data/ 2>/dev/null
cp assets/fonts/* dist/assets/fonts/ 2>/dev/null
# 从服务器补齐"运行时生成"的数据（书池 / 新闻 / 六大部索引）
scp -q -i "$KEY" "$SRV:/opt/nur/data/library/*.json" dist/data/library/ 2>/dev/null
scp -q -i "$KEY" "$SRV:/opt/nur/data/hadith/index.json" dist/data/hadith/ 2>/dev/null
scp -q -i "$KEY" "$SRV:/opt/nur/data/beltroad.json" dist/data/ 2>/dev/null
scp -q -i "$KEY" "$SRV:/opt/nur/data/covers.json" dist/data/ 2>/dev/null
echo "dist/ 已生成（含服务器数据）:"; du -sh dist; find dist -type f | wc -l
