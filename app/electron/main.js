// Electron 桌面壳：自包含 APP（内置服务 + 内置爬虫 + 动态数据）
const { app, BrowserWindow, shell, ipcMain } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const http = require('http');
const fs = require('fs');
const net = require('net');

const DIST_DIR = path.join(__dirname, 'dist');
const DATA_DIR = path.join(__dirname, 'data');
const SERVER_SCRIPT = path.join(__dirname, 'server.py');
const SCRAPER_SCRIPT = path.join(__dirname, 'scraper_hourly.py');
const APP_PORT = 8083;
const APP_URL = `http://127.0.0.1:${APP_PORT}/`;
const SCRAPE_INTERVAL = 60 * 60 * 1000;

let webServer = null;
let serverProc = null;
let win = null;
let scraperRunning = false;

function log(msg) {
  const t = new Date().toLocaleTimeString('zh-CN', { hour12: false });
  console.log(`[${t}] ${msg}`);
}

function isPortOpen(port, cb) {
  const s = net.createConnection({ port, host: '127.0.0.1' });
  s.on('connect', () => { s.destroy(); cb(true); });
  s.on('error', () => { s.destroy(); cb(false); });
}

// 启动 AI 数据服务（8080，供 APP 内 AI 对话使用）
function startAIServer() {
  isPortOpen(8080, (open) => {
    if (open) { log('✅ AI 服务已在运行 (8080)'); return; }
    try {
      serverProc = spawn('python3', [SERVER_SCRIPT], { stdio: 'ignore' });
      log('✅ AI 服务已启动 (8080)');
    } catch (e) { log(`⚠️ AI 服务启动失败: ${e.message}`); }
  });
}

// 内置 HTTP 服务：dist 静态 + /api/sentences（动态数据）+ /api/chat（代理AI）
function startWebServer() {
  const MIME = {
    '.html': 'text/html; charset=utf-8', '.js': 'application/javascript',
    '.css': 'text/css', '.json': 'application/json', '.png': 'image/png',
    '.ico': 'image/x-icon', '.svg': 'image/svg+xml', '.mp3': 'audio/mpeg',
  };
  webServer = http.createServer((req, res) => {
    const urlPath = decodeURIComponent(req.url.split('?')[0]);

    // 动态句子数据（爬虫更新后立即生效）— 返回 {cats, meta, stats}
    if (urlPath === '/api/sentences') {
      const catFile = path.join(DATA_DIR, 'categorized.json');
      const dataFile = path.join(DATA_DIR, 'data.json');
      fs.readFile(catFile, 'utf-8', (err, content) => {
        if (!err) {
          try {
            const arr = JSON.parse(content);
            const cats = {};
            arr.forEach((it) => {
              const k = it.cat || 'other';
              if (!cats[k]) cats[k] = [];
              cats[k].push({ a: it.ar || '', e: it.en || '', c: it.cn || '' });
            });
            const meta = {
              greeting: { icon: '👋', cn: '问候', ar: 'مرحبا' }, daily: { icon: '🌅', cn: '日常', ar: 'يومي' },
              food: { icon: '🍽', cn: '饮食', ar: 'طعام' }, travel: { icon: '✈️', cn: '旅行', ar: 'سفر' },
              family: { icon: '👨👩👧', cn: '家庭', ar: 'عائلة' }, work: { icon: '💼', cn: '工作', ar: 'عمل' },
              study: { icon: '📚', cn: '学习', ar: 'دراسة' }, religion: { icon: '🕌', cn: '宗教', ar: 'دين' },
              health: { icon: '🏥', cn: '健康', ar: 'صحة' }, weather: { icon: '🌤', cn: '天气', ar: 'طقس' },
              shopping: { icon: '🛍', cn: '购物', ar: 'تسوق' }, hobby: { icon: '🎨', cn: '爱好', ar: 'هواية' },
              other: { icon: '📖', cn: '其他', ar: 'أخرى' },
            };
            const payload = {
              cats, meta,
              stats: { sentences: arr.length, words: arr.reduce((s, i) => s + (i.ar || '').split(/\s+/).length, 0), cats: Object.keys(cats).length },
            };
            res.writeHead(200, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' });
            res.end(JSON.stringify(payload));
            return;
          } catch (e) {}
        }
        // 兜底：从 data.json 构建
        fs.readFile(dataFile, 'utf-8', (err2, content2) => {
          if (!err2) {
            try {
              const arr = JSON.parse(content2);
              const payload = { meta: {}, cats: {}, stats: { sentences: arr.length, words: 0, cats: 1 } };
              payload.cats.all = arr.slice(0, 30).map(i => ({ a: i.ar, e: i.en, c: i.cn }));
              payload.stats.words = arr.reduce((s, i) => s + (i.ar || '').split(/\s+/).length, 0);
              res.writeHead(200, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' });
              res.end(JSON.stringify(payload));
              return;
            } catch (e) {}
          }
          res.writeHead(404); res.end('{}');
        });
      });
      return;
    }

    // 文章列表
    if (urlPath === '/api/articles') {
      const af = path.join(DATA_DIR, 'articles.json');
      fs.readFile(af, 'utf-8', (err, content) => {
        if (err) { res.writeHead(404); res.end('{}'); return; }
        try {
          const arts = JSON.parse(content);
          const arr = Object.keys(arts).map(k => ({ key: k, title: arts[k].title || '', body: arts[k].body || '', cn: arts[k].cn || '' }));
          res.writeHead(200, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' });
          res.end(JSON.stringify({ total: arr.length, articles: arr }));
        } catch (e) { res.writeHead(500); res.end('{}'); }
      });
      return;
    }

    // AI 对话代理（转发到 8080 server.py）
    // 其余 /api/* 一律转发到 8080（server.py）——例如 /api/read（可读全文）
    if (urlPath.indexOf('/api/') === 0) {
      const proxy = http.request({
        host: '127.0.0.1', port: 8080, path: req.url, method: req.method,
        headers: { 'Content-Type': req.headers['content-type'] || 'application/json' },
      }, (pRes) => {
        res.writeHead(pRes.statusCode || 502, { 'Content-Type': pRes.headers['content-type'] || 'application/json' });
        pRes.pipe(res);
      });
      proxy.on('error', () => {
        res.writeHead(502, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'local server (8080) unavailable' }));
      });
      req.pipe(proxy);
      return;
    }

    if (urlPath === '/api/chat/message' && req.method === 'POST') {
      let body = '';
      req.on('data', (c) => { body += c; });
      req.on('end', () => {
        const proxy = http.request({
          host: '127.0.0.1', port: 8080, path: '/api/chat/message', method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) },
        }, (pRes) => {
          let data = '';
          pRes.on('data', (c) => { data += c; });
          pRes.on('end', () => {
            res.writeHead(pRes.statusCode || 200, { 'Content-Type': 'application/json' });
            res.end(data);
          });
        });
        proxy.on('error', () => {
          res.writeHead(200, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ arabic: '⚠️ AI 服务暂不可用，请稍后重试' }));
        });
        proxy.end(body);
      });
      return;
    }

    // 静态文件
    let filePath = urlPath === '/' ? '/index.html' : urlPath;
    const full = path.join(DIST_DIR, filePath);
    if (!full.startsWith(DIST_DIR)) { res.writeHead(403); res.end(); return; }
    fs.readFile(full, (err, data) => {
      if (err) { res.writeHead(404); res.end('Not Found'); return; }
      res.writeHead(200, { 'Content-Type': MIME[path.extname(full)] || 'application/octet-stream' });
      res.end(data);
    });
  });
  webServer.listen(APP_PORT, '127.0.0.1', () => log(`✅ 内置服务已启动 (${APP_PORT})`));
}

