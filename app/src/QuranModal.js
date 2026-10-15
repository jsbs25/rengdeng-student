// 古兰经模块：114 章阅读 + 逐字分解（AI 词法/语法分析，缓存结果）
import React, { useState, useEffect, useRef } from 'react';
import {
  View, Text, Modal, FlatList, TouchableOpacity, StyleSheet, ScrollView, ActivityIndicator,
  Alert, TextInput,
} from 'react-native';
import * as Speech from 'expo-speech';
import { createAudioPlayer } from 'expo-audio';
import { speak as ttsSpeak } from './tts';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Colors, Radius } from './theme';
import { ArchHeader } from './components';
import QURAN from './quranData';
import { getApiBase } from './api';
import DATA from './data';
import { chatMessage } from './api';
import { useStudyTimer } from './useStudyTimer';

const CACHE_KEY = 'nur_quran_analysis_v1';

// 诵读家（verses.quran.com 音频）
const RECITERS = [
  { label: '🎙 阿法西', path: 'Alafasy/mp3/' },
  { label: '🎙 苏达伊斯', path: 'Sudais/mp3/' },
  { label: '🎙 阿卜杜勒·巴西特', path: 'AbdulBaset/Murattal/mp3/' },
  { label: '🎙 巴西特·穆加瓦德', path: 'AbdulBaset/Mujawwad/mp3/' },
  { label: '🎙 沙特里', path: 'Shatri/mp3/' },
  { label: '🎙 明沙维', path: 'Minshawi/Mujawwad/mp3/' },
  { label: '🎙 舒莱姆', path: 'Shuraym/mp3/' },
];
const AUDIO_BASE = 'https://verses.quran.com/';
let _proxyBase = null;
// 音频走本地服务器代理（解决国外音频源访问慢/被墙）
async function proxyUrl(u) {
  try {
    if (!_proxyBase) _proxyBase = await getApiBase();
    return _proxyBase + '/api/quran/proxy?u=' + encodeURIComponent(u);
  } catch (e) { return u; }
}
// 整章诵读家（mp3quran 服务器：每章一个完整 mp3，非逐节拼接）
const FULL_RECITERS = [
  { label: '📼 阿法西·整章', url: 'https://server8.mp3quran.net/afs/' },
  { label: '📼 拉阿德·整章', url: 'https://server8.mp3quran.net/ra3ad/' },
  { label: '📼 哈尼·整章', url: 'https://server8.mp3quran.net/hani/' },
  { label: '📼 阿尤布·整章', url: 'https://server8.mp3quran.net/ayyub/' },
  { label: '📼 曼图里德·整章', url: 'https://server8.mp3quran.net/mtrod/' },
  { label: '📼 诺亚·整章', url: 'https://server8.mp3quran.net/noah/' },
  { label: '📼 萨比尔·整章', url: 'https://server8.mp3quran.net/saber/' },
];

