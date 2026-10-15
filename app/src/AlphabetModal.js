// 字母入门：28 字母学习 + 四种书写形式 + 小测验
import React, { useState } from 'react';
import {
  View, Text, Modal, FlatList, TouchableOpacity, StyleSheet,
} from 'react-native';
import { speak as ttsSpeak } from './tts';
import { Colors, Radius } from './theme';
import { ArchHeader } from './components';
import ALPHABET from './alphabetData';

const FORM_LABELS = ['独立', '词首', '词中', '词尾'];

export default function AlphabetModal({ visible, onClose }) {
  const [sel, setSel] = useState(null); // 选中的字母
  const [quizOn, setQuizOn] = useState(false);
  const [quiz, setQuiz] = useState([]);
  const [qIdx, setQIdx] = useState(0);
  const [qScore, setQScore] = useState(0);
  const [qWrong, setQWrong] = useState(0);
  const [qDone, setQDone] = useState(false);

  const startQuiz = () => {
    const qs = [];
    const pool = [...ALPHABET];
    for (let i = pool.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [pool[i], pool[j]] = [pool[j], pool[i]];
    }
    for (let k = 0; k < 10; k++) {
      const correct = pool[k];
      const opts = [correct];
      while (opts.length < 4) {
        const r = ALPHABET[Math.floor(Math.random() * ALPHABET.length)];
        if (!opts.includes(r)) opts.push(r);
      }
      for (let x = opts.length - 1; x > 0; x--) {
        const y = Math.floor(Math.random() * (x + 1));
        [opts[x], opts[y]] = [opts[y], opts[x]];
      }
      qs.push({ letter: correct, opts });
    }
    setQuiz(qs);
    setQIdx(0);
    setQScore(0);
    setQWrong(0);
    setQDone(false);
    setQuizOn(true);
  };

  const answerQuiz = (opt) => {
    const q = quiz[qIdx];
    if (opt.ar === q.letter.ar) setQScore((s) => s + 1);
    else setQWrong((w) => w + 1);
    if (qIdx + 1 >= quiz.length) setQDone(true);
    else setQIdx(qIdx + 1);
  };

  const speak = (text, rate = 0.6) => { if (text) ttsSpeak(text, { lang: 'ar-SA', rate }); };

  const close = () => {
    setSel(null);
    setQuizOn(false);
    onClose();
  };

  return (
    <Modal visible={visible} animationType="slide" onRequestClose={close}>
      <View style={styles.root}>
        <ArchHeader title="🔤 字母入门" subtitle="" zh="28 字母 · 书写形式 · 认读测验" />
        <View style={styles.topRow}>
          <Text style={styles.topTxt}>📖 点击字母学习发音与写法 · 不连写的字母（ا د ذ ر ز و）只有两种形态</Text>
          <TouchableOpacity style={styles.quizBtn} onPress={startQuiz}>
            <Text style={styles.quizTxt}>📝 认读测验</Text>
          </TouchableOpacity>
        </View>

        {quizOn ? (
          <View style={styles.quizWrap}>
            {!qDone ? (
              <>
                <Text style={styles.qProg}>{qIdx + 1} / 10 · 得分 {qScore}</Text>
                <View style={styles.qCard}>
                  <Text style={styles.qLetter}>{quiz[qIdx].letter.ar}</Text>
                  <Text style={styles.qHint}>这个字母怎么读？</Text>
                  <TouchableOpacity style={styles.qSpeak} onPress={() => speak(quiz[qIdx].letter.ar)}>
                    <Text style={styles.qSpeakTxt}>🔊 听发音</Text>
                  </TouchableOpacity>
                </View>
                {quiz[qIdx].opts.map((o) => (
                  <TouchableOpacity key={o.ar} style={styles.qOpt} onPress={() => answerQuiz(o)}>
                    <Text style={styles.qOptTxt}>{o.name} · {o.cn}</Text>
                  </TouchableOpacity>
                ))}
              </>
            ) : (
              <View style={styles.qDone}>
                <Text style={styles.qDoneEmoji}>🎉</Text>
                <Text style={styles.qDoneTitle}>测验完成！</Text>
                <Text style={styles.qDoneStat}>答对 {qScore} / 10{qWrong ? ` · 错 ${qWrong} 题` : ''}</Text>
                <TouchableOpacity style={styles.qBtn} onPress={startQuiz}>
                  <Text style={styles.qBtnTxt}>▶ 再来一次</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.qBtn} onPress={() => { setQuizOn(false); setSel(null); }}>
                  <Text style={styles.qBtnTxt}>← 返回字母表</Text>
                </TouchableOpacity>
              </View>
            )}
          </View>
        ) : !sel ? (
          <FlatList
            data={ALPHABET}
            keyExtractor={(a) => a.ar}
            numColumns={4}
            contentContainerStyle={{ padding: 14, paddingBottom: 30 }}
            renderItem={({ item }) => (
              <TouchableOpacity style={styles.cell} onPress={() => { setSel(item); setQuizOn(false); }}>
                <Text style={styles.cellAr}>{item.ar}</Text>
                <Text style={styles.cellCn}>{item.cn}</Text>
              </TouchableOpacity>
            )}
          />
        ) : (
          <View style={styles.detail}>
            <TouchableOpacity style={styles.backBtn} onPress={() => setSel(null)}>
              <Text style={styles.backTxt}>← 全部字母</Text>
            </TouchableOpacity>
            <Text style={styles.dAr}>{sel.ar}</Text>
            <Text style={styles.dName}>{sel.name} · {sel.cn} · {sel.tr}</Text>
            <TouchableOpacity style={styles.dSpeak} onPress={() => speak(sel.name)}>
              <Text style={styles.dSpeakTxt}>🔊 读字母名</Text>
            </TouchableOpacity>

            <Text style={styles.formTitle}>✍️ 四种书写形式</Text>
            <View style={styles.formRow}>
              {sel.forms.map((f, i) => (
                <View key={i} style={styles.formCell}>
                  <Text style={styles.formAr}>{f}</Text>
                  <Text style={styles.formLb}>{FORM_LABELS[i]}</Text>
                </View>
              ))}
            </View>

            <Text style={styles.formTitle}>📖 示例词</Text>
            {sel.ex.map((e, i) => (
              <TouchableOpacity key={i} style={styles.exRow} onPress={() => speak(e.w, 0.55)}>
                <Text style={styles.exAr}>{e.w}</Text>
                <Text style={styles.exCn}>{e.cn}</Text>
                <Text style={styles.exPlay}>🔊</Text>
              </TouchableOpacity>
            ))}
            <Text style={styles.dHint}>提示：大多数字母必须与前后字母连写；ا د ذ ر ز و 只和前面的字母连写。</Text>
          </View>
        )}
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: Colors.cream },
  topRow: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 16, paddingTop: 12, gap: 10 },
  topTxt: { flex: 1, fontSize: 10.5, color: Colors.muted, lineHeight: 16 },
  quizBtn: { paddingHorizontal: 14, paddingVertical: 8, borderRadius: 14, backgroundColor: Colors.greenDark },
  quizTxt: { fontSize: 11, fontWeight: '700', color: Colors.goldLight },
  cell: {
    width: '23%', margin: '1%', aspectRatio: 1, borderRadius: Radius.md,
    backgroundColor: Colors.white, alignItems: 'center', justifyContent: 'center',
    borderWidth: 1, borderColor: 'rgba(201,168,76,0.25)',
  },
  cellAr: { fontFamily: 'serif', fontSize: 26, fontWeight: '800', color: Colors.greenDark },
  cellCn: { fontSize: 8.5, color: Colors.muted, marginTop: 2 },
  detail: { flex: 1, padding: 20, alignItems: 'center' },
  backBtn: { alignSelf: 'flex-start', padding: 6 },
  backTxt: { fontSize: 12, color: Colors.green, fontWeight: '600' },
  dAr: { fontFamily: 'serif', fontSize: 72, fontWeight: '800', color: Colors.greenDark, marginTop: 6 },
  dName: { fontSize: 13, color: Colors.ink, marginTop: 6 },
  dSpeak: { marginTop: 12, paddingHorizontal: 18, paddingVertical: 8, borderRadius: 16, backgroundColor: 'rgba(26,92,74,0.1)', borderWidth: 1, borderColor: 'rgba(26,92,74,0.3)' },
  dSpeakTxt: { fontSize: 11, fontWeight: '700', color: Colors.green },
  formTitle: { fontSize: 13, fontWeight: '800', color: Colors.greenDark, marginTop: 22, alignSelf: 'flex-start' },
  formRow: { flexDirection: 'row', gap: 10, marginTop: 10, width: '100%' },
  formCell: { flex: 1, backgroundColor: Colors.white, borderRadius: Radius.md, paddingVertical: 14, alignItems: 'center', borderWidth: 1, borderColor: 'rgba(201,168,76,0.25)' },
  formAr: { fontFamily: 'serif', fontSize: 30, fontWeight: '800', color: Colors.greenDark },
  formLb: { fontSize: 9, color: Colors.muted, marginTop: 4 },
  exRow: {
    flexDirection: 'row', alignItems: 'center', width: '100%', marginTop: 8,
    backgroundColor: Colors.white, borderRadius: Radius.md, padding: 12,
    borderWidth: 1, borderColor: 'rgba(201,168,76,0.2)',
  },
  exAr: { fontFamily: 'serif', fontSize: 18, fontWeight: '700', color: Colors.greenDark, flex: 1, textAlign: 'right', writingDirection: 'rtl' },
  exCn: { fontSize: 11, color: Colors.ink, marginRight: 10 },
  exPlay: { fontSize: 13 },
  dHint: { fontSize: 9.5, color: Colors.muted, marginTop: 18, lineHeight: 15, textAlign: 'center' },
  quizWrap: { flex: 1, padding: 20 },
  qProg: { fontSize: 12, fontWeight: '800', color: Colors.goldDark, textAlign: 'center', marginBottom: 14 },
  qCard: { backgroundColor: Colors.greenDark, borderRadius: Radius.xl, padding: 28, alignItems: 'center', marginBottom: 14 },
  qLetter: { fontFamily: 'serif', fontSize: 64, fontWeight: '800', color: Colors.goldLight },
  qHint: { fontSize: 11, color: 'rgba(255,255,255,0.75)', marginTop: 6 },
  qSpeak: { marginTop: 10, paddingHorizontal: 14, paddingVertical: 6, borderRadius: 14, backgroundColor: 'rgba(232,212,139,0.15)', borderWidth: 1, borderColor: 'rgba(232,212,139,0.4)' },
  qSpeakTxt: { fontSize: 10, fontWeight: '700', color: Colors.goldLight },
  qOpt: { backgroundColor: Colors.white, borderRadius: Radius.md, padding: 14, marginBottom: 8, borderWidth: 1, borderColor: 'rgba(201,168,76,0.25)' },
  qOptTxt: { fontSize: 13, fontWeight: '600', color: Colors.ink, textAlign: 'center' },
  qDone: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  qDoneEmoji: { fontSize: 52 },
  qDoneTitle: { fontSize: 20, fontWeight: '800', color: Colors.greenDark, marginTop: 8 },
  qDoneStat: { fontSize: 14, color: Colors.ink, marginTop: 10, marginBottom: 24 },
  qBtn: { backgroundColor: Colors.greenDark, borderRadius: Radius.md, paddingVertical: 13, paddingHorizontal: 40, marginBottom: 10 },
  qBtnTxt: { fontSize: 13, fontWeight: '700', color: Colors.goldLight },
});
