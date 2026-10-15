// 公共组件：玻璃卡片、拱门、圆环、句子卡片
import React, { useState, useEffect, useRef } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, Animated, Easing, Alert,
} from 'react-native';
import * as Speech from 'expo-speech';
import { speak as ttsSpeak } from './tts';
import { Colors, Shadows, Radius } from './theme';

// ===== 玻璃卡片 =====
export function GlassCard({ children, style, onPress }) {
  const content = <View style={[styles.glass, style]}>{children}</View>;
  if (onPress) {
    return (
      <TouchableOpacity activeOpacity={0.85} onPress={onPress} style={{ borderRadius: Radius.lg }}>
        {content}
      </TouchableOpacity>
    );
  }
  return content;
}

// ===== 清真寺拱门头部 =====
export function ArchHeader({ title, subtitle, zh }) {
  return (
    <View style={styles.header}>
      <View style={styles.archRow}>
        <View style={styles.arch} />
        <Text style={styles.crescent}>☾</Text>
      </View>
      <Text style={styles.headerTitle}>{title}</Text>
      <Text style={styles.headerSub}>{subtitle}</Text>
      {zh ? <Text style={styles.headerZh}>{zh}</Text> : null}
    </View>
  );
}

// ===== 进度圆环 =====
import Svg, { Circle } from 'react-native-svg';
export function ProgressRing({ percent, size = 84, label }) {
  const [anim] = useState(new Animated.Value(0));
  useEffect(() => {
    Animated.timing(anim, {
      toValue: percent / 100,
      duration: 1200,
      easing: Easing.out(Easing.cubic),
      useNativeDriver: true,
    }).start();
  }, [percent]);

  const r = size / 2 - 7;
  const circumference = 2 * Math.PI * r;
  const offset = anim.interpolate({
    inputRange: [0, 1],
    outputRange: [circumference, circumference * (1 - percent / 100)],
  });

  return (
    <View style={{ width: size, height: size, justifyContent: 'center', alignItems: 'center' }}>
      <Svg width={size} height={size} style={{ position: 'absolute' }}>
        <Circle cx={size / 2} cy={size / 2} r={r} stroke="rgba(201,168,76,0.18)" strokeWidth="7" fill="none" />
        <AnimatedCircle
          cx={size / 2} cy={size / 2} r={r}
          stroke="#c9a84c" strokeWidth="7" fill="none"
          strokeLinecap="round" strokeDasharray={`${circumference}`}
          strokeDashoffset={offset}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </Svg>
      <View style={styles.ringCenter}>
        <Text style={styles.ringNum}>{Math.round(percent)}%</Text>
        <Text style={styles.ringLabel}>{label || ''}</Text>
      </View>
    </View>
  );
}

function AnimatedCircle(props) {
  return <AnimatedSvgCircle {...props} />;
}
const AnimatedSvgCircle = Animated.createAnimatedComponent(Circle);

// ===== 句子卡片 =====
export function SentenceCard({ sentence, id, index, onToggleFav, onToggleReview, isFav, isReview, showBtns = true, onSpeakAr }) {
  const [playing, setPlaying] = useState(null); // 'ar' | 'en'
  const anim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(anim, {
      toValue: 1,
      duration: 350,
      delay: Math.min(index * 40, 300),
      useNativeDriver: true,
    }).start();
  }, []);

  const speak = async (lang) => {
    Speech.stop();
    // 英语按钮读英语翻译，阿语按钮读阿语原文
    const text = lang === 'en' ? (sentence.e || sentence.a) : sentence.a;
    await ttsSpeak(text, {
      lang: lang === 'ar' ? 'ar-SA' : 'en-US',
      rate: lang === 'ar' ? 0.7 : 0.85,
      onStart: () => setPlaying(lang),
      onDone: () => setPlaying(null),
      onStopped: () => setPlaying(null),
      onError: () => {
        setPlaying(null);
        if (lang === 'en') {
          Alert.alert('英语朗读失败', '手机TTS缺少英语语音。请到 设置→语言和输入法→文字转语音 检查，或安装 Google 语音服务。');
        }
      },
    });
    if (lang === 'ar' && onSpeakAr) onSpeakAr();
  };

  return (
    <Animated.View
      style={[
        styles.sCard,
        { opacity: anim, transform: [{ translateY: anim.interpolate({ inputRange: [0, 1], outputRange: [12, 0] }) }] },
      ]}
    >
      <Text style={styles.sAr}>{sentence.a}</Text>
      <View style={styles.sTr}>
        <Text style={styles.sEn}>🇬🇧 {sentence.e}</Text>
        <Text style={styles.sCn}>🇨🇳 {sentence.c}</Text>
        {sentence.py ? <Text style={styles.sPy}>🗣 {sentence.py}</Text> : null}
      </View>
      {showBtns ? (
        <View style={styles.sBtns}>
          <RoundBtn icon={playing === 'ar' ? '🔊' : '🔇'} active={playing === 'ar'} onPress={() => speak('ar')} />
          <RoundBtn icon="🇬🇧" active={playing === 'en'} onPress={() => speak('en')} />
          <RoundBtn icon={isFav ? '⭐' : '☆'} active={isFav} onPress={onToggleFav} />
          <RoundBtn icon={isReview ? '📌' : '📍'} active={isReview} onPress={onToggleReview} />
        </View>
      ) : null}
    </Animated.View>
  );
}

