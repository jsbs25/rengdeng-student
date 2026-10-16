const api = require('../../utils/api');

Page({
  data: {
    books: [],
    meta: {},
    q: '',
    results: [],
    searching: false,
    loading: true
  },
  onLoad() {
    this.load();
  },
  load() {
    Promise.all([
      api.getBooksCached().catch(() => []),
      api.getCatalogMeta().catch(() => ({}))
    ]).then(([books, m]) => {
      this.setData({ books, meta: m, loading: false });
    });
  },
  onInput(e) {
    const q = e.detail.value.trim();
    this.setData({ q });
    if (!q) { this.setData({ results: [], searching: false }); return; }
    this.doSearch(q);
  },
  doSearch(q) {
    this.setData({ searching: true });
    api.search(q).then((d) => {
      this.setData({ results: (d.items || []).slice(0, 50), searching: false });
    }).catch(() => {
      this.setData({ searching: false });
      wx.showToast({ title: '搜索失败', icon: 'none' });
    });
  },
  openBook(e) {
    const t = e.currentTarget.dataset.title;
    wx.navigateTo({ url: '/pages/book/book?title=' + encodeURIComponent(t) });
  }
});
