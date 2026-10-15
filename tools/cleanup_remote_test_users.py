import json
from pathlib import Path

current = Path('/opt/nur/data/users.json')
backup = Path('/opt/nur/backups/20260925-0126-upgrade/data/users.json')
cur = json.loads(current.read_text(encoding='utf-8'))
bak = json.loads(backup.read_text(encoding='utf-8'))
changed_existing = [k for k in bak if cur.get(k) != bak.get(k)]
added = [k for k in cur if k not in bak]
if changed_existing:
    raise SystemExit('existing user records changed; refusing cleanup')
if not added:
    print('no added test records')
elif all(k.startswith('d') for k in added):
    current.write_text(backup.read_text(encoding='utf-8'), encoding='utf-8')
    print('removed temporary device records:', len(added))
else:
    raise SystemExit('unexpected added records; refusing cleanup')
