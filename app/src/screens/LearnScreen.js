// 学习模块 LearnScreen（分类课程 + 句子表 + 收藏 + 复习 + 已学）
import React, { useState, useEffect, useMemo } from 'react';
import {
  View, Text, ScrollView, StyleSheet, TouchableOpacity, FlatList, TextInput,
} from 'react-native';
import { Colors, Shadows, Radius } from '../theme';
import { ArchHeader, CategoryChip, SentenceCard } from '../components';
import DATA from '../data';
import { loadData } from '../api';
import { Store } from '../store';
import { SRS } from '../srs';
import { useStudyTimer } from '../useStudyTimer';
import WordModal from '../WordModal';
import FlashcardModal from '../FlashcardModal';
import AlphabetModal from '../AlphabetModal';
import QuizModal from '../QuizModal';
import WordBookModal from '../WordBookModal';
import QuranModal from '../QuranModal';
import HadithModal from '../HadithModal';
import HistoryModal from '../HistoryModal';
import DialogModal from '../DialogModal';
import LibraryModal from '../LibraryModal';

function Entry({ icon, title, desc, onPress }) {
  return (
    <TouchableOpacity style={styles.entry} activeOpacity={0.85} onPress={onPress}>
      <View style={styles.entryIcon}><Text style={{ fontSize: 17 }}>{icon}</Text></View>
      <Text style={styles.entryTitle}>{title}</Text>
      <Text style={styles.entryDesc}>{desc}</Text>
    </TouchableOpacity>
  );
}

