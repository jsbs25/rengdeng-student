// 圣训库模块：六大部圣训选录（阿语 + 中文 + 经注注解）
import React, { useState } from 'react';
import {
  View, Text, Modal, FlatList, TouchableOpacity, StyleSheet, ScrollView, Alert, TextInput,
} from 'react-native';
import * as Speech from 'expo-speech';
import { speak as ttsSpeak } from './tts';
import { Colors, Radius } from './theme';
import { ArchHeader } from './components';
import DATA from './data';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useStudyTimer } from './useStudyTimer';
import { SRS } from './srs';

const BOOKS = [
  { key: 'bukhari', icon: '📕', name: '布哈里' },
  { key: 'muslim', icon: '📗', name: '穆斯林' },
  { key: 'tirmidhi', icon: '📘', name: '提尔米济' },
  { key: 'abudawud', icon: '📙', name: '艾布·达伍德' },
  { key: 'nasai', icon: '📓', name: '奈萨仪' },
  { key: 'ibnmajah', icon: '📔', name: '伊本·马哲' },
  { key: 'other', icon: '📖', name: '综合' },
];

export default function HadithModal({ visible, onClose }) {
  useStudyTimer(visible);
  const hadiths = DATA.hadith || [];
  const [book, setBook] = useState('bukhari');
  const [cur, setCur] = useState(null);
  const [tag, setTag] = useState('');
  const [q, setQ] = useState('');
  const [favSet, setFavSet] = useState({});

  React.useEffect(() => {
    if (visible) {
      AsyncStorage.getItem('nur_hadith_fav').then((raw) => {
        if (raw) setFavSet(JSON.parse(raw));
      }).catch(() => {});
    }
  }, [visible]);

  // 今日一训（按日期 seed 稳定选取）
  const todayHadith = React.useMemo(() => {
    const d = new Date();
    const seed = d.getFullYear() * 10000 + (d.getMonth() + 1) * 100 + d.getDate();
    const pool = hadiths.filter((h) => h.book === 'other');
    return pool.length ? pool[seed % pool.length] : null;
  }, [hadiths]);

  const list = hadiths
    .filter((h) => h.book === book)
    .filter((h) => (tag ? h.tag === tag : true))
    .filter((h) => (q.trim() ? (h.topic || '').includes(q.trim()) || (h.cn || '').includes(q.trim()) : true));
  const tags = book === 'other' ? Array.from(new Set(hadiths.filter((h) => h.book === 'other').map((h) => h.tag || '其他'))) : [];

  React.useEffect(() => {
    if (visible) setCur(null);
    if (!visible) Speech.stop();
  }, [visible]);

  const speakAr = (text) => {
    Speech.stop();
    ttsSpeak(text, { lang: 'ar-SA', rate: 0.65 });
  };

  return (
    <Modal visible={visible} animationType="slide" onRequestClose={() => { setCur(null); onClose(); }}>
      <View style={styles.root}>
        <ArchHeader title={cur ? '📜 圣训' : '📜 圣训库'} subtitle="" zh={cur ? cur.topic : `六大部圣训 · 共 ${hadiths.length} 则`} />

        {!cur ? (
          <>
            <View style={styles.bookRow}>
              {BOOKS.map((b) => {
                const n = hadiths.filter((h) => h.book === b.key).length;
                return (
                  <TouchableOpacity key={b.key} style={[styles.bookChip, book === b.key && styles.bookChipOn]} onPress={() => setBook(b.key)}>
                    <Text style={[styles.bookTxt, book === b.key && styles.bookTxtOn]}>{b.icon} {b.name} {n}</Text>
                  </TouchableOpacity>
                );
              })}
            </View>
            {todayHadith ? (
              <TouchableOpacity style={styles.todayCard} onPress={() => setCur(todayHadith)}>
                <Text style={styles.todayLabel}>📜 今日一训</Text>
                <Text style={styles.todayText} numberOfLines={2}>{todayHadith.topic}</Text>
                <Text style={styles.todayGo}>点击阅读 ›</Text>
              </TouchableOpacity>
            ) : null}
            <View style={styles.randRow}>
              <TouchableOpacity
                style={styles.randBtn}
                onPress={() => {
                  const pool = hadiths.filter((h) => h.book === book);
                  if (pool.length) setCur(pool[Math.floor(Math.random() * pool.length)]);
                }}
              >
                <Text style={styles.randTxt}>🎲 随机一则</Text>
              </TouchableOpacity>
            </View>
            <View style={styles.searchRow}>
              <TextInput
                style={styles.search}
                value={q}
                onChangeText={setQ}
                placeholder="🔍 搜索圣训（标题/正文）..."
                placeholderTextColor="#b9b3a6"
              />
            </View>
            {book === 'other' ? (
              <View style={styles.tagRow}>
                <TouchableOpacity style={[styles.tagChip, tag === '' && styles.tagChipOn]} onPress={() => setTag('')}>
                  <Text style={[styles.tagTxt, tag === '' && styles.tagTxtOn]}>全部</Text>
                </TouchableOpacity>
                {tags.map((t) => (
                  <TouchableOpacity key={t} style={[styles.tagChip, tag === t && styles.tagChipOn]} onPress={() => setTag(tag === t ? '' : t)}>
                    <Text style={[styles.tagTxt, tag === t && styles.tagTxtOn]}>{t}</Text>
                  </TouchableOpacity>
                ))}
              </View>
            ) : null}
            <FlatList
              data={list}
              keyExtractor={(h) => h.topic}
              contentContainerStyle={{ padding: 14, paddingBottom: 30 }}
              renderItem={({ item }) => (
                <TouchableOpacity style={styles.item} onPress={() => setCur(item)}>
                  <Text style={styles.itemIcon}>📜</Text>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.itemTitle}>{item.topic}</Text>
                    {item.ar ? <Text style={styles.itemAr} numberOfLines={1}>{item.ar}</Text> : null}
                    {item.grade ? <Text style={styles.itemGrade}>{favSet[item.topic] ? '⭐ 已藏 · ' : ''}✅ {item.grade}</Text> : null}
                  </View>
                  <Text style={styles.itemGo}>›</Text>
                </TouchableOpacity>
              )}
              ListEmptyComponent={<Text style={styles.empty}>该部暂无收录</Text>}
            />
          </>
        ) : (
          <ScrollView contentContainerStyle={{ padding: 18, paddingBottom: 40 }}>
            <View style={styles.readTools}>
              <TouchableOpacity style={styles.toolBtn} onPress={() => speakAr(cur.ar)}>
                <Text style={styles.toolTxt}>🔊 诵读阿语</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.toolBtn}
                onPress={async () => {
                  if (cur.ar) {
                    await SRS.add('s', cur.ar);
                    Alert.alert('✅ 已加入复习', '这段圣训会按遗忘曲线提醒你记诵（闪卡→间隔复习）');
                  } else {
                    Alert.alert('提示', '综合圣训暂不支持加入复习，可先收藏');
                  }
                }}
              >
                <Text style={styles.toolTxt}>📌 复习</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.toolBtn}
                onPress={() => {
                  setFavSet((prev) => {
                    const next = { ...prev };
                    if (next[cur.topic]) delete next[cur.topic];
                    else next[cur.topic] = 1;
                    AsyncStorage.setItem('nur_hadith_fav', JSON.stringify(next)).catch(() => {});
                    return next;
                  });
                }}
              >
                <Text style={styles.toolTxt}>{favSet[cur.topic] ? '⭐ 已藏' : '☆ 收藏'}</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.toolBtn} onPress={() => setCur(null)}>
                <Text style={styles.toolTxt}>← 返回</Text>
              </TouchableOpacity>
            </View>
            <Text style={styles.hTopic}>{cur.topic}</Text>
            {cur.ar ? (
              <View style={styles.arCard}>
                <Text style={styles.hAr}>{cur.ar}</Text>
              </View>
            ) : null}
            <View style={styles.cnCard}>
              <Text style={styles.hCn}>🇨🇳 {cur.cn}</Text>
            </View>
            {cur.grade ? (
              <Text style={styles.gradeTxt}>✅ 等级：{cur.grade}</Text>
            ) : null}
            {cur.note ? (
              <View style={styles.noteCard}>
                <Text style={styles.noteLabel}>📖 经注注解</Text>
                <Text style={styles.noteBody}>{cur.note}</Text>
              </View>
            ) : null}
            <Text style={styles.srcTxt}>📚 出处：{cur.book_cn || '综合圣训'}{cur.attribution ? ` · ${cur.attribution}` : ''}{cur.source_cn ? ` · ${cur.source_cn}` : ''}</Text>
          </ScrollView>
        )}
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: Colors.cream },
  bookRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 6, paddingHorizontal: 14, paddingTop: 12 },
  bookChip: {
    paddingHorizontal: 11, paddingVertical: 7, borderRadius: 14,
    backgroundColor: Colors.white, borderWidth: 1, borderColor: 'rgba(201,168,76,0.3)',
  },
  bookChipOn: { backgroundColor: Colors.greenDark, borderColor: 'rgba(201,168,76,0.5)' },
  bookTxt: { fontSize: 10.5, fontWeight: '700', color: Colors.ink },
  bookTxtOn: { color: Colors.goldLight },
  item: {
    flexDirection: 'row', alignItems: 'center', backgroundColor: Colors.white,
    borderRadius: Radius.md, padding: 13, marginBottom: 8,
    borderWidth: 1, borderColor: 'rgba(201,168,76,0.2)',
  },
  itemIcon: { fontSize: 22, marginRight: 12 },
  itemTitle: { fontSize: 13, fontWeight: '700', color: Colors.ink },
  itemAr: { fontSize: 12, color: Colors.goldDark, marginTop: 3, writingDirection: 'rtl', textAlign: 'left' },
  itemGo: { fontSize: 18, color: Colors.gold },
  itemGrade: { fontSize: 9.5, color: Colors.green, marginTop: 2 },
  empty: { fontSize: 12, color: Colors.muted, textAlign: 'center', padding: 30 },
  todayCard: {
    marginHorizontal: 14, marginTop: 10, padding: 13, borderRadius: Radius.md,
    backgroundColor: Colors.greenDark,
  },
  todayLabel: { fontSize: 11, fontWeight: '800', color: Colors.goldLight, marginBottom: 5 },
  todayText: { fontSize: 12.5, color: '#fff', lineHeight: 19 },
  todayGo: { fontSize: 9.5, color: 'rgba(232,212,139,0.8)', marginTop: 5 },
  randRow: { paddingHorizontal: 14, paddingTop: 10 },
  randBtn: {
    backgroundColor: Colors.greenDark, borderRadius: 14, paddingVertical: 8, paddingHorizontal: 14,
    alignItems: 'center', marginBottom: 8,
  },
  randTxt: { fontSize: 11, fontWeight: '700', color: Colors.goldLight },
  searchRow: { paddingHorizontal: 14, paddingBottom: 8 },
  search: {
    backgroundColor: Colors.white, borderRadius: Radius.md, paddingHorizontal: 12, paddingVertical: 8,
    fontSize: 12, color: Colors.ink, borderWidth: 1, borderColor: 'rgba(201,168,76,0.3)',
  },
  tagRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 6, paddingHorizontal: 14, paddingBottom: 8 },
  tagChip: {
    paddingHorizontal: 10, paddingVertical: 5, borderRadius: 12,
    backgroundColor: Colors.white, borderWidth: 1, borderColor: 'rgba(201,168,76,0.3)',
  },
  tagChipOn: { backgroundColor: Colors.greenDark },
  tagTxt: { fontSize: 10, color: Colors.ink },
  tagTxtOn: { color: Colors.goldLight },
  readTools: { flexDirection: 'row', gap: 8, marginBottom: 14 },
  toolBtn: {
    paddingHorizontal: 13, paddingVertical: 8, borderRadius: 14,
    backgroundColor: Colors.white, borderWidth: 1, borderColor: 'rgba(201,168,76,0.3)',
  },
  toolTxt: { fontSize: 11, fontWeight: '600', color: Colors.ink },
  hTopic: { fontSize: 15, fontWeight: '800', color: Colors.greenDark, marginBottom: 10 },
  arCard: {
    backgroundColor: Colors.greenDark, borderRadius: Radius.md, padding: 16,
    marginBottom: 10,
  },
  hAr: { fontFamily: 'serif', fontSize: 17, fontWeight: '700', color: Colors.goldLight, lineHeight: 30, writingDirection: 'rtl', textAlign: 'center' },
  cnCard: {
    backgroundColor: Colors.white, borderRadius: Radius.md, padding: 14,
    borderWidth: 1, borderColor: 'rgba(201,168,76,0.2)', marginBottom: 10,
  },
  hCn: { fontSize: 13.5, color: Colors.ink, lineHeight: 23 },
  noteCard: {
    backgroundColor: '#fdf6e3', borderRadius: Radius.md, padding: 14,
    borderWidth: 1, borderColor: 'rgba(201,168,76,0.35)', marginBottom: 10,
  },
  noteLabel: { fontSize: 12, fontWeight: '800', color: Colors.goldDark, marginBottom: 6 },
  noteBody: { fontSize: 12, color: Colors.ink, lineHeight: 21 },
  srcTxt: { fontSize: 10.5, color: Colors.muted, marginTop: 4 },
  gradeTxt: { fontSize: 11, color: Colors.green, marginBottom: 8 },
});
