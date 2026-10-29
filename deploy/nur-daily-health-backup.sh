#!/usr/bin/env bash
set -u -o pipefail
umask 077

APP_ROOT=/opt/nur
BACKUP_ROOT=/var/backups/nur-daily
STATE_ROOT=/var/lib/nur-daily-health-backup
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$BACKUP_ROOT/$STAMP"
STATUS_FILE="$STATE_ROOT/latest.json"
TMP_DIR="$(mktemp -d /tmp/nur-daily-health.XXXXXX)"
HEALTH_FAIL=0
BACKUP_FAIL=0

after() { rm -rf "$TMP_DIR"; }
trap after EXIT

mkdir -p "$BACKUP_ROOT" "$STATE_ROOT" "$RUN_DIR/app" "$RUN_DIR/systemd"

check_unit() {
  local unit="$1"
  if systemctl is-active --quiet "$unit"; then return 0; fi
  echo "health: inactive unit $unit" >&2
  HEALTH_FAIL=1
  return 1
}

check_http() {
  local label="$1" url="$2" body
  body="$TMP_DIR/$label.body"
  if ! curl -fsS --max-time 20 -A 'NOUR-daily-health-backup/1.0' -o "$body" "$url"; then
    echo "health: HTTP failed $label $url" >&2
    HEALTH_FAIL=1
    return 1
  fi
  return 0
}

check_unit nur.service
check_unit nur-health-monitor.service
check_http local_home http://127.0.0.1:8080/
check_http local_daily http://127.0.0.1:8080/api/sentences/daily
check_http local_nodes http://127.0.0.1:8080/api/nodes
check_http local_catalog http://127.0.0.1:8080/api/catalog/meta
check_http public_daily https://xn--dqry4os3s3gb.com/api/sentences/daily

if [ -s "$TMP_DIR/local_daily.body" ]; then
  python3 - "$TMP_DIR/local_daily.body" <<'PY' || HEALTH_FAIL=1
import json, sys
x = json.load(open(sys.argv[1]))
assert x.get('item', {}).get('a')
assert len(json.dumps(x, ensure_ascii=False).encode('utf-8')) < 10000
PY
fi
if [ -s "$TMP_DIR/local_catalog.body" ]; then
  python3 - "$TMP_DIR/local_catalog.body" <<'PY' || HEALTH_FAIL=1
import json, sys
x = json.load(open(sys.argv[1]))
assert int(x.get('total', 0)) >= 8794
PY
fi

PREV="$(find "$BACKUP_ROOT" -mindepth 1 -maxdepth 1 -type d -name '20*' -printf '%p\n' 2>/dev/null | sort -r | head -1)"
RSYNC_ARGS=(
  -a --delete --numeric-ids
  --exclude='backups/'
  --exclude='backup-*/'
  --exclude='.deploy-*/'
  --exclude='.manus-backups/'
  --exclude='releases/'
  --exclude='cache/'
  --exclude='data/cache/'
  --exclude='data/backup/'
  --exclude='monitor/logs/'
  --exclude='tools/manus-results/'
  --exclude='*.log'
  --exclude='.env'
  --exclude='.env.*'
  --exclude='ai_key*'
  --exclude='ai_keys*'
  --exclude='users*'
  --exclude='payments*'
  --exclude='unlocks*'
  --exclude='codes*'
)
if [ -n "$PREV" ] && [ -d "$PREV/app" ]; then RSYNC_ARGS+=("--link-dest=$PREV/app"); fi
if ! rsync "${RSYNC_ARGS[@]}" "$APP_ROOT/" "$RUN_DIR/app/"; then
  echo "backup: rsync failed" >&2
  BACKUP_FAIL=1
fi

cp -a /etc/systemd/system/nur.service "$RUN_DIR/systemd/" 2>/dev/null || true
cp -a /etc/systemd/system/nur.service.d "$RUN_DIR/systemd/" 2>/dev/null || true
cp -a /etc/systemd/system/nur-health-monitor.service "$RUN_DIR/systemd/" 2>/dev/null || true
cp -a /etc/systemd/system/nur-health-monitor.service.d "$RUN_DIR/systemd/" 2>/dev/null || true

HEALTH="ok"; [ "$HEALTH_FAIL" -ne 0 ] && HEALTH="degraded"
BACKUP="ok"; [ "$BACKUP_FAIL" -ne 0 ] && BACKUP="failed"
printf '{"timestamp":"%s","health":"%s","backup":"%s","path":"%s","retention_days":14}\n' "$STAMP" "$HEALTH" "$BACKUP" "$RUN_DIR" > "$RUN_DIR/status.json"
cp -f "$RUN_DIR/status.json" "$STATUS_FILE"
ln -sfn "$RUN_DIR" "$BACKUP_ROOT/latest"
chmod -R go-rwx "$RUN_DIR" "$STATUS_FILE" "$BACKUP_ROOT/latest" 2>/dev/null || true

mapfile -t SNAPSHOTS < <(find "$BACKUP_ROOT" -mindepth 1 -maxdepth 1 -type d -name '20*' -printf '%p\n' 2>/dev/null | sort -r)
if [ "${#SNAPSHOTS[@]}" -gt 14 ]; then
  for old in "${SNAPSHOTS[@]:14}"; do rm -rf -- "$old"; done
fi

printf 'nur-daily-health-backup timestamp=%s health=%s backup=%s path=%s\n' "$STAMP" "$HEALTH" "$BACKUP" "$RUN_DIR"
[ "$BACKUP_FAIL" -eq 0 ] && [ "$HEALTH_FAIL" -eq 0 ]