export default function LearnScreen({ route }) {
  useStudyTimer(true);
  const initCat = (route.params && route.params.cat) || 'all';
  const [cat, setCat] = useState(initCat);
  const [data, setData] = useState(DATA);
  const [favs, setFavs] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [learned, setLearned] = useState([]);
  const [showFavs, setShowFavs] = useState(false);
  const [showReview, setShowReview] = useState(false);
  const [showLearned, setShowLearned] = useState(false);
  const [q, setQ] = useState('');
  const [wordOpen, setWordOpen] = useState(false);
  const [flashOpen, setFlashOpen] = useState(false);
  const [alphaOpen, setAlphaOpen] = useState(false);
  const [quizOpen, setQuizOpen] = useState(false);
  const [wbOpen, setWbOpen] = useState(false);
  const [quranOpen, setQuranOpen] = useState(false);
  const [hadithOpen, setHadithOpen] = useState(false);
  const [histOpen, setHistOpen] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [libOpen, setLibOpen] = useState(false);
  const [reviewMode, setReviewMode] = useState(false);

  useEffect(() => {
    Store.getFavorites().then(setFavs);
    Store.getReview().then(setReviews);
    Store.getLearned().then(setLearned);
    loadData().then(setData);
    const sub = Store.subscribe(() => Store.getLearned().then(setLearned));
    return () => sub();
  }, []);

  const refresh = async () => {
    setFavs(await Store.getFavorites());
    setReviews(await Store.getReview());
    setLearned(await Store.getLearned());
  };

  // 组装句子列表（带全局id）
  const all = useMemo(() => {
    const out = [];
    let gid = 0;
    Object.keys(data.cats || {}).forEach((k) => {
      (data.cats[k] || []).forEach((s) => {
        out.push({ ...s, _cat: k, _id: gid++ });
      });
    });
    return out;
  }, [data]);

  const filtered = useMemo(() => {
    let list = showFavs
      ? all.filter((s) => favs.includes(s._id))
      : showReview
        ? all.filter((s) => reviews.includes(s._id))
        : showLearned
          ? all.filter((s) => learned.includes(s._id))
          : cat === 'all' ? all : all.filter((s) => s._cat === cat);
    const t = q.trim().toLowerCase();
    if (t) {
      list = list.filter(
        (s) => s.a.includes(t) || (s.c || '').includes(t) || (s.e || '').toLowerCase().includes(t)
      );
    }
    return list;
  }, [all, cat, favs, reviews, learned, showFavs, showReview, showLearned, q]);

  const resetFilters = () => { setShowFavs(false); setShowReview(false); setShowLearned(false); };

  return (
    <View style={styles.root}>
      <ArchHeader title="📚 学习" subtitle="" zh="句子表 · 单词 · 分类课程" />

      {/* 学习功能入口 */}
      <View style={styles.entryGrid}>
        <Entry icon="🃏" title="闪卡" desc="SRS 间隔复习" onPress={() => { setReviewMode(false); setFlashOpen(true); }} />
        <Entry icon="🔤" title="字母入门" desc="28 字母 · 写法" onPress={() => setAlphaOpen(true)} />
        <Entry icon="📝" title="测验" desc="10 题闯关" onPress={() => setQuizOpen(true)} />
        <Entry icon="📕" title="生词本" desc="我的生词" onPress={() => setWbOpen(true)} />
        <Entry icon="🕌" title="古兰经" desc="114 章全文" onPress={() => setQuranOpen(true)} />
        <Entry icon="📜" title="圣训库" desc="六大部 · 2200 则" onPress={() => setHadithOpen(true)} />
        <Entry icon="📜" title="历史库" desc="回族 · 穆斯林" onPress={() => setHistOpen(true)} />
        <Entry icon="💬" title="日常对话" desc="每日 100 句" onPress={() => setDialogOpen(true)} />
        <Entry icon="📚" title="图书馆" desc="书籍 · 文章" onPress={() => setLibOpen(true)} />
        <Entry icon="📖" title="单词表" desc="词法分析" onPress={() => setWordOpen(true)} />
      </View>

      <View style={styles.filterRow}>
        <TouchableOpacity
          style={[styles.filterBtn, showFavs && styles.filterBtnOn]}
          onPress={() => { setShowFavs(!showFavs); setShowReview(false); setShowLearned(false); }}
        >
          <Text style={styles.filterTxt}>⭐ 收藏 ({favs.length})</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.filterBtn, showReview && styles.filterBtnOn]}
          onPress={() => { setShowReview(!showReview); setShowFavs(false); setShowLearned(false); }}
        >
          <Text style={styles.filterTxt}>📌 复习 ({reviews.length})</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.filterBtn, showLearned && styles.filterBtnOn]}
          onPress={() => { setShowLearned(!showLearned); setShowFavs(false); setShowReview(false); }}
        >
          <Text style={styles.filterTxt}>✅ 已学 ({learned.length})</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.filterBtn, styles.wordBtn]} onPress={() => setWordOpen(true)}>
          <Text style={styles.filterTxt}>📖 单词表</Text>
        </TouchableOpacity>
        <Text style={styles.filterCount}>共 {filtered.length} 句</Text>
      </View>

      <View style={styles.searchRow}>
        <TextInput
          style={styles.search}
          value={q}
          onChangeText={setQ}
          placeholder="🔍 搜索阿语 / 中文 / 英文..."
          placeholderTextColor={Colors.muted}
        />
      </View>

      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.catRow}>
        <CategoryChip icon="🏛" name="全部" ar="الكل" active={cat === 'all' && !showFavs && !showReview && !showLearned} onPress={() => { setCat('all'); resetFilters(); }} />
        {Object.entries(data.meta || {}).map(([key, m]) => (
          <CategoryChip
            key={key} icon={m.icon} name={m.cn} ar={m.ar}
            active={cat === key && !showFavs && !showReview && !showLearned}
            onPress={() => { setCat(key); resetFilters(); }}
          />
        ))}
      </ScrollView>

      <FlatList
        data={filtered}
        keyExtractor={(item) => String(item._id)}
        contentContainerStyle={{ padding: 16, paddingBottom: 30 }}
        renderItem={({ item, index }) => (
          <SentenceCard
            sentence={item}
            id={item._id}
            index={index}
            isFav={favs.includes(item._id)}
            isReview={reviews.includes(item._id)}
            onToggleFav={async () => { await Store.toggleFavorite(item._id); refresh(); }}
            onToggleReview={async () => {
              const nowIn = !reviews.includes(item._id);
              await Store.toggleReview(item._id);
              if (nowIn) await SRS.add('s', item.a);
              else await SRS.remove('s', item.a);
              refresh();
            }}
            onSpeakAr={async () => { await Store.markLearned(item._id); refresh(); }}
          />
        )}
        ListEmptyComponent={<Text style={styles.empty}>暂无内容，换个筛选试试</Text>}
      />

      <WordModal visible={wordOpen} onClose={() => setWordOpen(false)} />
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: Colors.cream },
  entryGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, paddingHorizontal: 16, paddingTop: 4 },
  entry: {
    width: '31%', backgroundColor: '#fff', borderRadius: 14, paddingVertical: 12, paddingHorizontal: 6,
    alignItems: 'center', borderWidth: 1, borderColor: 'rgba(201,168,76,.22)',
  },
  entryIcon: { width: 36, height: 36, borderRadius: 12, backgroundColor: 'rgba(201,168,76,.14)', alignItems: 'center', justifyContent: 'center', marginBottom: 5 },
  entryTitle: { fontSize: 11.5, fontWeight: '800', color: Colors.greenDark },
  entryDesc: { fontSize: 8, color: Colors.muted, marginTop: 2, textAlign: 'center' },
  filterRow: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 16, paddingTop: 12, gap: 6, flexWrap: 'wrap' },
  filterBtn: {
    paddingHorizontal: 11, paddingVertical: 6, borderRadius: 14,
    borderWidth: 1, borderColor: 'rgba(201,168,76,0.3)', backgroundColor: Colors.white,
  },
  filterBtnOn: { backgroundColor: Colors.gold },
  filterTxt: { fontSize: 10, color: Colors.ink, fontWeight: '600' },
  wordBtn: { borderColor: 'rgba(26,92,74,0.4)', backgroundColor: 'rgba(26,92,74,0.06)' },
  filterCount: { marginLeft: 'auto', fontSize: 10, color: Colors.muted },
  searchRow: { paddingHorizontal: 16, paddingTop: 8 },
  search: {
    backgroundColor: Colors.white, borderRadius: 18, paddingHorizontal: 14, paddingVertical: 9,
    fontSize: 12, borderWidth: 1, borderColor: 'rgba(201,168,76,0.25)', color: Colors.ink,
  },
  catRow: { paddingHorizontal: 16, paddingVertical: 10 },
  empty: { textAlign: 'center', color: Colors.muted, marginTop: 40, fontSize: 13 },
});