// 内置爬虫
function runScraper() {
  if (scraperRunning) return;
  scraperRunning = true;
  log('🕷 爬虫开始运行...');
  const p = spawn('python3', [SCRAPER_SCRIPT], { stdio: 'ignore' });
  p.on('close', (code) => {
    scraperRunning = false;
    log(`🕷 爬虫完成 (退出码 ${code})`);
    if (win && !win.isDestroyed()) win.webContents.reload();
  });
  p.on('error', (e) => { scraperRunning = false; log(`⚠️ 爬虫失败: ${e.message}`); });
}

// ===== 原生语音识别（macOS SFSpeechRecognizer）=====
var voiceProc = null;
function startVoiceListener(){
  if(voiceProc) return;
  var script = path.join(__dirname, 'voice_listener.swift');
  voiceProc = spawn('swift', [script], { env: process.env });
  voiceProc.stdout.on('data', function(chunk){
    var lines = String(chunk).split('\n');
    lines.forEach(function(l){
      l = l.trim();
      if(l && win && !win.isDestroyed()) win.webContents.send('voice-text', l);
    });
  });
  voiceProc.stderr.on('data', function(chunk){
    var msg = String(chunk).trim();
    if(msg && win && !win.isDestroyed()) win.webContents.send('voice-state', 'error:' + msg);
  });
  voiceProc.on('exit', function(){ voiceProc = null; });
  if(win && !win.isDestroyed()) win.webContents.send('voice-state', 'started');
}
function stopVoiceListener(){
  if(voiceProc){ voiceProc.kill(); voiceProc = null; }
  if(win && !win.isDestroyed()) win.webContents.send('voice-state', 'stopped');
}
ipcMain.on('voice-start', function(){ startVoiceListener(); });
ipcMain.on('voice-stop', function(){ stopVoiceListener(); });

function createWindow() {
  win = new BrowserWindow({
    width: 1180, height: 820, minWidth: 900, minHeight: 600,
    title: 'حامل المصباح · 燃灯者',
    backgroundColor: '#0f3d31',
    autoHideMenuBar: true,
    webPreferences: { nodeIntegration: false, contextIsolation: true, preload: path.join(__dirname, 'preload.js') },
  });
  try { win.webContents.session.clearCache(); } catch (e) {}
  win.webContents.session.setCacheEnabled ? win.webContents.session.setCacheEnabled(false) : null;
  win.loadURL(APP_URL);
  win.webContents.setWindowOpenHandler(({ url }) => { shell.openExternal(url); return { action: 'deny' }; });
  win.on('closed', () => { win = null; });
}

app.whenReady().then(() => {
  try {
    const { systemPreferences } = require('electron');
    if (systemPreferences && systemPreferences.askForMediaAccess) {
      systemPreferences.askForMediaAccess('microphone').then(function(ok){ log('🎙 麦克风权限: ' + ok); }).catch(function(){});
    }
  } catch (e) {}
  try {
    const { session } = require('electron');
    session.defaultSession.setPermissionRequestHandler(function(wc, permission, cb){ cb(true); });
  } catch (e) {}
  startAIServer();
  startWebServer();
  setTimeout(createWindow, 1500);

  setTimeout(runScraper, 6000); // 启动后立即爬一次
  setInterval(runScraper, SCRAPE_INTERVAL); // 每小时
  log(`⏰ 每小时自动爬虫已设置 (每 ${SCRAPE_INTERVAL / 60000} 分钟)`);
});

app.on('window-all-closed', () => app.quit());
app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
app.on('quit', () => {
  if (serverProc) { try { serverProc.kill(); } catch {} }
  if (webServer) { try { webServer.close(); } catch {} }
});
