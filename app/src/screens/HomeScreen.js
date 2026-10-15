// 首页 HomeScreen
import React, { useEffect, useState, useMemo } from 'react';
import * as Speech from 'expo-speech';
import AsyncStorage from '@react-native-async-storage/async-storage';
import {
  View, Text, ScrollView, StyleSheet, TouchableOpacity,
} from 'react-native';
import { Colors, Shadows, Radius } from '../theme';
import { ArchHeader, GlassCard, ProgressRing, CategoryChip } from '../components';
import DATA from '../data';
import QUOTES from '../quotesData';
import { loadData } from '../api';
import { Store } from '../store';
import LibraryModal from '../LibraryModal';
import WordModal from '../WordModal';
import QuranModal from '../QuranModal';
import FlashcardModal from '../FlashcardModal';
import QuizModal from '../QuizModal';
import AlphabetModal from '../AlphabetModal';
import WordBookModal from '../WordBookModal';
import DialogModal from '../DialogModal';
import HistoryModal from '../HistoryModal';
import HadithModal from '../HadithModal';
import PrayerModal from '../PrayerModal';
import MusicModal from '../MusicModal';
import { SRS } from '../srs';

const DIALOGUES = DATA.dialogues || [];

export default function HomeScreen({ navigation }) {
  const [data, setData] = useState(DATA);
  const [stats, setStats] = useState(null);
  const [libOpen, setLibOpen] = useState(false);
  const [wordOpen, setWordOpen] = useState(false);
  const [quranOpen, setQuranOpen] = useState(false);
  const [flashOpen, setFlashOpen] = useState(false);
  const [reviewMode, setReviewMode] = useState(false);
  const [quizOpen, setQuizOpen] = useState(false);
  const [alphaOpen, setAlphaOpen] = useState(false);
  const [wbOpen, setWbOpen] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [histOpen, setHistOpen] = useState(false);
  const [hadithOpen, setHadithOpen] = useState(false);
  const [prayerOpen, setPrayerOpen] = useState(false);
  const [musicOpen, setMusicOpen] = useState(false);
  const [dueCount, setDueCount] = useState(0);
  const [checkinDone, setCheckinDone] = useState(false);
  const [dlgDone, setDlgDone] = useState(false);

  const doCheckin = async () => {
    if (checkinDone) return;
    await Store.addMinutes(5);
    try {
      const d = new Date();
      const key = 'nur_checkin_' + d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
      await AsyncStorage.setItem(key, '1');
    } catch (e) {}
    setCheckinDone(true);
    Store.getStats().then(setStats);
  };

  useEffect(() => {
    (async () => {
      const d = new Date();
      const key = 'nur_checkin_' + d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
      try {
        const v = await AsyncStorage.getItem(key);
        setCheckinDone(v === '1');
      } catch (e) {}
      try {
        const d = new Date();
        const dk = 'nur_dlg_done_' + d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
        const v2 = await AsyncStorage.getItem(dk);
        setDlgDone(v2 === '1');
      } catch (e) {}
    })();
  }, []);

  // 今日对话句数（与 DialogModal 相同 seed 逻辑）
  const dlgTodayTotal = useMemo(() => {
    const d = new Date();
    const seed = d.getFullYear() * 10000 + (d.getMonth() + 1) * 100 + d.getDate();
    const all = [...DIALOGUES];
    for (let i = all.length - 1; i > 0; i--) {
      const j = (seed + i * 7) % (i + 1);
      [all[i], all[j]] = [all[j], all[i]];
    }
    return all.slice(0, 10).reduce((n, s) => n + (s.dialogue || []).length * 2, 0);
  }, []);

  useEffect(() => {
    SRS.counts().then((c) => setDueCount(c.due));
  }, [flashOpen, wbOpen]);

  useEffect(() => {
    loadData().then(setData);
  }, []);

  useEffect(() => {
    Store.getStats().then(setStats);
    const sub = Store.subscribe ? Store.subscribe(setStats) : null;
    return () => sub && sub();
  }, []);

  // 每日经文/名言：按日期初始化，点击可随机切换（70 条池）
  const [daily, setDaily] = useState(null);
  useEffect(() => {
    if (!QUOTES.length) return;
    const today = new Date();
    const seed = today.getFullYear() * 10000 + (today.getMonth() + 1) * 100 + today.getDate();
    setDaily(pickQuote(seed));
  }, []);

  const pickQuote = (seed) => {
    const q = QUOTES[seed % QUOTES.length];
    return { a: q.a, c: q.z, e: q.e, src: q.src };
  };

  const nextQuote = () => {
    if (!QUOTES.length) return;
    let i = Math.floor(Math.random() * QUOTES.length);
    const cur = daily ? daily.a : '';
    let q = QUOTES[i];
    if (q.a === cur && QUOTES.length > 1) q = QUOTES[(i + 1) % QUOTES.length];
    setDaily({ a: q.a, c: q.z, e: q.e, src: q.src });
  };

  const goCat = (key) => navigation.navigate('Learn', { cat: key });

  const learned = stats ? stats.learnedWords : 0;
  const goal = stats ? stats.goalWords : 20;
  const percent = goal > 0 ? Math.min(100, Math.round((learned / goal) * 100)) : 0;
  const minutes = stats ? stats.todayMinutes : 0;
  const streak = stats ? stats.streakDays : 0;

  return (
    <>
    <ScrollView style={styles.scroll} contentContainerStyle={{ paddingBottom: 30 }} showsVerticalScrollIndicator={false}>
      <ArchHeader title="حامل المصباح" subtitle="燃灯者 · 无声却引人归途" />

      {/* 每日经文/名言（顶部） */}
      {daily ? (
        <View style={styles.section}>
          <TouchableOpacity style={styles.quoteCard} activeOpacity={0.85} onPress={nextQuote}>
            <Text style={styles.quoteMark}>❝</Text>
            <Text style={styles.quoteAr}>{daily.a}</Text>
            <Text style={styles.quoteCn}>{daily.c}</Text>
            {daily.src ? <Text style={styles.quoteSrc}>🕯 {daily.src}</Text> : null}
            <Text style={styles.quoteSwitch}>🔄 点击换一条</Text>
            <View style={styles.quoteBtns}>
              <TouchableOpacity style={styles.quoteBtn} onPress={() => { Speech.stop(); Speech.speak(daily.a, { language: 'ar-SA', rate: 0.65 }); }}>
                <Text style={styles.quoteBtnTxt}>🔊 阿语</Text>
              </TouchableOpacity>
              {daily.e ? (
                <TouchableOpacity style={styles.quoteBtn} onPress={() => { Speech.stop(); Speech.speak(daily.e, { language: 'en-US', rate: 0.8 }); }}>
                  <Text style={styles.quoteBtnTxt}>🇬🇧 英语</Text>
                </TouchableOpacity>
              ) : null}
            </View>
          </TouchableOpacity>
        </View>
      ) : null}

      {/* 今日学习 */}
      <View style={styles.section}>
        <GlassCard style={styles.dailyCard}>
          <View style={styles.dailyRow}>
            <ProgressRing percent={percent} label="今日" />
            <View style={{ flex: 1, marginLeft: 16 }}>
              <DailyRow icon="🔥" text={`连续学习 ${streak} 天`} strong />
              <DailyRow icon="⏱" text={`今日学习 ${minutes} 分钟`} />
              <DailyRow icon="🎯" text={`今日目标：学习 ${goal} 个单词`} />
            </View>
          </View>
          <View style={styles.goalBar}>
            <Text style={styles.goalTxt}>{percent >= 100 ? '🎉 今日目标达成！' : `今日进度 · ${learned} / ${goal} 单词`}</Text>
            <View style={styles.barBg}><View style={[styles.barFg, { width: percent + '%' }]} /></View>
          </View>
        </GlassCard>
      </View>

      {/* 今日任务 */}
      <View style={styles.section}>
        <GlassCard style={styles.dailyCard}>
          <Text style={styles.taskTitle}>📋 今日任务</Text>
          <TaskRow icon="✅" label="每日打卡" done={checkinDone} onPress={doCheckin} hint={checkinDone ? '已完成 (+5分钟)' : '点击打卡 (+5分钟)'} />
          <TaskRow icon="📅" label="间隔复习" done={dueCount === 0} onPress={() => { setReviewMode(true); setFlashOpen(true); }} hint={dueCount > 0 ? `${dueCount} 张到期` : '今日已完成'} />
          <TaskRow icon="💬" label="日常对话" done={dlgDone} onPress={async () => {
            setDialogOpen(true);
            try {
              const d = new Date();
              await AsyncStorage.setItem('nur_dlg_done_' + d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'), '1');
              setDlgDone(true);
            } catch (e) {}
          }} hint={`今日 ${dlgTodayTotal} 句`} />
          <TaskRow icon="🎧" label="听力训练" done={false} last onPress={() => navigation.navigate('Listen')} hint="10 分钟跟读" />
        </GlassCard>
      </View>

      {/* 数据卡 */}
      <View style={styles.statRow}>
        <StatCard icon="📖" num={stats ? stats.sentences : data.stats.sentences} label="总句子" onPress={() => navigation.navigate('Learn')} />
        <StatCard icon="✅" num={learned} label="已学句子" onPress={() => navigation.navigate('Learn')} />
        <StatCard icon="🕌" num={data.stats.cats} label="学习分类" onPress={() => navigation.navigate('Learn')} />
      </View>

      {/* 分类引导 */}
      <View style={styles.section}>
        <View style={styles.catGuide}>
          <TouchableOpacity style={styles.guideCard} activeOpacity={0.85} onPress={() => navigation.navigate('Learn')}>
            <View style={[styles.guideIcon, { backgroundColor: 'rgba(201,168,76,.16)' }]}><Text style={{ fontSize: 24 }}>📚</Text></View>
            <Text style={styles.guideTitle}>学习</Text>
            <Text style={styles.guideDesc}>闪卡 · 单词 · 字母 · 古兰经 · 圣训</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.guideCard} activeOpacity={0.85} onPress={() => navigation.navigate('Listen')}>
            <View style={[styles.guideIcon, { backgroundColor: 'rgba(15,61,49,.1)' }]}><Text style={{ fontSize: 24 }}>🎧</Text></View>
            <Text style={styles.guideTitle}>听力</Text>
            <Text style={styles.guideDesc}>跟读 · 古兰诵读 · 宣礼 · AI 音乐</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.guideCard} activeOpacity={0.85} onPress={() => navigation.navigate('AI')}>
            <View style={[styles.guideIcon, { backgroundColor: 'rgba(201,168,76,.16)' }]}><Text style={{ fontSize: 24 }}>🤖</Text></View>
            <Text style={styles.guideTitle}>AI</Text>
            <Text style={styles.guideDesc}>语音对话 · 写文章 · 音乐生成</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.guideCard} activeOpacity={0.85} onPress={() => navigation.navigate('Profile')}>
            <View style={[styles.guideIcon, { backgroundColor: 'rgba(15,61,49,.1)' }]}><Text style={{ fontSize: 24 }}>👤</Text></View>
            <Text style={styles.guideTitle}>我的</Text>
            <Text style={styles.guideDesc}>统计 · 生词本 · 备份 · 设置</Text>
          </TouchableOpacity>
        </View>
        {/* 高频快捷 */}
        <View style={styles.quickRow}>
          <TouchableOpacity style={styles.quickChip} onPress={() => setPrayerOpen(true)}><Text style={styles.quickTxt}>🕌 礼拜时间 · 宣礼</Text></TouchableOpacity>
          <TouchableOpacity style={styles.quickChip} onPress={() => setDialogOpen(true)}><Text style={styles.quickTxt}>💬 今日对话</Text></TouchableOpacity>
          <TouchableOpacity style={styles.quickChip} onPress={() => { setReviewMode(false); setFlashOpen(true); }}><Text style={styles.quickTxt}>🃏 闪卡复习</Text></TouchableOpacity>
        </View>
      </View>

      {/* 分类 */}
      <View style={styles.secHead}><Text style={styles.secTitle}>📚 学习分类</Text></View>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.catRow}>
        <CategoryChip icon="🏛" name="全部" ar="الكل" active onPress={() => goCat('all')} />
        {Object.entries(data.meta || {}).map(([key, m]) => (
          <CategoryChip key={key} icon={m.icon} name={m.cn} ar={m.ar} onPress={() => goCat(key)} />
        ))}
      </ScrollView>


      {/* AI 入口 */}
      <View style={styles.section}>
        <TouchableOpacity style={styles.aiEntry} activeOpacity={0.85} onPress={() => navigation.navigate('AI')}>
          <Text style={styles.aiIcon}>🧞</Text>
          <View style={{ flex: 1 }}>
            <Text style={styles.aiTitle}>AI 阿拉伯语老师</Text>
            <Text style={styles.aiDesc}>翻译 · 纠错 · 发音 · 情景练习 · 逐词解释</Text>
          </View>
          <Text style={styles.aiGo}>›</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
    <LibraryModal visible={libOpen} onClose={() => setLibOpen(false)} />
    <WordModal visible={wordOpen} onClose={() => setWordOpen(false)} />
    <QuranModal visible={quranOpen} onClose={() => setQuranOpen(false)} />
    <FlashcardModal visible={flashOpen} onClose={() => { setFlashOpen(false); setReviewMode(false); }} initialMode={reviewMode ? 'review' : null} />
    <QuizModal visible={quizOpen} onClose={() => setQuizOpen(false)} />
    <AlphabetModal visible={alphaOpen} onClose={() => setAlphaOpen(false)} />
    <WordBookModal visible={wbOpen} onClose={() => setWbOpen(false)} />
    <DialogModal visible={dialogOpen} onClose={() => setDialogOpen(false)} />
    <HistoryModal visible={histOpen} onClose={() => setHistOpen(false)} />
    <HadithModal visible={hadithOpen} onClose={() => setHadithOpen(false)} />
    <PrayerModal visible={prayerOpen} onClose={() => setPrayerOpen(false)} />
    <MusicModal visible={musicOpen} onClose={() => setMusicOpen(false)} />
    </>
  );
}

