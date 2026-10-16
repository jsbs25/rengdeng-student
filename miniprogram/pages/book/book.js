const api = require('../../utils/api');

Page({
  data: {
    book: null,
    chapters: [],
    reading: false,
    current: null,
    title: ''
  },
  onLoad(options) {
    const title = decodeURIComponent(options.title || '');
    this.setData({ title });
    const book = api.getBookByTitle(title);
    if (book) {
      this.setBook(book);
    } else {
      // 冷启动直接进阅读页：先拉缓存再取
      api.getBooksCached().then(() => {
        this.setBook(api.getBookByTitle(title));
      });
    }
  },
  setBook(book) {
    if (!book) {
      wx.showToast({ title: '未找到该书', icon: 'none' });
      return;
    }
    this.setData({
      book,
      chapters: book.chapters || []
    });
    wx.setNavigationBarTitle({ title: book.title || '阅读' });
  },
  openChapter(e) {
    const i = e.currentTarget.dataset.i;
    const ch = this.data.chapters[i];
    this.setData({ reading: true, current: { t: ch.t, body: ch.body } });
  },
  backToList() {
    this.setData({ reading: false, current: null });
  }
});
