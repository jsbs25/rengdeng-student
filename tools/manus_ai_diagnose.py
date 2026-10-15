from pathlib import Path
import json, os, urllib.request, urllib.error, socket
ROOT = Path(__file__).resolve().parent.parent
key_file = ROOT / 'data' / 'ai_key.txt'
key = key_file.read_text().strip() if key_file.exists() else ''
key = key or os.environ.get('DEEPSEEK_API_KEY', '') or os.environ.get('LOBSTER_APIKEY_DEEPSEEK', '')
try:
    cfg = json.loads((ROOT / 'data' / 'ai_config.json').read_text())
except (OSError, ValueError):
    cfg = {}
print(json.dumps({'key_configured': bool(key), 'provider': cfg.get('provider', 'auto')}, ensure_ascii=False), flush=True)
if key:
    req = urllib.request.Request('https://api.deepseek.com/chat/completions', data=json.dumps({'model':'deepseek-chat', 'messages':[{'role':'user','content':'只回复 OK'}], 'max_tokens':16}).encode(), headers={'Content-Type':'application/json','Authorization':'Bearer '+key})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            data = json.load(r)
        print(json.dumps({'upstream_ok': True, 'reply': data['choices'][0]['message']['content'], 'usage': data.get('usage')}, ensure_ascii=False))
    except urllib.error.HTTPError as e:
        print(json.dumps({'upstream_ok':False,'http_status':e.code}))
    except Exception as e:
        text = str(e).replace(key, '[REDACTED]')
        print(json.dumps({'upstream_ok':False,'error_type':type(e).__name__,'detail':text[:300]}, ensure_ascii=False))
else:
    print('NO_CONFIGURED_DEEPSEEK_KEY')

req = urllib.request.Request('http://127.0.0.1:8080/api/chat/message', data=json.dumps({'message':'只回复 OK','session_id':'manus-diagnostic-20260925','device_id':'manus-diagnostic-20260925'}).encode(), headers={'Content-Type':'application/json'})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    print(json.dumps({'website_response':data}, ensure_ascii=False)[:1200])
except Exception as e:
    print(json.dumps({'website_error':str(e).replace(key or '\0','[REDACTED]')[:300]}, ensure_ascii=False))
