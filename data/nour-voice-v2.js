/* ============================================================
   补全缺失的语音/闯关函数（纯新增 ✗ 不改动任何既有代码 ✓）
   对应 HTML 里被调用但未定义的：
     nourSpeakReply(btn) · nourToggleAutoVoice() · showChallenge()
   语音：优先用服务端 Neural TTS（有感情 ✓）→ 失败回退浏览器语音 ✓
   ============================================================ */
(function(){
  var AUTO_KEY = 'nour_auto_voice';

  /* ---------- 判断文本语种 ---------- */
  function isArabic(s){ return /[\u0600-\u06FF]/.test(s); }

  /* ---------- 浏览器语音（兜底 ✓ 无感情 ✗）---------- */
  function speakBrowser(text, lang){
    try{
      if(!window.speechSynthesis) return false;
      window.speechSynthesis.cancel();
      var u = new SpeechSynthesisUtterance(text);
      u.lang = lang; u.rate = isArabic(text) ? 0.85 : 1.0; u.pitch = 1.0;
      var vs = window.speechSynthesis.getVoices() || [];
      var pick = vs.filter(function(v){ return (v.lang||'').toLowerCase().indexOf(lang.slice(0,2)) === 0; })[0];
      if(pick) u.voice = pick;
      window.speechSynthesis.speak(u);
      return true;
    }catch(e){ return false; }
  }

  /* ---------- 服务端 Neural TTS（有感情 ✓）---------- */
  function speakNeural(text, lang, onDone){
    try{
      var url = (typeof API_BASE === 'function' ? API_BASE() : '') + '/api/tts?lang=' + encodeURIComponent(lang) + '&text=' + encodeURIComponent(text.slice(0, 600));
      var a = new Audio(url);
      a.onended = function(){ if(onDone) onDone(); };
      a.onerror = function(){ speakBrowser(text, lang); if(onDone) onDone(); };
      var p = a.play();
      if(p && p.catch) p.catch(function(){ speakBrowser(text, lang); });
    }catch(e){ speakBrowser(text, lang); }
  }

  function speakText(text, onDone){
    var lang = isArabic(text) ? 'ar-SA' : 'zh-CN';
    speakNeural(text, lang, onDone);
  }

  /* ---------- ① 朗读某条 AI 回复 ---------- */
  function nourSpeakReply(btn){
    try{
      var box = btn;
      while(box && box.className !== undefined && String(box.className).indexOf('ps-ai-msg') < 0 && box.tagName !== 'BODY') box = box.parentNode;
      var text = '';
      if(box && box.getAttribute){
        text = box.getAttribute('data-raw') || box.innerText || '';
      } else if(btn && btn.parentNode) {
        text = btn.parentNode.innerText || '';
      }
      text = String(text).replace(/📋\s*复制|🔊\s*朗读/g,'').trim();
      if(!text) return;
      if(btn && !btn.__speaking){
        btn.__speaking = 1; var old = btn.textContent;
        btn.textContent = '⏸ 朗读中…';
        speakText(text, function(){ try{ btn.textContent = old; btn.__speaking = 0; }catch(e){} });
      }
    }catch(e){}
  };

  /* ---------- ② 人声开关（自动朗读 AI 回复）---------- */
  function nourToggleAutoVoice(){
    try{
      var on = localStorage.getItem(AUTO_KEY) === '1';
      on = !on;
      localStorage.setItem(AUTO_KEY, on ? '1' : '0');
      syncVoiceBtn();
      if(on) speakBrowser('人声已开启', 'zh-CN');
    }catch(e){}
  };
  function syncVoiceBtn(){
    try{
      var b = document.getElementById('aiVoiceToggle');
      if(!b) return;
      var on = localStorage.getItem(AUTO_KEY) === '1';
      b.textContent = on ? '🔊 人声：开' : '🔈 人声：关';
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    }catch(e){}
  }
  /* 自动朗读：监听 AI 回复区新增的机器人消息 */
  function hookAutoSpeak(){
    try{
      var box = document.getElementById('homeAI');
      if(!box || box.__autoHooked) return;
      box.__autoHooked = 1;
      new MutationObserver(function(muts){
        if(localStorage.getItem(AUTO_KEY) !== '1') return;
        muts.forEach(function(m){
          Array.prototype.forEach.call(m.addedNodes || [], function(n){
            try{
              if(n.nodeType !== 1) return;
              if(String(n.className||'').indexOf('bot') < 0) return;
              var txt = (n.getAttribute && n.getAttribute('data-raw')) || n.innerText || '';
              txt = String(txt).replace(/📋\s*复制|🔊\s*朗读|⏸\s*朗读中/g,'').trim();
              if(txt) speakText(txt);
            }catch(e){}
          });
        });
      });
      syncVoiceBtn();
    }catch(e){}
  }

  /* ---------- ③ 闯关练习 ---------- */
  function showChallenge(){
    try{
      var m = document.getElementById('mChallenge');
      if(!m){
        m = document.createElement('div');
        m.className = 'modal'; m.id = 'mChallenge';
        m.innerHTML = '<div class="m-head"><span>⚡</span><b>闯关练习</b>'
          + '<button class="m-close" onclick="closeModal(\'mChallenge\')">✕</button></div>'
          + '<div class="m-body" id="mChallengeBody"></div>';
        document.body.appendChild(m);
      }
      var body = document.getElementById('mChallengeBody');
      if(body && !body.__filled){
        body.__filled = 1;
        body.innerHTML = '<div style="padding:6px 2px 14px;opacity:.8;font-size:13px">选择一个题型开始练习</div>'
          + ['词汇 · 看阿语选中文', '语法 · 名词与格', '拼句 · 连词成句'].map(function(t){
              return '<div class="card" style="margin-bottom:10px;padding:14px 16px;cursor:pointer">'
                + '<b>' + t + '</b></div>';
            }).join('');
      }
      if(typeof openModal === 'function') openModal('mChallenge'); else m.classList.add('show');
    }catch(e){}
  };

  try{ window.nourSpeakReply = nourSpeakReply; }catch(e){}
  try{ window.nourToggleAutoVoice = nourToggleAutoVoice; }catch(e){}
  try{ window.showChallenge = showChallenge; }catch(e){}


  /* ---------- ④ 修正底部导航「诺尔老师」标签（纯新增 ✓ 不改别的）---------- */
  function fixAITab(){
    try{
      var t = document.querySelector('.tabbar'); if(!t) return;
      var b = t.querySelector('[data-tab="ai"]'); if(!b) return;
      var nm = b.querySelector('.t-nm');
      if(nm && nm.textContent !== '诺尔老师') nm.textContent = '诺尔老师';
      var ic = b.querySelector('.t-ic');
      if(ic && !ic.__ok){
        ic.__ok = 1;
        ic.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true" width="22" height="22">'
                     + '<circle cx="12" cy="12" r="8.2" fill="none" stroke="currentColor" stroke-width="1.6"/>'
                     + '<circle cx="12" cy="10.4" r="1.5" fill="currentColor"/>'
                     + '<path d="M8.6 16.2c1-1.5 2-2.2 3.4-2.2s2.4.7 3.4 2.2" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>'
                     + '</svg>';
      }
      // 顺便去掉可能重复的末尾项（若有重复「我的」）
      var all = t.querySelectorAll('.tb');
      if(all.length > 5){
        var seen = {};
        Array.prototype.forEach.call(all, function(x){
          var k = x.getAttribute('data-tab');
          if(seen[k]){ x.style.display = 'none'; } else { seen[k] = 1; }
        });
      }
    }catch(e){}
  }


  /* ---------- ⑤ 世界图书馆：追加「古兰经」「六大部」入口（纯新增 ✓）---------- */
  function addLibraryEntries(){
    try{
      var host = document.getElementById('mCat');
      if(!host) return;
      var wrap = host.querySelector('.m-body') || host;
      if(wrap.querySelector('#nourExtraEntries')) return;
      var box = document.createElement('div');
      box.id = 'nourExtraEntries';
      box.style.cssText = 'max-width:900px;margin:18px auto 6px;padding:0 18px';
      box.innerHTML =
          '<div style="font-size:11px;letter-spacing:.16em;opacity:.55;margin:0 0 10px">经典典籍</div>'
        + '<div class="card" onclick="nourOpenQuran()" style="margin-bottom:10px;padding:16px 18px;cursor:pointer;display:flex;align-items:center;gap:14px">'
        +   '<div style="width:44px;height:44px;border-radius:12px;display:flex;align-items:center;justify-content:center;background:rgba(232,212,139,.14);font-size:20px;flex:0 0 auto">📖</div>'
        +   '<div><b style="font-size:15px">古兰经</b><div style="font-size:12px;opacity:.6;margin-top:3px">القرآن الكريم · 114 章 · 阿语原文</div></div>'
        +   '<div style="margin-left:auto;opacity:.4">›</div></div>'
        + '<div class="card" onclick="nourOpenHadith()" style="margin-bottom:10px;padding:16px 18px;cursor:pointer;display:flex;align-items:center;gap:14px">'
        +   '<div style="width:44px;height:44px;border-radius:12px;display:flex;align-items:center;justify-content:center;background:rgba(232,212,139,.14);font-size:20px;flex:0 0 auto">📚</div>'
        +   '<div><b style="font-size:15px">六大部</b><div style="font-size:12px;opacity:.6;margin-top:3px">الكتب الستة · 六部圣训集 · 阿语原文</div></div>'
        +   '<div style="margin-left:auto;opacity:.4">›</div></div>';
      wrap.appendChild(box);
    }catch(e){}
  }
  window.nourOpenQuran = function(){ openBook('quran'); };
  window.nourOpenHadith = function(){ openBook('hadith'); };
  function openBook(kind){
    try{
      var id='nourBook_'+kind, m=document.getElementById(id);
      if(!m){
        m=document.createElement('div'); m.className='modal'; m.id=id;
        m.innerHTML='<div class="m-head"><span>'+((kind==='quran')?'📖':'📚')+'</span><b>'
          +((kind==='quran')?'古兰经':'六大部')+'</b><button class="m-close" onclick="closeModal(\''+id+'\')">✕</button></div>'
          +'<div class="m-body" id="'+id+'Body"></div>';
        document.body.appendChild(m);
      }
      var body=document.getElementById(id+'Body');
      body.innerHTML='<div style="padding:40px 18px;text-align:center;opacity:.6">加载中…</div>';
      if(typeof openModal==='function') openModal(id); else m.classList.add('show');
      fetch((typeof API_BASE==='function'?API_BASE():'')+'/api/'+kind+'/list')
        .then(function(r){return r.json()})
        .then(function(d){
          var items=(d && (d.books||d.surahs)) || [];
          if(!items.length){ body.innerHTML='<div style="padding:40px;text-align:center;opacity:.6">暂无数据</div>'; return; }
          body.innerHTML='<div style="padding:10px 4px">'+items.map(function(x,i){
            return '<div class="card" data-i="'+i+'" style="margin-bottom:8px;padding:13px 15px;cursor:pointer;display:flex;align-items:center;gap:12px">'
              +'<b style="flex:1">'+(x.name||x.title||'')+'</b>'
              +'<span style="font-size:12px;opacity:.5">'+(x.count!=null?x.count+' 条':'')+'</span></div>';
          }).join('')+'</div>';
        })
        .catch(function(){ body.innerHTML='<div style="padding:40px;text-align:center;opacity:.6">加载失败</div>'; });
    }catch(e){}
  }

  /* ---------- 启动 ---------- */
  function boot(){ syncVoiceBtn(); hookAutoSpeak(); fixAITab(); setTimeout(fixAITab,600); setTimeout(fixAITab,1800); setTimeout(fixAITab,4000); try{ setInterval(fixAITab, 400); }catch(e){} addLibraryEntries(); setTimeout(addLibraryEntries,2000); setTimeout(addLibraryEntries,5000); }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
  [1200, 3000, 6000].forEach(function(t){ setTimeout(boot, t); });
})();
