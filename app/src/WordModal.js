// 单词表模块：词汇表（词频）+ 单词拆解（逐词） + AI 词义解释
import React, { useState, useEffect, useMemo } from 'react';
import {
  View, Text, Modal, FlatList, TouchableOpacity, StyleSheet, TextInput, ActivityIndicator,
} from 'react-native';
import * as Speech from 'expo-speech';
import { speak as ttsSpeak } from './tts';
import { Colors, Radius } from './theme';
import { ArchHeader } from './components';
import DATA from './data';
import VOCAB_DATA from './vocabData';
import { loadData, buildVocab, splitWords, chatMessage } from './api';
import { WordBook } from './wordbook';
import { SRS } from './srs';
import { useStudyTimer } from './useStudyTimer';

export default function WordModal({ visible, onClose }) {
  useStudyTimer(visible);
  const [tab, setTab] = useState('vocab'); // vocab | split
  const [data, setData] = useState(DATA);
  const [q, setQ] = useState('');
  const [explain, setExplain] = useState(null); // {word, ar, en} AI 解释结果
  const [loading, setLoading] = useState(false);
  const [splitWord, setSplitWord] = useState(null); // {sentence, words[]}
  const [savedSet, setSavedSet] = useState({}); // 已收词集合

  useEffect(() => {
    if (visible) {
      loadData().then(setData);
      WordBook.getAll().then((l) => {
        const s = {};
        l.forEach((x) => { s[x.w] = 1; });
        setSavedSet(s);
      });
    }
  }, [visible]);

  // 收词/移出生词本
  const toggleSave = async (w, f) => {
    if (savedSet[w]) {
      await WordBook.remove(w);
      const s = { ...savedSet };
      delete s[w];
      setSavedSet(s);
    } else {
      await WordBook.add(w, f);
      setSavedSet({ ...savedSet, [w]: 1 });
      SRS.add('w', w); // 顺手进入间隔复习队列
    }
  };

  useEffect(() => {
    if (visible) loadData().then(setData);
  }, [visible]);

  const meanMap = useMemo(() => {
    const m = {};
    VOCAB_DATA.forEach((v) => { m[v.w] = { cn: v.cn, en: v.en }; });
    return m;
  }, []);

  const vocab = useMemo(() => buildVocab(data), [data]);
  const filtered = useMemo(() => {
    const t = q.trim().toLowerCase();
    if (!t) return vocab;
    return vocab.filter((v) => v.w.includes(t));
  }, [vocab, q]);

  const allSentences = useMemo(() => {
    const out = [];
    let gid = 0;
    Object.entries(data.cats || {}).forEach(([k, arr]) => {
      (arr || []).filter((s) => s.c && s.e).forEach((s) => {
        out.push({ ...s, _cat: k, _id: gid++ });
      });
    });
    return out;
  }, [data]);

  const sentFiltered = useMemo(() => {
    const t = q.trim().toLowerCase();
    if (!t) return allSentences;
    return allSentences.filter(
      (s) => s.a.includes(t) || (s.c || '').includes(t) || (s.e || '').toLowerCase().includes(t)
    );
  }, [allSentences, q]);

  const speak = async (text, rate = 0.6) => {
    Speech.stop();
    await ttsSpeak(text, { lang: 'ar-SA', rate, onError: () => Alert.alert('朗读失败', 'TTS 语音包不可用，请检查系统文字转语音设置') });
  };

  const askExplain = async (word) => {
    setLoading(true);
    try {
      const reply = await chatMessage(
        `请对这个阿拉伯语单词做词法语法分析，用这个格式回答（每行一个字段）：\n` +
        `词根：\n词性：（名词/动词/介词/代词等）\n语法：（格位/时态/人称/数）\n中文词义：\n英文词义：\n例句：（阿拉伯语+中文）\n\n单词：${word}`,
        'word_explain'
      );
      setExplain({ word, ar: reply });
    } catch (e) {
      setExplain({ word, ar: '⚠️ AI 服务未连接，请确认 server.py 已运行。' });
    }
    setLoading(false);
  };

  const openSplit = (s) => {
    setSplitWord({ ...s, words: splitWords(s.a) });
  };

  const closeAll = () => {
    setExplain(null);
    setSplitWord(null);
    onClose();
  };

  return (
    <Modal visible={visible} animationType="slide" onRequestClose={closeAll}>
      <View style={styles.root}>
        <ArchHeader title="📖 单词表" subtitle="AL-MUFRADĀT" zh="词汇表 · 单词拆解 · AI 解释" />

        <View style={styles.tabRow}>
          <TouchableOpacity style={[styles.tab, tab === 'vocab' && styles.tabOn]} onPress={() => { setTab('vocab'); setQ(''); }}>
            <Text style={[styles.tabTxt, tab === 'vocab' && styles.tabTxtOn]}>🔤 词汇表 ({vocab.length})</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.tab, tab === 'split' && styles.tabOn]} onPress={() => { setTab('split'); setQ(''); }}>
            <Text style={[styles.tabTxt, tab === 'split' && styles.tabTxtOn]}>✂️ 单词拆解 ({allSentences.length})</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.closeBtn} onPress={closeAll}>
            <Text style={styles.closeTxt}>✕</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.searchRow}>
          <TextInput
            style={styles.search}
            value={q}
            onChangeText={setQ}
            placeholder={tab === 'vocab' ? '搜索阿拉伯语单词...' : '搜索阿语 / 中文 / 英文句子...'}
            placeholderTextColor={Colors.muted}
          />
        </View>

        {tab === 'vocab' ? (
          <FlatList
            data={filtered}
            keyExtractor={(item) => item.w}
            contentContainerStyle={{ padding: 16, paddingBottom: 40 }}
            renderItem={({ item, index }) => (
              <View style={styles.wItem}>
                <Text style={styles.wRank}>{index + 1}</Text>
                <TouchableOpacity style={{ flex: 1 }} onPress={() => speak(item.w)}>
                  <Text style={styles.wText}>{item.w}</Text>
                  <Text style={styles.wFreq}>
                    {meanMap[item.w] ? `${meanMap[item.w].cn} · ${meanMap[item.w].en}` : `出现 ${item.f} 次`}
                  </Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.saveBtn} onPress={() => toggleSave(item.w, item.f)}>
                  <Text style={styles.saveTxt}>{savedSet[item.w] ? '📌 已收' : '📌 收词'}</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.aiBtn} onPress={() => askExplain(item.w)}>
                  <Text style={styles.aiBtnTxt}>🤖 解释</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.playBtn} onPress={() => speak(item.w)}>
                  <Text style={styles.playTxt}>🔊</Text>
                </TouchableOpacity>
              </View>
            )}
            ListEmptyComponent={<Text style={styles.empty}>无匹配单词</Text>}
          />
        ) : (
          <FlatList
            data={sentFiltered}
            keyExtractor={(item) => String(item._id)}
            contentContainerStyle={{ padding: 16, paddingBottom: 40 }}
            renderItem={({ item }) => (
              <TouchableOpacity style={styles.sItem} onPress={() => openSplit(item)}>
                <Text style={styles.sAr}>{item.a}</Text>
                <Text style={styles.sCn}>{item.c}</Text>
                <Text style={styles.sHint}>✂️ 点此拆解单词 →</Text>
              </TouchableOpacity>
            )}
            ListEmptyComponent={<Text style={styles.empty}>无匹配句子</Text>}
          />
        )}

        {loading ? (
          <View style={styles.loadingBar}><ActivityIndicator color={Colors.gold} /><Text style={styles.loadingTxt}>AI 正在解释...</Text></View>
        ) : null}

        {/* AI 解释弹层 */}
        {explain ? (
          <Modal visible transparent animationType="fade" onRequestClose={() => setExplain(null)}>
            <View style={styles.mask}>
              <View style={styles.explainCard}>
                <View style={styles.explainHead}>
                  <Text style={styles.explainWord}>{explain.word}</Text>
                  <View style={{ flexDirection: 'row', alignItems: 'center', gap: 10 }}>
                    <TouchableOpacity onPress={() => toggleSave(explain.word, 0)}>
                      <Text style={[styles.explainClose, { fontSize: 12, color: savedSet[explain.word] ? Colors.green : Colors.goldDark }]}>
                        {savedSet[explain.word] ? '📌 已收' : '📌 收词'}
                      </Text>
                    </TouchableOpacity>
                    <TouchableOpacity onPress={() => setExplain(null)}><Text style={styles.explainClose}>✕</Text></TouchableOpacity>
                  </View>
                </View>
                <View style={styles.explainBtns}>
                  <TouchableOpacity style={styles.explainSpeak} onPress={() => speak(explain.word)}>
                    <Text style={styles.explainSpeakTxt}>🔊 阿语发音</Text>
                  </TouchableOpacity>
                  <TouchableOpacity style={styles.explainSpeakEn} onPress={() => {
                    const m = (explain.ar || '').match(/英文词义[：:]\s*([^\n]+)/);
                    if (m && m[1]) ttsSpeak(m[1].trim(), { lang: 'en-US', rate: 0.85 });
                  }}>
                    <Text style={styles.explainSpeakTxt}>🇬🇧 读英文</Text>
                  </TouchableOpacity>
                </View>
                <Text style={styles.explainBody}>{explain.ar}</Text>
              </View>
            </View>
          </Modal>
        ) : null}

        {/* 单词拆解弹层 */}
        {splitWord ? (
          <Modal visible transparent animationType="fade" onRequestClose={() => setSplitWord(null)}>
            <View style={styles.mask}>
              <View style={styles.splitCard}>
                <View style={styles.splitHead}>
                  <Text style={styles.splitTitle}>✂️ 单词拆解</Text>
                  <TouchableOpacity onPress={() => setSplitWord(null)}><Text style={styles.explainClose}>✕</Text></TouchableOpacity>
                </View>
                <Text style={styles.splitSentence}>{splitWord.a}</Text>
                <View style={styles.chips}>
                  {splitWord.words.map((w, i) => (
                    <TouchableOpacity key={i} style={styles.chip} onPress={() => { speak(w); askExplain(w); }}>
                      <Text style={styles.chipTxt}>{w}</Text>
                    </TouchableOpacity>
                  ))}
                </View>
                <Text style={styles.splitHint}>👆 点任意单词：发音 + AI 词法语法分析（词根/词性/格位/时态）</Text>
                <View style={styles.transBox}>
                  <Text style={styles.transTxt}>🇨🇳 {splitWord.c}</Text>
                  <Text style={styles.transTxt}>🇬🇧 {splitWord.e}</Text>
                </View>
                <TouchableOpacity style={styles.splitPlayAll} onPress={() => speak(splitWord.a, 0.5)}>
                  <Text style={styles.splitPlayAllTxt}>🐢 慢速朗读整句</Text>
                </TouchableOpacity>
              </View>
            </View>
          </Modal>
        ) : null}
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: Colors.cream },
  tabRow: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 16, paddingTop: 12, gap: 8 },
  tab: {
    paddingHorizontal: 14, paddingVertical: 7, borderRadius: 16,
    backgroundColor: Colors.white, borderWidth: 1, borderColor: 'rgba(201,168,76,0.3)',
  },
  tabOn: { backgroundColor: Colors.greenDark, borderColor: 'rgba(201,168,76,0.5)' },
  tabTxt: { fontSize: 11, fontWeight: '600', color: Colors.ink },
  tabTxtOn: { color: '#fff' },
  closeBtn: { marginLeft: 'auto', width: 32, height: 32, borderRadius: 16, backgroundColor: 'rgba(192,57,43,0.1)', alignItems: 'center', justifyContent: 'center' },
  closeTxt: { fontSize: 14, color: Colors.danger },
  searchRow: { paddingHorizontal: 16, paddingTop: 10 },
  search: {
    backgroundColor: Colors.white, borderRadius: 18, paddingHorizontal: 14, paddingVertical: 9,
    fontSize: 12, borderWidth: 1, borderColor: 'rgba(201,168,76,0.25)', color: Colors.ink,
  },
  wItem: {
    flexDirection: 'row', alignItems: 'center', backgroundColor: Colors.white,
    borderRadius: Radius.md, padding: 12, marginBottom: 8,
    borderWidth: 1, borderColor: 'rgba(201,168,76,0.14)',
  },
  wRank: { fontSize: 11, color: Colors.muted, width: 30, textAlign: 'center' },
  wText: { fontFamily: 'serif', fontSize: 16, fontWeight: '700', color: Colors.greenDark, textAlign: 'right', writingDirection: 'rtl' },
  wFreq: { fontSize: 9.5, color: Colors.muted, marginTop: 2 },
  aiBtn: {
    paddingHorizontal: 10, paddingVertical: 5, borderRadius: 12,
    backgroundColor: 'rgba(201,168,76,0.12)', borderWidth: 1, borderColor: 'rgba(201,168,76,0.35)', marginLeft: 8,
  },
  aiBtnTxt: { fontSize: 9.5, fontWeight: '700', color: Colors.goldDark },
  saveBtn: {
    paddingHorizontal: 10, paddingVertical: 5, borderRadius: 12,
    backgroundColor: 'rgba(26,92,74,0.1)', borderWidth: 1, borderColor: 'rgba(26,92,74,0.35)', marginLeft: 8,
  },
  saveTxt: { fontSize: 9.5, fontWeight: '700', color: Colors.green },
  playBtn: {
    width: 30, height: 30, borderRadius: 15, backgroundColor: Colors.gold,
    alignItems: 'center', justifyContent: 'center', marginLeft: 8,
  },
  playTxt: { fontSize: 12 },
  sItem: {
    backgroundColor: Colors.white, borderRadius: Radius.md, padding: 13, marginBottom: 8,
    borderWidth: 1, borderColor: 'rgba(201,168,76,0.14)',
  },
  sAr: { fontFamily: 'serif', fontSize: 15, fontWeight: '700', color: Colors.greenDark, textAlign: 'right', writingDirection: 'rtl', lineHeight: 24 },
  sCn: { fontSize: 11, color: Colors.green, marginTop: 5 },
  sHint: { fontSize: 9.5, color: Colors.goldDark, marginTop: 6, textAlign: 'right' },
  empty: { textAlign: 'center', color: Colors.muted, marginTop: 40, fontSize: 13 },
  loadingBar: { position: 'absolute', bottom: 20, alignSelf: 'center', flexDirection: 'row', alignItems: 'center', backgroundColor: Colors.greenDark, paddingHorizontal: 14, paddingVertical: 8, borderRadius: 18, gap: 8 },
  loadingTxt: { fontSize: 11, color: '#fff' },
  mask: { flex: 1, backgroundColor: 'rgba(15,61,49,0.45)', justifyContent: 'center', padding: 24 },
  explainCard: { backgroundColor: Colors.cream, borderRadius: Radius.lg, padding: 20, maxHeight: '75%' },
  explainHead: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 },
  explainWord: { fontFamily: 'serif', fontSize: 24, fontWeight: '800', color: Colors.greenDark, textAlign: 'right', writingDirection: 'rtl' },
  explainClose: { fontSize: 16, color: Colors.muted },
  explainBtns: { flexDirection: 'row', gap: 8, marginBottom: 10 },
  explainSpeak: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 14, backgroundColor: Colors.gold },
  explainSpeakEn: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 14, backgroundColor: 'rgba(90,127,158,0.9)' },
  explainSpeakTxt: { fontSize: 11, fontWeight: '700', color: '#fff' },
  explainBody: { fontSize: 13, color: Colors.ink, lineHeight: 22 },
  splitCard: { backgroundColor: Colors.cream, borderRadius: Radius.lg, padding: 20, maxHeight: '80%' },
  splitHead: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 },
  splitTitle: { fontSize: 15, fontWeight: '700', color: Colors.greenDark },
  splitSentence: { fontFamily: 'serif', fontSize: 17, fontWeight: '700', color: Colors.greenDark, textAlign: 'right', writingDirection: 'rtl', lineHeight: 30 },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginTop: 14 },
  chip: {
    paddingHorizontal: 12, paddingVertical: 8, borderRadius: 16,
    backgroundColor: Colors.white, borderWidth: 1, borderColor: 'rgba(201,168,76,0.35)',
  },
  chipTxt: { fontFamily: 'serif', fontSize: 14, fontWeight: '700', color: Colors.greenDark },
  splitHint: { fontSize: 10, color: Colors.muted, marginTop: 10 },
  transBox: { backgroundColor: Colors.white, borderRadius: Radius.md, padding: 12, marginTop: 12, borderWidth: 1, borderColor: 'rgba(201,168,76,0.14)' },
  transTxt: { fontSize: 12, color: Colors.ink, lineHeight: 20 },
  splitPlayAll: { marginTop: 12, backgroundColor: Colors.greenDark, borderRadius: Radius.md, paddingVertical: 11, alignItems: 'center' },
  splitPlayAllTxt: { fontSize: 12, fontWeight: '700', color: Colors.goldLight },
});