function RoundBtn({ icon, onPress, active }) {
  return (
    <TouchableOpacity
      onPress={onPress}
      style={[styles.roundBtn, active && styles.roundBtnOn]}
      activeOpacity={0.7}
    >
      <Text style={{ fontSize: 12 }}>{icon}</Text>
    </TouchableOpacity>
  );
}

// ===== 分类入口 =====
export function CategoryChip({ icon, name, ar, onPress, active }) {
  return (
    <TouchableOpacity
      style={[styles.catChip, active && styles.catChipOn]}
      onPress={onPress}
      activeOpacity={0.8}
    >
      <Text style={styles.catIcon}>{icon}</Text>
      <Text style={[styles.catName, active && styles.catNameOn]}>{name}</Text>
      <Text style={[styles.catAr, active && styles.catArOn]}>{ar}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  glass: {
    backgroundColor: 'rgba(255,255,255,0.6)',
    borderRadius: Radius.lg,
    borderWidth: 1,
    borderColor: 'rgba(201,168,76,0.28)',
    ...Shadows.card,
  },
  header: {
    backgroundColor: Colors.greenDark,
    paddingTop: 56,
    paddingBottom: 30,
    paddingHorizontal: 20,
    alignItems: 'center',
  },
  archRow: { alignItems: 'center', marginBottom: 6 },
  arch: {
    width: 56,
    height: 36,
    borderWidth: 2.5,
    borderColor: 'rgba(232,212,139,0.55)',
    borderBottomWidth: 0,
    borderTopLeftRadius: 28,
    borderTopRightRadius: 28,
  },
  crescent: { fontSize: 16, color: Colors.goldLight, marginTop: -14, textShadowRadius: 8 },
  headerTitle: { fontFamily: 'serif', fontSize: 30, fontWeight: '700', color: Colors.goldLight },
  headerSub: { fontSize: 11, color: 'rgba(247,243,236,0.75)', letterSpacing: 3, marginTop: 2 },
  headerZh: { fontSize: 11, color: 'rgba(232,212,139,0.85)', marginTop: 8, letterSpacing: 2 },
  ringCenter: { position: 'absolute', alignItems: 'center' },
  ringNum: { fontSize: 15, fontWeight: '800', color: Colors.greenDark },
  ringLabel: { fontSize: 8, color: Colors.muted },
  sCard: {
    backgroundColor: Colors.white,
    borderRadius: Radius.md,
    padding: 13,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: 'rgba(201,168,76,0.14)',
    ...Shadows.card,
  },
  sAr: {
    fontFamily: 'serif', fontSize: 16, fontWeight: '700',
    textAlign: 'right', writingDirection: 'rtl', color: Colors.greenDark, lineHeight: 26,
  },
  sTr: { marginTop: 6, paddingTop: 6, borderTopWidth: 1, borderTopColor: 'rgba(201,168,76,0.2)', borderStyle: 'dashed' },
  sEn: { fontSize: 10.5, color: '#6b7270', textAlign: 'left' },
  sCn: { fontSize: 10.5, color: Colors.green, textAlign: 'left', marginTop: 2 },
  sPy: { fontSize: 9.5, color: Colors.goldDark, textAlign: 'left', marginTop: 2, fontStyle: 'italic' },
  sBtns: { flexDirection: 'row', gap: 8, marginTop: 8, justifyContent: 'flex-end' },
  roundBtn: {
    width: 30, height: 30, borderRadius: 15,
    borderWidth: 1, borderColor: 'rgba(201,168,76,0.3)',
    backgroundColor: Colors.white, alignItems: 'center', justifyContent: 'center',
  },
  roundBtnOn: { backgroundColor: Colors.gold, borderColor: Colors.goldDark },
  catChip: {
    minWidth: 76, paddingVertical: 10, paddingHorizontal: 10,
    borderRadius: 16, borderWidth: 1, borderColor: 'rgba(201,168,76,0.2)',
    backgroundColor: Colors.white, alignItems: 'center', marginRight: 8,
  },
  catChipOn: { backgroundColor: Colors.greenDark, borderColor: 'rgba(201,168,76,0.5)' },
  catIcon: { fontSize: 20 },
  catName: { fontSize: 10, fontWeight: '600', color: Colors.ink, marginTop: 2 },
  catNameOn: { color: '#fff' },
  catAr: { fontSize: 9, color: Colors.muted },
  catArOn: { color: 'rgba(255,255,255,0.65)' },
});
