/* Nour in-app audio library: local lossless/audio assets stay inside the app. */
(function(){
  'use strict';
  var state = {items:[], loaded:false, query:'', filter:'all', audio:null, localUrls:[]};
  var EXT_LABEL = {flac:'FLAC 无损',wav:'WAV 无损',m4a:'M4A',mp3:'MP3',ogg:'OGG',aac:'AAC'};
  function esc(v){
    v = String(v == null ? '' : v);
    if(typeof window.catEsc === 'function') return window.catEsc(v);
    return v.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
  }
  function bytes(n){
    n = Number(n || 0);
    if(n < 1024) return n + ' B';
    if(n < 1024 * 1024) return (n / 1024).toFixed(1) + ' KB';
    if(n < 1024 * 1024 * 1024) return (n / 1024 / 1024).toFixed(1) + ' MB';
    return (n / 1024 / 1024 / 1024).toFixed(2) + ' GB';
  }
  function icon(item){
    var e = String(item.ext || '').toLowerCase();
    return e === 'flac' || e === 'wav' ? '◉' : (e === 'm4a' ? '◌' : '♪');
  }
  function filtered(){
    var q = state.query.trim().toLowerCase();
    return state.items.filter(function(x){
      var matchQ = !q || [x.title,x.name,x.category,x.ext].join(' ').toLowerCase().indexOf(q) >= 0;
      var matchF = state.filter === 'all' || String(x.ext).toLowerCase() === state.filter;
      return matchQ && matchF;
    });
  }
  function ensureModal(){
    var el = document.getElementById('mAudioLibrary');
    if(el) return el;
    el = document.createElement('div');
    el.className = 'modal audio-library-modal';
    el.id = 'mAudioLibrary';
    el.setAttribute('role','dialog');
    el.setAttribute('aria-label','音频资料库');
    el.innerHTML = '<div class="m-head"><span>🎧</span><b>音频资料库 · 应用内播放</b><button class="m-close" type="button" aria-label="关闭" onclick="closeAudioLibrary()">✕</button></div><div class="m-body audio-library-body"><div id="audioLibraryMount"></div></div>';
    document.body.appendChild(el);
    return el;
  }
  function mount(){ return document.getElementById('audioLibraryMount'); }
  function importLocal(files){
    Array.prototype.slice.call(files || []).forEach(function(file, i){
      var name = String(file.name || ''), match = name.toLowerCase().match(/\.([a-z0-9]+)$/), ext = match ? match[1] : '';
      if(EXT_LABEL[ext] === undefined) return;
      var url = URL.createObjectURL(file); state.localUrls.push(url);
      state.items.unshift({id:'local-' + Date.now() + '-' + i, root:'local', name:name, title:name.replace(/\.[^.]+$/,''), category:'本机文件 · 仅当前页面', ext:ext, size:file.size || 0, codec:ext === 'flac' || ext === 'wav' ? '本机无损 / 原生播放' : '本机临时播放', url:url, local:true});
    });
    render();
  }
  function showLoading(msg){
    var el = mount();
    if(el) el.innerHTML = '<div class="audio-library-loading"><span class="audio-library-spinner"></span><strong>' + esc(msg || '正在读取音频目录…') + '</strong><small>只读取本机/服务器已存在的音频文件，不跳转到其他应用。</small></div>';
  }
  function render(){
    var el = mount(); if(!el) return;
    var list = filtered();
    var formats = ['all'];
    state.items.forEach(function(x){ var e=String(x.ext||'').toLowerCase(); if(e && formats.indexOf(e)<0) formats.push(e); });
    var html = '<div class="audio-library-hero"><div><div class="audio-library-kicker">NOUR MEDIA SHELF</div><h2>你的音频，都可以在这里看</h2><p>FLAC / WAV 无损音频、M4A、MP3 等文件直接在软件内播放；关闭窗口不会打开外部 App。</p></div><div class="audio-library-count"><b>' + state.items.length + '</b><span>个文件</span></div></div>';
    html += '<div class="audio-library-tools"><label class="audio-library-search"><span>⌕</span><input id="audioLibrarySearch" value="' + esc(state.query) + '" placeholder="搜索音频名称、类别或格式…" autocomplete="off"></label><label class="audio-library-import">＋ 导入本机音频<input id="audioLibraryImport" type="file" accept=".flac,.wav,.m4a,.mp3,.ogg,.aac,audio/*" multiple></label><div class="audio-library-filters">';
    formats.forEach(function(e){ html += '<button type="button" class="audio-library-filter' + (state.filter === e ? ' is-on' : '') + '" data-audio-filter="' + esc(e) + '">' + esc(e === 'all' ? '全部' : (EXT_LABEL[e] || e.toUpperCase())) + '</button>'; });
    html += '</div></div>';
    html += '<div class="audio-library-status"><span>显示 ' + list.length + ' / ' + state.items.length + '</span><span>支持断点与浏览器原生进度条</span></div>';
    if(!list.length){
      html += '<div class="audio-library-empty"><div>⌁</div><strong>没有匹配的音频</strong><span>换一个名称或格式筛选试试。</span></div>';
    } else {
      html += '<div class="audio-library-grid">';
      list.forEach(function(x, i){
        var ext=String(x.ext||'').toLowerCase();
        html += '<article class="audio-library-card" data-audio-card="' + esc(x.id || x.url || String(i)) + '"><div class="audio-library-card-top"><span class="audio-library-file-icon">' + icon(x) + '</span><div class="audio-library-card-title"><strong>' + esc(x.title || x.name || '未命名音频') + '</strong><small>' + esc(x.category || '音频资料') + '</small></div><span class="audio-library-format">' + esc(EXT_LABEL[ext] || ext.toUpperCase()) + '</span></div><div class="audio-library-meta"><span>' + esc(bytes(x.size)) + '</span><span>' + esc(x.codec || '浏览器原生播放') + '</span></div><audio class="audio-library-player" controls preload="none" src="' + esc(x.url) + '" aria-label="' + esc(x.title || x.name) + '"></audio><div class="audio-library-file-name" dir="ltr" title="' + esc(x.name || '') + '">' + esc(x.name || '') + '</div><div class="audio-library-error" hidden>此文件暂时无法播放，请检查服务器音频响应。</div></article>';
      });
      html += '</div>';
    }
    html += '<div class="audio-library-note"><b>格式说明</b>：FLAC/WAV 是无损或近无损文件，浏览器支持情况取决于设备；如果某个浏览器不支持，页面会明确提示，不会把你带出应用。音频文件仅来自当前项目已有目录。</div>';
    el.innerHTML = html;
    var search = document.getElementById('audioLibrarySearch');
    if(search) search.addEventListener('input', function(){ state.query=this.value||''; render(); var s=document.getElementById('audioLibrarySearch'); if(s){s.focus(); try{s.setSelectionRange(s.value.length,s.value.length);}catch(e){}} });
    var importer = document.getElementById('audioLibraryImport');
    if(importer) importer.addEventListener('change', function(){ importLocal(this.files); this.value=''; });
    el.querySelectorAll('[data-audio-filter]').forEach(function(btn){ btn.addEventListener('click', function(){ state.filter=this.getAttribute('data-audio-filter')||'all'; render(); }); });
    el.querySelectorAll('.audio-library-player').forEach(function(a){
      a.addEventListener('play', function(){ if(state.audio && state.audio !== a){ try{state.audio.pause();}catch(e){} } state.audio=a; });
      a.addEventListener('error', function(){ var card=a.closest('.audio-library-card'); var er=card&&card.querySelector('.audio-library-error'); if(er) er.hidden=false; });
    });
  }
  async function load(){
    if(state.loaded){ render(); return; }
    showLoading('正在读取音频目录…');
    try{
      var base = typeof window.API_BASE === 'function' ? window.API_BASE() : '';
      var r = await fetch(base + '/api/audio/library?limit=240', {cache:'no-store'});
      var d = await r.json();
      if(!r.ok || !d || d.error) throw new Error((d&&d.error)||'目录读取失败');
      state.items = Array.isArray(d.items) ? d.items : [];
      state.loaded = true;
      render();
    }catch(e){
      var el=mount();
      if(el) el.innerHTML='<div class="audio-library-empty audio-library-failed"><div>!</div><strong>音频目录暂时打不开</strong><span>' + esc(e && e.message || '请稍后重试') + '</span><button type="button" class="act-btn" onclick="window.nurReloadAudioLibrary&&window.nurReloadAudioLibrary()">重新读取</button></div>';
    }
  }
  window.showAudioLibrary = function(){ ensureModal(); if(typeof window.openModal === 'function') window.openModal('mAudioLibrary'); else document.getElementById('mAudioLibrary').classList.add('show'); load(); };
  window.closeAudioLibrary = function(){ var el=document.getElementById('mAudioLibrary'); if(!el) return; el.querySelectorAll('audio').forEach(function(a){try{a.pause();a.currentTime=0;}catch(e){}}); if(typeof window.closeModal === 'function') window.closeModal('mAudioLibrary'); else el.classList.remove('show'); state.audio=null; };
  window.nurReloadAudioLibrary = function(){ state.loaded=false; state.items=[]; load(); };
})();
