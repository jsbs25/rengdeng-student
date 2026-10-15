// 生词本：个人收藏词汇 · 搜索 · 发音 · 释义 · 一键加入间隔复习
import React, { useState, useEffect } from 'react';
import {
  View, Text, Modal, FlatList, TouchableOpacity, StyleSheet, TextInput, Alert,
} from 'react-native';
import { speak as ttsSpeak } from './tts';
import { Colors, Radius } from './theme';
import { ArchHeader } from './components';
import VOCAB from './vocabData';
import { WordBook } from './wordbook';
import { SRS } from './srs';
import { useStudyTimer } from './useStudyTimer';

export default function WordBookModal({ visible, onClose, onStartReview }) {
  useStudyTimer(visible);
  const [list, setList] = useState([]);
  const [q, setQ] = useState('');

  const refresh = async () => {
    const l = await WordBook.getAll();
    // 附带内置释义
    const withMean = l.map((x) => {
      const m = VOCAB.find((v) => v.w === x.w);
      return { ...x, cn: m ? m.cn : '', en: m ? m.en : '' };
    });
    setList(withMean);
  };

  useEffect(() => { if (visible) refresh(); }, [visible]);

  const remove = async (w) => {
    await WordBook.remove(w);
    refresh();
  };

  const addAllToSrs = async () => {
    for (const x of list) await SRS.add('w', x.w);
    Alert.alert('✅ 已加入复习队列', `生词本 ${list.length} 个词已加入间隔复习，明天开始按遗忘曲线提醒你。`);
    if (onStartReview) onStartReview();
    onClose();
  };

  const shown = q.trim() ? list.filter((x) => x.w.includes(q.trim())) : list;

  return (
    <Modal visible={visible} animationType="slide" onRequestClose={onClose}>
      <View style={styles.root}>
        <ArchHeader title="📕 生词本" subtitle="" zh={`我的生词 · ${list.length} 个`} />
        <View style={styles.searchRow}>
          <TextInput
            style={styles.search}
            placeholder="🔍 搜索生词..."
            value={q}
            onChangeText={setQ}
            placeholderTextColor="#b9b3a6"
          />
        </View>
        {list.length > 0 ? (
          <>
            <FlatList
              data={shown}
              keyExtractor={(x) => x.w}
              contentContainerStyle={{ padding: 16, paddingBottom: 30 }}
              renderItem={({ item }) => (
                <View style={styles.item}>
                  <TouchableOpacity style={{ flex: 1 }} onPress={() => ttsSpeak(item.w, { lang: 'ar-SA', rate: 0.6 })}>
                    <Text style={styles.wAr}>{item.w}</Text>
                    {item.cn ? <Text style={styles.wCn}>🇨🇳 {item.cn}　{item.en ? `🇬🇧 ${item.en}` : ''}</Text> : <Text style={styles.wCn}>词频 {item.f}</Text>}
                  </TouchableOpacity>
                  <TouchableOpacity style={styles.rmBtn} onPress={() => remove(item.w)}>
                    <Text style={styles.rmTxt}>🗑</Text>
                  </TouchableOpacity>
                </View>
              )}
              ListEmptyComponent={<Text style={styles.empty}>没有匹配的生词</Text>}
            />
            <View style={styles.foot}>
              <TouchableOpacity style={styles.srsBtn} onPress={addAllToSrs}>
                <Text style={styles.srsTxt}>📅 全部加入间隔复习</Text>
              </TouchableOpacity>
            </View>
          </>
        ) : (
          <View style={styles.emptyWrap}>
            <Text style={styles.emptyEmoji}>📭</Text>
            <Text style={styles.emptyTitle}>生词本还是空的</Text>
            <Text style={styles.emptyDesc}>在单词表或句子拆解里点「📌 收词」，生词就会出现在这里，随时复习。</Text>
          </View>
        )}
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: Colors.cream },
  searchRow: { paddingHorizontal: 16, paddingTop: 12 },
  search: {
    backgroundColor: Colors.white, borderRadius: Radius.md, paddingHorizontal: 14, paddingVertical: 9,
    fontSize: 12.5, color: Colors.ink, borderWidth: 1, borderColor: 'rgba(201,168,76,0.3)',
  },
  item: {
    flexDirection: 'row', alignItems: 'center', backgroundColor: Colors.white,
    borderRadius: Radius.md, padding: 12, marginBottom: 8,
    borderWidth: 1, borderColor: 'rgba(201,168,76,0.2)',
  },
  wAr: { fontFamily: 'serif', fontSize: 17, fontWeight: '700', color: Colors.greenDark, textAlign: 'right', writingDirection: 'rtl' },
  wCn: { fontSize: 10.5, color: Colors.muted, marginTop: 3 },
  rmBtn: { padding: 8, marginLeft: 8 },
  rmTxt: { fontSize: 13 },
  foot: { padding: 16, paddingTop: 4 },
  srsBtn: { backgroundColor: Colors.greenDark, borderRadius: Radius.md, paddingVertical: 13, alignItems: 'center' },
  srsTxt: { fontSize: 13, fontWeight: '700', color: Colors.goldLight },
  emptyWrap: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 30 },
  emptyEmoji: { fontSize: 52 },
  emptyTitle: { fontSize: 16, fontWeight: '800', color: Colors.greenDark, marginTop: 10 },
  emptyDesc: { fontSize: 11.5, color: Colors.muted, marginTop: 8, textAlign: 'center', lineHeight: 18 },
  empty: { fontSize: 11, color: Colors.muted, textAlign: 'center', padding: 20 },
});
