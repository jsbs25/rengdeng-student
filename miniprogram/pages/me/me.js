const api = require('../../utils/api');

Page({
  data: {
    stats: {},
    deviceId: '',
    version: '1.0.0'
  },
  onLoad() {
    this.setData({ deviceId: api.getDeviceId() });
    api.getHomeStats().then((s) => {
      this.setData({ stats: s || {} });
    }).catch(() => {});
  },
  login() {
    api.deviceLogin().then((d) => {
      if (d && d.token) {
        getApp().setToken(d.token);
        wx.showToast({ title: '已登录', icon: 'success' });
      } else {
        wx.showToast({ title: (d && d.msg) || '登录失败', icon: 'none' });
      }
    }).catch(() => {
      wx.showToast({ title: '网络错误', icon: 'none' });
    });
  },
  copyDomain() {
    wx.setClipboardData({ data: 'https://燃灯同学.com' });
  }
});
