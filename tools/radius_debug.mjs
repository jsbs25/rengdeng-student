// 调试：列出所有非 4/8/12/16/50%/999 计算圆角的元素（含 outerHTML 片段）
import { spawn } from 'node:child_process';
import { setTimeout as sleep } from 'node:timers/promises';
const PORT = 9334;
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const chrome = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${PORT}`, '--user-data-dir=/tmp/cdp-dbg', '--no-first-run', '--disable-gpu', 'about:blank'], { stdio: 'ignore' });
async function getWs() { for (let i = 0; i < 60; i++) { try { const r = await fetch(`http://127.0.0.1:${PORT}/json/list`); const p = (await r.json()).find(t => t.type === 'page'); if (p?.webSocketDebuggerUrl) return p.webSocketDebuggerUrl; } catch {} await sleep(250); } throw new Error('no cdp'); }
const ws = new WebSocket(await getWs());
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
let id = 0; const pending = new Map();
ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } };
const send = (method, params = {}) => new Promise(res => { const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
await send('Page.enable'); await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });
await send('Page.navigate', { url: 'http://127.0.0.1:8899/arabic_learning.html' });
await sleep(4000);
const r = await send('Runtime.evaluate', { returnByValue: true, expression: `(() => {
  const SCALE = ['4px','8px','12px','16px','50%','999px','0px'];
  const out = [];
  document.querySelectorAll('*').forEach(el => {
    const cs = getComputedStyle(el);
    const r0 = cs.borderTopLeftRadius;
    if (SCALE.includes(r0)) return;
    out.push(el.tagName.toLowerCase() + ' | class=' + el.className + ' | id=' + el.id + ' | r=' + r0 + ' | inline=' + (el.getAttribute('style')||'').slice(0,80) + ' | html=' + el.outerHTML.slice(0,110));
  });
  return JSON.stringify(out.slice(0,25), null, 1);
})()` });
console.log(r.result.result.value);
ws.close(); chrome.kill(); process.exit(0);
