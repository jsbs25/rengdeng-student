// 闪卡模块：句子闪卡 + 单词闪卡 + 📅 间隔复习（SRS 遗忘曲线）
import React, { useState, useEffect } from 'react';
import {
  View, Text, Modal, TouchableOpacity, StyleSheet, Animated, Alert,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { speak as ttsSpeak } from './tts';
import { Colors, Radius } from './theme';
import { ArchHeader } from './components';
import DATA from './data';
import VOCAB from './vocabData';
import { loadData, buildVocab, chatMessage } from './api';
import { SRS } from './srs';
import { WordBook } from './wordbook';
import { useStudyTimer } from './useStudyTimer';

const AI_CACHE_KEY = 'nur_word_mean_v2';

// 稳定键 ↔ 卡片解析
function buildSentenceMap(data) {
  const map = {};
  Object.values(data.cats || {}).forEach((arr) => {
    (arr || []).forEach((s) => {
      if (s.a) map[SRS.key('s', s.a)] = s;
    });
  });
  return map;
}

export default function FlashcardModal({ visible, onClose, initialMode }) {
  useStudyTimer(visible);
  const [mode, setMode] = useState('sentence'); // sentence | word | review
  const [deck, setDeck] = useState([]);
  const [idx, setIdx] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [known, setKnown] = useState(0);
  const [again, setAgain] = useState([]);
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [anim] = useState(new Animated.Value(0));
  const [dueCount, setDueCount] = useState(0);
  const [aiCache, setAiCache] = useState({});

  useEffect(() => {
    if (visible) {
      // 重新打开时回到模式选择（避免残留上一局）
      setDeck([]);
      setDone(false);
      setFlipped(false);
      setAiMean(null);
      if (initialMode === 'review') {
        startGame('review');
      }
    }
    AsyncStorage.getItem(AI_CACHE_KEY).then((raw) => raw && setAiCache(JSON.parse(raw))).catch(() => {});
    SRS.counts().then((c) => setDueCount(c.due));
  }, [visible]);

  const shuffle = (arr) => {
    const a = [...arr];
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  };

  // 开始新一局
  const startGame = async (m) => {
    const data = await loadData();
    let cards = [];
    if (m === 'sentence') {
      const all = Object.values(data.cats || {}).flat().filter((s) => s.a && s.c);
      cards = shuffle(all).slice(0, 12).map((s) => ({ kind: 's', card: s }));
    } else if (m === 'word') {
      const vocab = (buildVocab(data) || []).filter((v) => v.w).slice(0, 300);
      cards = shuffle(vocab).slice(0, 12).map((v) => ({ kind: 'w', word: v.w, card: v }));
    } else {
      // 复习模式：到期队列（句子 + 单词混合）
      const sMap = buildSentenceMap(data);
      const vSet = {};
      (buildVocab(data) || []).forEach((v) => { if (v.w) vSet[v.w] = 1; });
      const due = await SRS.due();
      const sent = [], words = [];
      due.forEach((d) => {
        if (d.key.startsWith('s:')) {
          const s = sMap[d.key];
          if (s) sent.push({ kind: 's', card: s });
        } else if (d.key.startsWith('w:')) {
          const w = d.key.slice(2);
          if (vSet[w]) {
            const m = VOCAB.find((x) => x.w === w);
            words.push({ kind: 'w', word: w, card: { w }, cn: m ? m.cn : '', en: m ? m.en : '' });
          }
        }
      });
      cards = shuffle([...sent, ...words]);
      if (cards.length === 0) {
        Alert.alert('🎉 没有到期的复习', '今天的复习任务已完成！明天再来。闪卡答题时点「不会」的词句会自动进入复习队列。');
        return;
      }
    }
    setMode(m);
    setDeck(cards);
    setIdx(0);
    setFlipped(false);
    setKnown(0);
    setAgain([]);
    setDone(false);
    setAnimVal(0);
    SRS.counts().then((c) => setDueCount(c.due));
  };

  const flip = () => {
    setFlipped(!flipped);
    Animated.spring(anim, { toValue: flipped ? 0 : 1, friction: 7, tension: 60, useNativeDriver: true }).start();
  };

  // 单词 AI 释义（缓存；无 AI 时用内置释义兜底）
  const explainWord = async (w) => {
    if (aiCache[w]) return aiCache[w];
    setLoading(true);
    try {
      const reply = await chatMessage(
        `请用中文解释阿拉伯语单词「${w}」：词义、词根、词性，一句话即可。`,
        'flash_' + Date.now()
      );
      const c = { ...aiCache, [w]: reply };
      const ck = Object.keys(c);
      if (ck.length > 300) {
        const sorted = ck.sort();
        for (let i = 0; i < sorted.length - 300; i++) delete c[sorted[i]];
      }
      setAiCache(c);
      AsyncStorage.setItem(AI_CACHE_KEY, JSON.stringify(c)).catch(() => {});
      setLoading(false);
      return reply;
    } catch (e) {
      setLoading(false);
      return null;
    }
  };

  const answer = async (isKnown) => {
    const item = deck[idx];
    if (!item) return;
    // 记录到 SRS：认识→升盒；不会→加入队列并降盒
    if (item.kind === 's') {
      await SRS.add('s', item.card.a);
      await SRS.answer('s', item.card.a, isKnown);
    } else if (item.word) {
      await SRS.add('w', item.word);
      await SRS.answer('w', item.word, isKnown);
    }
    if (isKnown) {
      setKnown(known + 1);
    } else {
      setAgain((a) => [...a, item]);
    }
    setFlipped(false);
    setAiMean(null);
    setAnimVal(0);
    SRS.counts().then((c) => setDueCount(c.due));
    if (idx + 1 >= deck.length) setDone(true);
    else setIdx(idx + 1);
  };

  const [aiMean, setAiMean] = useState(null);
  const setAnimVal = (v) => { anim.setValue(v); };

  const restart = () => startGame(mode);

  const item = deck[idx];
  const front = item ? (item.kind === 's' ? item.card.a : item.word) : '';
  let backCn = null;
  let backEn = null;
  if (item) {
    if (item.kind === 's') { backCn = item.card.c; backEn = item.card.e; }
    else { backCn = item.cn || aiMean || (VOCAB.find((v) => v.w === item.word) || {}).cn || '—'; backEn = item.en || (VOCAB.find((v) => v.w === item.word) || {}).en || ''; }
  }

  const rotateY = anim.interpolate({ inputRange: [0, 1], outputRange: ['0deg', '180deg'] });
  const rotateYBack = anim.interpolate({ inputRange: [0, 1], outputRange: ['180deg', '360deg'] });

  const speakFront = () => { if (front) ttsSpeak(front, { lang: 'ar-SA', rate: 0.7 }); };

  return (
    <Modal visible={visible} animationType="slide" onRequestClose={onClose}>
      <View style={styles.root}>
        <ArchHeader title="🃏 闪卡" subtitle="" zh="句子卡 · 单词卡 · 间隔复习" />

        {deck.length === 0 ? (
          <View style={styles.startWrap}>
            <Text style={styles.startTitle}>选择卡片模式</Text>
            {dueCount > 0 ? (
              <TouchableOpacity style={[styles.modeBtn, styles.reviewModeBtn]} onPress={() => startGame('review')}>
                <Text style={styles.modeIcon}>📅</Text>
                <View style={{ flex: 1 }}>
                  <Text style={styles.modeTitle}>间隔复习</Text>
                  <Text style={styles.modeDesc}>按遗忘曲线复习到期内容 · 今天有 {dueCount} 张到期</Text>
                </View>
                <View style={styles.badge}><Text style={styles.badgeTxt}>{dueCount}</Text></View>
              </TouchableOpacity>
            ) : (
              <TouchableOpacity style={styles.modeBtn} onPress={() => startGame('review')}>
                <Text style={styles.modeIcon}>📅</Text>
                <View style={{ flex: 1 }}>
                  <Text style={styles.modeTitle}>间隔复习</Text>
                  <Text style={styles.modeDesc}>今天的复习已完成 · 答题积累新内容</Text>
                </View>
                <Text style={styles.modeGo}>›</Text>
              </TouchableOpacity>
            )}
            <TouchableOpacity style={styles.modeBtn} onPress={() => startGame('sentence')}>
              <Text style={styles.modeIcon}>📖</Text>
              <View style={{ flex: 1 }}>
                <Text style={styles.modeTitle}>句子闪卡</Text>
                <Text style={styles.modeDesc}>12 张随机句子 · 正面阿语 · 翻面看中英翻译</Text>
              </View>
              <Text style={styles.modeGo}>›</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.modeBtn} onPress={() => startGame('word')}>
              <Text style={styles.modeIcon}>🔤</Text>
              <View style={{ flex: 1 }}>
                <Text style={styles.modeTitle}>单词闪卡</Text>
                <Text style={styles.modeDesc}>高频词 · 内置释义离线可用 · 点 AI 深度解析</Text>
              </View>
              <Text style={styles.modeGo}>›</Text>
            </TouchableOpacity>
            <Text style={styles.hint}>会 / 不会 按钮记录掌握情况，不会的自动进入间隔复习队列（1/3/7/15/30 天）</Text>
          </View>
        ) : done ? (
          <View style={styles.startWrap}>
            <Text style={styles.doneEmoji}>🎉</Text>
            <Text style={styles.doneTitle}>本局完成！</Text>
            <Text style={styles.doneStat}>认识 {known} / {deck.length} 张</Text>
            <Text style={styles.doneStat2}>待复习 {again.length} 张 · 已按遗忘曲线排期</Text>
            {again.length > 0 ? (
              <TouchableOpacity style={styles.reviewBtn} onPress={() => { setDeck(again); setIdx(0); setAgain([]); setKnown(0); setDone(false); setFlipped(false); }}>
                <Text style={styles.reviewTxt}>🔄 重来这 {again.length} 张</Text>
              </TouchableOpacity>
            ) : null}
            <TouchableOpacity style={styles.reviewBtn} onPress={restart}>
              <Text style={styles.reviewTxt}>▶ 再来一局</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.closeBtn} onPress={onClose}>
              <Text style={styles.closeTxt}>✕ 关闭</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <View style={styles.gameWrap}>
            <Text style={styles.progress}>{idx + 1} / {deck.length}{mode === 'review' ? ' · 复习' : ''}</Text>

            <TouchableOpacity style={styles.cardWrap} onPress={flip} activeOpacity={0.9}>
              <Animated.View style={[styles.card, { transform: [{ rotateY }] }]}>
                <Text style={styles.cardFrontAr}>{front}</Text>
                <Text style={styles.cardHint}>👆 点击翻面</Text>
              </Animated.View>
              <Animated.View style={[styles.card, styles.cardBack, { transform: [{ rotateY: rotateYBack }] }]}>
                <Text style={styles.cardBackCn}>🇨🇳 {backCn}</Text>
                {backEn ? <Text style={styles.cardBackEn}>🇬🇧 {backEn}</Text> : null}
                {item && item.kind === 's' && item.card.py ? <Text style={styles.cardBackPy}>🗣 {item.card.py}</Text> : null}
                <View style={styles.backBtns}>
                  <TouchableOpacity style={styles.backSpeakBtn} onPress={() => { if (backCn) ttsSpeak(backCn, { lang: 'zh-CN', rate: 0.85 }); }}>
                    <Text style={styles.backSpeakTxt}>🔊 中文</Text>
                  </TouchableOpacity>
                  {backEn ? (
                    <TouchableOpacity style={styles.backSpeakBtn} onPress={() => { if (backEn) ttsSpeak(backEn, { lang: 'en-US', rate: 0.85 }); }}>
                      <Text style={styles.backSpeakTxt}>🔊 英文</Text>
                    </TouchableOpacity>
                  ) : null}
                  {item && item.kind === 'w' ? (
                    <TouchableOpacity
                      style={styles.backSpeakBtn}
                      onPress={async () => {
                        await WordBook.add(item.word);
                        Alert.alert('✅ 已收进生词本', `${item.word} 已保存，随时可复习`);
                      }}
                    >
                      <Text style={styles.backSpeakTxt}>📌 收词</Text>
                    </TouchableOpacity>
                  ) : null}
                </View>
                <Text style={styles.cardHint}>👆 点击翻回</Text>
              </Animated.View>
            </TouchableOpacity>

            <View style={styles.actionRow}>
              <TouchableOpacity style={styles.speakBtn} onPress={speakFront}>
                <Text style={styles.speakTxt}>🔊 朗读</Text>
              </TouchableOpacity>
              {item && item.kind === 'w' ? (
                <TouchableOpacity style={styles.speakBtn} onPress={async () => {
                  const r = await explainWord(item.word);
                  if (r) setAiMean(r);
                }}>
                  <Text style={styles.speakTxt}>🤖 AI 解析{loading ? '…' : ''}</Text>
                </TouchableOpacity>
              ) : null}
            </View>

            <View style={styles.answerRow}>
              <TouchableOpacity style={[styles.answerBtn, styles.againBtn]} onPress={() => answer(false)}>
                <Text style={styles.answerTxt}>❌ 不会</Text>
              </TouchableOpacity>
              <TouchableOpacity style={[styles.answerBtn, styles.knownBtn]} onPress={() => answer(true)}>
                <Text style={styles.answerTxt}>✅ 认识</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: Colors.cream },
  startWrap: { flex: 1, padding: 24, justifyContent: 'center' },
  startTitle: { fontSize: 17, fontWeight: '800', color: Colors.greenDark, textAlign: 'center', marginBottom: 18 },
  modeBtn: {
    flexDirection: 'row', alignItems: 'center', backgroundColor: Colors.white,
    borderRadius: Radius.lg, padding: 16, marginBottom: 12,
    borderWidth: 1, borderColor: 'rgba(201,168,76,0.25)',
  },
  reviewModeBtn: { borderColor: Colors.gold, borderWidth: 1.5, backgroundColor: '#fdf9ee' },
  modeIcon: { fontSize: 28, marginRight: 14 },
  modeTitle: { fontSize: 14.5, fontWeight: '700', color: Colors.ink },
  modeDesc: { fontSize: 10.5, color: Colors.muted, marginTop: 3, lineHeight: 16 },
  modeGo: { fontSize: 22, color: Colors.gold },
  badge: {
    minWidth: 26, height: 26, borderRadius: 13, backgroundColor: Colors.gold,
    alignItems: 'center', justifyContent: 'center', paddingHorizontal: 6,
  },
  badgeTxt: { fontSize: 12, fontWeight: '800', color: '#fff' },
  hint: { fontSize: 10.5, color: Colors.muted, textAlign: 'center', marginTop: 10, lineHeight: 16 },
  gameWrap: { flex: 1, padding: 20, alignItems: 'center' },
  progress: { fontSize: 13, fontWeight: '800', color: Colors.goldDark, marginBottom: 14 },
  cardWrap: { width: '100%', height: 300, marginBottom: 16 },
  card: {
    position: 'absolute', width: '100%', height: '100%', borderRadius: Radius.xl,
    backgroundColor: Colors.greenDark, padding: 24, alignItems: 'center', justifyContent: 'center',
    backfaceVisibility: 'hidden',
  },
  cardBack: { backgroundColor: Colors.white, borderWidth: 1.5, borderColor: Colors.gold },
  cardFrontAr: {
    fontFamily: 'serif', fontSize: 24, fontWeight: '800', color: Colors.goldLight,
    textAlign: 'center', writingDirection: 'rtl', lineHeight: 40,
  },
  cardBackCn: { fontSize: 16, color: Colors.ink, textAlign: 'center', lineHeight: 26 },
  cardBackEn: { fontSize: 12, color: '#5a7f9e', textAlign: 'center', marginTop: 8, lineHeight: 20 },
  cardBackPy: { fontSize: 11, color: '#8a8578', fontStyle: 'italic', textAlign: 'center', marginTop: 6 },
  backBtns: { flexDirection: 'row', gap: 10, marginTop: 14 },
  backSpeakBtn: {
    paddingHorizontal: 13, paddingVertical: 6, borderRadius: 13,
    backgroundColor: 'rgba(26,92,74,0.08)', borderWidth: 1, borderColor: 'rgba(26,92,74,0.3)',
  },
  backSpeakTxt: { fontSize: 10, fontWeight: '700', color: Colors.green },
  cardHint: { position: 'absolute', bottom: 16, fontSize: 10, color: 'rgba(255,255,255,0.5)' },
  actionRow: { flexDirection: 'row', gap: 10, marginBottom: 18 },
  speakBtn: {
    paddingHorizontal: 20, paddingVertical: 9, borderRadius: 18,
    backgroundColor: 'rgba(26,92,74,0.1)', borderWidth: 1, borderColor: 'rgba(26,92,74,0.3)',
  },
  speakTxt: { fontSize: 12, fontWeight: '700', color: Colors.green },
  answerRow: { flexDirection: 'row', gap: 14, width: '100%' },
  answerBtn: { flex: 1, paddingVertical: 15, borderRadius: Radius.md, alignItems: 'center' },
  againBtn: { backgroundColor: 'rgba(192,57,43,0.1)', borderWidth: 1, borderColor: 'rgba(192,57,43,0.35)' },
  knownBtn: { backgroundColor: 'rgba(26,138,92,0.12)', borderWidth: 1, borderColor: 'rgba(26,138,92,0.4)' },
  answerTxt: { fontSize: 14, fontWeight: '800', color: Colors.ink },
  doneEmoji: { fontSize: 52, textAlign: 'center' },
  doneTitle: { fontSize: 20, fontWeight: '800', color: Colors.greenDark, textAlign: 'center', marginTop: 8 },
  doneStat: { fontSize: 15, color: Colors.ink, textAlign: 'center', marginTop: 12 },
  doneStat2: { fontSize: 13, color: Colors.muted, textAlign: 'center', marginTop: 4, marginBottom: 20 },
  reviewBtn: {
    backgroundColor: Colors.greenDark, borderRadius: Radius.md, paddingVertical: 13,
    alignItems: 'center', marginBottom: 10,
  },
  reviewTxt: { fontSize: 13, fontWeight: '700', color: Colors.goldLight },
  closeBtn: { alignItems: 'center', padding: 10, marginTop: 4 },
  closeTxt: { fontSize: 12, color: Colors.green },
});
