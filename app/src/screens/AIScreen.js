// AI老师模块 AIScreen：DeepSeek 对话（三段式 阿/中/英）+ 语音聊天（中/阿/英）
// 语音输入：expo-speech-recognition；语音回复：expo-speech 按所选语言朗读
import React, { useState, useRef } from 'react';
import {
  View, Text, TextInput, ScrollView, StyleSheet, TouchableOpacity, KeyboardAvoidingView, Platform, Switch, Alert, Modal, Image,
} from 'react-native';
import * as Speech from 'expo-speech';
import { speak as ttsSpeak } from '../tts';
import { ExpoSpeechRecognitionModule, useSpeechRecognitionEvent } from 'expo-speech-recognition';
import { useFocusEffect } from '@react-navigation/native';
import { AudioModule, RecordingPresets, requestRecordingPermissionsAsync } from 'expo-audio';
import { Colors, Radius } from '../theme';
import { ArchHeader } from '../components';
import { getApiBase } from '../api';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useStudyTimer } from '../useStudyTimer';
import MusicModal from '../MusicModal';

// 语音语言选项（识别 + 朗读）
const VOICE_LANGS = [
  { label: '🇨🇳 中文', lang: 'zh-CN', speak: 'zh-CN' },
  { label: '🇸🇦 阿语', lang: 'ar-SA', speak: 'ar-SA' },
  { label: '🇬🇧 英语', lang: 'en-US', speak: 'en-US' },
];

const SUGGESTIONS = [
  { icon: '🖐', label: '打招呼', text: 'السلام عليكم' },
  { icon: '☕', label: '写咖啡文章', text: 'اكتب مقالا عن القهوة' },
  { icon: '📖', label: '学习方法', text: 'كيف أتعلم العربية؟' },
  { icon: '🔍', label: '词义查询', text: 'What does Shukran mean?' },
  { icon: '🌙', label: '斋月介绍', text: 'اكتب مقالا عن رمضان' },
  { icon: '✏️', label: '纠正我的句子', text: 'صحح هذه الجملة: أنا ذهب إلى السوق أمس' },
  { icon: '💬', label: '咖啡店对话', text: 'دعنا نتدرب على حوار في المقهى' },
  { icon: '🎓', label: '机场对话', text: 'دعنا نتدرب على حوار في المطار' },
  { icon: '🛒', label: '超市对话', text: 'دعنا نتدرب على حوار في السوبرماركت' },
  { icon: '🕌', label: '讲历史故事', text: 'احكِ لي قصة من التاريخ الإسلامي بالعربية' },
];

