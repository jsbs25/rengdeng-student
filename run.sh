#!/bin/bash
cd "/Users/mafucheng/Desktop/arabic-learning"
nohup python3 server.py > /tmp/arabic_server.log 2>&1 &
echo "✅ 服务已启动: http://localhost:8080"
echo "日志: /tmp/arabic_server.log"
