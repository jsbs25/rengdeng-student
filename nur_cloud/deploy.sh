#!/bin/bash
# ============================================
# 燃灯者 · 云端服务器一键部署脚本
# 适用：阿里云 / 腾讯云 轻量应用服务器（Ubuntu 22.04 / Debian 12）
# 用法：把整个 nur_cloud 文件夹上传到服务器，然后执行：
#   chmod +x deploy.sh && sudo ./deploy.sh
# ============================================
set -e

echo "=========================================="
echo "  🕌 燃灯者 · 云端服务器部署开始"
echo "=========================================="

# 1. 安装依赖
echo "[1/5] 安装 Python 环境..."
apt-get update -y
apt-get install -y python3 python3-pip python3-venv curl || true

# 2. Python 依赖（只用核心库 + edge-tts）
echo "[2/5] 安装 Python 依赖..."
pip3 install edge-tts --break-system-packages 2>/dev/null || pip3 install edge-tts

# 3. 确认 AI 密钥
echo "[3/5] 检查 AI 密钥..."
if [ ! -f "data/ai_key.txt" ]; then
  echo "⚠️  未找到 data/ai_key.txt"
  echo "   请在 data/ai_key.txt 里填写你的 DeepSeek API Key（或 AionClaw AI Key）"
  echo "   然后重新运行本脚本"
  exit 1
fi
echo "    ✅ AI 密钥已就绪"

# 4. 启动服务
echo "[4/5] 启动服务（端口 8080）..."
pkill -f cloud_server.py 2>/dev/null || true
sleep 1
nohup python3 cloud_server.py > server.log 2>&1 &
sleep 3

# 5. 验证
echo "[5/5] 验证服务..."
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8080/ | grep -q 200; then
  echo ""
  echo "=========================================="
  echo "  ✅ 部署成功！服务已启动"
  echo "=========================================="
  echo "  本机测试:   http://127.0.0.1:8080"
  echo "  公网访问:   http://$(curl -s ifconfig.me):8080"
  echo ""
  echo "  ⚠️ 下一步（重要）:"
  echo "  1. 登录云服务器控制台 → 防火墙/安全组"
  echo "     → 放行端口 8080（TCP）"
  echo "  2. 用浏览器打开 http://<公网IP>:8080 验证"
  echo "  3. 把公网 IP 告诉管理员，重新打包 App"
  echo "=========================================="
else
  echo "❌ 启动失败，查看日志: tail -20 server.log"
fi
