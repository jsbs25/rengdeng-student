// 日常对话模块：留学生场景对话（有来有往 · 每天 10 场景 100 句轮换）
import React, { useState, useRef } from 'react';
import {
  View, Text, Modal, FlatList, TouchableOpacity, StyleSheet, Alert,
} from 'react-native';
import * as Speech from 'expo-speech';
import { speak as ttsSpeak } from './tts';
import { AudioModule, RecordingPresets, requestRecordingPermissionsAsync } from 'expo-audio';
import { getApiBase } from './api';
import { Colors, Radius } from './theme';
import { ArchHeader } from './components';
import DATA from './data';
const DIALOGUES = DATA.dialogues || [];
import { SRS } from './srs';
import { useStudyTimer } from './useStudyTimer';

// 按日期 seed 选今日场景（稳定不重复）
function todayScenes() {
  const d = new Date();
  const seed = d.getFullYear() * 10000 + (d.getMonth() + 1) * 100 + d.getDate();
  const all = [...DIALOGUES];
  for (let i = all.length - 1; i > 0; i--) {
    const j = (seed + i * 7) % (i + 1);
    [all[i], all[j]] = [all[j], all[i]];
  }
  return all.slice(0, 10);
}

export default function DialogModal({ visible, onClose }) {
  useStudyTimer(visible);
  React.useEffect(() => {
    if (!visible) setScene(null);
  }, [visible]);
  const [scenes, setScenes] = useState(todayScenes());
  const [scene, setScene] = useState(null); // 当前对话场景
  const [hideCn, setHideCn] = useState(false);

  const speakLine = (text, idx) => {
    Speech.stop();
    ttsSpeak(text, {
      lang: 'ar-SA', rate: 0.7,
      onStart: () => setPlayingIdx(idx),
      onDone: () => setPlayingIdx(null),
      onStopped: () => setPlayingIdx(null),
    });
  };
  const [playingIdx, setPlayingIdx] = useState(null);
  const stopRef = useRef(false);
  const [gradeRec, setGradeRec] = useState(null); // 正在跟读的句子
  const [gradeRes, setGradeRes] = useState(null); // {key, score, heard}

  // 对话句跟读评分（whisper 识别比对）
  const gradeLine = async (text, key) => {
    if (gradeRec === key) {
      try { await gradeRecRef.current?.stop(); } catch (e) {}
      const uri = gradeRecRef.current && gradeRecRef.current.uri;
      if (!uri) { setGradeRec(null); return; }
      try {
        const fd = new FormData();
        fd.append('file', { uri, name: 'audio.m4a', type: 'audio/m4a' });
        const res = await fetch((await getApiBase()) + '/api/asr', {
          method: 'POST', headers: { 'X-ASR-Lang': 'ar' }, body: fd,
        });
        const d = await res.json();
        const heard = (d.text || '').trim();
        // 词级比对（复用 normAr 逻辑）
        const norm = (t) => String(t || '').replace(/[\u064B-\u0652\u0670\u0640\u06D6-\u06ED\u0610-\u061A]/g, '').replace(/[^\u0600-\u06FF\s]/g, ' ').replace(/\s+/g, ' ').trim();
        const tw = norm(text).split(' ').filter(Boolean);
        const hw = norm(heard).split(' ').filter(Boolean);
        let matched = 0;
        const hs = new Set(hw);
        tw.forEach((w) => { if (hs.has(w)) matched++; });
        const score = tw.length ? Math.round((matched / tw.length * 0.7 + (hw.length ? matched / hw.length : 0) * 0.3) * 100) : 0;
        setGradeRes({ key, score, heard: heard || '（没有听清）' });
      } catch (e) {
        setGradeRes({ key, score: 0, heard: '（需连接电脑服务器）' });
      }
      setGradeRec(null);
      return;
    }
    try {
      stopRef.current = false;
      Speech.stop();
      setPlayingIdx(null);
      const perm = await requestRecordingPermissionsAsync();
      if (!perm.granted) { Alert.alert('权限', '需要麦克风权限'); return; }
      const rec = new AudioModule.AudioRecorder(RecordingPresets.HIGH_QUALITY);
      await rec.prepareToRecordAsync();
      rec.record();
      gradeRecRef.current = rec;
      setGradeRes(null);
      setGradeRec(key);
    } catch (e) {
      Alert.alert('录音失败', String(e));
    }
  };
  const gradeRecRef = useRef(null);

  const playAll = async () => {
    if (!scene) return;
    if (stopRef.current) { // 再点 = 停止
      stopRef.current = false;
      Speech.stop();
      setPlayingIdx(null);
      return;
    }
    stopRef.current = true;
    Speech.stop();
    const lines = scene.dialogue.flatMap((r, i) => [
      { t: r.a, k: i * 2 }, { t: r.b, k: i * 2 + 1 },
    ]);
    for (const l of lines) {
      if (!stopRef.current || !visible) { stopRef.current = false; break; }
      setPlayingIdx(l.k);
      await new Promise((resolve) => {
        ttsSpeak(l.t, {
          lang: 'ar-SA', rate: 0.7,
          onDone: resolve, onStopped: resolve, onError: resolve,
        });
      });
    }
    stopRef.current = false;
    setPlayingIdx(null);
  };

  const [playingAll, setPlayingAll] = useState(false);

  const playAllScenes = async () => {
    if (playingAll) { // 再点 = 停止
      stopRef.current = false;
      Speech.stop();
      setPlayingAll(false);
      setPlayingIdx(null);
      return;
    }
    stopRef.current = true;
    setPlayingAll(true);
    Speech.stop();
    for (const s of scenes) {
      if (!stopRef.current || !visible) break;
      for (const r of s.dialogue) {
        if (!stopRef.current || !visible) break;
        setPlayingIdx(-2); // 播放中标记
        await new Promise((resolve) => {
          ttsSpeak(r.a, { lang: 'ar-SA', rate: 0.7, onDone: resolve, onStopped: resolve, onError: resolve });
        });
        if (!stopRef.current || !visible) break;
        await new Promise((resolve) => {
          ttsSpeak(r.b, { lang: 'ar-SA', rate: 0.7, onDone: resolve, onStopped: resolve, onError: resolve });
        });
      }
    }
    stopRef.current = false;
    setPlayingAll(false);
    setPlayingIdx(null);
  };

  const nextDay = () => {
    // 模拟"第二天"：随机换一组
    const all = [...DIALOGUES];
    for (let i = all.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [all[i], all[j]] = [all[j], all[i]];
    }
    setScenes(all.slice(0, 10));
    setScene(null);
    setGradeRec(null);
    setGradeRes(null);
  };

  const totalLines = scenes.reduce((n, s) => n + (s.dialogue || []).length * 2, 0);

  return (
    <Modal visible={visible} animationType="slide" onRequestClose={() => { setScene(null); onClose(); }}>
      <View style={styles.root}>
        <ArchHeader
          title={scene ? `💬 ${scene.scene}` : '💬 日常对话'}
          subtitle=""
          zh={scene ? `${scene.scene_ar} · ${scene.dialogue.length} 轮有来有往` : `今日 ${scenes.length} 场景 · ${totalLines} 句有来有往`}
        />

        {!scene ? (
          <>
            <View style={styles.todayBar}>
              <Text style={styles.todayTxt}>📅 今日推荐 · {scenes.length} 场景 {totalLines} 句（每日自动轮换）</Text>
              <TouchableOpacity style={styles.nextBtn} onPress={playAllScenes}>
                <Text style={styles.nextTxt}>{playingAll ? '⏹ 停止' : '▶ 连续播放'}</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.nextBtn} onPress={nextDay}>
                <Text style={styles.nextTxt}>🔄 换一组</Text>
              </TouchableOpacity>
            </View>
            <FlatList
              data={scenes}
              keyExtractor={(s) => s.scene}
              contentContainerStyle={{ padding: 14, paddingBottom: 30 }}
              renderItem={({ item }) => (
                <TouchableOpacity style={styles.sceneItem} onPress={() => { setScene(item); setHideCn(false); }}>
                  <Text style={styles.sceneIcon}>{item.icon || '💬'}</Text>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.sceneName}>{item.scene}</Text>
                    <Text style={styles.sceneAr}>{item.scene_ar}</Text>
                  </View>
                  <Text style={styles.sceneGo}>{item.dialogue.length * 2} 句 ›</Text>
                </TouchableOpacity>
              )}
            />
          </>
        ) : (
          <>
            <View style={styles.toolRow}>
              <TouchableOpacity style={styles.toolBtn} onPress={playAll}>
                <Text style={styles.toolTxt}>{playingIdx !== null ? '⏹ 停止播放' : '🔊 整段播放'}</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.toolBtn} onPress={() => setHideCn(!hideCn)}>
                <Text style={styles.toolTxt}>{hideCn ? '👁 显示中文' : '🙈 隐藏中文'}</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.toolBtn} onPress={() => setScene(null)}>
                <Text style={styles.toolTxt}>← 列表</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.toolBtn}
                onPress={() => {
                  const cur = scenes.findIndex((s) => s.scene === scene.scene);
                  const next = scenes[(cur + 1) % scenes.length];
                  setScene(next);
                  setHideCn(false);
                }}
              >
                <Text style={styles.toolTxt}>下一场景 ›</Text>
              </TouchableOpacity>
            </View>
            <FlatList
              data={scene.dialogue}
              keyExtractor={(_, i) => String(i)}
              contentContainerStyle={{ padding: 14, paddingBottom: 30 }}
              renderItem={({ item, index }) => {
                const k0 = index * 2, k1 = index * 2 + 1;
                return (
                  <View style={styles.turn}>
                    <Text style={styles.turnLabel}>第 {index + 1} 轮</Text>
                    <TouchableOpacity style={[styles.bubble, styles.bubbleA, playingIdx === k0 && styles.bubbleOn]} onPress={() => speakLine(item.a, k0)}>
                      <Text style={styles.bubbleAr}>{item.a}</Text>
                      {!hideCn && item.a_cn ? <Text style={styles.bubbleCn}>🇨🇳 {item.a_cn}</Text> : null}
                      <Text style={styles.bubblePlay}>🔊</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                      style={styles.addReviewBtn}
                      onPress={async () => {
                        await SRS.add('s', item.a);
                        Alert.alert('✅ 已加入复习', '这句会按遗忘曲线提醒你复习（闪卡→间隔复习）');
                      }}
                    >
                      <Text style={styles.addReviewTxt}>📌 复习</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                      style={[styles.addReviewBtn, gradeRec === k0 && { backgroundColor: 'rgba(192,57,43,0.15)' }]}
                      onPress={() => gradeLine(item.a, k0)}
                    >
                      <Text style={styles.addReviewTxt}>{gradeRec === k0 ? '⏹ 停止' : '🎯 跟读'}</Text>
                    </TouchableOpacity>
                    {gradeRes && gradeRes.key === k0 ? (
                      <View style={[styles.gradeBox]}>
                        <Text style={[styles.gradeScore, gradeRes.score >= 80 && { color: Colors.green }]}>AI {gradeRes.score}分</Text>
                        <Text style={styles.gradeHeard} numberOfLines={1}>听到：{gradeRes.heard}</Text>
                      </View>
                    ) : null}
                    <TouchableOpacity style={[styles.bubble, styles.bubbleB, playingIdx === k1 && styles.bubbleOn]} onPress={() => speakLine(item.b, k1)}>
                      <Text style={styles.bubbleAr}>{item.b}</Text>
                      {!hideCn && item.b_cn ? <Text style={styles.bubbleCn}>🇨🇳 {item.b_cn}</Text> : null}
                      <Text style={styles.bubblePlay}>🔊</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                      style={[styles.addReviewBtn, styles.addReviewBtnB]}
                      onPress={async () => {
                        await SRS.add('s', item.b);
                        Alert.alert('✅ 已加入复习', '这句会按遗忘曲线提醒你复习（闪卡→间隔复习）');
                      }}
                    >
                      <Text style={styles.addReviewTxt}>📌 复习</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                      style={[styles.addReviewBtn, styles.addReviewBtnB, gradeRec === k1 && { backgroundColor: 'rgba(192,57,43,0.15)' }]}
                      onPress={() => gradeLine(item.b, k1)}
                    >
                      <Text style={styles.addReviewTxt}>{gradeRec === k1 ? '⏹ 停止' : '🎯 跟读'}</Text>
                    </TouchableOpacity>
                    {gradeRes && gradeRes.key === k1 ? (
                      <View style={[styles.gradeBox, styles.addReviewBtnB]}>
                        <Text style={[styles.gradeScore, gradeRes.score >= 80 && { color: Colors.green }]}>AI {gradeRes.score}分</Text>
                        <Text style={styles.gradeHeard} numberOfLines={1}>听到：{gradeRes.heard}</Text>
                      </View>
                    ) : null}
                  </View>
                );
              }}
            />
          </>
        )}
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: Colors.cream },
  todayBar: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 14, paddingTop: 12, gap: 8 },
  todayTxt: { flex: 1, fontSize: 10.5, color: Colors.muted, lineHeight: 15 },
  nextBtn: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 13, backgroundColor: Colors.greenDark },
  nextTxt: { fontSize: 10, fontWeight: '700', color: Colors.goldLight },
  sceneItem: {
    flexDirection: 'row', alignItems: 'center', backgroundColor: Colors.white,
    borderRadius: Radius.md, padding: 13, marginBottom: 8,
    borderWidth: 1, borderColor: 'rgba(201,168,76,0.2)',
  },
  sceneIcon: { fontSize: 24, marginRight: 12 },
  sceneName: { fontSize: 13.5, fontWeight: '700', color: Colors.ink },
  sceneAr: { fontSize: 10.5, color: Colors.goldDark, marginTop: 2, writingDirection: 'rtl', textAlign: 'left' },
  sceneGo: { fontSize: 11, color: Colors.green, fontWeight: '600' },
  toolRow: { flexDirection: 'row', gap: 8, paddingHorizontal: 14, paddingTop: 12 },
  toolBtn: {
    paddingHorizontal: 12, paddingVertical: 7, borderRadius: 14,
    backgroundColor: Colors.white, borderWidth: 1, borderColor: 'rgba(201,168,76,0.3)',
  },
  toolTxt: { fontSize: 10.5, fontWeight: '600', color: Colors.ink },
  turn: { marginBottom: 6 },
  turnLabel: { fontSize: 9, color: Colors.muted, marginBottom: 4, marginLeft: 4 },
  bubble: {
    maxWidth: '92%', padding: 11, borderRadius: 14, marginBottom: 7,
    borderWidth: 1, borderColor: 'rgba(201,168,76,0.18)',
  },
  bubbleA: { alignSelf: 'flex-start', backgroundColor: '#fff', borderTopLeftRadius: 4 },
  bubbleB: { alignSelf: 'flex-end', backgroundColor: '#fdf6e3', borderTopRightRadius: 4 },
  bubbleOn: { borderColor: Colors.gold, borderWidth: 1.5 },
  bubbleAr: { fontFamily: 'serif', fontSize: 15, fontWeight: '700', color: Colors.greenDark, writingDirection: 'rtl', lineHeight: 24 },
  bubbleCn: { fontSize: 10.5, color: Colors.muted, marginTop: 4 },
  bubblePlay: { position: 'absolute', top: 8, right: 10, fontSize: 11, opacity: 0.7 },
  addReviewBtn: { alignSelf: 'flex-start', marginLeft: 6, marginBottom: 6, paddingHorizontal: 10, paddingVertical: 4, borderRadius: 11, backgroundColor: 'rgba(26,92,74,0.08)', borderWidth: 1, borderColor: 'rgba(26,92,74,0.3)' },
  addReviewBtnB: { alignSelf: 'flex-end', marginLeft: 0, marginRight: 6 },
  addReviewTxt: { fontSize: 9, fontWeight: '700', color: Colors.green },
  gradeBox: { marginBottom: 6, paddingHorizontal: 8, paddingVertical: 4, borderRadius: 10, backgroundColor: 'rgba(201,168,76,0.08)', borderWidth: 1, borderColor: 'rgba(201,168,76,0.3)', maxWidth: '85%' },
  gradeScore: { fontSize: 11, fontWeight: '800', color: Colors.goldDark },
  gradeHeard: { fontSize: 9, color: Colors.muted, marginTop: 2 },
});
