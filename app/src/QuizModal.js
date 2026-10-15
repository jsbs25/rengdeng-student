// 测验模块：10 题句子选择题（阿语→中文 4 选 1）
import React, { useState, useEffect } from 'react';
import {
  View, Text, Modal, TouchableOpacity, StyleSheet, ScrollView, Alert,
} from 'react-native';
import * as Speech from 'expo-speech';
import { speak as ttsSpeak } from './tts';
import { Colors, Radius } from './theme';
import { ArchHeader } from './components';
import DATA from './data';
import { loadData } from './api';
import { useStudyTimer } from './useStudyTimer';
import { SRS } from './srs';

export default function QuizModal({ visible, onClose }) {
  useStudyTimer(visible);
  const [questions, setQuestions] = useState([]);
  const [idx, setIdx] = useState(0);
  const [score, setScore] = useState(0);
  const [picked, setPicked] = useState(null); // 用户选的选项文本
  const [done, setDone] = useState(false);

  const start = async () => {
    const data = await loadData();
    const all = Object.values(data.cats || {}).flat().filter((s) => s.a && s.c);
    const shuffled = [...all].sort(() => Math.random() - 0.5);
    const qs = shuffled.slice(0, 10).map((correct) => {
      const opts = [correct];
      while (opts.length < 4) {
        const r = all[Math.floor(Math.random() * all.length)];
        if (!opts.includes(r)) opts.push(r);
      }
      opts.sort(() => Math.random() - 0.5);
      return { correct, opts };
    });
    setQuestions(qs);
    setIdx(0);
    setScore(0);
    setPicked(null);
    setDone(false);
  };

  useEffect(() => {
    if (visible) start();
  }, [visible]);

  const answer = (opt) => {
    if (picked) return;
    setPicked(opt.c);
    if (opt === questions[idx].correct) setScore(score + 1);
    else SRS.add('s', questions[idx].correct.a); // 错题自动进遗忘曲线复习
    setTimeout(() => {
      if (idx + 1 >= questions.length) setDone(true);
      else { setIdx(idx + 1); setPicked(null); }
    }, 800);
  };

  const speakQ = () => {
    if (questions[idx]) ttsSpeak(questions[idx].correct.a, { lang: 'ar-SA', rate: 0.65 });
  };

  return (
    <Modal visible={visible} animationType="slide" onRequestClose={onClose}>
      <View style={styles.root}>
        <ArchHeader title="📝 测验" subtitle="AL-IKHTIBĀR" zh="句子选择 · 每日 10 题" />

        {done ? (
          <View style={styles.doneWrap}>
            <Text style={styles.doneEmoji}>🎉</Text>
            <Text style={styles.doneTitle}>测验完成！</Text>
            <Text style={styles.doneScore}>得分：{score} / {questions.length}</Text>
            <Text style={styles.doneHint}>❌ 错题已自动加入间隔复习（闪卡→间隔复习可复习）</Text>
            <TouchableOpacity style={styles.reBtn} onPress={start}>
              <Text style={styles.reTxt}>▶ 再来一局</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.reBtn} onPress={onClose}>
              <Text style={styles.reTxt}>📅 去闪卡复习 →</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.closeBtn} onPress={onClose}>
              <Text style={styles.closeTxt}>✕ 关闭</Text>
            </TouchableOpacity>
          </View>
        ) : questions.length > 0 ? (
          <ScrollView style={styles.body} contentContainerStyle={{ padding: 16, paddingBottom: 40 }}>
            <Text style={styles.progress}>{idx + 1} / {questions.length} · 得分 {score}</Text>
            <View style={styles.qCard}>
              <Text style={styles.qAr}>{questions[idx].correct.a}</Text>
              <TouchableOpacity style={styles.speakBtn} onPress={speakQ}>
                <Text style={styles.speakTxt}>🔊 听题</Text>
              </TouchableOpacity>
            </View>
            <Text style={styles.hint}>请选择正确的中文翻译</Text>
            {questions[idx].opts.map((o, i) => {
              const isCorrect = o === questions[idx].correct;
              const isPicked = picked === o.c;
              let bg = 'rgba(255,255,255,0.9)';
              let border = 'rgba(201,168,76,0.4)';
              if (picked) {
                if (isCorrect) { bg = 'rgba(26,138,92,0.15)'; border = '#1a8a5c'; }
                else if (isPicked) { bg = 'rgba(192,57,43,0.12)'; border = '#c0392b'; }
              }
              return (
                <TouchableOpacity
                  key={i}
                  style={[styles.opt, { backgroundColor: bg, borderColor: border }]}
                  onPress={() => answer(o)}
                >
                  <Text style={styles.optTxt}>{o.c}</Text>
                </TouchableOpacity>
              );
            })}
          </ScrollView>
        ) : null}
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: Colors.cream },
  body: { flex: 1 },
  progress: { fontSize: 13, fontWeight: '800', color: Colors.goldDark, textAlign: 'center', marginBottom: 12 },
  qCard: {
    backgroundColor: Colors.greenDark, borderRadius: Radius.lg, padding: 22, alignItems: 'center',
    borderWidth: 1, borderColor: 'rgba(201,168,76,0.3)',
  },
  qAr: {
    fontFamily: 'serif', fontSize: 18, fontWeight: '700', color: Colors.goldLight,
    textAlign: 'center', lineHeight: 32, writingDirection: 'rtl',
  },
  speakBtn: { marginTop: 12, paddingHorizontal: 16, paddingVertical: 7, borderRadius: 15, backgroundColor: 'rgba(232,212,139,0.15)', borderWidth: 1, borderColor: 'rgba(232,212,139,0.35)' },
  speakTxt: { fontSize: 11, fontWeight: '700', color: Colors.goldLight },
  hint: { fontSize: 11, color: Colors.muted, textAlign: 'center', marginVertical: 12 },
  opt: {
    paddingVertical: 14, paddingHorizontal: 16, borderRadius: Radius.md, marginBottom: 10,
    borderWidth: 1.5, alignItems: 'center',
  },
  optTxt: { fontSize: 13.5, color: Colors.ink },
  doneWrap: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24 },
  doneEmoji: { fontSize: 52 },
  doneTitle: { fontSize: 20, fontWeight: '800', color: Colors.greenDark, marginTop: 10 },
  doneHint: { fontSize: 10.5, color: Colors.muted, marginTop: 6, marginBottom: 14, textAlign: 'center' },
  doneScore: { fontSize: 15, color: Colors.ink, marginTop: 10 },
  reBtn: { backgroundColor: Colors.greenDark, borderRadius: Radius.md, paddingVertical: 13, paddingHorizontal: 40, marginTop: 24 },
  reTxt: { fontSize: 13, fontWeight: '700', color: Colors.goldLight },
  closeBtn: { marginTop: 12, padding: 10 },
  closeTxt: { fontSize: 12, color: Colors.green },
});
