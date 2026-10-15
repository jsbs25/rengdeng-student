#!/bin/bash
# ============================================================
# 燃灯者 · 一键部署高速专属节点（Xray VLESS + WebSocket）
# 适用：Ubuntu 20/22/24、Debian 11/12（Vultr / 甲骨文 / 腾讯云等）
# 用法：把本文件上传到服务器，执行：
#   bash deploy_node.sh
# 完成后会打印：订阅链接 + vless 节点 + 桌面 yaml 文件（node_clash.yaml）
# ============================================================
set -e
echo "=============================================="
echo "  🚀 燃灯者 · 高速专属节点部署开始"
echo "=============================================="

# 1. 检查 root
if [ "$(id -u)" != "0" ]; then
  echo "❌ 请用 root 运行：sudo bash deploy_node.sh"
  exit 1
fi

# 2. 安装 Xray（官方脚本，走 ghproxy 加速国内）
echo "[1/4] 安装 Xray..."
if ! command -v xray >/dev/null 2>&1; then
  bash -c "$(curl -L https://ghproxy.net/https://raw.githubusercontent.com/XTLS/Xray-install/main/install-release.sh)" @ install || \
  bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install
fi
command -v xray >/dev/null 2>&1 || { echo "❌ Xray 安装失败"; exit 1; }
echo "    ✅ Xray 已安装: $(xray version | head -1)"

# 3. 生成随机配置
UUID=$(cat /proc/sys/kernel/random/uuid)
PORT=$((20000 + RANDOM % 30000))
WSPATH="/nur$(date +%s | tail -c 5)"
IP=$(curl -s -m 10 ifconfig.me || curl -s -m 10 ip.sb || hostname -I | awk '{print $1}')

echo "[2/4] 生成配置（端口 $PORT / UUID $UUID）..."

cat > /usr/local/etc/xray/config.json <<EOF
{
  "log": { "loglevel": "warning" },
  "inbounds": [
    {
      "port": $PORT,
      "protocol": "vless",
      "settings": {
        "clients": [ { "id": "$UUID" } ],
        "decryption": "none"
      },
      "streamSettings": {
        "network": "ws",
        "wsSettings": { "path": "$WSPATH" }
      }
    }
  ],
  "outbounds": [ { "protocol": "freedom" } ]
}
EOF

# 4. 启动
echo "[3/4] 启动服务..."
systemctl restart xray 2>/dev/null || service xray restart 2>/dev/null || (xray -c /usr/local/etc/xray/config.json >/tmp/xray.log 2>&1 &)
sleep 2

# 5. 输出结果
VLESS="vless://$UUID@$IP:$PORT?encryption=none&security=none&type=ws&path=$WSPATH#燃灯者专属节点"

cat > /root/node_clash.yaml <<YAMLEOF
# 燃灯者 · 高速专属节点（$IP:$PORT）
mixed-port: 7890
allow-lan: true
mode: rule
log-level: info

proxies:
  - name: 🚀 燃灯者专属节点
    type: vless
    server: $IP
    port: $PORT
    uuid: $UUID
    network: ws
    ws-opts:
      path: $WSPATH
    udp: true

proxy-groups:
  - name: '🚀 节点选择'
    type: select
    proxies: ['🚀 燃灯者专属节点']

rules:
  - GEOIP,CN,DIRECT
  - MATCH,🚀 节点选择
YAMLEOF

echo ""
echo "=============================================="
echo "  ✅ 部署成功！你的高速专属节点："
echo "=============================================="
echo ""
echo "  🌐 服务器 IP : $IP"
echo "  🔌 端口      : $PORT"
echo "  🔑 UUID      : $UUID"
echo ""
echo "  📥 vless 链接（Clash Verge 粘贴导入）:"
echo "  $VLESS"
echo ""
echo "  📄 订阅文件（下载后拖入 Clash Verge）:"
echo "  /root/node_clash.yaml"
echo ""
echo "  ⚠️ 防火墙放行（必做）:"
echo "     Vultr控制台 → 服务器 → 防火墙 → 放行 TCP $PORT"
echo "     或执行: ufw allow $PORT/tcp"
echo "=============================================="

# 验证
echo ""
echo "验证中..."
if curl -s -m 10 -o /dev/null -w "本机端口: %{http_code}\n" "http://127.0.0.1:$PORT/" 2>/dev/null; then
  echo "✅ 端口已监听（返回非200属正常，说明服务在运行）"
else
  echo "⚠️ 端口检测异常，查看日志: tail -20 /usr/local/etc/xray/config.json"
fi
