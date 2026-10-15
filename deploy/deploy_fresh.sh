#!/bin/bash
# 燃灯同学 · 一键部署（适用于任何全新 Linux 服务器：Oracle/Fly/Koyeb/腾讯云…）
# 用法：把 nur-backup.tar.gz 和本脚本放同一目录，然后 sudo bash deploy_fresh.sh 你的域名
set -e
DOMAIN="${1:-}"
echo "=== 燃灯同学 一键部署 开始 ==="

# 1. 基础环境
if command -v apt >/dev/null; then
  apt update -y && apt install -y python3 python3-pip nginx certbot python3-certbot-nginx curl rsync || true
elif command -v dnf >/dev/null; then
  dnf install -y python3 nginx certbot python3-certbot-nginx curl rsync || true
fi

# 2. 解包
mkdir -p /opt/nur
tar xzf nur-backup.tar.gz -C /opt/
echo "  已解包到 /opt/nur ✓"

# 3. 服务
cat > /etc/systemd/system/nur.service <<EOF
[Unit]
Description=Nur (燃灯同学) web app
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/nur
ExecStart=/usr/bin/python3 /opt/nur/server.py
Environment=PYTHONUTF8=1
Environment=NUR_PORT=8080
Restart=always
RestartSec=3
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
EOF

# 4. 反向代理
cat > /etc/nginx/conf.d/nur.conf <<EOF
server {
  listen 80;
  server_name ${DOMAIN} _;
  client_max_body_size 200m;
  location / {
    proxy_pass http://127.0.0.1:8080;
    proxy_set_header Host \$host;
    proxy_set_header X-Forwarded-For \$remote_addr;
    proxy_read_timeout 300s;
    proxy_buffering off;
  }
}
EOF

systemctl daemon-reload
systemctl enable --now nur
systemctl enable --now nginx || true

# 5. HTTPS（可选，有域名就自动签）
if [ -n "$DOMAIN" ] && [ "$DOMAIN" != "_" ]; then
  certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --register-unsafely-without-email --redirect || echo "  ⚠️ 证书签发失败（可能 DNS 还没指向本机）"
fi

# 6. 定时任务
cat > /etc/cron.d/nur <<EOF
*/3 * * * * root /opt/nur/harvest/health.sh
17 * * * * root cd /opt/nur && /usr/bin/python3 harvest/build_beltroad.py >> /var/log/beltroad.log 2>&1
35 */2 * * * root cd /opt/nur && /usr/bin/python3 harvest/warm_fast.py novels_pool.json lit_pool.json >> /var/log/warmfast.log 2>&1
30 3 * * * root /opt/nur/harvest/backup.sh
EOF
chmod +x /opt/nur/harvest/*.sh 2>/dev/null || true

echo "=== 完成 ✅ ==="
echo "本机测试：curl -s -o /dev/null -w '%{http_code}\\n' http://127.0.0.1/"
echo "访问：http://${DOMAIN:-本机IP}"
