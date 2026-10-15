// 历史库模块：回族历史 + 穆斯林历史 + 中国穆斯林历史
import React, { useState } from 'react';
import {
  View, Text, Modal, FlatList, TouchableOpacity, StyleSheet, TextInput, ScrollView,
} from 'react-native';
import * as Speech from 'expo-speech';
import { speak as ttsSpeak } from './tts';
import { Colors, Radius } from './theme';
import { ArchHeader } from './components';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useStudyTimer } from './useStudyTimer';
import DATA from './data';

const CATS = [
  { key: 'huihui', icon: '🌙', name: '回族历史' },
  { key: 'muslim', icon: '🕌', name: '穆斯林历史' },
  { key: 'cnmuslim', icon: '🕋', name: '中国穆斯林' },
];

export default function HistoryModal({ visible, onClose }) {
  useStudyTimer(visible);
  const articles = DATA.history || [];
  const [cat, setCat] = useState('huihui');
  const [q, setQ] = useState('');
  const [cur, setCur] = useState(null); // 当前阅读文章
  const [fontScale, setFontScale] = useState(1);
  const [readSet, setReadSet] = useState({});
  const [favSet, setFavSet] = useState({});

  // 关闭时回到列表 + 加载已读标记
  React.useEffect(() => {
    if (!visible) {
      Speech.stop();
    }
    if (visible) {
      setCur(null);
      AsyncStorage.getItem('nur_hist_read').then((raw) => {
        if (raw) setReadSet(JSON.parse(raw));
      }).catch(() => {});
      AsyncStorage.getItem('nur_hist_fav').then((raw) => {
        if (raw) setFavSet(JSON.parse(raw));
      }).catch(() => {});
    }
  }, [visible]);

  const openArticle = (item) => {
    setCur(item);
    setReadSet((prev) => {
      const next = { ...prev, [item.title]: 1 };
      AsyncStorage.setItem('nur_hist_read', JSON.stringify(next)).catch(() => {});
      return next;
    });
  };

  const list = articles
    .filter((a) => a.cat === cat)
    .filter((a) => (q.trim() ? a.title.includes(q.trim()) : true));

  const speakCn = (text) => {
    if (!text) return;
    Speech.stop();
    ttsSpeak(text.replace(/[🕌🕋🌙📜]/g, ''), { lang: 'zh-CN', rate: 0.85 });
  };

  return (
    <Modal visible={visible} animationType="slide" onRequestClose={() => { setCur(null); onClose(); }}>
      <View style={styles.root}>
        <ArchHeader title={cur ? cur.title : '📜 历史库'} subtitle="" zh={cur ? `${cur.icon} ${cur.cat_cn} · ${cur.body.length} 字` : '回族 · 穆斯林 · 中国穆斯林'} />

        {!cur ? (
          <>
            <View style={styles.catRow}>
              {CATS.map((c) => {
                const n = articles.filter((a) => a.cat === c.key).length;
                return (
                  <TouchableOpacity key={c.key} style={[styles.catChip, cat === c.key && styles.catChipOn]} onPress={() => { setCat(c.key); setQ(''); }}>
                    <Text style={[styles.catTxt, cat === c.key && styles.catTxtOn]}>{c.icon} {c.name} · {n}</Text>
                  </TouchableOpacity>
                );
              })}
            </View>
            <View style={styles.searchRow}>
              <TouchableOpacity
                style={styles.randBtn}
                onPress={() => {
                  const pool = articles.filter((a) => a.cat === cat);
                  if (pool.length) openArticle(pool[Math.floor(Math.random() * pool.length)]);
                }}
              >
                <Text style={styles.randTxt}>🎲 随机一篇</Text>
              </TouchableOpacity>
            </View>
            <View style={styles.searchRow}>
              <TextInput
                style={styles.search}
                value={q}
                onChangeText={setQ}
                placeholder="🔍 搜索文章标题..."
                placeholderTextColor="#b9b3a6"
              />
            </View>
            <FlatList
              data={list}
              keyExtractor={(a) => a.title}
              contentContainerStyle={{ padding: 14, paddingBottom: 30 }}
              renderItem={({ item }) => (
                <TouchableOpacity style={styles.item} onPress={() => openArticle(item)}>
                  <Text style={styles.itemIcon}>{item.icon || '📜'}</Text>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.itemTitle}>{item.title}</Text>
                    <Text style={styles.itemMeta}>{favSet[item.title] ? '⭐ ' : ''}{readSet[item.title] ? '✅ 已读' : `${item.body.length} 字`} · 点击阅读</Text>
                  </View>
                  <Text style={styles.itemGo}>›</Text>
                </TouchableOpacity>
              )}
              ListEmptyComponent={<Text style={styles.empty}>暂无文章</Text>}
            />
          </>
        ) : (
          <View style={styles.readWrap}>
            <View style={styles.readTools}>
              <TouchableOpacity style={styles.toolBtn} onPress={() => speakCn(cur.body)}>
                <Text style={styles.toolTxt}>🔊 朗读</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.toolBtn}
                onPress={() => {
                  setFavSet((prev) => {
                    const next = { ...prev };
                    if (next[cur.title]) delete next[cur.title];
                    else next[cur.title] = 1;
                    AsyncStorage.setItem('nur_hist_fav', JSON.stringify(next)).catch(() => {});
                    return next;
                  });
                }}
              >
                <Text style={styles.toolTxt}>{favSet[cur.title] ? '⭐ 已收藏' : '☆ 收藏'}</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.toolBtn} onPress={() => setFontScale(fontScale === 1 ? 1.15 : fontScale === 1.15 ? 0.9 : 1)}>
                <Text style={styles.toolTxt}>🔠 字号 {fontScale}x</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.toolBtn}
                onPress={() => {
                  const i = list.findIndex((a) => a.title === cur.title);
                  setCur(list[Math.max(0, i - 1)]);
                }}
              >
                <Text style={styles.toolTxt}>‹ 上一篇</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.toolBtn}
                onPress={() => {
                  const i = list.findIndex((a) => a.title === cur.title);
                  const next = list[(i + 1) % list.length];
                  setCur(next);
                }}
              >
                <Text style={styles.toolTxt}>下一篇 ›</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.toolBtn} onPress={() => setCur(null)}>
                <Text style={styles.toolTxt}>← 列表</Text>
              </TouchableOpacity>
            </View>
            <ScrollView contentContainerStyle={{ padding: 18, paddingBottom: 40 }}>
              <Text style={[styles.body, { fontSize: 15.5 * fontScale }]}>{cur.body}</Text>
              <Text style={styles.relTitle}>📚 相关文章（{cur.cat_cn}）</Text>
              {list.filter((a) => a.title !== cur.title).slice(0, 5).map((a) => (
                <TouchableOpacity key={a.title} style={styles.relItem} onPress={() => openArticle(a)}>
                  <Text style={styles.relTxt}>{a.icon} {a.title}</Text>
                  <Text style={styles.relGo}>›</Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
        )}
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: Colors.cream },
  catRow: { flexDirection: 'row', gap: 8, paddingHorizontal: 16, paddingTop: 12 },
  catChip: {
    paddingHorizontal: 14, paddingVertical: 8, borderRadius: 16,
    backgroundColor: Colors.white, borderWidth: 1, borderColor: 'rgba(201,168,76,0.3)',
  },
  catChipOn: { backgroundColor: Colors.greenDark, borderColor: 'rgba(201,168,76,0.5)' },
  catTxt: { fontSize: 11.5, fontWeight: '700', color: Colors.ink },
  catTxtOn: { color: Colors.goldLight },
  searchRow: { paddingHorizontal: 16, paddingTop: 10 },
  randBtn: {
    backgroundColor: Colors.greenDark, borderRadius: 14, paddingVertical: 8, paddingHorizontal: 14,
    alignItems: 'center', marginBottom: 8,
  },
  randTxt: { fontSize: 11, fontWeight: '700', color: Colors.goldLight },
  search: {
    backgroundColor: Colors.white, borderRadius: Radius.md, paddingHorizontal: 14, paddingVertical: 9,
    fontSize: 12.5, color: Colors.ink, borderWidth: 1, borderColor: 'rgba(201,168,76,0.3)',
  },
  item: {
    flexDirection: 'row', alignItems: 'center', backgroundColor: Colors.white,
    borderRadius: Radius.md, padding: 13, marginBottom: 8,
    borderWidth: 1, borderColor: 'rgba(201,168,76,0.2)',
  },
  itemIcon: { fontSize: 24, marginRight: 12 },
  itemTitle: { fontSize: 13.5, fontWeight: '700', color: Colors.ink },
  itemMeta: { fontSize: 10, color: Colors.muted, marginTop: 3 },
  itemGo: { fontSize: 18, color: Colors.gold },
  empty: { fontSize: 12, color: Colors.muted, textAlign: 'center', padding: 30 },
  readWrap: { flex: 1 },
  readTools: { flexDirection: 'row', gap: 8, paddingHorizontal: 14, paddingTop: 12 },
  toolBtn: {
    paddingHorizontal: 12, paddingVertical: 7, borderRadius: 14,
    backgroundColor: Colors.white, borderWidth: 1, borderColor: 'rgba(201,168,76,0.3)',
  },
  toolTxt: { fontSize: 10.5, fontWeight: '600', color: Colors.ink },
  body: { color: Colors.ink, lineHeight: 28, textAlign: 'justify', letterSpacing: 0.3 },
  relTitle: { fontSize: 13, fontWeight: '800', color: Colors.greenDark, marginTop: 22, marginBottom: 8 },
  relItem: {
    flexDirection: 'row', alignItems: 'center', backgroundColor: Colors.white,
    borderRadius: 12, padding: 11, marginBottom: 6,
    borderWidth: 1, borderColor: 'rgba(201,168,76,0.2)',
  },
  relTxt: { fontSize: 12, color: Colors.ink, flex: 1 },
  relGo: { fontSize: 15, color: Colors.gold },
});
