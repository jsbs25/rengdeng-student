#!/bin/bash
# 在服务器上执行：安装 systemd 服务 + nginx 反代
set -e
DIR=/opt/nur
python3 -c "import server" 2>/dev/null || true

cp "$DIR/deploy/nur.service" /etc/systemd/system/nur.service
systemctl daemon-reload
systemctl enable --now nur

mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled
cp "$DIR/deploy/nginx.conf" /etc/nginx/sites-available/nur.conf
echo "-> 请把 nginx.conf 里的 your-domain.com 改成你的域名（或服务器 IP）"
ln -sf /etc/nginx/sites-available/nur.conf /etc/nginx/sites-enabled/nur.conf
nginx -t && systemctl reload nginx

chmod 600 "$DIR/data/ai_key.txt" 2>/dev/null || true
echo "✅ 服务已启动：systemctl status nur"
echo "   本机自测： curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8080/"
