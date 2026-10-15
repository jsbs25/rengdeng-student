/* Nour natural voice — ordinary learning dialogue only; synthetic audio is labelled. */
(function(){
  'use strict';
  var AUDIO = null;
  var RUN = 0;
  var AUTO_KEY = 'nur_ai_voice_auto_v1';
  var VOICE_KEY = 'nur_ai_voice_id_v1';
  var DEFAULT_AR = 'ar-SA-HamedNeural';
  var DEFAULT_ZH = 'zh-CN-XiaoxiaoNeural';

  function api(){ return (typeof API_BASE === 'function') ? API_BASE() : ''; }
  function getAuto(){ try{ return localStorage.getItem(AUTO_KEY) === '1'; }catch(e){ return false; } }
  function setAuto(v){ try{ localStorage.setItem(AUTO_KEY, v ? '1' : '0'); }catch(e){} }
  function getVoice(){ try{ return localStorage.getItem(VOICE_KEY) || DEFAULT_AR; }catch(e){ return DEFAULT_AR; } }
  function setVoice(v){ try{ localStorage.setItem(VOICE_KEY, v); }catch(e){} }
  function isArabic(text){ return /[\u0600-\u06ff]/.test(String(text || '')); }
  function langFor(text){ return isArabic(text) ? 'ar' : (/[\u4e00-\u9fff]/.test(String(text || '')) ? 'zh' : 'en'); }
  function clean(text){
    var s = String(text || '').replace(/https?:\/\/\S+/g, '').trim();
    var lines = s.split(/\n+/).map(function(x){ return x.replace(/^\s*(?:[🕌📖🔊🎙🤖⚠️✅🇨🇳🇬🇧]|\d+[.)、])\s*/g, '').trim(); }).filter(Boolean);
    var ar = lines.filter(function(x){ return isArabic(x); });
    if(ar.length) return ar.join('。').slice(0, 700);
    return lines.join(' ').slice(0, 500);
  }
  function label(){
    var b = document.getElementById('aiVoiceToggle');
    if(!b) return;
    b.textContent = getAuto() ? '🔊 人声：开' : '🔈 人声：关';
    b.setAttribute('aria-pressed', getAuto() ? 'true' : 'false');
    b.title = getAuto() ? '普通对话将尝试自动朗读（服务器合成音色）' : '开启普通对话朗读（服务器合成音色）';
  }
  function stop(){
    RUN++;
    if(AUDIO){ try{ AUDIO.pause(); AUDIO.src=''; }catch(e){} AUDIO=null; }
    document.querySelectorAll('.ps-ai-speak.is-playing').forEach(function(b){ b.classList.remove('is-playing'); b.textContent='🔊 朗读'; });
  }
  async function play(text, button){
    var t = clean(text); if(!t) return;
    stop();
    var run = RUN;
    if(button){ button.classList.add('is-loading'); button.textContent='…'; }
    try{
      var lang = langFor(t);
      var voice = lang === 'ar' ? getVoice() : (lang === 'zh' ? DEFAULT_ZH : 'en-US-JennyNeural');
      var r = await fetch(api() + '/api/tts', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({
        text:t, lang:lang, locale:lang === 'ar' ? 'ar-SA' : (lang === 'zh' ? 'zh-CN' : 'en-US'), voice_id:voice,
        content_kind:'dialogue', speed:0.98, format:'mp3', request_id:'web-' + Date.now().toString(36)
      })});
      var d = await r.json();
      if(!r.ok || !d.url) throw new Error(d.error || '语音暂时不可用');
      if(run !== RUN) return;
      AUDIO = new Audio((api() || '') + d.url);
      if(button){ button.classList.remove('is-loading'); button.classList.add('is-playing'); button.textContent='⏹ 停止'; }
      AUDIO.onended = function(){ if(button){ button.classList.remove('is-playing'); button.textContent='🔊 朗读'; } AUDIO=null; };
      AUDIO.onerror = function(){ if(button){ button.classList.remove('is-playing'); button.textContent='🔊 重试'; } AUDIO=null; };
      await AUDIO.play();
    }catch(e){
      if(button){ button.classList.remove('is-loading'); button.textContent='🔊 重试'; button.title = e && e.message ? e.message : '语音不可用'; }
    }
  }
  window.nourSpeakReply = function(button){
    if(!button) return;
    if(AUDIO && button.classList.contains('is-playing')){ stop(); return; }
    var box = button.closest ? button.closest('.ps-ai-msg') : button.parentNode;
    play(box && box.dataset ? box.dataset.full : '', button);
  };
  window.nourMaybeSpeak = function(text){ if(getAuto()) play(text, null); };
  window.nourToggleAutoVoice = function(){ setAuto(!getAuto()); label(); };
  window.nourStopVoice = stop;
  window.nourCycleVoice = function(){
    var next = getVoice() === DEFAULT_AR ? 'ar-SA-ZariyahNeural' : DEFAULT_AR;
    setVoice(next);
    var b = document.getElementById('aiVoiceToggle');
    if(b) b.title = '当前阿语音色：' + next + '（合成音色）';
  };
  function boot(){ label(); }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
