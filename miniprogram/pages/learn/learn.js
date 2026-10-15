const api = require('../../utils/api');

const CAT_NAMES = {
  greeting: ['👋', '问候'], daily: ['🌅', '日常'], food: ['🍽', '饮食'],
  travel: ['✈️', '旅行'], family: ['👨‍👩‍👧', '家庭'], work: ['💼', '工作'],
  study: ['📚', '学习'], religion: ['🕌', '宗教'], health: ['🏥', '健康'],
  weather: ['🌤', '天气'], shopping: ['🛍', '购物'], hobby: ['🎨', '爱好'],
  other: ['📖', '其他'], jordan_greet: ['✈️', '旅途问候'], jordan_airport: ['🛫', '机场'],
  jordan_hotel: ['🏨', '住宿'], jordan_food: ['🍽', '餐厅'], jordan_shop: ['🛍', '购物讲价'],
  jordan_dir: ['🧭', '问路'], jordan_campus: ['🎓', '校园'], jordan_emerg: ['🚨', '紧急'],
  jordan_social: ['👥', '社交'], jordan_daily: ['☕', '日常表达']
};

Page({
  data: {
    cats: [],
    catKeys: [],
    activeCat: '',
    sentences: [],
    stats: {},
    loading: true
  },
  onLoad() {
    this.load();
  },
  load() {
    api.getSentences().then((d) => {
      const cats = d.cats || {};
      const keys = Object.keys(cats);
      const first = keys[0] || '';
      this.setData({
        cats,
        catKeys: keys,
        activeCat: first,
        sentences: (cats[first] || []).slice(0, 60),
        stats: d.stats || {},
        loading: false
      });
    }).catch(() => {
      this.setData({ loading: false });
      wx.showToast({ title: '加载失败，请检查网络', icon: 'none' });
    });
  },
  catName(key) {
    const m = CAT_NAMES[key] || ['📖', key];
    return m[0] + ' ' + m[1];
  },
  onCatTap(e) {
    const key = e.currentTarget.dataset.key;
    this.setData({
      activeCat: key,
      sentences: (this.data.cats[key] || []).slice(0, 60)
    });
  }
});
