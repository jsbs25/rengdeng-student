// 本地持久化存储：收藏、学习进度、统计、状态订阅
import AsyncStorage from '@react-native-async-storage/async-storage';

const KEYS = {
  favorites: 'nur_favorites',
  learned: 'nur_learned',
  review: 'nur_review',
  stats: 'nur_stats',
};

const DEFAULT_STATS = {
  streakDays: 0,
  todayMinutes: 0,
  goalWords: 20,
  learnedWords: 0,
  totalMinutes: 0,
  lastDate: '',
  studyDates: [], // ['2026-07-29', ...] 用于连续天数计算
  historyMinutes: {}, // {'2026-07-29': 12, ...} 每日学习分钟（近30天）
};

const listeners = new Set();

function emit() {
  Store.getStats().then((s) => listeners.forEach((fn) => fn(s)));
}

function todayStr() {
  const d = new Date();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${d.getFullYear()}-${m}-${day}`;
}

function computeStreak(dates) {
  if (!dates || dates.length === 0) return 0;
  const set = new Set(dates);
  const today = todayStr();
  let cursor = new Date();
  if (!set.has(today)) {
    cursor.setDate(cursor.getDate() - 1); // 允许今天还没学，从昨天回溯
  }
  let streak = 0;
  while (true) {
    const m = String(cursor.getMonth() + 1).padStart(2, '0');
    const day = String(cursor.getDate()).padStart(2, '0');
    const key = `${cursor.getFullYear()}-${m}-${day}`;
    if (!set.has(key)) break;
    streak++;
    cursor.setDate(cursor.getDate() - 1);
  }
  return streak;
}

async function get(key, fallback) {
  try {
    const raw = await AsyncStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

async function set(key, value) {
  try {
    await AsyncStorage.setItem(key, JSON.stringify(value));
  } catch {}
}

export const Store = {
  // 收藏
  async getFavorites() { return get(KEYS.favorites, []); },
  async toggleFavorite(id) {
    const favs = await this.getFavorites();
    const idx = favs.indexOf(id);
    if (idx >= 0) favs.splice(idx, 1);
    else favs.push(id);
    await set(KEYS.favorites, favs);
    return favs;
  },
  async isFavorite(id) {
    const favs = await this.getFavorites();
    return favs.includes(id);
  },

  // 已学习
  async getLearned() { return get(KEYS.learned, []); },
  async markLearned(id) {
    const learned = await this.getLearned();
    if (!learned.includes(id)) {
      learned.push(id);
      await set(KEYS.learned, learned);
      const stats = await this.getStats();
      stats.learnedWords = learned.length;
      stats.studyDates = Array.from(new Set([...(stats.studyDates || []), todayStr()]));
      stats.streakDays = computeStreak(stats.studyDates);
      stats.lastDate = todayStr();
      await this.saveStats(stats);
      emit();
    }
    return learned;
  },
  async isLearned(id) {
    const learned = await this.getLearned();
    return learned.includes(id);
  },

  // 复习队列
  async getReview() { return get(KEYS.review, []); },
  async toggleReview(id) {
    const list = await this.getReview();
    const idx = list.indexOf(id);
    if (idx >= 0) list.splice(idx, 1);
    else list.push(id);
    await set(KEYS.review, list);
    return list;
  },

  // 统计
  async getStats() {
    const stats = await get(KEYS.stats, DEFAULT_STATS);
    // 跨天重置今日分钟数
    const today = todayStr();
    if (stats.lastDate !== today) {
      stats.todayMinutes = 0;
      stats.lastDate = today;
      await set(KEYS.stats, stats);
    }
    return stats;
  },
  async saveStats(stats) { await set(KEYS.stats, stats); },
  async addMinutes(min) {
    const stats = await this.getStats();
    stats.todayMinutes = (stats.todayMinutes || 0) + min;
    stats.totalMinutes = (stats.totalMinutes || 0) + min;
    stats.studyDates = Array.from(new Set([...(stats.studyDates || []), todayStr()]));
    stats.streakDays = computeStreak(stats.studyDates);
    const hist = stats.historyMinutes || {};
    hist[todayStr()] = (hist[todayStr()] || 0) + min;
    // 只保留近 30 天
    const keys = Object.keys(hist).sort().slice(-30);
    stats.historyMinutes = {};
    keys.forEach((k) => { stats.historyMinutes[k] = hist[k]; });
    await set(KEYS.stats, stats);
    emit();
    return stats;
  },

  // 状态订阅（供首页等实时刷新）
  subscribe(fn) {
    listeners.add(fn);
    return () => listeners.delete(fn);
  },
};
