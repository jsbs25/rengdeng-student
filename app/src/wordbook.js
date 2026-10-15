// 生词本：个人收藏词汇（离线存储）
import AsyncStorage from '@react-native-async-storage/async-storage';

const KEY = 'nur_wordbook_v1';

export const WordBook = {
  async getAll() {
    try {
      const raw = await AsyncStorage.getItem(KEY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  },
  async has(w) {
    const list = await this.getAll();
    return list.some((x) => x.w === w);
  },
  async add(w, f) {
    const list = await this.getAll();
    if (!list.some((x) => x.w === w)) {
      list.unshift({ w, f: f || 0, added: Date.now() });
      await AsyncStorage.setItem(KEY, JSON.stringify(list));
    }
    return list;
  },
  async remove(w) {
    const list = await this.getAll();
    const next = list.filter((x) => x.w !== w);
    await AsyncStorage.setItem(KEY, JSON.stringify(next));
    return next;
  },
};