function DailyRow({ icon, text, strong }) {
  return (
    <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 8 }}>
      <Text style={{ fontSize: 13 }}>{icon}</Text>
      <Text style={[styles.dailyTxt, strong && { color: Colors.greenDark, fontWeight: '700' }]}>{text}</Text>
    </View>
  );
}

function StatCard({ icon, num, label, onPress }) {
  return (
    <TouchableOpacity style={styles.statCard} onPress={onPress} activeOpacity={0.8}>
      <Text style={styles.statIcon}>{icon}</Text>
      <Text style={styles.statNum}>{num != null ? num.toLocaleString() : '—'}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </TouchableOpacity>
  );
}

function TaskRow({ icon, label, done, hint, onPress, last }) {
  return (
    <TouchableOpacity style={[styles.taskRow, last && { borderBottomWidth: 0 }]} onPress={onPress} activeOpacity={0.7}>
      <Text style={styles.taskIcon}>{done ? '✅' : icon}</Text>
      <Text style={[styles.taskLabel, done && { color: Colors.muted }]}>{label}</Text>
      <Text style={[styles.taskHint, done && { color: Colors.green }]}>{hint}</Text>
      <Text style={styles.taskGo}>›</Text>
    </TouchableOpacity>
  );
}

function Entry({ icon, title, desc, onPress }) {
  return (
    <TouchableOpacity style={styles.entry} activeOpacity={0.85} onPress={onPress}>
      <View style={styles.entryIcon}><Text style={{ fontSize: 18 }}>{icon}</Text></View>
      <Text style={styles.entryTitle}>{title}</Text>
      <Text style={styles.entryDesc}>{desc}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: Colors.cream },
  section: { paddingHorizontal: 16, marginTop: 14 },
  dailyCard: { padding: 18 },
  dailyRow: { flexDirection: 'row', alignItems: 'center' },
  dailyTxt: { fontSize: 12.5, color: Colors.ink, marginLeft: 7 },
  goalBar: { marginTop: 12, paddingTop: 12, borderTopWidth: 1, borderTopColor: 'rgba(201,168,76,0.3)', borderStyle: 'dashed' },
  taskTitle: { fontSize: 13, fontWeight: '800', color: Colors.greenDark, marginBottom: 8 },
  taskRow: { flexDirection: 'row', alignItems: 'center', paddingVertical: 9, borderBottomWidth: 1, borderBottomColor: 'rgba(201,168,76,0.12)' },
  taskIcon: { fontSize: 15, width: 24 },
  taskLabel: { fontSize: 12, fontWeight: '600', color: Colors.ink, flex: 1 },
  taskHint: { fontSize: 10, color: Colors.muted, marginRight: 6 },
  taskGo: { fontSize: 15, color: Colors.gold },
  goalTxt: { fontSize: 11, color: Colors.muted, marginBottom: 6 },
  barBg: { height: 7, borderRadius: 4, backgroundColor: 'rgba(201,168,76,0.15)', overflow: 'hidden' },
  barFg: { height: '100%', borderRadius: 4, backgroundColor: Colors.gold },
  statRow: { flexDirection: 'row', gap: 10, paddingHorizontal: 16, marginTop: 14 },
  statCard: {
    flex: 1, backgroundColor: '#fff', borderRadius: 16,
    borderWidth: 1, borderColor: 'rgba(201,168,76,0.25)', paddingVertical: 14, alignItems: 'center',
    shadowColor: '#0f3d31', shadowOpacity: 0.07, shadowRadius: 10, shadowOffset: { width: 0, height: 4 }, elevation: 2,
  },
  statIcon: {
    width: 36, height: 36, lineHeight: 36, borderRadius: 11, textAlign: 'center', fontSize: 17, overflow: 'hidden',
    backgroundColor: 'rgba(201,168,76,0.13)', borderWidth: 1, borderColor: 'rgba(201,168,76,0.25)',
  },
  statNum: { fontSize: 22, fontWeight: '800', color: Colors.greenDark, marginTop: 4 },
  statLabel: { fontSize: 9.5, color: Colors.muted, marginTop: 2 },
  catGuide: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  guideCard: {
    width: '48%', backgroundColor: '#fff', borderRadius: 16, padding: 14,
    borderWidth: 1, borderColor: 'rgba(201,168,76,.22)', alignItems: 'flex-start',
  },
  guideIcon: { width: 44, height: 44, borderRadius: 14, alignItems: 'center', justifyContent: 'center', marginBottom: 8 },
  guideTitle: { fontSize: 15, fontWeight: '800', color: '#0f3d31' },
  guideDesc: { fontSize: 9.5, color: '#8a9c8f', marginTop: 4, lineHeight: 14 },
  quickRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginTop: 12 },
  quickChip: { backgroundColor: 'rgba(201,168,76,.12)', borderWidth: 1, borderColor: 'rgba(201,168,76,.3)', borderRadius: 20, paddingHorizontal: 13, paddingVertical: 8 },
  quickTxt: { fontSize: 11, fontWeight: '700', color: '#0f3d31' },
  entryGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  entry: {
    width: '32.3%', alignItems: 'center', backgroundColor: '#fff', paddingVertical: 12,
    borderRadius: 15, borderWidth: 1, borderColor: 'rgba(201,168,76,0.22)',
    shadowColor: '#0f3d31', shadowOpacity: 0.08, shadowRadius: 10, shadowOffset: { width: 0, height: 4 }, elevation: 3,
  },
  entryIcon: {
    width: 40, height: 40, borderRadius: 13, alignItems: 'center', justifyContent: 'center',
    backgroundColor: 'rgba(201,168,76,0.14)', borderWidth: 1, borderColor: 'rgba(201,168,76,0.3)', marginBottom: 6,
    shadowColor: '#c9a84c', shadowOpacity: 0.25, shadowRadius: 6, shadowOffset: { width: 0, height: 2 }, elevation: 2,
  },
  entryTitle: { fontSize: 11.5, fontWeight: '700', color: Colors.ink },
  entryDesc: { fontSize: 8.5, color: Colors.muted, marginTop: 2 },
  secHead: { paddingHorizontal: 16, marginTop: 22, flexDirection: 'row', alignItems: 'center' },
  secTitle: { fontSize: 15, fontWeight: '700', color: Colors.greenDark },
  catRow: { paddingHorizontal: 16, paddingTop: 10, paddingBottom: 4 },
  quoteCard: {
    backgroundColor: Colors.greenDark, borderRadius: Radius.md, padding: 12, alignItems: 'center',
    overflow: 'hidden', position: 'relative', borderWidth: 1, borderColor: 'rgba(201,168,76,0.3)',
  },
  quoteMark: { position: 'absolute', top: 2, left: 12, fontSize: 52, color: 'rgba(232,212,139,0.18)', fontFamily: 'serif' },
  quoteAr: { fontFamily: 'serif', fontSize: 15, fontWeight: '700', color: Colors.goldLight, textAlign: 'center', lineHeight: 26, writingDirection: 'rtl' },
  quoteCn: { fontSize: 10.5, color: 'rgba(255,255,255,0.82)', marginTop: 4, textAlign: 'center' },
  quoteEn: { fontSize: 10, color: 'rgba(232,212,139,0.7)', marginTop: 4, textAlign: 'center' },
  quoteBtns: { flexDirection: 'row', gap: 8, marginTop: 12 },
  quoteBtn: {
    paddingHorizontal: 12, paddingVertical: 6, borderRadius: 13,
    backgroundColor: 'rgba(232,212,139,0.14)', borderWidth: 1, borderColor: 'rgba(232,212,139,0.35)',
  },
  quoteBtnTxt: { fontSize: 10.5, fontWeight: '700', color: Colors.goldLight },
  quoteSrc: { fontSize: 9.5, color: 'rgba(232,212,139,0.65)', marginTop: 8 },
  quoteSwitch: { position: 'absolute', bottom: 8, right: 14, fontSize: 9, color: 'rgba(232,212,139,0.5)' },
  aiEntry: {
    flexDirection: 'row', alignItems: 'center', padding: 16, borderRadius: Radius.lg,
    backgroundColor: 'rgba(255,255,255,0.6)', borderWidth: 1, borderColor: 'rgba(201,168,76,0.25)',
  },
  aiIcon: { fontSize: 30, marginRight: 12 },
  aiTitle: { fontSize: 14, fontWeight: '700', color: Colors.greenDark },
  aiDesc: { fontSize: 10.5, color: Colors.muted, marginTop: 2 },
  aiGo: { fontSize: 22, color: Colors.gold },
});