export default function QuranModal({ visible, onClose }) {
  useStudyTimer(visible);
  const [view, setView] = useState('list'); // list | surah | analysis
  const [surah, setSurah] = useState(null);
  const [analysis, setAnalysis] = useState(null); // {ayahIdx, words:[{w, root, pos, func, cn, en}]}
  const [loading, setLoading] = useState(false);
  const [cache, setCache] = useState({});
  const [reciter, setReciter] = useState(-1);
  const [fullReciter, setFullReciter] = useState(-1); // 整章诵读家（-1 未选）
  const [fullPlaying, setFullPlaying] = useState(false);
  const [fullProg, setFullProg] = useState({ s: 1, cur: 0, dur: 0 });
  const playerRef = useRef(null);
  const [playingKey, setPlayingKey] = useState(null);
  const [playingAll, setPlayingAll] = useState(false);
  const [allProg, setAllProg] = useState({ s: 1, a: 0 }); // 整本诵读进度
  const allPosRef = useRef({ s: 1, a: 0 });
  const allStopRef = useRef(false);
  const [readSet, setReadSet] = useState({}); // 已读章节 {id: 1}
  const [tafsirOpen, setTafsirOpen] = useState({}); // {surahId_ayahIdx: true}
  const TAFSIR = DATA.tafsir || [];
  const [q, setQ] = useState('');                    // 章节搜索
  const [bookmarks, setBookmarks] = useState({});    // {surahId_ayahIdx: true}
  const [recent, setRecent] = useState([]);          // 最近阅读 [{id, n, tz}]
  const [playingSurah, setPlayingSurah] = useState(false); // 整章连播
  const surahStopRef = useRef(false);

  // 加载已读标记
  useEffect(() => {
    AsyncStorage.getItem('nur_quran_read').then((raw) => {
      if (raw) setReadSet(JSON.parse(raw));
    }).catch(() => {});
  }, [visible]);
  // 加载书签 + 最近阅读
  useEffect(() => {
    AsyncStorage.multiGet(['nur_quran_bookmarks', 'nur_quran_recent']).then((pairs) => {
      pairs.forEach(([k, v]) => {
        if (!v) return;
        try {
          if (k === 'nur_quran_bookmarks') setBookmarks(JSON.parse(v));
          else setRecent(JSON.parse(v));
        } catch (e) {}
      });
    }).catch(() => {});
  }, [visible]);

  // 打开章节时标记已读
  const openSurah = (s) => {
    setSurah(s);
    setAnalysis(null);
    setView('surah');
    setReadSet((prev) => {
      const next = { ...prev, [s.id]: 1 };
      AsyncStorage.setItem('nur_quran_read', JSON.stringify(next)).catch(() => {});
      return next;
    });
    // 记录最近阅读（最多 12）
    setRecent((prev) => {
      const next = [{ id: s.id, n: s.n, tz: s.tz || s.t }, ...prev.filter((x) => x.id !== s.id)].slice(0, 12);
      AsyncStorage.setItem('nur_quran_recent', JSON.stringify(next)).catch(() => {});
      return next;
    });
  };
  // 书签切换
  const toggleBookmark = (surahId, ayahIdx) => {
    setBookmarks((prev) => {
      const key = surahId + '_' + ayahIdx;
      const next = { ...prev };
      if (next[key]) delete next[key]; else next[key] = true;
      AsyncStorage.setItem('nur_quran_bookmarks', JSON.stringify(next)).catch(() => {});
      return next;
    });
  };

  // 加载缓存
  useEffect(() => {
    if (!visible) { setView('list'); setSurah(null); setAnalysis(null); }
  }, [visible]);
  useEffect(() => {
    AsyncStorage.getItem(CACHE_KEY)
      .then((raw) => raw && setCache(JSON.parse(raw)))
      .catch(() => {});
  }, []);

  const saveCache = (c) => {
    // 容量上限：最多保留 300 条分析（防无限增长）
    const keys = Object.keys(c);
    if (keys.length > 300) {
      const sorted = keys.sort();
      for (let i = 0; i < sorted.length - 300; i++) delete c[sorted[i]];
    }
    setCache(c);
    AsyncStorage.setItem(CACHE_KEY, JSON.stringify(c)).catch(() => {});
  };

  const speak = async (text) => {
    if (!text) return;
    Speech.stop();
    await ttsSpeak(text.replace(/[\u06D6-\u06ED\u064B-\u0652]/g, ''), { lang: 'ar-SA', rate: 0.75, onError: () => Alert.alert('朗读失败', 'TTS 语音包不可用，请检查系统文字转语音设置') });
  };



  // 播放诵读家音频（整节）
  const playRecitation = async (surahId, ayahIdx) => {
    if (reciter < 0) {
      Alert.alert('诵读家', '请先在顶部选择一位诵读家');
      return;
    }
    const key = surahId + '_' + ayahIdx;
    if (playingKey === key) {
      try { playerRef.current && playerRef.current.release(); } catch (e) {}
      playerRef.current = null;
      setPlayingKey(null);
      return;
    }
    const r = RECITERS[reciter];
    const url = await proxyUrl(AUDIO_BASE + r.path +
      String(surahId).padStart(3, '0') + String(ayahIdx + 1).padStart(3, '0') + '.mp3');
    try {
      const player = createAudioPlayer(url);
      if (playerRef.current) { try { playerRef.current.release(); } catch (e) {} }
      playerRef.current = player;
      player.play();
      setPlayingKey(key);
      // 播放出错 → 尝试 expo-av 兜底
      try {
        player.addListener('playbackStatusUpdate', (st) => {
          if (st && st.error) { player.release(); playerRef.current = null; playWithAv(url, key); }
        });
      } catch (e) {}
    } catch (e) {
      playWithAv(url, key);
    }
  };
  // expo-av 兜底播放（更可靠）
  const playWithAv = async (url, key) => {
    try {
      const { Audio } = require('expo-av');
      const { sound } = await Audio.Sound.createAsync({ uri: url }, { shouldPlay: true });
      if (playerRef.current) { try { playerRef.current.release(); } catch (e) {} }
      playerRef.current = sound;
      setPlayingKey(key);
    } catch (e) {
      Alert.alert('播放失败', '网络或音频源不可达，请检查网络后重试');
    }
  };

  // ===== 🎧 整本诵读（114 章连续播放）=====
  const playAllNext = async () => {
    if (allStopRef.current) return;
    const { s, a } = allPosRef.current;
    const ch = QURAN.find((x) => x.id === s);
    if (!ch) {
      stopAllPlay();
      Alert.alert('🎉 完成', '整本古兰经诵读完成！');
      return;
    }
    if (a >= ch.vs.length) {
      allPosRef.current = { s: s + 1, a: 0 };
      return playAllNext();
    }
    const r = RECITERS[reciter];
    const url = await proxyUrl(AUDIO_BASE + r.path + String(s).padStart(3, '0') + String(a + 1).padStart(3, '0') + '.mp3');
    try {
      if (playerRef.current) { try { playerRef.current.release(); } catch (e) {} }
      const player = createAudioPlayer(url);
      playerRef.current = player;
      const sub = player.addListener('playbackStatusUpdate', (status) => {
        if (status && status.didJustFinish && !allStopRef.current) {
          sub.remove();
          allPosRef.current = { s, a: a + 1 };
          setAllProg({ s, a: a + 1 });
          playAllNext();
        }
      });
      player.play();
      setPlayingKey(s + '_' + a);
      setAllProg({ s, a });
    } catch (e) {
      Alert.alert('播放失败', String(e));
      stopAllPlay();
    }
  };

  const stopAllPlay = () => {
    allStopRef.current = true;
    setPlayingAll(false);
    setPlayingKey(null);
    if (playerRef.current) { try { playerRef.current.release(); } catch (e) {} }
    playerRef.current = null;
  };

  const startAllPlay = (fromSurah) => {
    if (playingAll) { stopAllPlay(); return; }
    if (reciter < 0) { Alert.alert('诵读家', '请先选择一位诵读家'); return; }
    // 停止整章连播（互斥）
    surahStopRef.current = true;
    setPlayingSurah(false);
    allStopRef.current = false;
    allPosRef.current = { s: fromSurah, a: 0 };
    setPlayingAll(true);
    playAllNext();
  };

  // AI 逐词语法分析一节
  const analyzeAyah = async (idx) => {
    if (!surah) return;
    const ayah = surah.vs[idx];
    const key = `${surah.id}_${idx}`;
    if (cache[key]) {
      setAnalysis({ ayahIdx: idx, words: cache[key] });
      return;
    }
    setLoading(true);
    setAnalysis(null);
    try {
      const prompt =
        `请对这句古兰经经文做逐词语法分析（现代标准阿拉伯语语法）。要求每个词一行，用竖线分隔 6 个字段：\n` +
        `词（保留原文）| 词根 | 词性（اسم名词/فعل动词/حرف介词等）| 语法功能（如主格/宾格/属格/过去式/现在式/命令式/人称数）| 中文词义 | 英文词义\n\n经文：${ayah.a}`;
      const reply = await chatMessage(prompt, 'quran_' + Date.now());
      const words = [];
      const seen = new Set();
      reply.split('\n').forEach((line) => {
        const parts = line.split('|').map((p) => p.trim());
        if (parts.length >= 3 && /[\u0600-\u06FF]/.test(parts[0])) {
          const w = parts[0].replace(/[\u064B-\u0652\u06D6-\u06ED]/g, '');
          if (seen.has(w)) return; // 去重（AI 可能给阿中文双份注释）
          seen.add(w);
          words.push({
            w: parts[0],
            root: parts[1] || '',
            pos: parts[2] || '',
            func: parts[3] || '',
            cn: parts[4] || '',
            en: parts[5] || '',
          });
        }
      });
      if (words.length >= 2) {
        setAnalysis({ ayahIdx: idx, words });
        const c = { ...cache, [key]: words };
        saveCache(c);
      } else {
        setAnalysis({ ayahIdx: idx, words: null, err: reply.slice(0, 200) });
      }
    } catch (e) {
      setAnalysis({ ayahIdx: idx, words: null, err: '⚠️ AI 服务未连接，请确认 server.py 已运行' });
    }
    setLoading(false);
  };

  // ===== 整章单音频诵读（mp3quran 整章 mp3）=====
  const playSurahFull = async (surahId) => {
    if (fullReciter < 0) { Alert.alert('整章诵读', '请先选择一位「整章诵读」诵读家'); return; }
    if (fullPlaying) {
      setFullPlaying(false);
      setPlayingKey(null);
      if (playerRef.current) { try { playerRef.current.release(); } catch (e) {} }
      playerRef.current = null;
      return;
    }
    // 停止其他播放
    surahStopRef.current = true;
    setPlayingSurah(false);
    allStopRef.current = true;
    setPlayingAll(false);
    const r = FULL_RECITERS[fullReciter];
    const rawUrl = r.url + String(surahId).padStart(3, '0') + '.mp3';
    const url = await proxyUrl(rawUrl);
    setFullPlaying(true);
    setFullProg({ s: surahId, cur: 0, dur: 0 });
    setPlayingKey('full_' + surahId);
    const play = (player) => {
      try {
        player.play();
        try {
          player.addListener('playbackStatusUpdate', (st) => {
            if (st && st.currentTime != null) setFullProg({ s: surahId, cur: st.currentTime, dur: st.duration || 0 });
            if (st && st.didJustFinish) { setFullPlaying(false); setPlayingKey(null); }
          });
        } catch (e) {}
      } catch (e) {
        // expo-av 兜底
        try {
          const { Audio } = require('expo-av');
          Audio.Sound.createAsync({ uri: url }, { shouldPlay: true }).then(({ sound }) => {
            if (playerRef.current) { try { playerRef.current.release(); } catch (e2) {} }
            playerRef.current = sound;
            sound.setOnPlaybackStatusUpdate((st) => {
              if (st && st.positionMillis != null) setFullProg({ s: surahId, cur: st.positionMillis / 1000, dur: st.durationMillis ? st.durationMillis / 1000 : 0 });
              if (st && st.didJustFinish) { setFullPlaying(false); setPlayingKey(null); }
            });
          }).catch(() => {});
        } catch (e2) {}
      }
    };
    try {
      if (playerRef.current) { try { playerRef.current.release(); } catch (e) {} }
      const player = createAudioPlayer(url);
      playerRef.current = player;
      play(player);
    } catch (e) {
      try {
        const { Audio } = require('expo-av');
        Audio.Sound.createAsync({ uri: url }, { shouldPlay: true }).then(({ sound }) => {
          if (playerRef.current) { try { playerRef.current.release(); } catch (e2) {} }
          playerRef.current = sound;
          play(sound);
        }).catch(() => {});
      } catch (e2) {}
    }
  };

  const playSurahNext = async (idx) => {
    if (surahStopRef.current) { setPlayingSurah(false); return; }
    if (idx >= surah.vs.length) {
      setPlayingSurah(false);
      Alert.alert('🎉 完成', `「${surah.tz || surah.n}」诵读完成`);
      return;
    }
    if (reciter < 0) {
      setPlayingSurah(false);
      Alert.alert('诵读家', '请先选择一位诵读家');
      return;
    }
    const r = RECITERS[reciter];
    const url = await proxyUrl(AUDIO_BASE + r.path + String(surah.id).padStart(3, '0') + String(idx + 1).padStart(3, '0') + '.mp3');
    setPlayingKey(surah.id + '_' + idx);
    try {
      if (playerRef.current) { try { playerRef.current.release(); } catch (e) {} }
      const player = createAudioPlayer(url);
      playerRef.current = player;
      const sub = player.addListener('playbackStatusUpdate', (st) => {
        if (st && st.didJustFinish && !surahStopRef.current) {
          sub.remove();
          playSurahNext(idx + 1);
        }
      });
      player.play();
    } catch (e) {
      // expo-av 兜底
      try {
        const { Audio } = require('expo-av');
        Audio.Sound.createAsync({ uri: url }, { shouldPlay: true }).then(({ sound }) => {
          if (playerRef.current) { try { playerRef.current.release(); } catch (e2) {} }
          playerRef.current = sound;
          sound.setOnPlaybackStatusUpdate((st) => {
            if (st && st.didJustFinish && !surahStopRef.current) {
              sound.unloadAsync().catch(() => {});
              playSurahNext(idx + 1);
            }
          });
        }).catch(() => { playSurahNext(idx + 1); });
      } catch (e3) { playSurahNext(idx + 1); }
    }
  };
  const toggleSurahPlay = () => {
    if (playingSurah) {
      surahStopRef.current = true;
      setPlayingSurah(false);
      setPlayingKey(null);
      if (playerRef.current) { try { playerRef.current.release(); } catch (e) {} }
      playerRef.current = null;
      return;
    }
    allStopRef.current = true;
    setPlayingAll(false);
    surahStopRef.current = false;
    setPlayingSurah(true);
    playSurahNext(0);
  };

  const closeAll = () => { setView('list'); setSurah(null); setAnalysis(null); setFullPlaying(false); onClose(); };

  const renderAnalysis = () => {
    if (!analysis) return null;
    const ayah = surah.vs[analysis.ayahIdx];
    return (
      <ScrollView style={styles.body} contentContainerStyle={{ padding: 16, paddingBottom: 40 }}>
        <TouchableOpacity style={styles.backBtn} onPress={() => { setAnalysis(null); }}>
          <Text style={styles.backTxt}>← 返回经文</Text>
        </TouchableOpacity>
        <Text style={styles.surahTitle}>🔬 逐字分解 · {surah.tz || surah.n}</Text>
        <Text style={styles.ayahNum}>第 {analysis.ayahIdx + 1} 节</Text>
        <View style={styles.ayahCard}>
          <Text style={styles.ayahAr}>{ayah.a}</Text>
          <Text style={styles.ayahZh}>{ayah.z}</Text>
        </View>
        <TouchableOpacity style={styles.listenBtn} onPress={() => speak(ayah.a)}>
          <Text style={styles.listenTxt}>🔊 朗读本节</Text>
        </TouchableOpacity>

        {analysis.words ? (
          <>
            <Text style={styles.sectionLabel}>📖 逐词语法分析（点击词看详情）</Text>
            {analysis.words.map((wd, i) => (
              <TouchableOpacity key={i} style={styles.wordCard} onPress={() => { speak(wd.w); }}>
                <View style={styles.wordHead}>
                  <Text style={styles.wordAr}>{wd.w}</Text>
                  <View style={{ flex: 1 }} />
                  <Text style={styles.wordPos}>{wd.pos}</Text>
                </View>
                <View style={styles.wordGrid}>
                  <WordInfo label="词根" value={wd.root} />
                  <WordInfo label="语法" value={wd.func} />
                  <WordInfo label="中文" value={wd.cn} wide />
                  <WordInfo label="English" value={wd.en} wide />
                </View>
              </TouchableOpacity>
            ))}
          </>
        ) : (
          <Text style={styles.err}>{analysis.err || '解析失败'}</Text>
        )}
      </ScrollView>
    );
  };

  return (
    <Modal visible={visible} animationType="slide" onRequestClose={closeAll}>
      <View style={styles.root}>
        <ArchHeader title="🕌 古兰经" subtitle="AL-QUR'ĀN" zh="114 章 · 逐字分解 · 词法语法" />

        {view === 'full' ? (
          // 整章诵读播放器：选诵读家 + 选章 + 播放
          <View style={styles.body}>
            <TouchableOpacity style={styles.backBtn} onPress={() => { setView('list'); setFullPlaying(false); }}>
              <Text style={styles.backTxt}>← 返回列表</Text>
            </TouchableOpacity>
            <Text style={styles.surahTitle}>📼 整章单音频诵读</Text>
            <Text style={styles.surahMeta}>每章一个完整音频，从头到尾一气呵成</Text>
            <View style={styles.reciterRow}>
              <Text style={styles.reciterLabel}>诵读家</Text>
              {FULL_RECITERS.map((r, i) => (
                <TouchableOpacity key={i} style={[styles.reciterChip, fullReciter === i && styles.reciterOn]} onPress={() => { setFullReciter(i); setFullPlaying(false); }}>
                  <Text style={[styles.reciterTxt, fullReciter === i && styles.reciterTxtOn]}>{r.label.replace('📼 ', '')}</Text>
                </TouchableOpacity>
              ))}
            </View>
            {fullReciter >= 0 ? (
              <Text style={styles.quickLabel}>📖 选择章节（当前：{FULL_RECITERS[fullReciter].label.replace('📼 ', '')}）</Text>
            ) : (
              <Text style={styles.err}>⚠️ 请先选择一位整章诵读家</Text>
            )}
            <ScrollView>
              <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 6 }}>
                {QURAN.map((ch) => (
                  <TouchableOpacity
                    key={ch.id}
                    style={[styles.quickChip, { width: '48%' }]}
                    onPress={() => { if (fullReciter < 0) { Alert.alert('整章诵读', '请先选择一位诵读家'); return; } playSurahFull(ch.id); }}
                  >
                    <Text style={styles.quickTxt}>{ch.id}. {ch.tz || ch.n}</Text>
                  </TouchableOpacity>
                ))}
              </View>
            </ScrollView>
            {fullPlaying ? (
              <View style={[styles.allPlayBtn, styles.allPlayBtnOn, { marginTop: 10 }]}>
                <Text style={styles.allPlayTxt}>
                  ▶ 播放中：第{fullProg.s}章 · {fullProg.dur ? Math.floor(fullProg.cur / 60) + ':' + String(Math.floor(fullProg.cur % 60)).padStart(2, '0') + ' / ' + Math.floor(fullProg.dur / 60) + ':' + String(Math.floor(fullProg.dur % 60)).padStart(2, '0') : '加载中...'}
                </Text>
              </View>
            ) : null}
            {fullPlaying ? (
              <TouchableOpacity style={[styles.allPlayBtn, { marginTop: 8 }]} onPress={() => { setFullPlaying(false); setPlayingKey(null); if (playerRef.current) { try { playerRef.current.release(); } catch (e) {} } playerRef.current = null; }}>
                <Text style={styles.allPlayTxt}>⏹ 停止</Text>
              </TouchableOpacity>
            ) : null}
          </View>
        ) : view === 'surah' && surah ? (
          // 章节阅读页
          <FlatList
            style={styles.body}
            data={surah.vs}
            keyExtractor={(item, i) => String(i)}
            contentContainerStyle={{ padding: 16, paddingBottom: 40 }}
            ListHeaderComponent={
              <>
                <TouchableOpacity
                  style={[styles.allPlayBtn, playingAll && styles.allPlayBtnOn]}
                  onPress={() => startAllPlay(1)}
                >
                  <Text style={styles.allPlayTxt}>
                    {playingAll ? `⏹ 停止诵读 · 第${allProg.s}章 第${allProg.a + 1}节` : '▶ 整本诵读（114 章连续）'}
                  </Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.allPlayBtn, playingSurah && styles.allPlayBtnOn]}
                  onPress={toggleSurahPlay}
                >
                  <Text style={styles.allPlayTxt}>
                    {playingSurah ? '⏹ 停止本章诵读' : `▶ 播放本章（${surah.vs.length} 节连续）`}
                  </Text>
                </TouchableOpacity>
                {fullReciter >= 0 ? (
                  <TouchableOpacity
                    style={[styles.allPlayBtn, fullPlaying && styles.allPlayBtnOn]}
                    onPress={() => playSurahFull(surah.id)}
                  >
                    <Text style={styles.allPlayTxt}>
                      {fullPlaying
                        ? `⏹ 停止整章 · ${fullProg.dur ? Math.floor(fullProg.cur / 60) + ':' + String(Math.floor(fullProg.cur % 60)).padStart(2, '0') + ' / ' + Math.floor(fullProg.dur / 60) + ':' + String(Math.floor(fullProg.dur % 60)).padStart(2, '0') : '加载中...'}`
                        : `📼 整章单音频诵读（${FULL_RECITERS[fullReciter].label}）`}
                    </Text>
                  </TouchableOpacity>
                ) : null}
                <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
                  <TouchableOpacity
                    style={styles.backBtn}
                    disabled={surah.id <= 1}
                    onPress={() => { const prev = QURAN.find((q) => q.id === surah.id - 1); if (prev) openSurah(prev); }}
                  >
                    <Text style={[styles.backTxt, surah.id <= 1 && { opacity: 0.3 }]}>‹ 上一章</Text>
                  </TouchableOpacity>
                  <TouchableOpacity style={styles.backBtn} onPress={() => { setView('list'); setSurah(null); }}>
                    <Text style={styles.backTxt}>← 章节列表</Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={styles.backBtn}
                    disabled={surah.id >= QURAN.length}
                    onPress={() => { const next = QURAN.find((q) => q.id === surah.id + 1); if (next) openSurah(next); }}
                  >
                    <Text style={[styles.backTxt, surah.id >= QURAN.length && { opacity: 0.3 }]}>下一章 ›</Text>
                  </TouchableOpacity>
                </View>
                <Text style={styles.surahTitle}>🕌 {surah.n} · {surah.tz}</Text>
                <Text style={styles.surahMeta}>{surah.t} · {surah.ty === 'meccan' ? '麦加章' : '麦地那章'} · {surah.vs.length} 节</Text>
                {/* 诵读家选择 */}
                <View style={styles.reciterRow}>
                  <Text style={styles.reciterLabel}>🎙 诵读家</Text>
                  <TouchableOpacity style={[styles.reciterChip, reciter < 0 && styles.reciterOn]} onPress={() => { setReciter(-1); setPlayingKey(null); }}>
                    <Text style={[styles.reciterTxt, reciter < 0 && styles.reciterTxtOn]}>🔇 无</Text>
                  </TouchableOpacity>
                  {RECITERS.map((r, i) => (
                    <TouchableOpacity key={i} style={[styles.reciterChip, reciter === i && styles.reciterOn]} onPress={() => { setReciter(i); setFullReciter(-1); setPlayingKey(null); setFullPlaying(false); }}>
                      <Text style={[styles.reciterTxt, reciter === i && styles.reciterTxtOn]}>{r.label}</Text>
                    </TouchableOpacity>
                  ))}
                </View>
                <View style={styles.reciterRow}>
                  <Text style={styles.reciterLabel}>📼 整章诵读</Text>
                  <TouchableOpacity style={[styles.reciterChip, fullReciter < 0 && styles.reciterOn]} onPress={() => { setFullReciter(-1); setPlayingKey(null); setFullPlaying(false); }}>
                    <Text style={[styles.reciterTxt, fullReciter < 0 && styles.reciterTxtOn]}>🔇 无</Text>
                  </TouchableOpacity>
                  {FULL_RECITERS.map((r, i) => (
                    <TouchableOpacity key={i} style={[styles.reciterChip, fullReciter === i && styles.reciterOn]} onPress={() => { setFullReciter(i); setReciter(-1); setPlayingKey(null); setFullPlaying(false); }}>
                      <Text style={[styles.reciterTxt, fullReciter === i && styles.reciterTxtOn]}>{r.label}</Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </>
            }
            renderItem={({ item, index }) => (
              <View style={styles.ayahItem}>
                <View style={styles.ayahHead}>
                  <View style={styles.ayahBadge}><Text style={styles.ayahBadgeTxt}>{index + 1}</Text></View>
                  <Text style={styles.ayahArList}>{item.a}</Text>
                </View>
                {item.z ? <Text style={styles.ayahZh}>🇨🇳 {item.z}</Text> : null}
                <View style={styles.ayahBtns}>
                  <TouchableOpacity style={styles.miniBtn} onPress={() => speak(item.a)}>
                    <Text style={styles.miniBtnTxt}>🔊</Text>
                  </TouchableOpacity>
                  {reciter >= 0 ? (
                    <TouchableOpacity
                      style={[styles.miniBtn, styles.miniBtnGold, playingKey === surah.id + '_' + index && styles.miniBtnPlaying]}
                      onPress={() => playRecitation(surah.id, index)}
                    >
                      <Text style={styles.miniBtnTxt}>{playingKey === surah.id + '_' + index ? '⏹' : '🎙'} 诵读</Text>
                    </TouchableOpacity>
                  ) : null}
                  <TouchableOpacity
                    style={[styles.miniBtn, styles.miniBtnGold]}
                    onPress={() => analyzeAyah(index)}
                    disabled={loading}
                  >
                    <Text style={styles.miniBtnTxt}>{loading ? '⏳' : '🔬'} 逐字分解</Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={[styles.miniBtn, styles.miniBtnGold, bookmarks[surah.id + '_' + index] && styles.miniBtnPlaying]}
                    onPress={() => toggleBookmark(surah.id, index)}
                  >
                    <Text style={styles.miniBtnTxt}>{bookmarks[surah.id + '_' + index] ? '⭐' : '☆'} 书签</Text>
                  </TouchableOpacity>
                  {TAFSIR.some((t) => t.surah === surah.id && t.ayah === index + 1) ? (
                    <TouchableOpacity
                      style={[styles.miniBtn, styles.miniBtnGold]}
                      onPress={() => setTafsirOpen((prev) => ({ ...prev, [surah.id + '_' + index]: !prev[surah.id + '_' + index] }))}
                    >
                      <Text style={styles.miniBtnTxt}>📖 经注</Text>
                    </TouchableOpacity>
                  ) : null}
                </View>
                {tafsirOpen[surah.id + '_' + index] ? (() => {
                  const t = TAFSIR.find((x) => x.surah === surah.id && x.ayah === index + 1);
                  return t ? (
                    <View style={styles.tafsirBox}>
                      <Text style={styles.tafsirLabel}>📖 经注（{t.source}）</Text>
                      <Text style={styles.tafsirBody}>{t.tafsir}</Text>
                    </View>
                  ) : null;
                })() : null}
              </View>
            )}
          />
        ) : view === 'analysis' && analysis ? (
          renderAnalysis()
        ) : (
          // 章节列表
          <FlatList
            style={styles.body}
            data={QURAN.filter((x) => {
              if (!q) return true;
              const s = String(x.id) + x.n + (x.tz || '') + x.t;
              return s.includes(q);
            })}
            keyExtractor={(item) => String(item.id)}
            numColumns={2}
            columnWrapperStyle={{ gap: 8 }}
            contentContainerStyle={{ padding: 16, paddingBottom: 40, gap: 8 }}
            ListHeaderComponent={
              <>
                <TouchableOpacity
                  style={[styles.allPlayBtn, fullPlaying && styles.allPlayBtnOn]}
                  onPress={() => setView('full')}
                >
                  <Text style={styles.allPlayTxt}>
                    📼 整章诵读（{fullReciter >= 0 ? FULL_RECITERS[fullReciter].label.replace('📼 ', '') : '选诵读家·整章连诵'}）
                  </Text>
                </TouchableOpacity>
                <TextInput
                  style={styles.searchInput}
                  placeholder="🔍 搜索章节（编号 / 阿语名 / 中文名）"
                  placeholderTextColor="#9aa88f"
                  value={q}
                  onChangeText={setQ}
                />
                <Text style={styles.quickLabel}>✨ 常用章节</Text>
                <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 6, paddingBottom: 6 }}>
                  {[[1, '法谛哈'], [2, '黄牛·库尔西'], [18, '山洞'], [36, '雅辛'], [55, '至仁主'], [56, '大事'], [67, '国权'], [112, '忠诚'], [113, '曙光'], [114, '世人']].map(([id, name]) => {
                    const ch = QURAN.find((x) => x.id === id);
                    return ch ? (
                      <TouchableOpacity key={id} style={styles.quickChip} onPress={() => openSurah(ch)}>
                        <Text style={styles.quickTxt}>{id}. {name}</Text>
                      </TouchableOpacity>
                    ) : null;
                  })}
                </ScrollView>
                {recent.length > 0 ? (
                  <>
                    <Text style={styles.quickLabel}>🕘 最近阅读</Text>
                    <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 6, paddingBottom: 6 }}>
                      {recent.map((r) => {
                        const ch = QURAN.find((x) => x.id === r.id);
                        return ch ? (
                          <TouchableOpacity key={r.id} style={styles.quickChip} onPress={() => openSurah(ch)}>
                            <Text style={styles.quickTxt}>{r.id}. {r.tz || r.n}</Text>
                          </TouchableOpacity>
                        ) : null;
                      })}
                    </ScrollView>
                  </>
                ) : null}
                {Object.keys(bookmarks).length > 0 ? (
                  <>
                    <Text style={styles.quickLabel}>⭐ 我的书签（{Object.keys(bookmarks).length}）</Text>
                    <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 6, paddingBottom: 6 }}>
                      {Object.keys(bookmarks).slice(0, 20).map((key) => {
                        const [sid, aidx] = key.split('_').map(Number);
                        const ch = QURAN.find((x) => x.id === sid);
                        if (!ch) return null;
                        return (
                          <TouchableOpacity key={key} style={styles.quickChip} onPress={() => openSurah(ch)}>
                            <Text style={styles.quickTxt}>{ch.tz || ch.n} {aidx + 1}节</Text>
                          </TouchableOpacity>
                        );
                      })}
                    </ScrollView>
                  </>
                ) : null}
                <Text style={styles.quickLabel}>📖 全部 114 章</Text>
              </>
            }
            renderItem={({ item }) => (
              <TouchableOpacity style={[styles.surahItem, readSet[item.id] && styles.surahItemRead]} onPress={() => openSurah(item)}>
                <View style={styles.surahNum}><Text style={styles.surahNumTxt}>{item.id}</Text></View>
                <Text style={styles.surahName}>{item.n}</Text>
                <Text style={styles.surahZh}>{item.tz || item.t}</Text>
                <Text style={styles.surahMeta}>{readSet[item.id] ? '✅ 已读' : `${item.vs.length} 节`}</Text>
              </TouchableOpacity>
            )}
          />
        )}

        {/* 返回/关闭 */}
        <View style={styles.footer}>
          <TouchableOpacity style={styles.closeBtn} onPress={closeAll}>
            <Text style={styles.closeTxt}>✕ 关闭</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
}

