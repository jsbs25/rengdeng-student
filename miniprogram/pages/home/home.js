const api = require('../../utils/api');

Page({
  data: {
    daily: null,
    stats: {},
    loading: true
  },
  onLoad() {
    this.load();
  },
  onPullDownRefresh() {
    this.load().finally(() => wx.stopPullDownRefresh());
  },
  load() {
    this.setData({ loading: true });
    return Promise.all([
      api.getDaily().catch(() => null),
      api.getHomeStats().catch(() => null)
    ]).then(([daily, stats]) => {
      const s = stats || {};
      this.setData({
        daily,
        stats: {
          sentences: s.sentences || '—',
          vocab: s.vocab || '—',
          quran: s.quran || '—'
        },
        loading: false
      });
    });
  },
  goLearn() { wx.switchTab({ url: '/pages/learn/learn' }); },
  goLibrary() { wx.switchTab({ url: '/pages/library/library' }); },
  goAI() { wx.switchTab({ url: '/pages/ai/ai' }); }
});
