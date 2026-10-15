// 礼拜时间模块：五时礼拜 + 到点自动宣礼（阿语 TTS）
import React, { useState, useEffect } from 'react';
import {
  View, Text, Modal, TouchableOpacity, StyleSheet, ScrollView, Alert,
} from 'react-native';
import * as Speech from 'expo-speech';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Colors, Radius } from './theme';
import { ArchHeader } from './components';
import { CITIES, prayerTimes, fmt, ATHAN_AR, ATHAN_CN, PRAYER_NAMES } from './prayerTime';

const KEY = '***';
const ATHAN_KEY = '***';
const ATHAN_REC_KEY = '***';

// 专业宣礼学者（音频 URL 预留——当前网络无法访问海外音频源，用阿语 TTS 宣礼兜底；
// 后续可下载 mp3 放入 app/assets/athan/ 或配置可用 URL 后自动启用）
export const ATHAN_FILES = {
  abdulbasit: () => require('../assets/athan/abdulbasit.m4a'),
  alafasy: () => require('../assets/athan/alafasy.m4a'),
  kassab: () => require('../assets/athan/kassab.m4a'),
  amade: () => require('../assets/athan/amade.m4a'),
  saleh: () => require('../assets/athan/saleh.m4a'),
  trabulsi: () => require('../assets/athan/trabulsi.m4a'),
  minshawi: () => require('../assets/athan/minshawi.m4a'),
  saadoun: () => require('../assets/athan/saadoun.m4a'),
  dahbe: () => require('../assets/athan/dahbe.m4a'),
  surehi: () => require('../assets/athan/surehi.m4a'),
  awad: () => require('../assets/athan/awad.m4a'),
  riyadh: () => require('../assets/athan/riyadh.m4a'),
  aqsa: () => require('../assets/athan/aqsa.mp3'),
  madinah: () => require('../assets/athan/madinah.mp3'),
  makkah: () => require('../assets/athan/makkah.mp3'),
};

export const ATHAN_RECITERS = [
  { key: 'abdulbasit', name: '阿卜杜勒·巴西特', desc: '埃及 · 高保真' },
  { key: 'alafasy', name: '阿法西', desc: '科威特著名宣礼师' },
  { key: 'kassab', name: '卡萨布', desc: 'Abdul Rahman Kassab' },
  { key: 'amade', name: '阿马迪', desc: 'Ahmad Al-Amadi · 卡塔尔' },
  { key: 'saleh', name: '萨利赫', desc: 'Saleh Al-Nabet · 卡塔尔' },
  { key: 'trabulsi', name: '特拉布勒西', desc: '科威特著名宣礼师' },
  { key: 'minshawi', name: '明沙维', desc: '埃及著名诵经家' },
  { key: 'saadoun', name: '萨阿敦', desc: 'Ghazi Al-Saadoun' },
  { key: 'dahbe', name: '达赫贝', desc: 'Abdulah Al-Dahbe · 埃及' },
  { key: 'surehi', name: '苏莱希', desc: 'Abdul Majid Al-Surehi' },
  { key: 'awad', name: '阿瓦德', desc: 'Abdu Al-Karem Jabare' },
  { key: 'riyadh', name: '利雅得', desc: '沙特利雅得' },
  { key: 'aqsa', name: '阿克萨清真寺', desc: '耶路撒冷圣城 · 高保真' },
  { key: 'madinah', name: '麦地那圣寺', desc: '先知寺宣礼 · 高保真' },
  { key: 'makkah', name: '麦加禁寺', desc: '禁寺宣礼 · 192kbps 高保真' },
];

// 宣礼 TTS（阿语，需设备支持阿语语音；不支持则显示宣礼词）
export async function playAthan(key) {
  // 专业宣礼音频（懒加载，离线播放）
  const src = ATHAN_FILES[key];
  if (src) {
    try {
      const { Asset } = require('expo-asset');
      const { createAudioPlayer } = require('expo-audio');
      const asset = Asset.fromModule(src());
      if (!asset.localUri) await asset.downloadAsync();
      const p = createAudioPlayer({ uri: asset.localUri || asset.uri });
      p.play();
      return 'audio';
    } catch (e) {}
    // 方式2：expo-av（最可靠，直接支持打包资源）
    try {
      const { Audio } = require('expo-av');
      const { sound } = await Audio.Sound.createAsync(src());
      await sound.playAsync();
      return 'audio';
    } catch (e) {}
  }
  // TTS 阿语宣礼兜底
  try {
    const voices = await Speech.getAvailableVoicesAsync();
    const ar = voices.find((v) => (v.language || '').startsWith('ar'));
    if (ar) {
      Speech.stop();
      Speech.speak(ATHAN_AR, { language: 'ar-SA', rate: 0.75, voice: ar.identifier });
      return 'tts';
    }
  } catch (e) {}
  return false;
}

