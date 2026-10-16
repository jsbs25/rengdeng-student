// 燃灯同学 · API 封装（对接 server.py 的 /api/*）
const { API_BASE } = require('../config');

function getApp_() {
  return getApp();
}

function request(path, opts = {}) {
  return new Promise((resolve, reject) => {
    const app = getApp_();
    const header = { 'Content-Type': 'application/json' };
    const token = opts.token || (app && app.globalData.token) || '';
    if (token) header['X-Token'] = token;
    wx.request({
      url: API_BASE + path,
      method: (opts.method || 'GET').toUpperCase(),
      data: opts.data || {},
      header,
      timeout: 20000,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) resolve(res.data);
        else reject(new Error('HTTP ' + res.statusCode));
      },
      fail: (err) => reject(new Error(err.errMsg || '网络错误'))
    });
  });
}

// 今日一句
function getDaily() {
  return request('/api/sentences/daily');
}

// 句子库（分类）
function getSentences() {
  return request('/api/sentences');
}

// 词汇表
function getVocab() {
  return request('/api/vocab');
}

// 首页统计
function getHomeStats() {
  return request('/api/home_stats');
}

// 精选书籍
function getBooks() {
  return request('/api/books');
}

// 世界图书馆书目
function getCatalog(page = 0, size = 60) {
  return request('/api/catalog?page=' + page + '&size=' + size);
}
function getCatalogMeta() {
  return request('/api/catalog/meta');
}

// 全站搜索（POST）
function search(q) {
  return request('/api/search', { method: 'POST', data: { q } });
}

// AI 对话（POST）
function chat(message, sessionId = 'mp') {
  return request('/api/chat/message', {
    method: 'POST',
    data: { message, session_id: sessionId }
  });
}

// 设备登录（无账号）
function deviceLogin() {
  return request('/api/device/login', {
    method: 'POST',
    data: { device_id: 'mp-' + getDeviceId() }
  });
}

function getDeviceId() {
  let id = wx.getStorageSync('nur_device_id');
  if (!id) {
    id = 'mp' + Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
    wx.setStorageSync('nur_device_id', id);
  }
  return id;
}

// 书籍缓存（整书 2.3MB，跨页复用，避免重复拉取）
let _booksCache = null;
function getBooksCached() {
  if (_booksCache) return Promise.resolve(_booksCache);
  return getBooks().then((d) => {
    _booksCache = (d && d.books) || [];
    return _booksCache;
  });
}
function getBookByTitle(title) {
  return (_booksCache || []).find((b) => b.title === title) || null;
}

module.exports = {
  API_BASE,
  request,
  getDaily,
  getSentences,
  getVocab,
  getHomeStats,
  getBooks,
  getCatalog,
  getCatalogMeta,
  search,
  chat,
  deviceLogin,
  getDeviceId,
  getBooksCached,
  getBookByTitle
};
