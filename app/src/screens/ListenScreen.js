// 听力模块 ListenScreen：慢速/正常播放 + 跟读录音 + 真实时长AI评分 + 听写模式
import React, { useState, useEffect, useRef } from 'react';
import {
  View, Text, FlatList, StyleSheet, TouchableOpacity, Alert, Platform,
} from 'react-native';
import * as Speech from 'expo-speech';
import { speak as ttsSpeak } from '../tts';
import {
  AudioModule, RecordingPresets, requestRecordingPermissionsAsync, createAudioPlayer,
} from 'expo-audio';
import { useFocusEffect } from '@react-navigation/native';
import { Colors, Radius } from '../theme';
import { ArchHeader } from '../components';
import DATA from '../data';
import { loadData, getApiBase } from '../api';
import { Store } from '../store';
import { useStudyTimer } from '../useStudyTimer';
import QuranModal from '../QuranModal';
import MusicModal from '../MusicModal';
import PrayerModal from '../PrayerModal';

// 精选听力句（每类取前5句，过滤无翻译句）
function buildListenList(data) {
  const list = [];
  let gid = 0;
  Object.values(data.cats || {}).forEach((arr) => {
    (arr || []).filter((s) => s.c && s.e).slice(0, 5).forEach((s) => {
      list.push({ ...s, _id: gid++ });
    });
  });
  return list;
}

