#!/bin/bash
# 主站健康检查 → 连续失败 N 次则自动把域名切到备服务器（Cloudflare API）
CONF=/opt/nur/data/backup.conf
[ -f "$CONF" ] || exit 0
# shellcheck disable=SC1090
. "$CONF"
[ -z "$CF_TOKEN" ] && exit 0
STATE=/opt/nur/data/failover.state
FAILS=$(cat "$STATE" 2>/dev/null || echo 0)
CODE=$(curl -s -o /dev/null -m 15 -w '%{http_code}' "https://${DOMAIN:-xn--dqry4os3s3gb.com}/" || echo 000)
if [ "$CODE" = "200" ]; then
  if [ "$FAILS" != "0" ]; then echo 0 > "$STATE"; echo "$(date) 主站恢复 ✓（已重置计数）"; fi
  exit 0
fi
FAILS=$((FAILS+1)); echo "$FAILS" > "$STATE"
echo "$(date) 主站异常($CODE) 第 $FAILS 次"
if [ "$FAILS" -lt 3 ]; then exit 0; fi
[ -z "$BACKUP_IP" ] && { echo "未配置 BACKUP_IP，无法切换"; exit 0; }
echo "$(date) ⇒ 触发切换：域名 → $BACKUP_IP"
# 取 zone id
ZONE=$(curl -s -m 20 "https://api.cloudflare.com/client/v4/zones?name=${DOMAIN:-xn--dqry4os3s3gb.com}" \
  -H "Authorization: Bearer $CF_TOKEN" | python3 -c "import sys,json;d=json.load(sys.stdin);print((d.get('result') or [{}])[0].get('id',''))")
[ -z "$ZONE" ] && { echo "取 zone 失败"; exit 1; }
REC=$(curl -s -m 20 "https://api.cloudflare.com/client/v4/zones/$ZONE/dns_records?type=A&name=${DOMAIN:-xn--dqry4os3s3gb.com}" \
  -H "Authorization: Bearer $CF_TOKEN" | python3 -c "import sys,json;d=json.load(sys.stdin);print((d.get('result') or [{}])[0].get('id',''))")
[ -z "$REC" ] && { echo "取记录失败"; exit 1; }
curl -s -m 20 -X PUT "https://api.cloudflare.com/client/v4/zones/$ZONE/dns_records/$REC" \
  -H "Authorization: Bearer $CF_TOKEN" -H "Content-Type: application/json" \
  --data "{\"type\":\"A\",\"name\":\"${DOMAIN:-xn--dqry4os3s3gb.com}\",\"content\":\"$BACKUP_IP\",\"ttl\":60,\"proxied\":true}" \
  -o /tmp/fo.json -w "  API %{http_code}\n"
echo "$(date) 切换结果已写入 /tmp/fo.json"
