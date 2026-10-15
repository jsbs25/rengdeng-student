// 间隔重复复习引擎（SRS）：盒子法 0/1/3/7/15/30 天
// 句子键 's:'+原文，单词键 'w:'+词 —— 数据更新后依然稳定
import AsyncStorage from '@react-native-async-storage/async-storage';

const KEY = 'nur_srs_v1';
const BOX_DAYS = [0, 1, 3, 7, 15, 30];

function todayStr() {
  const d = new Date();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${d.getFullYear()}-${m}-${day}`;
}

function addDays(days) {
  const d = new Date();
  d.setDate(d.getDate() + days);
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${d.getFullYear()}-${m}-${day}`;
}

async function load() {
  try {
    const raw = await AsyncStorage.getItem(KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

async function save(map) {
  try { await AsyncStorage.setItem(KEY, JSON.stringify(map)); } catch {}
}

export const SRS = {
  key(kind, text) {
    return kind + ':' + (text || '').replace(/\s+/g, ' ').trim();
  },
  // 加入复习队列（首次学习）
  async add(kind, text) {
    const k = this.key(kind, text);
    const map = await load();
    if (!map[k]) {
      map[k] = { box: 1, due: addDays(1), reps: 0, lapses: 0, last: todayStr() };
      await save(map);
    }
    return map[k];
  },
  // 答题：ok=认识（升盒），否则降盒；按盒子天数排下次到期
  async answer(kind, text, ok) {
    const k = this.key(kind, text);
    const map = await load();
    const rec = map[k] || { box: 0, reps: 0, lapses: 0 };
    rec.reps = (rec.reps || 0) + 1;
    if (ok) rec.box = Math.min(5, (rec.box || 0) + 1);
    else { rec.lapses = (rec.lapses || 0) + 1; rec.box = Math.max(0, (rec.box || 0) - 1); }
    rec.due = addDays(BOX_DAYS[rec.box]);
    rec.last = todayStr();
    map[k] = rec;
    await save(map);
    return rec;
  },
  // 到期列表
  async due() {
    const map = await load();
    const t = todayStr();
    return Object.entries(map)
      .filter(([, r]) => r.due <= t)
      .map(([k, r]) => ({ key: k, box: r.box, due: r.due }));
  },
  // 统计：到期数 / 总数
  async counts() {
    const map = await load();
    const t = todayStr();
    let due = 0;
    for (const k in map) if (map[k].due <= t) due++;
    return { due, total: Object.keys(map).length };
  },
  async remove(kind, text) {
    const k = this.key(kind, text);
    const map = await load();
    if (map[k]) { delete map[k]; await save(map); }
  },
};
