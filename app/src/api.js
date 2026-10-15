// 数据层：优先从本地服务(server.py)拉取，失败自动降级到内置数据
// 真机通过局域网 IP 访问；Web 用 localhost；IP 可在「我的 → 服务器设置」里改
import DATA from './data';
import ARTICLES from './articlesData';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_BASE as DEFAULT_BASE, PORT } from './config';
import * as Network from 'expo-network';

let baseOverride = null;
let cachedBase = null;
let discovering = null;

async function ping(url) {
  try {
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), 1500);
    const r = await fetch(url, { signal: ctrl.signal, cache: 'no-store' });
    clearTimeout(t);
    return r.ok;
  } catch (e) { return false; }
}

// 自动扫描局域网找服务器（手机 IP 变化也能连上）
async function findServer() {
  if (await ping(DEFAULT_BASE)) return DEFAULT_BASE;
  try {
    const myIp = await Network.getIpAddressAsync();
    if (myIp && myIp !== '0.0.0.0' && myIp.indexOf('.') > 0) {
      const seg = myIp.substring(0, myIp.lastIndexOf('.') + 1);
      // 先扫常用主机位 1-60（服务器通常在路由器附近）
      const ips = [];
      for (let i = 1; i <= 254; i++) ips.push(seg + i);
      for (let i = 0; i < 60; i += 15) {
        const batch = ips.slice(i, i + 15);
        const res = await Promise.all(batch.map(ip => ping(`http://${ip}:${PORT}`)));
        const hit = batch.find((ip, j) => res[j]);
        if (hit) return `http://${hit}:${PORT}`;
      }
    }
  } catch (e) {}
  return null;
}

// 重置发现缓存（服务器切换时调用）
export function resetServerDiscovery() {
  cachedBase = null;
  baseOverride = null;
}

// 获取当前 API 基址（自动发现：默认 IP → 局域网扫描）
export async function getApiBase() {
  if (baseOverride) return baseOverride;
  if (cachedBase) return cachedBase;
  if (discovering) return discovering;
  discovering = (async () => {
    try {
      const ip = await AsyncStorage.getItem('nur_server_ip');
      if (ip && ip.trim()) {
        cachedBase = `http://${ip.trim()}:${PORT}`;
        return cachedBase;
      }
    } catch (e) {}
    const found = await findServer();
    cachedBase = found || DEFAULT_BASE;
    return cachedBase;
  })();
  const r = await discovering;
  discovering = null;
  return r;
}

export function setServerIp(ip) {
  baseOverride = ip && ip.trim() ? `http://${ip.trim()}:${PORT}` : null;
  clearDataCache();
}

let cache = null;

export async function loadData() {
  if (cache) return cache;
  try {
    const res = await fetch(`${await getApiBase()}/api/sentences`, { cache: 'no-store' });
    if (res.ok) {
      const json = await res.json();
      if (json && json.cats) {
        cache = json;
        return json;
      }
    }
  } catch (e) {
    // 静默降级到内置数据
  }
  return DATA;
}

export function clearDataCache() {
  cache = null;
}

// ===== 图书馆文章 =====
let artCache = null;
export async function loadArticles() {
  if (artCache) return artCache;
  try {
    const res = await fetch(`${await getApiBase()}/api/articles`, { cache: 'no-store' });
    if (res.ok) {
      const json = await res.json();
      if (json && Array.isArray(json.articles) && json.articles.length > 0) {
        artCache = json.articles;
        return artCache;
      }
    }
  } catch (e) {
    // 降级
  }
  return ARTICLES;
}

// ===== 图书馆书籍（整本书）=====
import BOOKS from './booksData';
let bookCache = null;
export async function loadBooks() {
  if (bookCache) return bookCache;
  try {
    const res = await fetch(`${await getApiBase()}/api/books`, { cache: 'no-store' });
    if (res.ok) {
      const json = await res.json();
      if (json && Array.isArray(json.books) && json.books.length > 0) {
        bookCache = json.books;
        return bookCache;
      }
    }
  } catch (e) {
    // 降级
  }
  return BOOKS;
}

// ===== AI 对话 =====
export async function chatMessage(message, sessionId = 'app') {
  let token = '';
  try { token = (await AsyncStorage.getItem('nur_token')) || ''; } catch (e) {}
  const res = await fetch(`${await getApiBase()}/api/chat/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, session_id: sessionId, token }),
  });
  if (!res.ok) throw new Error('HTTP ' + res.status);
  const data = await res.json();
  return data.arabic || '';
}

// ===== 本地词频表（无需服务器）=====
const ARABIC_RE = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+/g;
const TASHKEEL_RE = /[\u064B-\u0652\u0670\u0640\u06D6-\u06ED]/g;

export function buildVocab(data) {
  const freq = {};
  Object.values(data.cats || {}).forEach((arr) => {
    (arr || []).forEach((s) => {
      const m = (s.a || '').match(ARABIC_RE) || [];
      m.forEach((raw) => {
        const w = raw.replace(TASHKEEL_RE, '');
        if (w.length >= 2) freq[w] = (freq[w] || 0) + 1;
      });
    });
  });
  return Object.entries(freq)
    .map(([w, f]) => ({ w, f }))
    .sort((x, y) => y.f - x.f);
}

// ===== 句子词拆分（去音符，供拆解/跟读用）=====
export function splitWords(sentence) {
  const m = (sentence || '').match(ARABIC_RE) || [];
  return m.map((raw) => raw.replace(TASHKEEL_RE, ''));
}

// ===== 学习进度写入（学一句 +1 已学）=====
export async function logLearned(store, id) {
  try {
    await store.markLearned(id);
  } catch (e) {
    // 忽略
  }
}