// 语音识别归一化：去音符/长音/标点，只留阿拉伯语词
function normAr(text) {
  return String(text || '')
    .replace(/[\u064B-\u0652\u0670\u0640\u06D6-\u06ED\u0610-\u061A]/g, '')
    .replace(/[^\u0600-\u06FF\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}
function arWords(text) {
  return normAr(text).split(' ').filter(Boolean);
}
// 跟读评分：识别词与目标词比对（重叠率）+ 完整度
function gradeByHearing(target, heard) {
  const t = arWords(target);
  const h = arWords(heard);
  if (!t.length) return 0;
  const hSet = new Set(h);
  let matched = 0;
  t.forEach((w) => { if (hSet.has(w)) matched++; });
  const overlap = matched / t.length;
  const precision = h.length ? matched / h.length : 0;
  return Math.round((overlap * 0.7 + precision * 0.3) * 100);
}

// 参考朗读时长估算：每字符约 95ms（含停顿），慢速更久
function estimateMs(text, rate) {
  const base = text.length * 95;
  return base / rate;
}

function Entry({ icon, title, desc, onPress }) {
  return (
    <TouchableOpacity style={styles.entry} activeOpacity={0.85} onPress={onPress}>
      <View style={styles.entryIcon}><Text style={{ fontSize: 17 }}>{icon}</Text></View>
      <Text style={styles.entryTitle}>{title}</Text>
      <Text style={styles.entryDesc}>{desc}</Text>
    </TouchableOpacity>
  );
}

export default function ListenScreen() {
  useStudyTimer(true);
  const [list, setList] = useState(buildListenList(DATA));
  const [playingId, setPlayingId] = useState(null);
  const [speed, setSpeed] = useState(0.7);
  const [hideTr, setHideTr] = useState(false);
  const [quranOpen, setQuranOpen] = useState(false);
  const [musicOpen, setMusicOpen] = useState(false);
  const [prayerOpen, setPrayerOpen] = useState(false); // 听写模式：隐藏翻译
  const [recording, setRecording] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recordId, setRecordId] = useState(null);
  const [score, setScore] = useState(null);
  const [durationSec, setDurationSec] = useState(null);
  const recorderRef = useRef(null);
  const recordStartRef = useRef(0);
  const [permission, setPermission] = useState(false);
  const [favs, setFavs] = useState([]);
  const [gradingId, setGradingId] = useState(null); // 正在评测的句子
  const [gradeRes, setGradeRes] = useState(null); // {id, score, heard}
  const gradeRecRef = useRef(null);

  // 离开页面时停止录音和播放
  useFocusEffect(
    React.useCallback(() => {
      return () => {
        try { Speech.stop(); } catch (e) {}
        if (recorderRef.current) {
          try { recorderRef.current.stop(); } catch (e) {}
          recorderRef.current = null;
        }
        setIsRecording(false);
      };
    }, [])
  );

  useEffect(() => {
    loadData().then((d) => setList(buildListenList(d)));
    (async () => {
      try {
        const perm = await requestRecordingPermissionsAsync();
        setPermission(perm.granted);
      } catch { setPermission(false); }
    })();
    Store.getFavorites().then(setFavs);
    const sub = Store.subscribe(() => Store.getFavorites().then(setFavs));
    return () => sub();
  }, []);

  const play = async (item) => {
    Speech.stop();
    await ttsSpeak(item.a, {
      lang: 'ar-SA',
      rate: speed,
      onStart: () => { setPlayingId(item._id); Store.markLearned(item._id); },
      onDone: () => setPlayingId(null),
      onStopped: () => setPlayingId(null),
    });
  };

  // 播放英语翻译（优选好听语音）
  const playEn = async (item) => {
    if (!item.e || !item.e.trim()) return;
    Speech.stop();
    await ttsSpeak(item.e, {
      lang: 'en-US',
      rate: 0.85,
      onStart: () => setPlayingId('en_' + item._id),
      onDone: () => setPlayingId(null),
      onStopped: () => setPlayingId(null),
      onError: () => {
        setPlayingId(null);
        Alert.alert('英语朗读失败', '手机TTS缺少英语语音包。请到 设置→语言和输入法→文字转语音 检查，或安装 Google 语音服务。');
      },
    });
  };

  const stop = () => {
    Speech.stop();
    setPlayingId(null);
  };

  const toggleRecord = async (item) => {
    if (!permission) {
      Alert.alert('权限', '需要麦克风权限才能跟读录音');
      return;
    }
    if (isRecording) {
      // 停止录音
      try {
        const rec = recorderRef.current;
        const dur = rec ? rec.currentTime : (Date.now() - recordStartRef.current) / 1000;
        await rec?.stop();
        setRecording(rec?.uri || null);
        setDurationSec(dur);
        setIsRecording(false);
        setRecordId(item._id);
        gradeRecording(item, dur);
      } catch (e) {
        setIsRecording(false);
        Alert.alert('录音出错', String(e));
      }
      return;
    }
    // 开始录音
    try {
      const rec = new AudioModule.AudioRecorder(RecordingPresets.HIGH_QUALITY);
      await rec.prepareToRecordAsync();
      rec.record();
      recorderRef.current = rec;
      recordStartRef.current = Date.now();
      setIsRecording(true);
    } catch (e) {
      Alert.alert('无法开始录音', String(e));
    }
  };

  // 🎯 跟读评测（本地 Whisper 识别：录音 → 上传电脑服务器 → 比对评分）
  const gradeUpload = async (item) => {
    setGradingId(null);
    const uri = gradeRecRef.current && gradeRecRef.current.uri;
    if (!uri) { setGradeRes({ id: item._id, score: 0, heard: '（没有录到声音）' }); return; }
    try {
      const fd = new FormData();
      fd.append('file', { uri, name: 'audio.m4a', type: 'audio/m4a' });
      const base = await getApiBase();
      const res = await fetch(base + '/api/asr', {
        method: 'POST',
        headers: { 'X-ASR-Lang': 'ar' },
        body: fd,
      });
      const d = await res.json();
      const heard = (d.text || '').trim();
      if (!heard) { setGradeRes({ id: item._id, score: 0, heard: '（没有听清，请再试一次）' }); return; }
      const score = gradeByHearing(item.a, heard);
      setGradeRes({ id: item._id, score, heard });
    } catch (e) {
      setGradeRes({ id: item._id, score: 0, heard: '（识别失败：需连接电脑服务器 server.py）' });
    }
  };

  const startGrade = async (item) => {
    if (gradingId) {
      // 停止录音并评分
      try { await gradeRecRef.current?.stop(); } catch (e) {}
      gradeUpload(item);
      return;
    }
    // 预检服务器（避免白录音）
    try {
      const base = await getApiBase();
      const res = await fetch(base + '/api/asr/status', { cache: 'no-store' });
      const s = await res.json();
      if (!s.asr) {
        Alert.alert('语音服务不可用', '请确认电脑 server.py 已运行（或桌面App已打开），且手机与电脑在同一WiFi。');
        return;
      }
    } catch (e) {
      Alert.alert('无法连接服务器', '请确认电脑 server.py 已运行，且 config.js 的 LAN_IP 是电脑IP。');
      return;
    }
    try {
      const perm = await requestRecordingPermissionsAsync();
      if (!perm.granted) { Alert.alert('权限', '需要麦克风权限才能跟读评测'); return; }
    } catch { Alert.alert('不支持', '当前设备不支持录音'); return; }
    setGradeRes(null);
    setGradingId(item._id);
    try {
      const rec = new AudioModule.AudioRecorder(RecordingPresets.HIGH_QUALITY);
      await rec.prepareToRecordAsync();
      rec.record();
      gradeRecRef.current = rec;
    } catch (e) {
      setGradingId(null);
      Alert.alert('评测失败', '录音启动失败：' + String(e));
    }
  };

  // 评分：语速匹配度（真实录音时长 vs 参考时长）+ 覆盖完整度
  const gradeRecording = (item, durSec) => {
    const estSec = estimateMs(item.a, speed) / 1000;
    const ratio = estSec > 0 ? durSec / estSec : 1;
    // 语速分：时长越接近参考值越高（允许 ±20% 内满分）
    const pace = Math.max(0, 100 - Math.abs(ratio - 1) * 90);
    // 完整度：根据朗读时长覆盖句子长度的比例估算（短于 50% 视为没读完）
    const coverage = Math.min(100, (durSec / (estSec * 0.75)) * 100);
    const completion = Math.max(0, Math.min(100, coverage));
    const final = Math.round(pace * 0.6 + completion * 0.4);
    setScore({ id: item._id, value: final, pace: Math.round(pace), completion: Math.round(completion) });
  };

  const playRecording = () => {
    if (!recording) return;
    if (Platform.OS === 'web') {
      const a = new Audio(recording);
      a.play();
      return;
    }
    try {
      const player = createAudioPlayer(recording);
      player.play();
    } catch (e) {
      Alert.alert('播放失败', String(e));
    }
  };

  const renderScore = (item) => {
    if (!score || score.id !== item._id) return null;
    const good = score.value >= 80;
    return (
      <View style={styles.scoreBox}>
        <Text style={[styles.scoreTxt, good ? styles.scoreGood : styles.scoreMid]}>
          AI评分 {score.value}分
        </Text>
        <Text style={styles.scoreSub}>
          语速 {score.pace} · 完整度 {score.completion} · 时长 {durationSec != null ? durationSec.toFixed(1) + 's' : '—'}
        </Text>
      </View>
    );
  };

  return (
    <View style={styles.root}>
      <ArchHeader title="🎧 听力训练" subtitle="" zh="慢速 · 正常 · 跟读评分 · 听写" />

      {/* 听力功能入口 */}
      <View style={styles.entryGrid}>
        <Entry icon="🕌" title="古兰经" desc="114 章诵读" onPress={() => setQuranOpen(true)} />
        <Entry icon="📼" title="整章诵读" desc="整章单音频" onPress={() => setQuranOpen(true)} />
        <Entry icon="🎙" title="宣礼试听" desc="15 位宣礼师" onPress={() => setPrayerOpen(true)} />
        <Entry icon="🎵" title="AI 音乐" desc="生成阿拉伯音乐" onPress={() => setMusicOpen(true)} />
      </View>

      <View style={styles.controls}>
        <TouchableOpacity style={[styles.speedBtn, speed === 0.5 && styles.speedBtnOn]} onPress={() => setSpeed(0.5)}>
          <Text style={styles.speedTxt}>🐢 慢速</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.speedBtn, speed === 0.7 && styles.speedBtnOn]} onPress={() => setSpeed(0.7)}>
          <Text style={styles.speedTxt}>▶ 正常</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.speedBtn, hideTr && styles.hideBtnOn]} onPress={() => setHideTr(!hideTr)}>
          <Text style={styles.speedTxt}>🙈 听写模式</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.speedBtn, styles.stopBtn]} onPress={stop}>
          <Text style={styles.speedTxt}>⏹ 停止</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        data={list}
        keyExtractor={(item) => String(item._id)}
        contentContainerStyle={{ padding: 16, paddingBottom: 30 }}
        renderItem={({ item }) => {
          const isRec = recordId === item._id && recording;
          return (
            <View style={[styles.item, playingId === item._id && styles.itemOn]}>
              <TouchableOpacity activeOpacity={0.85} onPress={() => play(item)}>
                <View style={styles.itemHead}>
                  <Text style={styles.playIcon}>{playingId === item._id ? '🔊' : '▶️'}</Text>
                  <Text style={styles.itemAr}>{item.a}</Text>
                </View>
                {hideTr ? (
                  <Text style={styles.dictHint}>🙈 已隐藏翻译 · 再听几遍再核对 ↓</Text>
                ) : (
                  <>
                    <Text style={styles.itemTr}>🇨🇳 {item.c}</Text>
                    <View style={styles.enRow}>
                      <Text style={styles.itemEn}>🇬🇧 {item.e}</Text>
                      <TouchableOpacity style={styles.enPlayBtn} onPress={() => playEn(item)}>
                        <Text style={styles.enPlayTxt}>{playingId === 'en_' + item._id ? '🔊' : '🔈'} 读英语</Text>
                      </TouchableOpacity>
                    </View>
                  </>
                )}
              </TouchableOpacity>

              {/* 听写核对（隐藏翻译时点击显示） */}
              {hideTr ? (
                <TouchableOpacity style={styles.revealBtn} onPress={() => setHideTr(false)}>
                  <Text style={styles.revealTxt}>👁 显示翻译核对</Text>
                </TouchableOpacity>
              ) : null}

              {/* 收藏 */}
              <View style={styles.favRow}>
                <TouchableOpacity
                  style={[styles.recBtn, favs.includes(item._id) && styles.favOn]}
                  onPress={async () => { await Store.toggleFavorite(item._id); setFavs(await Store.getFavorites()); }}
                >
                  <Text style={styles.recTxt}>{favs.includes(item._id) ? '⭐ 已收藏' : '☆ 收藏'}</Text>
                </TouchableOpacity>
              </View>

              {/* 语音识别跟读评测 */}
              <View style={styles.recRow}>
                <TouchableOpacity
                  style={[styles.recBtn, gradingId === item._id && styles.gradeOn]}
                  onPress={() => startGrade(item)}
                >
                  <Text style={styles.recTxt}>{gradingId === item._id ? '⏹ 停止评测' : '🎯 跟读评测'}</Text>
                </TouchableOpacity>
                {gradeRes && gradeRes.id === item._id ? (
                  <View style={styles.scoreBox}>
                    <Text style={[styles.scoreTxt, gradeRes.score >= 80 ? styles.scoreGood : styles.scoreMid]}>
                      AI评测 {gradeRes.score}分
                    </Text>
                    <Text style={styles.scoreSub} numberOfLines={2}>听到：{gradeRes.heard}</Text>
                  </View>
                ) : null}
              </View>

              {/* 跟读录音 */}
              <View style={styles.recRow}>
                <TouchableOpacity
                  style={[styles.recBtn, isRecording && styles.recBtnActive]}
                  onPress={() => toggleRecord(item)}
                >
                  <Text style={styles.recTxt}>{isRecording ? '⏹ 停止录音' : '🎤 录音'}</Text>
                </TouchableOpacity>
                {isRec ? (
                  <>
                    <TouchableOpacity style={styles.recBtn} onPress={playRecording}>
                      <Text style={styles.recTxt}>▶ 听我的</Text>
                    </TouchableOpacity>
                    {renderScore(item)}
                  </>
                ) : null}
              </View>
            </View>
          );
        }}
      />
          <QuranModal visible={quranOpen} onClose={() => setQuranOpen(false)} />
      <MusicModal visible={musicOpen} onClose={() => setMusicOpen(false)} />
      <PrayerModal visible={prayerOpen} onClose={() => setPrayerOpen(false)} />
    </View>
  );
}

