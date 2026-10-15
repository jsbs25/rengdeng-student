// CDP 量测：computed border-radius 档位 / 横向滚动 / 控制台报错 / 关键函数
// 用法: node tools/radius_measure.mjs <url> <width> <height>
import { spawn } from 'node:child_process';
import { setTimeout as sleep } from 'node:timers/promises';

const URL_ = process.argv[2] || 'http://127.0.0.1:8899/arabic_learning.html';
const W = +(process.argv[3] || 1440);
const H = +(process.argv[4] || 900);
const PORT = 9333;
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PROFILE = '/tmp/cdp-radius-profile';

const chrome = spawn(CHROME, [
  '--headless=new', `--remote-debugging-port=${PORT}`, `--user-data-dir=${PROFILE}`,
  '--no-first-run', '--no-default-browser-check', '--disable-gpu', '--hide-scrollbars', 'about:blank',
], { stdio: 'ignore' });

async function getWs() {
  for (let i = 0; i < 60; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${PORT}/json/list`);
      const list = await r.json();
      const p = list.find(t => t.type === 'page');
      if (p?.webSocketDebuggerUrl) return p.webSocketDebuggerUrl;
    } catch {}
    await sleep(250);
  }
  throw new Error('chrome cdp not ready');
}

const ws = new WebSocket(await getWs());
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
let id = 0;
const pending = new Map();
const errors = [];
ws.onmessage = (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
  else if (m.method === 'Runtime.exceptionThrown') errors.push('EXC:' + (m.params.exceptionDetails?.text || ''));
  else if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') errors.push('ERR:' + m.params.args.map(a => a.value || a.description || '').join(' '));
  else if (m.method === 'Log.entryAdded' && m.params.entry.level === 'error') errors.push('LOG:' + m.params.entry.text);
};
const send = (method, params = {}) => new Promise((res) => { const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
const evalJS = async (expression) => {
  const r = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  return r.result?.result?.value;
};

await send('Page.enable');
await send('Runtime.enable');
await send('Log.enable');
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: W < 600 });
await send('Page.navigate', { url: URL_ });
await sleep(4500);

const FN_LIST = ['nav', 'ec', 'ap', 'em', 'sp', 'esc', 'cp', 'tr', 'qs', 'rc', 'go', 'openReader', 'closeReader', 'toggleTheme', 'speak', 'openDict', 'closeDict', 'sendAI', 'openPage', 'toggleLang', 'switchTab'];
const out = await evalJS(`(() => {
  const vals = {};
  document.querySelectorAll('*').forEach(el => {
    const r = getComputedStyle(el).borderTopLeftRadius || '0px';
    vals[r] = (vals[r] || 0) + 1;
  });
  const distinct = Object.keys(vals).filter(v => v !== '0px').sort((a, b) => parseFloat(a) - parseFloat(b));
  const SCALE = ['4px', '8px', '12px', '16px', '50%', '999px'];
  const samples = {};
  document.querySelectorAll('*').forEach(el => {
    const r = getComputedStyle(el).borderTopLeftRadius || '0px';
    if (SCALE.includes(r) || r === '0px') return;
    const key = (el.id ? '#' + el.id : '') + (typeof el.className === 'string' && el.className ? '.' + el.className.trim().split(/\s+/).join('.') : '');
    (samples[r] = samples[r] || []);
    if (samples[r].length < 4) samples[r].push(el.tagName.toLowerCase() + key);
  });
  const fns = ${JSON.stringify(FN_LIST)};
  const fnOk = fns.filter(f => typeof window[f] === 'function');
  return JSON.stringify({
    distinct,
    counts: vals,
    samples,
    hscroll: document.documentElement.scrollWidth - window.innerWidth,
    vw: window.innerWidth,
    n: document.querySelectorAll('*').length,
    fnTotal: fns.length, fnOk: fnOk.length, fnMissing: fns.filter(f => typeof window[f] !== 'function'),
    canScroll: document.documentElement.scrollHeight > window.innerHeight,
  });
})()`);
console.log(JSON.stringify({ size: W + 'x' + H, ...JSON.parse(out), errors: errors.slice(0, 10) }, null, 1));
ws.close();
chrome.kill();
process.exit(0);
