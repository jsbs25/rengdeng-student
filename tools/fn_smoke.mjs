import { spawn } from 'node:child_process';
import { setTimeout as sleep } from 'node:timers/promises';
import { readFileSync } from 'node:fs';
const names = JSON.parse(readFileSync('/tmp/fnlist.json', 'utf8'));
const PORT = 9336;
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const chrome = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${PORT}`, '--user-data-dir=/tmp/cdp-fn', '--no-first-run', '--disable-gpu', 'about:blank'], { stdio: 'ignore' });
async function getWs() { for (let i = 0; i < 60; i++) { try { const p = (await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json()).find(t => t.type === 'page'); if (p?.webSocketDebuggerUrl) return p.webSocketDebuggerUrl; } catch {} await sleep(250); } throw new Error('no cdp'); }
const ws = new WebSocket(await getWs());
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
let id = 0; const pending = new Map();
ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } };
const send = (m, p = {}) => new Promise(res => { const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method: m, params: p })); });
await send('Page.enable'); await send('Runtime.enable');
await send('Page.navigate', { url: 'https://xn--dqry4os3s3gb.com/arabic_learning.html' });
await sleep(6000);
const expr = `(() => {
  const names = ${JSON.stringify(names)};
  const defined = names.filter(n => { try { return typeof window[n] === 'function'; } catch (e) { return false; } });
  return JSON.stringify({ total: names.length, defined: defined.length, missing: names.filter(n => !defined.includes(n)) });
})()`;
const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
console.log(r.result.result.value);
ws.close(); chrome.kill(); process.exit(0);
