#!/bin/bash
# 主服务器 → 备服务器：每天同步全部内容（数据 + 代码 + 封面 + 书池）
# 配置在 /opt/nur/data/backup.conf ：BACKUP_HOST / BACKUP_USER / BACKUP_PORT
CONF=/opt/nur/data/backup.conf
[ -f "$CONF" ] || { echo "$(date) 未配置 backup.conf，跳过"; exit 0; }
# shellcheck disable=SC1090
. "$CONF"
[ -z "$BACKUP_HOST" ] && { echo "$(date) BACKUP_HOST 为空，跳过"; exit 0; }
KEY=/root/.ssh/id_ed25519
OPTS="-az --delete --exclude=m --exclude=dist --exclude=.git"
echo "$(date) 开始同步 → $BACKUP_HOST"
rsync $OPTS -e "ssh -i $KEY -p ${BACKUP_PORT:-22} -o StrictHostKeyChecking=no -o BatchMode=yes" \
  /opt/nur/ "$BACKUP_USER@$BACKUP_HOST:/opt/nur/"
if [ $? -eq 0 ]; then
  ssh -i $KEY -p ${BACKUP_PORT:-22} -o BatchMode=yes "$BACKUP_USER@$BACKUP_HOST" "systemctl is-active nur >/dev/null 2>&1 || systemctl start nur" 2>/dev/null
  echo "$(date) 同步完成 ✓"
else
  echo "$(date) 同步失败 ✗"
fi
