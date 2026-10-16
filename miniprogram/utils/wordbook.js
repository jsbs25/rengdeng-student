// 生词本：本地收藏（wx.storage），无网络也可用
const KEY = 'nur_wordbook';

function list() {
  return wx.getStorageSync(KEY) || [];
}

function save(items) {
  wx.setStorageSync(KEY, items);
}

function add(word) {
  const items = list();
  // 去重（按阿拉伯语原文）
  if (!items.some((w) => w.a === word.a)) {
    items.unshift(word);
    save(items);
    return true;
  }
  return false;
}

function remove(a) {
  const items = list().filter((w) => w.a !== a);
  save(items);
  return items;
}

function has(a) {
  return list().some((w) => w.a === a);
}

module.exports = { list, add, remove, has };
