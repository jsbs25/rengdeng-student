// 燃灯同学 · 全局入口
const { API_BASE } = require('./config');

App({
  globalData: {
    apiBase: API_BASE,
    token: ''
  },
  onLaunch() {
    const token = wx.getStorageSync('nur_token');
    if (token) this.globalData.token = token;
  },
  setToken(token) {
    this.globalData.token = token || '';
    if (token) wx.setStorageSync('nur_token', token);
    else wx.removeStorageSync('nur_token');
  }
});
