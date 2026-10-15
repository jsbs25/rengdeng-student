/* Nour Fast Voice — browser SpeechRecognition -> streaming DeepSeek -> instant speech */
(function () {
  'use strict';

  var C = {
    active: false,
    busy: false,
    recognition: null,
    speech: null,
    speechText: '',
    finalText: '',
    interimText: '',
    debounce: null,
    seq: 0,
    liveNode: null,
    fallbackStream: null,
    fallbackRecorder: null,
    fallbackChunks: [],
    fallbackTimer: null,
    fallbackAnalyser: null,
    fallbackCtx: null,
    level: 0,
    raf: 0,
    status: ''
  };

  function apiBase() {
    try { return typeof API_BASE === 'function' ? API_BASE() : location.origin; }
    catch (e) { return location.origin; }
  }
  function deviceId() {
    try { return typeof devId === 'function' ? devId() : (localStorage.getItem('nur_device_id') || 'web-anon'); }
    catch (e) { return 'web-anon'; }
  }
  function getOrb() { return document.querySelector('#page-home .nour-orb'); }
  function escText(text) {
    try { return typeof esc === 'function' ? esc(String(text)) : String(text).replace(/[&<>"']/g, function (c) { return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]); }); }
    catch (e) { return String(text); }
  }

  function ensureHud() {
    var hero = document.querySelector('#page-home .tk-hero');
    if (!hero) return null;
    var hud = document.getElementById('nourRealtimeHud');
    if (!hud) {
      hud = document.createElement('div');
      hud.id = 'nourRealtimeHud';
      hud.className = 'nour-realtime-hud';
      hud.setAttribute('aria-live', 'polite');
      hud.innerHTML = '<span class="nour-rt-dot"></span><span id="nourRealtimeStatus">点按光球开始快速语音对话</span><span id="nourRealtimeTranscript"></span>';
      var orb = hero.querySelector('.nour-orb');
      if (orb && orb.nextSibling) hero.insertBefore(hud, orb.nextSibling); else hero.appendChild(hud);
    }
    return hud;
  }
  function setStatus(text, kind) {
    C.status = text || '';
    var hud = ensureHud(), el = document.getElementById('nourRealtimeStatus'), orb = getOrb();
    if (el) el.textContent = text || '';
    if (hud) { hud.classList.toggle('is-error', kind === 'error'); hud.classList.toggle('is-live', !!C.active); }
    if (orb) {
      orb.setAttribute('aria-label', text || '点按 Nour AI 开始快速语音对话');
      orb.classList.toggle('is-live', !!C.active);
      orb.classList.toggle('is-connecting', !!(C.active && C.busy));
      orb.classList.toggle('is-user-speaking', !!C.recognition && !!C.interimText);
      orb.classList.toggle('is-ai-speaking', !!C.speech);
    }
  }
  function setTranscript(text) {
    var el = document.getElementById('nourRealtimeTranscript');
    if (el) el.textContent = text ? ' · ' + String(text).slice(-120) : '';
  }
  function appendChat(role, text) {
    var box = document.getElementById('homeAI');
    if (!box || !text) return;
    var div = document.createElement('div');
    div.className = 'ps-ai-msg ' + (role === 'user' ? 'user' : 'bot');
    div.dataset.full = String(text);
    div.innerHTML = '<span style="white-space:pre-wrap">' + escText(text) + '</span>';
    box.appendChild(div); box.scrollTop = box.scrollHeight;
    return div;
  }
  function updateLive(text) {
    if (!C.liveNode) C.liveNode = appendChat('ai', text || '');
    if (!C.liveNode) return;
    C.liveNode.dataset.full = String(text || '');
    var span = C.liveNode.querySelector('span');
    if (span) span.textContent = text || '';
    var box = document.getElementById('homeAI');
    if (box) box.scrollTop = box.scrollHeight;
  }

  function stopSpeech() {
    try { if (window.speechSynthesis) window.speechSynthesis.cancel(); } catch (e) {}
    C.speech = null; C.speechText = '';
    var orb = getOrb(); if (orb) orb.classList.remove('is-ai-speaking');
  }
  function chooseVoice(text) {
    var lang = /[\u0600-\u06FF]/.test(text) ? 'ar' : 'zh';
    var voices = window.speechSynthesis ? (window.speechSynthesis.getVoices() || []) : [];
    for (var i = 0; i < voices.length; i++) {
      var vlang = String(voices[i].lang || '').toLowerCase();
      if ((lang === 'ar' && vlang.indexOf('ar') === 0) || (lang === 'zh' && (vlang.indexOf('zh') === 0 || vlang.indexOf('cmn') === 0))) return voices[i];
    }
    return null;
  }
  function speakFast(text, sequence, done) {
    text = String(text || '').replace(/[#*>`]+/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 500);
    if (!text || !C.active || sequence !== C.seq) { if (done) done(); return; }
    stopSpeech();
    if (!window.speechSynthesis) { speakServer(text, sequence, done); return; }
    var u = new SpeechSynthesisUtterance(text), v = chooseVoice(text);
    if (v) { u.voice = v; u.lang = v.lang; } else u.lang = /[\u0600-\u06FF]/.test(text) ? 'ar-SA' : 'zh-CN';
    u.rate = .96; u.pitch = 1;
    C.speech = u;
    u.onstart = function () { if (C.active && sequence === C.seq) setStatus('正在说话 · 点光球可立即打断'); };
    u.onend = function () { if (C.speech === u) C.speech = null; if (done) done(); };
    u.onerror = function () { if (C.speech === u) C.speech = null; if (done) done(); };
    window.speechSynthesis.speak(u);
  }
  function speakServer(text, sequence, done) {
    fetch(apiBase() + '/api/tts', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({text: text, lang: /[\u0600-\u06FF]/.test(text) ? 'ar' : 'zh'}) })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (!C.active || sequence !== C.seq || !d || !d.url) { if (done) done(); return; }
        var a = new Audio(apiBase() + d.url); C.speech = a;
        a.onplay = function () { setStatus('正在说话 · 点光球可立即打断'); };
        a.onended = function () { if (C.speech === a) C.speech = null; if (done) done(); };
        a.onerror = function () { if (C.speech === a) C.speech = null; if (done) done(); };
        a.play().catch(function () { if (done) done(); });
      }).catch(function () { if (done) done(); });
  }

  function arabicToSpeak(full) {
    var s = String(full || '').replace(/\r/g, '');
    var first = s.split(/\n|中文\s*[:：]/i)[0].trim();
    // Stream output may contain a complete first sentence before the newline.
    var m = first.match(/^(.+?[。！？!?؟；;])(?:\s|$)/);
    return (m ? m[1] : first).replace(/[#*>`]+/g, ' ').trim().slice(0, 300);
  }
  function maybeSpeak(full, sequence, final) {
    if (!C.active || sequence !== C.seq || C.speech) return;
    var first = arabicToSpeak(full), hasBoundary = /\n|中文\s*[:：]|[。！？!?؟；;]/.test(full);
    if (first && (hasBoundary || final) && first.length >= 2) {
      C.spoken = true;
      speakFast(first, sequence, function () { if (C.active && sequence === C.seq && !C.busy) startListening(); });
    }
  }

  function parseSSEChunk(text, state, sequence) {
    state.buffer += text;
    var lines = state.buffer.split(/\n/); state.buffer = lines.pop() || '';
    lines.forEach(function (line) {
      line = line.replace(/\r$/, '');
      if (line.indexOf('data:') !== 0) return;
      var raw = line.slice(5).trim();
      if (!raw || raw === '[DONE]') return;
      try {
        var d = JSON.parse(raw), delta = d.choices && d.choices[0] && d.choices[0].delta;
        var part = delta && delta.content ? String(delta.content) : '';
        if (part) { state.full += part; updateLive(state.full); setTranscript(state.full); maybeSpeak(state.full, sequence, false); }
      } catch (e) {}
    });
  }
  async function streamDeepSeek(text, sequence) {
    setStatus('DeepSeek 正在回答…'); C.liveNode = null; C.spoken = false;
    var state = {buffer: '', full: ''};
    try {
      var r = await fetch(apiBase() + '/api/chat/stream_voice', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({message: text, session_id: 'voice_' + deviceId()}) });
      if (!r.ok || !r.body) throw new Error('stream HTTP ' + r.status);
      var reader = r.body.getReader(), decoder = new TextDecoder('utf-8');
      while (true) { var item = await reader.read(); if (item.done) break; parseSSEChunk(decoder.decode(item.value, {stream:true}), state, sequence); }
      parseSSEChunk(decoder.decode(), state, sequence);
      if (!C.active || sequence !== C.seq) return;
      if (!state.full) throw new Error('empty response');
      maybeSpeak(state.full, sequence, true);
      C.busy = false;
      if (!C.speech) startListening();
    } catch (e) {
      if (!C.active || sequence !== C.seq) return;
      // Old endpoint is a compatibility fallback for servers not yet carrying SSE.
      try {
        var r2 = await fetch(apiBase() + '/api/chat/message', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message:'请作为阿拉伯语老师简短回答：' + text, session_id:'voice_fallback', token:(typeof webToken==='function'?webToken():''), device_id:deviceId()})});
        var d2 = await r2.json(), full = String((d2 && (d2.arabic || d2.message)) || '').trim();
        if (!full) throw e; updateLive(full); maybeSpeak(full, sequence, true);
      } catch (e2) { updateLive('（语音回答失败，请再说一次）'); setStatus('DeepSeek 连接失败，请重试', 'error'); }
      C.busy = false; if (!C.speech) setTimeout(function(){ if(C.active) startListening(); }, 350);
    }
  }
  function onFinal(text) {
    text = String(text || '').trim(); if (!C.active || !text) return;
    if (C.debounce) clearTimeout(C.debounce);
    C.debounce = setTimeout(function () {
      if (!C.active || C.busy) return;
      C.seq++; var sequence = C.seq; C.busy = true;
      stopListening(); appendChat('user', text); setTranscript(text); setStatus('已听到，正在回答…');
      if (/退出|再见|拜拜|结束|挂断|不说了/.test(text)) { stopChain(); return; }
      streamDeepSeek(text, sequence);
    }, 60);
  }
  function startListening() {
    if (!C.active || C.busy || !C.recognition) return;
    C.finalText = ''; C.interimText = '';
    try { C.recognition.start(); } catch (e) {}
    setStatus('正在听你说…说完停顿即可');
  }
  function stopListening() {
    if (C.debounce) { clearTimeout(C.debounce); C.debounce = null; }
    try { if (C.recognition) C.recognition.stop(); } catch (e) {}
    C.interimText = '';
  }
  function makeRecognition() {
    var R = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!R) return null;
    var r = new R(); r.lang = 'ar-SA'; r.continuous = false; r.interimResults = true; r.maxAlternatives = 1;
    r.onstart = function () { if (C.active) { C.interimText = ''; setStatus('正在听你说…说完停顿即可'); } };
    r.onresult = function (event) {
      var final = '', interim = '';
      for (var i = event.resultIndex; i < event.results.length; i++) {
        var s = event.results[i][0].transcript || '';
        if (event.results[i].isFinal) final += s; else interim += s;
      }
      C.interimText = interim; setTranscript(final || interim);
      var orb = getOrb(); if (orb) orb.style.setProperty('--voice-level', Math.min(1, ((final || interim).length / 26)).toFixed(3));
      if (final.trim()) onFinal(final.trim());
    };
    r.onerror = function (event) {
      if (!C.active) return;
      if (event.error === 'not-allowed' || event.error === 'service-not-allowed' || event.error === 'language-not-supported') {
        setStatus('浏览器识别不可用，切换本地语音识别…'); useRecorderFallback();
      }
    };
    r.onend = function () { if (C.active && !C.busy && !C.speech) setTimeout(startListening, 80); };
    return r;
  }

  // Fallback: existing offline Whisper endpoint, used only when Web SpeechRecognition is unavailable.
  async function useRecorderFallback() {
    if (!C.active || C.fallbackRecorder) return;
    try {
      C.fallbackStream = await navigator.mediaDevices.getUserMedia({audio:{channelCount:1,echoCancellation:true,noiseSuppression:true,autoGainControl:true}});
      C.fallbackCtx = new (window.AudioContext || window.webkitAudioContext)();
      var src = C.fallbackCtx.createMediaStreamSource(C.fallbackStream); C.fallbackAnalyser = C.fallbackCtx.createAnalyser(); C.fallbackAnalyser.fftSize = 512; src.connect(C.fallbackAnalyser);
      function record() {
        if (!C.active || C.busy) return;
        var mime = ''; try { if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) mime = 'audio/webm;codecs=opus'; } catch (e) {}
        C.fallbackChunks = []; C.fallbackRecorder = mime ? new MediaRecorder(C.fallbackStream,{mimeType:mime}) : new MediaRecorder(C.fallbackStream);
        var rec = C.fallbackRecorder, silence = 0, heard = false, started = Date.now();
        rec.ondataavailable = function(e){ if(e.data && e.data.size) C.fallbackChunks.push(e.data); };
        rec.onstop = function(){ C.fallbackRecorder=null; var blob=new Blob(C.fallbackChunks,{type:rec.mimeType||'audio/webm'}); C.fallbackChunks=[]; if(C.active) processFallback(blob); };
        rec.start(220); setStatus('正在听你说…（本地识别）');
        if(C.fallbackTimer) clearInterval(C.fallbackTimer);
        C.fallbackTimer=setInterval(function(){
          if(!C.active || C.fallbackRecorder!==rec || rec.state!=='recording') return;
          var data=new Uint8Array(C.fallbackAnalyser.fftSize); C.fallbackAnalyser.getByteTimeDomainData(data); var sum=0;
          for(var i=0;i<data.length;i++){var x=(data[i]-128)/128;sum+=x*x;} var lev=Math.sqrt(sum/data.length); C.level=lev;
          if(lev>.025){heard=true;silence=0;} else if(heard) silence++;
          if((heard && silence>10 && Date.now()-started>700) || Date.now()-started>16000){try{rec.stop();}catch(e){}}
        },110);
      }
      C.fallbackRecord=record; record();
    } catch (e) { setStatus('麦克风不可用，请检查浏览器权限', 'error'); }
  }
  function processFallback(blob) {
    if (!C.active) return; C.busy=true; var seq=++C.seq; setStatus('正在识别…');
    fetch(apiBase()+'/api/asr',{method:'POST',headers:{'Content-Type':blob.type||'audio/webm','X-ASR-Lang':'ar'},body:blob}).then(function(r){return r.json();}).then(function(d){
      var t=String((d&&d.text)||'').trim(); if(!t){C.busy=false;setStatus('没有听清，请再说一次');setTimeout(C.fallbackRecord,450);return;}
      appendChat('user',t); stopListening(); streamDeepSeek(t,seq);
    }).catch(function(){C.busy=false;setStatus('本地识别失败，请重试','error');setTimeout(C.fallbackRecord,600);});
  }

  async function stopChain() {
    C.active=false; C.busy=false; C.seq++;
    stopListening(); stopSpeech();
    if(C.fallbackTimer){clearInterval(C.fallbackTimer);C.fallbackTimer=null;}
    if(C.fallbackRecorder && C.fallbackRecorder.state!=='inactive'){try{C.fallbackRecorder.stop();}catch(e){}}
    C.fallbackRecorder=null;
    if(C.fallbackStream){C.fallbackStream.getTracks().forEach(function(t){try{t.stop();}catch(e){}});C.fallbackStream=null;}
    try{if(C.fallbackCtx) await C.fallbackCtx.close();}catch(e){} C.fallbackCtx=null; C.fallbackAnalyser=null;
    if(C.raf) cancelAnimationFrame(C.raf); C.raf=0;
    var orb=getOrb(); if(orb){orb.classList.remove('is-live','is-connecting','is-user-speaking','is-ai-speaking');orb.style.removeProperty('--voice-level');}
    try{window.HOME_TALK=false;}catch(e){}
    setStatus('点按光球开始快速语音对话');
  }
  async function startChain() {
    if(C.active){if(C.speech){stopSpeech();C.busy=false;startListening();setStatus('已打断，请继续说…');return;} await stopChain();return;}
    C.active=true; C.busy=false; C.recognition=makeRecognition(); C.raf=requestAnimationFrame(function tick(){if(!C.active)return;var orb=getOrb();if(orb){var pulse=C.recognition&&C.interimText?Math.min(1,C.interimText.length/30):0;orb.style.setProperty('--voice-level',pulse.toFixed(3));orb.classList.toggle('is-user-speaking',!!C.interimText);orb.classList.toggle('is-ai-speaking',!!C.speech);}C.raf=requestAnimationFrame(tick);});
    setStatus('正在开启快速语音…');
    if(C.recognition){appendChat('ai','快速语音已开启。请直接说阿拉伯语，回答会边生成边播放。');startListening();}
    else {appendChat('ai','当前浏览器不支持实时识别，已切换本地 Whisper。');await useRecorderFallback();}
  }

  window.startNourVoice=startChain; window.closeNourVoice=stopChain;
  window.NourRealtime={start:startChain,stop:stopChain,state:C,mode:'speech-recognition-deepseek-stream-tts'};
  var oldNav=window.nav;
  if(typeof oldNav==='function'){window.nav=function(tab){if(tab!=='home'&&C.active)stopChain();return oldNav.apply(this,arguments);};}
  var mic=document.getElementById('homeMic'); if(mic){mic.onclick=startChain;mic.title='快速语音：浏览器实时识别 + DeepSeek 流式回答';}
  var style=document.createElement('style'); style.textContent='\
.nour-realtime-hud{display:flex;align-items:center;justify-content:center;gap:7px;min-height:22px;margin:6px auto 0;max-width:min(92%,620px);font-size:11px;color:rgba(255,246,214,.76);opacity:.92;transition:opacity .2s ease,color .2s ease}.nour-realtime-hud.is-live{color:#ffe6a5}.nour-realtime-hud.is-error{color:#ffb6a8}.nour-rt-dot{width:7px;height:7px;border-radius:50%;background:#8b927e;box-shadow:0 0 0 rgba(255,221,120,0);transition:background .2s,box-shadow .2s}.nour-realtime-hud.is-live .nour-rt-dot{background:#eac768;box-shadow:0 0 14px 4px rgba(234,199,104,.42);animation:nourRtBlink 1.2s ease-in-out infinite}.nour-orb{--voice-level:0}.nour-orb.is-live{animation:nourOrbRealtime 1.8s ease-in-out infinite!important;box-shadow:inset -18px -24px 38px rgba(0,0,0,.38),inset 10px 10px 34px rgba(255,247,207,.38),0 0 48px rgba(238,200,100,calc(.36 + var(--voice-level)*.5)),0 0 calc(86px + var(--voice-level)*60px) rgba(32,167,132,calc(.22 + var(--voice-level)*.25))!important}.nour-orb.is-user-speaking{transform:translate(-50%,-50%) scale(calc(1 + var(--voice-level)*.06))!important}.nour-orb.is-ai-speaking{filter:saturate(1.18) brightness(calc(1 + var(--voice-level)*.12))}.nour-orb.is-connecting{cursor:wait;animation:nourOrbRealtime .9s ease-in-out infinite!important}@keyframes nourRtBlink{0%,100%{opacity:.45}50%{opacity:1}}@keyframes nourOrbRealtime{0%,100%{transform:translate(-50%,-50%) scale(.985)}50%{transform:translate(-50%,-50%) scale(1.025)}}\
'; document.head.appendChild(style); ensureHud();
})();