export default function AIScreen() {
  useStudyTimer(true);
  const sessionRef = useRef('app_' + Date.now().toString(36));
  const [messages, setMessages] = useState([
    {
      role: 'bot',
      ar: 'أَهْلًا بِكَ يَا صَدِيقِي! أَنَا رَفِيقُكَ الذَّكِيُّ.',
      tr: '亲爱的朋友，欢迎！我是你的AI阿拉伯语老师。翻译、纠错、陪练、写文章都可以 🧞',
      en: 'Welcome, my friend! I am your AI Arabic teacher.',
    },
  ]);
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const [autoSpeak, setAutoSpeak] = useState(true);
  const [voiceLang, setVoiceLang] = useState('zh-CN');
  const [listening, setListening] = useState(false);

  // ===== 🎙 语音唤醒（本地 Whisper · 喊「马晓梅」） =====
  const [wakeOn, setWakeOn] = useState(false);
  const [musicOpen, setMusicOpen] = useState(false);
  const [imgOpen, setImgOpen] = useState(false);
  const [imgPrompt, setImgPrompt] = useState('');
  const [imgBusy, setImgBusy] = useState(false);
  const [imgUrl, setImgUrl] = useState('');
  const [imgErr, setImgErr] = useState('');
  const [wakeTalk, setWakeTalk] = useState(false);
  const [wakeStatusTxt, setWakeStatusTxt] = useState('');
  const wakeTimerRef = useRef(null);
  const wakeOnRef = useRef(false);
  const wakeTalkRef = useRef(false);

  const uploadAsr = async (uri, lang) => {
    const fd = new FormData();
    fd.append('file', { uri, name: 'audio.m4a', type: 'audio/m4a' });
    const res = await fetch(`${await getApiBase()}/api/asr`, {
      method: 'POST',
      headers: lang ? { 'X-ASR-Lang': lang } : {},
      body: fd,
    });
    const d = await res.json();
    return (d.text || '').trim();
  };

  const stopWake = () => {
    wakeOnRef.current = false;
    setWakeOn(false);
    if (wakeTimerRef.current) clearTimeout(wakeTimerRef.current);
  };

  // 离开 AI 页时停止唤醒监听和语音识别（省电）
  useFocusEffect(
    React.useCallback(() => {
      return () => {
        stopWake();
        try { ExpoSpeechRecognitionModule.stop(); } catch (e) {}
        setListening(false);
      };
    }, [])
  );

  const wakeLoop = async () => {
    if (!wakeOnRef.current) return;
    let rec = null;
    try {
      const perm = await requestRecordingPermissionsAsync();
      if (!perm.granted) {
        setWakeStatusTxt('⚠️ 需要麦克风权限');
        stopWake();
        return;
      }
      rec = new AudioModule.AudioRecorder(RecordingPresets.HIGH_QUALITY);
      await rec.prepareToRecordAsync();
      rec.record();
      await new Promise((r) => setTimeout(r, wakeTalkRef.current ? 6000 : 4000));
      if (!wakeOnRef.current) { try { await rec.stop(); } catch (e) {} return; }
      await rec.stop();
      setWakeStatusTxt(wakeTalkRef.current ? '🔍 识别你的话…' : '👂 聆听中…');
      const t = await uploadAsr(rec.uri, null);
      if (t) {
        if (wakeTalkRef.current) {
          if (/退出|再见|拜拜|结束|停止|不说了/.test(t)) {
            wakeTalkRef.current = false;
            setWakeTalk(false);
            setWakeStatusTxt('👂 聆听中：喊「马晓梅」');
            Speech.stop();
            Speech.speak('好的，随时叫我', { language: 'zh-CN' });
          } else {
            setWakeStatusTxt('🚀 已发送，AI 回复中…');
            send(t);
          }
        } else if (/马\s*[晓小]\s*梅|小梅|晓梅/.test(t)) {
          wakeTalkRef.current = true;
          setWakeTalk(true);
          setWakeStatusTxt('💬 对话模式：直接说（「退出」结束）');
          Speech.stop();
          Speech.speak('我在，请说', { language: 'zh-CN' });
        }
      } else {
        setWakeStatusTxt(wakeTalkRef.current ? '💬 对话模式：直接说' : '👂 聆听中：喊「马晓梅」');
      }
    } catch (e) {
      setWakeStatusTxt('⚠️ 识别失败（需连接电脑服务器）');
    } finally {
      if (rec) { try { await rec.release?.(); } catch (e) {} }
    }
    if (wakeOnRef.current) {
      wakeTimerRef.current = setTimeout(wakeLoop, 1200);
    }
  };

  const toggleWake = async () => {
    if (wakeOn) { stopWake(); setWakeStatusTxt(''); return; }
    try {
      const res = await fetch(`${await getApiBase()}/api/asr/status`, { cache: 'no-store' });
      const s = await res.json();
      if (!s.asr) {
        Alert.alert('语音服务不可用', '请确认电脑上 server.py 已运行（或桌面App已打开），且手机与电脑在同一WiFi。首次使用需联网下载语音模型（约460MB）。');
        return;
      }
    } catch (e) {
      Alert.alert('无法连接服务器', '请确认电脑 server.py 已运行，且 config.js 的 LAN_IP 是电脑IP。');
      return;
    }
    wakeOnRef.current = true;
    wakeTalkRef.current = false;
    setWakeOn(true);
    setWakeTalk(false);
    setWakeStatusTxt('👂 聆听中：喊「马晓梅」');
    wakeLoop();
  };

  // ===== 语音识别事件 =====
  useSpeechRecognitionEvent('result', (e) => {
    const t = e.results && e.results[0] && e.results[0].transcript;
    if (t && t.trim()) send(t.trim());
  });
  useSpeechRecognitionEvent('end', () => setListening(false));
  useSpeechRecognitionEvent('error', () => setListening(false));

  // 当前语音语言配置
  const voiceCfg = VOICE_LANGS.find((v) => v.lang === voiceLang) || VOICE_LANGS[0];

  const toggleVoice = async () => {
    if (listening) {
      ExpoSpeechRecognitionModule.stop();
      setListening(false);
      return;
    }
    try {
      const perm = await ExpoSpeechRecognitionModule.requestPermissionsAsync();
      if (!perm.granted) {
        Alert.alert('麦克风权限', '需要麦克风权限才能语音输入');
        return;
      }
      ExpoSpeechRecognitionModule.start({
        lang: voiceLang,
        interimResults: false,
        continuous: false,
      });
      setListening(true);
    } catch (e) {
      Alert.alert('语音不可用', '当前设备不支持语音识别：' + String(e));
    }
  };

  const speak = async (text, lang) => {
    if (!text || !text.trim()) return;
    Speech.stop();
    await ttsSpeak(text, { lang: lang || 'ar-SA', rate: 0.8, onError: () => Alert.alert('朗读失败', 'TTS 语音包不可用，请检查系统文字转语音设置') });
  };

  // 按所选语言朗读 AI 回复（阿/中/英三段对应）；唤醒对话模式读中文
  const speakReply = (reply) => {
    if (!autoSpeak) return;
    if (wakeTalkRef.current) {
      speak(reply.tr || reply.ar, 'zh-CN');
      return;
    }
    const cfg = VOICE_LANGS.find((v) => v.lang === voiceLang) || VOICE_LANGS[0];
    let text = reply.ar;
    if (voiceLang === 'zh-CN') text = reply.tr || reply.ar;
    else if (voiceLang === 'en-US') text = reply.en || reply.ar;
    speak(text, cfg.speak);
  };

  // 解析三段式回复：阿语 / 中文 / 英文
  const parseReply = (reply) => {
    const text = (reply || '').trim();
    const parts = text.split('\n').map((p) => p.trim()).filter(Boolean);
    // 兼容旧三行格式（阿语 / 中文 / 英文）：第一行含阿语且第二行含中文才拆分
    if (parts.length <= 3 && /[\u0600-\u06FF]/.test(parts[0] || '') && parts[1] && /[\u4e00-\u9fff]/.test(parts[1])) {
      return { ar: parts[0], tr: parts[1] || '', en: parts[2] || '' };
    }
    // 新格式（文章/中文回答）：整篇完整显示
    return { ar: text, tr: '', en: '' };
  };


// 复制 AI 回复（expo-clipboard 可用则用，否则提示长按复制）
const copyText = async (text) => {
  try {
    const Clipboard = require('expo-clipboard');
    if (Clipboard && Clipboard.setStringAsync) {
      await Clipboard.setStringAsync(text);
      Alert.alert('✅ 已复制', '文章内容已复制到剪贴板，可粘贴到备忘录/微信');
      return;
    }
  } catch (e) {}
  Alert.alert('💡 复制方法', '请长按消息文本，在弹出的菜单中选择"复制"');
};

  const send = async (text) => {
    const msg = (text || input).trim();
    if (!msg || busy) return;
    setInput('');
    setMessages((m) => [...m, { role: 'user', text: msg }]);
    setBusy(true);
    try {
      const res = await fetch(`${await getApiBase()}/api/chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, session_id: sessionRef.current, device_id: (await AsyncStorage.getItem('nur_device_id')) || '' }),
      });
      const data = await res.json();
      const reply = data.arabic || '（无回复）';
      const parsed = parseReply(reply);
      const msgId = Date.now();
      setMessages((m) => [...m, { role: 'bot', _id: msgId, ar: '', tr: parsed.tr, en: parsed.en }]);
      // 打字机效果：短文逐字显示；长文（文章）直接完整显示
      speakReply(parsed); // 先朗读（与打字同步）
      if (parsed.ar.length > 500) {
        // 长文章：立即完整显示，不等待
        setMessages((m) => m.map((x) => (x._id === msgId ? { ...x, ar: parsed.ar } : x)));
      } else {
        let shown = '';
        const timer = setInterval(() => {
          shown = parsed.ar.slice(0, shown.length + 2);
          setMessages((m) => m.map((x) => (x._id === msgId ? { ...x, ar: shown } : x)));
          if (shown.length >= parsed.ar.length) clearInterval(timer);
        }, 18);
      }
    } catch (e) {
      setMessages((m) => [...m, { role: 'bot', ar: '⚠️', tr: '无法连接AI服务器：请确认电脑上 server.py 已运行，且手机与电脑在同一WiFi（config.js 的 LAN_IP 需为电脑IP）', en: '' }]);
    }
    setBusy(false);
  };

  const genImage = async () => {
    if (!imgPrompt.trim()) { setImgErr('请先输入图片描述'); return; }
    setImgBusy(true); setImgErr(''); setImgUrl('');
    try {
      const base = await getApiBase();
      const r = await fetch(`${base}/api/image`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: imgPrompt.trim(), width: 512, height: 512 }),
      });
      const d = await r.json();
      if (d.url) setImgUrl(base + d.url);
      else setImgErr(d.error || '生成失败，请换一个描述试试');
    } catch (e) { setImgErr('无法连接服务器，请确认手机与电脑同一 WiFi'); }
    setImgBusy(false);
  };

  return (
    <KeyboardAvoidingView style={styles.root} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ArchHeader title="🤖 AI 老师" subtitle="" zh="文本 · 语音聊天 · 唤醒对话" />
      <View style={{ flexDirection: 'row', gap: 8, paddingHorizontal: 16, paddingTop: 4 }}>
        <TouchableOpacity style={{ flex: 1, backgroundColor: '#fff', borderRadius: 12, paddingVertical: 11, alignItems: 'center', borderWidth: 1, borderColor: 'rgba(201,168,76,.3)' }} onPress={() => setMusicOpen(true)}>
          <Text style={{ fontSize: 12.5, fontWeight: '800', color: '#0f3d31' }}>🎵 AI 音乐生成</Text>
        </TouchableOpacity>
        <TouchableOpacity style={{ flex: 1, backgroundColor: '#0f3d31', borderRadius: 12, paddingVertical: 11, alignItems: 'center' }} onPress={() => setImgOpen(true)}>
          <Text style={{ fontSize: 12.5, fontWeight: '800', color: '#e8d48b' }}>🖼 AI 画图</Text>
        </TouchableOpacity>
      </View>      <View style={styles.wakeRow}>
        <TouchableOpacity
          style={styles.wakeBtn}
          onPress={() => {
            sessionRef.current = 'app_' + Date.now().toString(36);
            setMessages([{
              role: 'bot',
              ar: 'أَهْلًا بِكَ يَا صَدِيقِي! أَنَا رَفِيقُكَ الذَّكِيُّ.',
              tr: '新会话开始啦！今天想学什么？翻译 · 纠错 · 情景对话 🧞',
              en: 'Welcome! New conversation started.',
            }]);
          }}
        >
          <Text style={styles.wakeTxt}>🔄 新会话</Text>
        </TouchableOpacity>
      </View>

      {/* 语音唤醒（喊马晓梅） */}
      <View style={styles.wakeRow}>
        <TouchableOpacity style={[styles.wakeBtn, wakeOn && styles.wakeBtnOn]} onPress={toggleWake}>
          <Text style={[styles.wakeTxt, wakeOn && { color: '#fff' }]}>{wakeOn ? '🎙 聆听中' : '🎙 唤醒（喊马晓梅）'}</Text>
        </TouchableOpacity>
        {wakeStatusTxt ? <Text style={styles.wakeStatus} numberOfLines={1}>{wakeStatusTxt}</Text> : <Text style={styles.wakeHint}>需电脑服务器 · 局域网同一WiFi</Text>}
      </View>

      <ScrollView
        style={styles.body}
        contentContainerStyle={{ padding: 16, paddingBottom: 10 }}
        ref={(ref) => { this.scroll = ref; }}
        onContentSizeChange={() => this.scroll && this.scroll.scrollToEnd({ animated: true })}
      >
        {messages.map((m, i) => (
          <View key={i} style={[styles.msg, m.role === 'user' ? styles.msgUser : styles.msgBot]}>
            {m.role === 'bot' ? (
              <>
                <Text style={styles.msgAr} selectable>{m.ar}</Text>
                {m.tr ? <Text style={styles.msgTr} selectable>🇨🇳 {m.tr}</Text> : null}
                {m.en ? <Text style={styles.msgEn} selectable>🇬🇧 {m.en}</Text> : null}
                {m.ar && m.ar.length > 0 ? (
                  <TouchableOpacity style={styles.copyBtn} onPress={() => copyText(m.ar + (m.tr ? '\n' + m.tr : '') + (m.en ? '\n' + m.en : ''))}>
                    <Text style={styles.copyTxt}>📋 复制</Text>
                  </TouchableOpacity>
                ) : null}
              </>
            ) : (
              <Text style={styles.msgUserTxt}>{m.text}</Text>
            )}
          </View>
        ))}
        {busy ? <Text style={styles.typing}>🧞 正在思考...</Text> : null}
      </ScrollView>

      {/* 语音语言选择 */}
      <View style={styles.langRow}>
        <Text style={styles.langLabel}>🎤 语音语言</Text>
        {VOICE_LANGS.map((v) => (
          <TouchableOpacity
            key={v.lang}
            style={[styles.langChip, voiceLang === v.lang && styles.langChipOn]}
            onPress={() => setVoiceLang(v.lang)}
          >
            <Text style={[styles.langTxt, voiceLang === v.lang && styles.langTxtOn]}>{v.label}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <View style={styles.speakRow}>
        <Text style={styles.speakLabel}>🔊 自动朗读回复（按语音语言朗读）</Text>
        <Switch value={autoSpeak} onValueChange={setAutoSpeak} trackColor={{ true: Colors.gold }} thumbColor="#fff" />
      </View>

      <View style={styles.sugRow}>
        {SUGGESTIONS.map((s, i) => (
          <TouchableOpacity key={i} style={styles.sug} onPress={() => send(s.text)}>
            <Text style={styles.sugTxt}>{s.icon} {s.label}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <View style={styles.inpRow}>
        <TouchableOpacity
          style={[styles.voiceBtn, listening && styles.voiceBtnOn, wakeOn && { opacity: 0.4 }]}
          onPress={wakeOn ? () => Alert.alert('提示', '唤醒聆听中，直接说话即可（说「退出」结束）') : toggleVoice}
        >
          <Text style={styles.voiceTxt}>{listening ? '⏹' : '🎤'}</Text>
        </TouchableOpacity>
        <TextInput
          style={styles.input}
          value={input}
          onChangeText={setInput}
          placeholder={listening ? '🎙 正在听...（用' + voiceCfg.label + '说话）' : '输入阿语 / 中文 / 英语...'}
          placeholderTextColor={Colors.muted}
          onSubmitEditing={() => send()}
          returnKeyType="send"
        />
        <TouchableOpacity style={styles.sendBtn} onPress={() => send()} disabled={busy}>
          <Text style={styles.sendTxt}>➤</Text>
        </TouchableOpacity>
      </View>
      <Modal visible={imgOpen} animationType="slide" transparent onRequestClose={() => setImgOpen(false)}>
        <View style={{ flex: 1, backgroundColor: 'rgba(6,25,19,.92)', paddingTop: 60, paddingHorizontal: 20 }}>
          <Text style={{ color: '#e8d48b', fontSize: 16, fontWeight: '800', marginBottom: 4 }}>🖼 AI 画图</Text>
          <Text style={{ color: '#8fae9c', fontSize: 11, marginBottom: 14 }}>描述你想画的画面（支持中文），约 10-30 秒出图</Text>
          <TextInput
            style={{ backgroundColor: '#fff', borderRadius: 12, padding: 12, fontSize: 13, marginBottom: 10 }}
            placeholder="例如：暮色中的清真寺，新月挂在天边，伊斯兰艺术风格"
            placeholderTextColor="#999"
            value={imgPrompt}
            onChangeText={setImgPrompt}
            multiline
          />
          <View style={{ flexDirection: 'row', gap: 8 }}>
            <TouchableOpacity style={{ flex: 1, backgroundColor: '#a8892e', borderRadius: 12, paddingVertical: 12, alignItems: 'center' }} onPress={genImage} disabled={imgBusy}>
              <Text style={{ color: '#fff', fontWeight: '800', fontSize: 13 }}>{imgBusy ? '⏳ 绘制中...' : '🎨 生成图片'}</Text>
            </TouchableOpacity>
            <TouchableOpacity style={{ paddingVertical: 12, paddingHorizontal: 16, borderRadius: 12, backgroundColor: 'rgba(255,255,255,.1)' }} onPress={() => setImgOpen(false)}>
              <Text style={{ color: '#cfe3d6', fontWeight: '700', fontSize: 13 }}>关闭</Text>
            </TouchableOpacity>
          </View>
          {imgErr ? <Text style={{ color: '#e8a0a0', fontSize: 11, marginTop: 10 }}>{imgErr}</Text> : null}
          {imgBusy ? (
            <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
              <ActivityIndicator color="#e8d48b" size="large" />
              <Text style={{ color: '#cfe3d6', fontSize: 12, marginTop: 10 }}>AI 正在为你作画...</Text>
            </View>
          ) : imgUrl ? (
            <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', marginTop: 16 }}>
              <Image source={{ uri: imgUrl }} style={{ width: 300, height: 300, borderRadius: 14 }} resizeMode="cover" />
              <Text style={{ color: '#8fae9c', fontSize: 10, marginTop: 10 }}>长按图片可保存 · 想换个风格就重新描述</Text>
            </View>
          ) : null}
        </View>
      </Modal>
      <MusicModal visible={musicOpen} onClose={() => setMusicOpen(false)} />
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: Colors.cream },
  body: { flex: 1 },
  msg: { maxWidth: '88%', marginBottom: 8, padding: 11, borderRadius: 14 },
  msgBot: { alignSelf: 'flex-start', backgroundColor: Colors.white, borderWidth: 1, borderColor: 'rgba(201,168,76,0.16)' },
  msgUser: { alignSelf: 'flex-end', backgroundColor: Colors.gold },
  msgAr: { fontFamily: 'serif', fontSize: 13.5, fontWeight: '700', color: Colors.greenDark, writingDirection: 'rtl', lineHeight: 22 },
  msgTr: { fontSize: 10, color: Colors.muted, marginTop: 3 },
  msgEn: { fontSize: 10, color: '#5a7f9e', marginTop: 2 },
  msgUserTxt: { fontSize: 13, color: '#fff' },
  typing: { fontSize: 11, color: Colors.muted, marginLeft: 6 },
  langRow: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 16, paddingBottom: 4, gap: 6 },
  langLabel: { fontSize: 10, color: Colors.muted, marginRight: 2 },
  wakeRow: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 16, paddingTop: 10, gap: 8 },
  wakeBtn: {
    paddingHorizontal: 14, paddingVertical: 7, borderRadius: 16,
    backgroundColor: Colors.white, borderWidth: 1, borderColor: 'rgba(201,168,76,0.35)',
  },
  wakeBtnOn: { backgroundColor: Colors.greenDark, borderColor: 'rgba(201,168,76,0.5)' },
  wakeTxt: { fontSize: 11, fontWeight: '700', color: Colors.ink },
  wakeBtnOnTxt: { color: '#fff' },
  copyBtn: {
    alignSelf: 'flex-end', marginTop: 6, backgroundColor: 'rgba(201,168,76,.15)',
    borderWidth: 1, borderColor: 'rgba(201,168,76,.35)', borderRadius: 8,
    paddingHorizontal: 12, paddingVertical: 4,
  },
  copyTxt: { fontSize: 11, color: '#0f3d31', fontWeight: '700' },
  wakeStatus: { flex: 1, fontSize: 10, color: Colors.green },
  wakeHint: { flex: 1, fontSize: 9, color: Colors.muted },
  langChip: {
    paddingHorizontal: 10, paddingVertical: 5, borderRadius: 12,
    backgroundColor: Colors.white, borderWidth: 1, borderColor: 'rgba(201,168,76,0.3)',
  },
  langChipOn: { backgroundColor: Colors.greenDark, borderColor: 'rgba(201,168,76,0.5)' },
  langTxt: { fontSize: 10, fontWeight: '600', color: Colors.ink },
  langTxtOn: { color: '#fff' },
  speakRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'flex-end', paddingHorizontal: 16, paddingBottom: 4, gap: 8 },
  speakLabel: { fontSize: 10, color: Colors.muted },
  sugRow: { flexDirection: 'row', flexWrap: 'wrap', paddingHorizontal: 12, gap: 6, paddingBottom: 8 },
  sug: {
    paddingHorizontal: 10, paddingVertical: 6, borderRadius: 14,
    backgroundColor: Colors.white, borderWidth: 1, borderColor: 'rgba(201,168,76,0.3)',
  },
  sugTxt: { fontSize: 10, color: Colors.ink },
  inpRow: { flexDirection: 'row', gap: 8, padding: 12, paddingBottom: 24 },
  input: {
    flex: 1, backgroundColor: Colors.white, borderRadius: 20, paddingHorizontal: 16, paddingVertical: 10,
    fontSize: 12, borderWidth: 1, borderColor: 'rgba(201,168,76,0.25)', color: Colors.ink,
  },
  voiceBtn: {
    width: 42, height: 42, borderRadius: 21, backgroundColor: Colors.greenDark,
    alignItems: 'center', justifyContent: 'center',
  },
  voiceBtnOn: { backgroundColor: 'rgba(192,57,43,0.9)' },
  voiceTxt: { fontSize: 17 },
  sendBtn: {
    width: 40, height: 40, borderRadius: 20, backgroundColor: Colors.gold,
    alignItems: 'center', justifyContent: 'center',
  },
  sendTxt: { fontSize: 16, color: '#fff' },
});