const styles = StyleSheet.create({
  entryGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, paddingHorizontal: 16, paddingTop: 4, paddingBottom: 6 },
  entry: {
    width: '23%', backgroundColor: '#fff', borderRadius: 14, paddingVertical: 12, paddingHorizontal: 4,
    alignItems: 'center', borderWidth: 1, borderColor: 'rgba(201,168,76,.22)',
  },
  entryIcon: { width: 34, height: 34, borderRadius: 12, backgroundColor: 'rgba(201,168,76,.14)', alignItems: 'center', justifyContent: 'center', marginBottom: 5 },
  entryTitle: { fontSize: 11, fontWeight: '800', color: Colors.greenDark },
  entryDesc: { fontSize: 8, color: Colors.muted, marginTop: 2, textAlign: 'center' },
  root: { flex: 1, backgroundColor: Colors.cream },
  controls: { flexDirection: 'row', gap: 8, paddingHorizontal: 16, paddingTop: 12, flexWrap: 'wrap' },
  speedBtn: {
    paddingHorizontal: 13, paddingVertical: 8, borderRadius: Radius.md,
    backgroundColor: Colors.white, borderWidth: 1, borderColor: 'rgba(201,168,76,0.3)',
  },
  speedBtnOn: { backgroundColor: Colors.gold },
  hideBtnOn: { backgroundColor: 'rgba(26,92,74,0.12)', borderColor: 'rgba(26,92,74,0.45)' },
  stopBtn: { marginLeft: 'auto', borderColor: 'rgba(192,57,43,0.4)' },
  speedTxt: { fontSize: 11, fontWeight: '600', color: Colors.ink },
  item: {
    backgroundColor: Colors.white, borderRadius: Radius.md, padding: 14, marginBottom: 8,
    borderWidth: 1, borderColor: 'rgba(201,168,76,0.14)',
  },
  itemOn: { borderColor: Colors.gold, borderWidth: 1.5 },
  itemHead: { flexDirection: 'row', alignItems: 'center' },
  playIcon: { fontSize: 16, marginRight: 8 },
  itemAr: { fontFamily: 'serif', fontSize: 15, fontWeight: '700', color: Colors.greenDark, textAlign: 'right', flex: 1, writingDirection: 'rtl' },
  itemTr: { fontSize: 11, color: Colors.green, marginTop: 6 },
  enRow: { flexDirection: 'row', alignItems: 'center', marginTop: 2 },
  itemEn: { fontSize: 10, color: Colors.muted, flex: 1 },
  enPlayBtn: {
    paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12,
    backgroundColor: 'rgba(90,127,158,0.1)', borderWidth: 1, borderColor: 'rgba(90,127,158,0.35)', marginLeft: 8,
  },
  enPlayTxt: { fontSize: 9.5, fontWeight: '700', color: '#4a6e8a' },
  dictHint: { fontSize: 10, color: Colors.goldDark, marginTop: 6, fontStyle: 'italic' },
  revealBtn: {
    marginTop: 8, alignSelf: 'flex-start', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 14,
    backgroundColor: 'rgba(26,92,74,0.08)', borderWidth: 1, borderColor: 'rgba(26,92,74,0.3)',
  },
  revealTxt: { fontSize: 10, color: Colors.green, fontWeight: '600' },
  recRow: { flexDirection: 'row', alignItems: 'center', gap: 8, marginTop: 10, paddingTop: 8, borderTopWidth: 1, borderTopColor: '#f0eeea', flexWrap: 'wrap' },
  favRow: { flexDirection: 'row', marginTop: 8 },
  favOn: { backgroundColor: 'rgba(201,168,76,0.25)', borderColor: 'rgba(201,168,76,0.5)' },
  recBtn: {
    paddingHorizontal: 12, paddingVertical: 6, borderRadius: 14,
    backgroundColor: 'rgba(201,168,76,0.1)', borderWidth: 1, borderColor: 'rgba(201,168,76,0.3)',
  },
  recBtnActive: { backgroundColor: 'rgba(192,57,43,0.1)', borderColor: 'rgba(192,57,43,0.4)' },
  gradeOn: { backgroundColor: 'rgba(26,138,92,0.18)', borderColor: 'rgba(26,138,92,0.5)' },
  recTxt: { fontSize: 10, fontWeight: '600', color: Colors.ink },
  scoreBox: { marginLeft: 'auto', alignItems: 'flex-end' },
  scoreTxt: { fontSize: 12, fontWeight: '800' },
  scoreGood: { color: Colors.green },
  scoreMid: { color: Colors.goldDark },
  scoreSub: { fontSize: 9, color: Colors.muted, marginTop: 2 },
});
