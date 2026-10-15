#!/bin/bash
# 一键把 燃灯同学.com 绑到本机服务（Cloudflare 隧道）
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
CF="$DIR/bin/cloudflared"
DOMAIN="xn--dqry4os3s3gb.com"          # 燃灯同学.com
HOSTURL="https://$DOMAIN"

echo "▶ 0/5 确认本机服务在跑"
curl -s -o /dev/null -m 5 http://127.0.0.1:8080/ || { echo "❌ 本机 8080 没在跑，先启动：cd ~/Desktop/arabic-learning && nohup python3 server.py &"; exit 1; }

echo "▶ 1/5 登录 Cloudflare（会弹浏览器，请点授权）"
"$CF" tunnel login

echo "▶ 2/5 创建隧道 nur"
"$CF" tunnel create nur 2>/dev/null || echo "   （隧道已存在，继续）"

echo "▶ 3/5 路由 DNS（$DOMAIN → 隧道）"
"$CF" tunnel route dns nur "$DOMAIN" || true
"$CF" tunnel route dns nur "www.$DOMAIN" || true

echo "▶ 4/5 启动隧道"
cp "$DIR/cloudflared-config.yml" ~/.cloudflared/config.yml
nohup "$CF" tunnel run nur > /tmp/cf_nur.log 2>&1 &
sleep 8
tail -3 /tmp/cf_nur.log || true

echo "▶ 5/5 完成"
echo "✅ 打开：$HOSTURL"
echo "   若 DNS 还没生效，等几分钟；可在 Cloudflare 面板看状态。"
