// 智能语音选择：自动挑选系统中最动听的语音
// 英语优先高品质（iOS: Samantha/Enhanced；Android: Google 神经网络语音 x-tpf 等）
import * as Speech from 'expo-speech';

const voiceCache = {};

async function pickVoice(lang) {
  if (voiceCache[lang] !== undefined) return voiceCache[lang];
  try {
    const voices = await Speech.getAvailableVoicesAsync();
    const list = voices || [];
    let best = null;
    if (lang === 'en-US') {
      // 高品质英语语音关键词（按优先级）
      const ranks = ['Enhanced', 'Samantha', 'x-tpf', 'Neural', 'Natural', 'Online', 'Premium'];
      for (const kw of ranks) {
        best = list.find(
          (v) => v.language === 'en-US' && ((v.name || '') + ' ' + (v.identifier || '')).includes(kw)
        );
        if (best) break;
      }
      if (!best) best = list.find((v) => v.language === 'en-US');
      if (!best) best = list.find((v) => (v.language || '').startsWith('en'));
    } else if (lang === 'ar-SA') {
      best = list.find((v) => (v.language || '').startsWith('ar'));
    } else if (lang === 'zh-CN') {
      // 中文：优先高品质女声
      const ranks = ['Ting-Ting', 'Xiaoxiao', 'Meijia', 'Yaoyao', 'Huihui'];
      for (const kw of ranks) {
        best = list.find(
          (v) => (v.language || '').startsWith('zh') && ((v.name || '') + ' ' + (v.identifier || '')).includes(kw)
        );
        if (best) break;
      }
      if (!best) best = list.find((v) => (v.language || '').startsWith('zh'));
    }
    voiceCache[lang] = best ? best.identifier : undefined;
  } catch (e) {
    voiceCache[lang] = undefined;
  }
  return voiceCache[lang];
}

// 统一朗读（带语音优选）
export async function speak(text, options = {}) {
  const { lang = 'ar-SA', rate = 0.7, onStart, onDone, onStopped, onError } = options;
  if (!text || !text.trim()) return;
  Speech.stop();
  const voice = await pickVoice(lang);
  Speech.speak(text, { language: lang, rate, voice, onStart, onDone, onStopped, onError });
}