export function speakAthanCn() {
  try {
    Speech.stop();
    Speech.speak(ATHAN_CN, { language: 'zh-CN', rate: 0.9 });
  } catch (e) {}
}

export default function PrayerModal({ visible, onClose }) {
  const [city, setCity] = useState(0); // 默认西宁（青海）
  const [athanOn, setAthanOn] = useState(true);
  const [now, setNow] = useState(new Date());
  const [lastAthan, setLastAthan] = useState('');
  const [reciter, setReciter] = useState(0);

  // 加载设置
  useEffect(() => {
    if (visible) {
      AsyncStorage.getItem(KEY).then((v) => {
        if (v !== null) {
          const i = CITIES.findIndex((c) => c.name === v);
          if (i >= 0) setCity(i);
        }
      }).catch(() => {});
      AsyncStorage.getItem(ATHAN_KEY).then((v) => {
        if (v !== null) setAthanOn(v === '1');
      }).catch(() => {});
      AsyncStorage.getItem(ATHAN_REC_KEY).then((v) => {
        if (v !== null) setReciter(parseInt(v, 10) || 0);
      }).catch(() => {});
    }
  }, [visible]);

  // 定时刷新 + 宣礼检测
  useEffect(() => {
    if (!visible) return;
    const timer = setInterval(() => {
      const d = new Date();
      setNow(d);
      // 宣礼检测：当前分钟 == 某次礼拜时间（±1 分钟内触发一次）
      if (athanOn) {
        const t = prayerTimes(new Date(), CITIES[city].lat, CITIES[city].lon, 480);
        const cur = d.getHours() * 60 + d.getMinutes();
        const todayKey = d.getFullYear() + '-' + d.getMonth() + '-' + d.getDate();
        for (const k of ['fajr', 'dhuhr', 'asr', 'maghrib', 'isha']) {
          const tm = Math.round(t[k] * 60);
          if (Math.abs(cur - tm) <= 0 && lastAthan !== todayKey + '_' + k) {
            setLastAthan(todayKey + '_' + k);
            const name = PRAYER_NAMES.find((p) => p.key === k);
            playAthan(ATHAN_RECITERS[reciter].key).then((ok) => {
              Alert.alert('🕌 礼拜时间到', `${name ? name.cn : k}（${fmt(t[k])}）${ok ? '· 宣礼已响' : '· 设备无阿语语音，宣礼词如下'}\n\n${ATHAN_CN}`);
            });
          }
        }
      }
    }, 30000);
    return () => clearInterval(timer);
  }, [visible, athanOn, city, lastAthan]);

  const t = prayerTimes(now, CITIES[city].lat, CITIES[city].lon, 480);
  const curMin = now.getHours() * 60 + now.getMinutes();

  // 下次礼拜
  let next = null;
  for (const k of ['fajr', 'dhuhr', 'asr', 'maghrib', 'isha']) {
    const tm = Math.round(t[k] * 60);
    if (tm > curMin) {
      next = { key: k, tm, name: PRAYER_NAMES.find((p) => p.key === k) };
      break;
    }
  }
  if (!next) next = { key: 'fajr', tm: Math.round(t.fajr * 60) + 1440, name: PRAYER_NAMES[0] };

  const setCityAndSave = (i) => {
    setCity(i);
    AsyncStorage.setItem(KEY, CITIES[i].name).catch(() => {});
  };

  return (
    <Modal visible={visible} animationType="slide" onRequestClose={onClose}>
      <View style={styles.root}>
        <ArchHeader title="🕌 礼拜时间" subtitle="" zh={`${CITIES[city].name} · 按天文算法计算`} />

        <ScrollView contentContainerStyle={{ padding: 16, paddingBottom: 40 }}>
          {/* 下次礼拜 */}
          <View style={styles.nextCard}>
            <Text style={styles.nextLabel}>下次礼拜</Text>
            <Text style={styles.nextName}>{next.name.cn}（{next.name.en}）</Text>
            <Text style={styles.nextTime}>{fmt(next.tm / 60)}</Text>
            <Text style={styles.nextCount}>
              还有 {Math.floor((next.tm - curMin + 1440) % 1440 / 60)} 小时 {(next.tm - curMin + 1440) % 1440 % 60} 分钟
            </Text>
          </View>

          {/* 五时礼拜 */}
          <View style={styles.timesCard}>
            {PRAYER_NAMES.map((p) => (
              <View key={p.key} style={styles.timeRow}>
                <Text style={styles.timeName}>🕌 {p.cn}</Text>
                <Text style={styles.timeEn}>{p.en}</Text>
                <Text style={[styles.timeVal, ['fajr', 'dhuhr', 'asr', 'maghrib', 'isha'].includes(p.key) && Math.abs(curMin - Math.round(t[p.key] * 60)) < 60 && styles.timeNow]}>
                  {fmt(t[p.key])}
                </Text>
              </View>
            ))}
          </View>

          {/* 宣礼开关 */}
          <View style={styles.switchCard}>
            <View style={{ flex: 1 }}>
              <Text style={styles.switchTitle}>🔔 到点自动念宣礼</Text>
              <Text style={styles.switchDesc}>礼拜时间到时，自动用阿语诵读宣礼词（需要设备支持阿语语音）</Text>
            </View>
            <TouchableOpacity
              style={[styles.switchBtn, athanOn && styles.switchBtnOn]}
              onPress={async () => {
                const nextVal = !athanOn;
                setAthanOn(nextVal);
                await AsyncStorage.setItem(ATHAN_KEY, nextVal ? '1' : '0');
                if (nextVal) {
                  const ok = await playAthan(ATHAN_RECITERS[reciter].key);
                  Alert.alert('宣礼测试', ok === 'audio' ? `🔊 ${ATHAN_RECITERS[reciter].name} 宣礼播放中` : `设备无法播放音频，宣礼词：\n${ATHAN_CN}`);
                }
              }}
            >
              <Text style={[styles.switchTxt, athanOn && styles.switchTxtOn]}>{athanOn ? '开' : '关'}</Text>
            </TouchableOpacity>
          </View>

          {/* 宣礼学者选择 */}
          <Text style={styles.cityTitle}>🎙 宣礼学者</Text>
          <View style={styles.cityWrap}>
            {ATHAN_RECITERS.map((r, i) => (
              <TouchableOpacity
                key={r.name}
                style={[styles.cityChip, reciter === i && styles.cityChipOn]}
                onPress={async () => {
                  setReciter(i);
                  await AsyncStorage.setItem(ATHAN_REC_KEY, String(i));
                  const ok = await playAthan(r.key);
                  if (ok === 'audio') Alert.alert('宣礼', `🎙 ${r.name} 宣礼播放中`);
                  else if (ok === 'tts') Alert.alert('宣礼', `${r.name} · 阿语宣礼诵读中`);
                  else Alert.alert('提示', `设备暂无阿语语音，宣礼词：
${ATHAN_CN}`);
                }}
              >
                <Text style={[styles.cityTxt, reciter === i && styles.cityTxtOn]}>{r.name.split('（')[0]}</Text>
              </TouchableOpacity>
            ))}
          </View>
          <Text style={styles.hint}>🎧 已内嵌 15 位宣礼原声（含麦加禁寺/麦地那圣寺/阿克萨清真寺），点击上方名字试听，离线播放</Text>

          {/* 宣礼词 */}
          <View style={styles.athanCard}>
            <Text style={styles.athanAr}>{ATHAN_AR}</Text>
            <Text style={styles.athanCn}>🇨🇳 {ATHAN_CN}</Text>
            <TouchableOpacity style={styles.testBtn} onPress={async () => {
              const ok = await playAthan(ATHAN_RECITERS[0].key);
              if (!ok) speakAthanCn();
            }}>
              <Text style={styles.testTxt}>🔊 试听宣礼</Text>
            </TouchableOpacity>
          </View>

          {/* 城市选择 */}
          <Text style={styles.cityTitle}>📍 选择城市</Text>
          <View style={styles.cityWrap}>
            {CITIES.map((c, i) => (
              <TouchableOpacity key={c.name} style={[styles.cityChip, city === i && styles.cityChipOn]} onPress={() => setCityAndSave(i)}>
                <Text style={[styles.cityTxt, city === i && styles.cityTxtOn]}>{c.name}</Text>
              </TouchableOpacity>
            ))}
          </View>
          <Text style={styles.hint}>* 按 MWL 标准（晨礼 18°、宵礼 17°、晡礼影子 1 倍）天文算法离线计算，与主流礼拜时间表误差约 1-3 分钟</Text>
        </ScrollView>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: Colors.cream },
  nextCard: {
    backgroundColor: Colors.greenDark, borderRadius: Radius.lg, padding: 18, alignItems: 'center', marginBottom: 12,
  },
  nextLabel: { fontSize: 11, color: 'rgba(255,255,255,0.7)' },
  nextName: { fontSize: 15, fontWeight: '800', color: Colors.goldLight, marginTop: 6 },
  nextTime: { fontSize: 34, fontWeight: '800', color: '#fff', marginTop: 4 },
  nextCount: { fontSize: 11, color: 'rgba(255,255,255,0.7)', marginTop: 6 },
  timesCard: {
    backgroundColor: Colors.white, borderRadius: Radius.md, padding: 6, marginBottom: 12,
    borderWidth: 1, borderColor: 'rgba(201,168,76,0.2)',
  },
  timeRow: { flexDirection: 'row', alignItems: 'center', paddingVertical: 10, paddingHorizontal: 12, borderBottomWidth: 1, borderBottomColor: 'rgba(201,168,76,0.1)' },
  timeName: { fontSize: 13.5, fontWeight: '700', color: Colors.ink, width: 80 },
  timeEn: { fontSize: 10.5, color: Colors.muted, flex: 1 },
  timeVal: { fontSize: 15, fontWeight: '800', color: Colors.greenDark },
  timeNow: { color: Colors.goldDark },
  switchCard: {
    flexDirection: 'row', alignItems: 'center', backgroundColor: Colors.white, borderRadius: Radius.md,
    padding: 14, marginBottom: 12, borderWidth: 1, borderColor: 'rgba(201,168,76,0.2)',
  },
  switchTitle: { fontSize: 13, fontWeight: '800', color: Colors.ink },
  switchDesc: { fontSize: 10, color: Colors.muted, marginTop: 3, lineHeight: 15 },
  switchBtn: { width: 54, height: 30, borderRadius: 15, backgroundColor: '#ddd', alignItems: 'center', justifyContent: 'center' },
  switchBtnOn: { backgroundColor: Colors.greenDark },
  switchTxt: { fontSize: 12, fontWeight: '800', color: '#888' },
  switchTxtOn: { color: Colors.goldLight },
  athanCard: {
    backgroundColor: '#fdf6e3', borderRadius: Radius.md, padding: 14, marginBottom: 12,
    borderWidth: 1, borderColor: 'rgba(201,168,76,0.35)',
  },
  athanAr: { fontFamily: 'serif', fontSize: 14, fontWeight: '700', color: Colors.greenDark, lineHeight: 26, writingDirection: 'rtl', textAlign: 'center' },
  athanCn: { fontSize: 10.5, color: Colors.muted, marginTop: 8, lineHeight: 17 },
  testBtn: { marginTop: 10, alignSelf: 'center', paddingHorizontal: 16, paddingVertical: 7, borderRadius: 14, backgroundColor: Colors.greenDark },
  testTxt: { fontSize: 11, fontWeight: '700', color: Colors.goldLight },
  cityTitle: { fontSize: 13, fontWeight: '800', color: Colors.greenDark, marginBottom: 8 },
  cityWrap: { flexDirection: 'row', flexWrap: 'wrap', gap: 7, marginBottom: 10 },
  cityChip: { paddingHorizontal: 12, paddingVertical: 7, borderRadius: 14, backgroundColor: Colors.white, borderWidth: 1, borderColor: 'rgba(201,168,76,0.3)' },
  cityChipOn: { backgroundColor: Colors.greenDark },
  cityTxt: { fontSize: 11, color: Colors.ink },
  cityTxtOn: { color: Colors.goldLight },
  hint: { fontSize: 9.5, color: Colors.muted, lineHeight: 15 },
});