function WordInfo({ label, value, wide }) {
  return (
    <View style={[styles.wordInfo, wide && styles.wordInfoWide]}>
      <Text style={styles.wordInfoLabel}>{label}</Text>
      <Text style={styles.wordInfoValue}>{value || '—'}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: Colors.cream },
  body: { flex: 1 },
  footer: { padding: 12, alignItems: 'center', borderTopWidth: 1, borderTopColor: 'rgba(201,168,76,0.15)' },
  closeBtn: { paddingHorizontal: 20, paddingVertical: 9, borderRadius: 18, backgroundColor: Colors.greenDark },
  closeTxt: { fontSize: 12, color: Colors.goldLight, fontWeight: '700' },
  backBtn: { alignSelf: 'flex-start', padding: 8 },
  backTxt: { fontSize: 12, color: Colors.green },
  surahTitle: { fontSize: 18, fontWeight: '800', color: Colors.greenDark, textAlign: 'center', marginTop: 4 },
  surahMeta: { fontSize: 10.5, color: Colors.muted, textAlign: 'center', marginTop: 4, marginBottom: 12 },
  reciterRow: { flexDirection: 'row', alignItems: 'center', flexWrap: 'wrap', gap: 6, marginBottom: 12, justifyContent: 'center' },
  reciterLabel: { fontSize: 11, color: Colors.muted, fontWeight: '700' },
  allPlayBtn: {
    backgroundColor: Colors.greenDark, borderRadius: 14, paddingVertical: 11,
    alignItems: 'center', marginBottom: 10, borderWidth: 1, borderColor: 'rgba(201,168,76,0.5)',
  },
  allPlayBtnOn: { backgroundColor: 'rgba(192,57,43,0.15)', borderColor: 'rgba(192,57,43,0.4)' },
  allPlayTxt: { fontSize: 12.5, fontWeight: '800', color: Colors.goldLight },
  reciterChip: {
    paddingHorizontal: 10, paddingVertical: 5, borderRadius: 13,
    backgroundColor: Colors.white, borderWidth: 1, borderColor: 'rgba(201,168,76,0.35)',
  },
  reciterOn: { backgroundColor: Colors.greenDark, borderColor: 'rgba(201,168,76,0.5)' },
  reciterTxt: { fontSize: 10, fontWeight: '700', color: Colors.ink },
  reciterTxtOn: { color: '#fff' },
  miniBtnPlaying: { backgroundColor: 'rgba(192,57,43,0.15)', borderColor: 'rgba(192,57,43,0.4)' },
  ayahNum: { fontSize: 11, color: Colors.muted, textAlign: 'center', marginTop: 4 },
  surahItemRead: { borderColor: 'rgba(26,138,92,0.5)', backgroundColor: 'rgba(26,138,92,0.05)' },
  surahItem: {
    flex: 1, backgroundColor: Colors.white, borderRadius: Radius.md, padding: 12,
    borderWidth: 1, borderColor: 'rgba(201,168,76,0.16)', alignItems: 'center', minHeight: 110,
  },
  surahNum: {
    width: 30, height: 30, borderRadius: 15, backgroundColor: 'rgba(201,168,76,0.12)',
    alignItems: 'center', justifyContent: 'center', marginBottom: 6,
  },
  surahNumTxt: { fontSize: 13, fontWeight: '800', color: Colors.goldDark },
  surahName: { fontFamily: 'serif', fontSize: 15, fontWeight: '700', color: Colors.greenDark },
  surahZh: { fontSize: 10, color: Colors.ink, marginTop: 2, textAlign: 'center' },
  ayahItem: {
    backgroundColor: Colors.white, borderRadius: Radius.md, padding: 14, marginBottom: 8,
    borderWidth: 1, borderColor: 'rgba(201,168,76,0.14)',
  },
  ayahHead: { flexDirection: 'row', alignItems: 'flex-start' },
  ayahBadge: {
    width: 24, height: 24, borderRadius: 12, backgroundColor: Colors.greenDark,
    alignItems: 'center', justifyContent: 'center', marginRight: 8, marginTop: 2,
  },
  ayahBadgeTxt: { fontSize: 11, color: Colors.goldLight, fontWeight: '700' },
  ayahArList: { fontFamily: 'serif', fontSize: 16, fontWeight: '700', color: Colors.greenDark, flex: 1, writingDirection: 'rtl', lineHeight: 30 },
  ayahZh: { fontSize: 11, color: Colors.green, marginTop: 8, lineHeight: 19 },
  tafsirBox: {
    marginTop: 8, backgroundColor: '#fdf6e3', borderRadius: 12, padding: 12,
    borderWidth: 1, borderColor: 'rgba(201,168,76,0.35)',
  },
  tafsirLabel: { fontSize: 11, fontWeight: '800', color: Colors.goldDark, marginBottom: 5 },
  tafsirBody: { fontSize: 11.5, color: Colors.ink, lineHeight: 20 },
  searchInput: {
    backgroundColor: '#fff', borderWidth: 1, borderColor: 'rgba(201,168,76,.35)',
    borderRadius: 12, paddingHorizontal: 14, paddingVertical: 9, fontSize: 13, color: Colors.ink,
    marginBottom: 10,
  },
  quickLabel: { fontSize: 12.5, fontWeight: '800', color: Colors.goldDark, marginTop: 4, marginBottom: 6 },
  quickChip: {
    backgroundColor: 'rgba(201,168,76,.14)', borderWidth: 1, borderColor: 'rgba(201,168,76,.3)',
    borderRadius: 10, paddingHorizontal: 11, paddingVertical: 7,
  },
  quickTxt: { fontSize: 11.5, fontWeight: '700', color: Colors.greenDark },
  ayahBtns: { flexDirection: 'row', gap: 8, marginTop: 10, justifyContent: 'flex-end' },
  miniBtn: {
    paddingHorizontal: 12, paddingVertical: 6, borderRadius: 14,
    backgroundColor: 'rgba(26,92,74,0.08)', borderWidth: 1, borderColor: 'rgba(26,92,74,0.3)',
  },
  miniBtnGold: { backgroundColor: 'rgba(201,168,76,0.12)', borderColor: 'rgba(201,168,76,0.4)' },
  miniBtnTxt: { fontSize: 10.5, fontWeight: '700', color: Colors.ink },
  ayahCard: {
    backgroundColor: Colors.greenDark, borderRadius: Radius.lg, padding: 18, marginTop: 8,
  },
  ayahAr: {
    fontFamily: 'serif', fontSize: 17, fontWeight: '700', color: Colors.goldLight,
    textAlign: 'center', lineHeight: 32, writingDirection: 'rtl',
  },
  listenBtn: {
    marginTop: 10, paddingVertical: 11, borderRadius: Radius.md,
    backgroundColor: Colors.gold, alignItems: 'center',
  },
  listenTxt: { fontSize: 12.5, fontWeight: '700', color: '#fff' },
  sectionLabel: { fontSize: 13, fontWeight: '700', color: Colors.greenDark, marginTop: 16, marginBottom: 8 },
  wordCard: {
    backgroundColor: Colors.white, borderRadius: Radius.md, padding: 12, marginBottom: 8,
    borderWidth: 1, borderColor: 'rgba(201,168,76,0.16)',
  },
  wordHead: { flexDirection: 'row', alignItems: 'center', marginBottom: 8 },
  wordAr: { fontFamily: 'serif', fontSize: 17, fontWeight: '800', color: Colors.greenDark, writingDirection: 'rtl' },
  wordPos: {
    fontSize: 10, fontWeight: '700', color: Colors.goldDark,
    backgroundColor: 'rgba(201,168,76,0.12)', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 10,
  },
  wordGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  wordInfo: { width: '48%', backgroundColor: 'rgba(247,243,236,0.6)', borderRadius: 10, padding: 7 },
  wordInfoWide: { width: '100%' },
  wordInfoLabel: { fontSize: 9, color: Colors.muted },
  wordInfoValue: { fontSize: 11.5, color: Colors.ink, marginTop: 2, lineHeight: 16 },
  err: { fontSize: 12, color: Colors.danger, textAlign: 'center', marginTop: 20, lineHeight: 20 },
});
