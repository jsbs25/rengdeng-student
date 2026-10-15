// AI 阿拉伯音乐生成：提示词 → MusicGen 本地生成 → 播放
import React, { useState, useRef } from 'react';
import {
  View, Text, Modal, TextInput, TouchableOpacity, StyleSheet, ScrollView, ActivityIndicator, Alert,
} from 'react-native';
import { Colors, Radius } from './theme';
import { ArchHeader } from './components';
import { getApiBase } from './api';
import AsyncStorage from '@react-native-async-storage/async-storage';

const PRESETS = [
  '阿拉伯传统音乐，乌德琴与纳伊笛，沉思的木卡姆旋律',
  '宁静的阿拉伯祈祷氛围音乐，笛声悠扬，缓慢冥想',
  '阿拉伯庆典鼓乐，达布卡鼓节奏，欢快热情',
  '沙漠夜晚的阿拉伯旋律，乌德琴独奏，神秘悠远',
  '阿拉伯咖啡馆音乐，传统乐器合奏，温馨典雅',
  '苏菲旋转舞音乐，纳伊笛与手鼓，空灵神圣',
];

export default function MusicModal({ visible, onClose }) {
  const [prompt, setPrompt] = useState('');
  const [seconds, setSeconds] = useState(10);
  const [lyricsLang, setLyricsLang] = useState(''); // ''纯音乐 'zh'中文 'en'英文 'ar'阿语
  const [lyrics, setLyrics] = useState('');
  const [busy, setBusy] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const [msg, setMsg] = useState('');
  const soundRef = useRef(null);

  const closeAll = () => {
    try { if (soundRef.current) { soundRef.current.unloadAsync().catch(() => {}); soundRef.current = null; } } catch (e) {}
    setAudioUrl(null);
    setMsg('');
    onClose();
  };

  const generate = async () => {
    if (!prompt.trim()) { Alert.alert('提示', '请先输入音乐描述'); return; }
    setBusy(true);
    setMsg(seconds > 45
      ? '🎵 AI 正在创作完整歌曲（' + seconds + ' 秒，4 段续写中）...预计 6-10 分钟，请耐心等待，生成完自动播放'
      : '🎵 AI 正在创作...（' + seconds + ' 秒约 ' + Math.ceil(seconds / 10 * 0.7) + ' 分钟，请稍候）');
    setAudioUrl(null);
    try {
      const base = await getApiBase();
      const res = await fetch(`${base}/api/music`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: prompt.trim(), seconds, lang: lyricsLang, device_id: (await AsyncStorage.getItem('nur_device_id')) || '' }),
      });
      const data = await res.json();
      if (data.url) {
        const full = base + data.url;
        setAudioUrl(full);
        setLyrics(data.lyrics || '');
        setMsg(`✅ 生成完成！时长 ${data.duration || '?'} 秒${data.lyrics ? '（含歌词）' : ''}，自动播放中`);
        // 自动播放
        try {
          const { Audio } = require('expo-av');
          if (soundRef.current) { soundRef.current.unloadAsync().catch(() => {}); }
          const { sound } = await Audio.Sound.createAsync({ uri: full });
          soundRef.current = sound;
          await sound.playAsync();
        } catch (e) {}
      } else {
        setMsg('⚠️ ' + (data.error || '生成失败，请重试'));
      }
    } catch (e) {
      setMsg('⚠️ 无法连接 AI 服务器：请确认电脑 App/服务器已运行，且手机与电脑在同一 WiFi');
    }
    setBusy(false);
  };

  const stopPlay = async () => {
    try { if (soundRef.current) { await soundRef.current.stopAsync(); soundRef.current.unloadAsync().catch(() => {}); soundRef.current = null; } } catch (e) {}
  };

  return (
    <Modal visible={visible} animationType="slide" onRequestClose={closeAll}>
      <View style={styles.root}>
        <ArchHeader title="🎵 AI 阿拉伯音乐" subtitle="MUSIC AI" zh="提示词 · 生成 · 聆听" />
        <ScrollView style={styles.body} contentContainerStyle={{ padding: 16, paddingBottom: 40 }}>
          <Text style={styles.label}>🎼 描述你想要的音乐</Text>
          <TextInput
            style={styles.input}
            placeholder="例如：宁静的阿拉伯祈祷氛围音乐，笛声悠扬，缓慢冥想"
            placeholderTextColor="#9aa88f"
            multiline
            value={prompt}
            onChangeText={setPrompt}
          />
          <Text style={styles.label}>✨ 快捷灵感</Text>
          <View style={styles.presetWrap}>
            {PRESETS.map((p, i) => (
              <TouchableOpacity key={i} style={styles.preset} onPress={() => setPrompt(p)}>
                <Text style={styles.presetTxt}>{p}</Text>
              </TouchableOpacity>
            ))}
          </View>
          <Text style={styles.label}>🎤 歌词语言（可选）</Text>
          <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8 }}>
            {[['', '🎹 纯音乐'], ['zh', '🇨🇳 中文'], ['en', '🇬🇧 English'], ['ar', '🇸🇦 العربية']].map(([v, label]) => (
              <TouchableOpacity
                key={v}
                style={[styles.secBtn, lyricsLang === v && styles.secBtnOn]}
                onPress={() => setLyricsLang(v)}
              >
                <Text style={[styles.secTxt, lyricsLang === v && styles.secTxtOn]}>{label}</Text>
              </TouchableOpacity>
            ))}
          </View>
          <Text style={styles.label}>⏱ 时长</Text>
          <View style={{ flexDirection: 'row', gap: 8 }}>
            {[10, 15, 20, 30, 60].map((s) => (
              <TouchableOpacity
                key={s}
                style={[styles.secBtn, seconds === s && styles.secBtnOn]}
                onPress={() => setSeconds(s)}
              >
                <Text style={[styles.secTxt, seconds === s && styles.secTxtOn]}>{s} 秒</Text>
              </TouchableOpacity>
            ))}
          </View>
          <TouchableOpacity style={[styles.genBtn, busy && { opacity: 0.6 }]} onPress={generate} disabled={busy}>
            {busy ? <ActivityIndicator color="#0f3d31" /> : <Text style={styles.genTxt}>{seconds >= 90 ? '🎵 生成完整歌曲（约2分钟）' : '🎵 生成阿拉伯音乐'}</Text>}
          </TouchableOpacity>
          <TouchableOpacity style={[styles.genBtn, { backgroundColor: '#0f3d31', marginTop: 8 }, busy && { opacity: 0.6 }]} onPress={() => { setSeconds(120); }} disabled={busy}>
            <Text style={[styles.genTxt, { color: '#e8d48b' }]}>🎶 完整歌曲模式（2分钟 · 约8分钟生成）</Text>
          </TouchableOpacity>
          {msg ? <Text style={styles.msg}>{msg}</Text> : null}
          {lyrics ? (
            <View style={styles.lyricsBox}>
              <Text style={styles.lyricsTitle}>📜 歌词（AI 创作）</Text>
              <Text style={styles.lyricsBody}>{lyrics}</Text>
            </View>
          ) : null}
          {audioUrl && !busy ? (
            <View style={{ flexDirection: 'row', gap: 8, marginTop: 6 }}>
              <TouchableOpacity style={[styles.genBtn, { flex: 1 }]} onPress={generate}>
                <Text style={styles.genTxt}>🔁 再生成一次</Text>
              </TouchableOpacity>
              <TouchableOpacity style={[styles.genBtn, { flex: 1, backgroundColor: '#b03a2e' }]} onPress={stopPlay}>
                <Text style={[styles.genTxt, { color: '#fff' }]}>⏹ 停止</Text>
              </TouchableOpacity>
            </View>
          ) : null}
          <Text style={styles.hint}>💡 提示：描述越具体越好——乐器（乌德琴/纳伊笛/达布卡鼓）、风格（木卡姆/苏菲/庆典）、情绪（宁静/欢快/神秘）</Text>
        </ScrollView>
        <View style={styles.footer}>
          <TouchableOpacity style={styles.closeBtn} onPress={closeAll}>
            <Text style={styles.closeTxt}>✕ 关闭</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: Colors.bg },
  body: { flex: 1 },
  label: { fontSize: 13, fontWeight: '800', color: Colors.greenDark, marginTop: 12, marginBottom: 6 },
  input: {
    backgroundColor: '#fff', borderWidth: 1, borderColor: 'rgba(201,168,76,.35)', borderRadius: 12,
    padding: 12, fontSize: 13.5, color: Colors.ink, minHeight: 72, textAlignVertical: 'top', lineHeight: 21,
  },
  presetWrap: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  preset: {
    backgroundColor: 'rgba(201,168,76,.14)', borderWidth: 1, borderColor: 'rgba(201,168,76,.3)',
    borderRadius: 10, paddingHorizontal: 10, paddingVertical: 7, maxWidth: '48%',
  },
  presetTxt: { fontSize: 11, fontWeight: '700', color: Colors.greenDark, lineHeight: 15 },
  secBtn: { backgroundColor: '#fff', borderWidth: 1, borderColor: 'rgba(201,168,76,.3)', borderRadius: 10, paddingHorizontal: 16, paddingVertical: 8 },
  secBtnOn: { backgroundColor: Colors.greenDark, borderColor: Colors.greenDark },
  secTxt: { fontSize: 12.5, fontWeight: '700', color: Colors.greenDark },
  secTxtOn: { color: Colors.gold },
  genBtn: {
    backgroundColor: Colors.gold, borderRadius: 12, paddingVertical: 13, alignItems: 'center',
    marginTop: 16, minHeight: 46, justifyContent: 'center',
  },
  genTxt: { fontSize: 14, fontWeight: '800', color: Colors.greenDark },
  msg: { fontSize: 12, color: Colors.greenDark, marginTop: 12, lineHeight: 19 },
  hint: { fontSize: 10.5, color: '#8a9c8f', marginTop: 16, lineHeight: 17 },
  lyricsBox: { backgroundColor: '#fdf6e3', borderWidth: 1, borderColor: 'rgba(201,168,76,.35)', borderRadius: 12, padding: 12, marginTop: 14 },
  lyricsTitle: { fontSize: 12, fontWeight: '800', color: '#a8892e', marginBottom: 8 },
  lyricsBody: { fontSize: 12.5, color: Colors.ink, lineHeight: 22, textAlign: 'left' },
  footer: { padding: 14, borderTopWidth: 1, borderTopColor: 'rgba(201,168,76,.2)' },
  closeBtn: { backgroundColor: '#fff', borderWidth: 1, borderColor: 'rgba(201,168,76,.3)', borderRadius: 12, paddingVertical: 11, alignItems: 'center' },
  closeTxt: { fontSize: 13, fontWeight: '700', color: Colors.greenDark },
});
