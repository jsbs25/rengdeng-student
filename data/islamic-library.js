/* Nour Islamic Library — source-aware catalogue, metadata first, official links preserved. */
(function(){
  'use strict';
  var ISL_SOURCE = 'all', ISL_QUERY = '', ISL_PAGE = 1, ISL_LOADING = false;
  var SOURCES = [
    {id:'maktabah',icon:'📚',title:'Maktabah Salafiyyah',ar:'مكتبة السلفية',desc:'信仰 · 法学 · 圣训 · 经注 · 宣教书籍',lang:'阿拉伯语 / 乌尔都语',url:'https://maktabahsalafiyyah.org/category/books/',kind:'公开书目 API'},
    {id:'shamela',icon:'🗂',title:'المكتبة الشاملة',ar:'Shamela',desc:'法学 · 法源学 · 经注 · 圣训 · 语言',lang:'阿拉伯语',url:'https://shamela.ws/',kind:'官方只读目录 / MCP'},
    {id:'sunnah',icon:'📜',title:'六大部圣训',ar:'الكتب الستة',desc:'布哈里 · 穆斯林 · 艾布·达伍德 · 提尔密济 · 奈萨仪 · 伊本·马哲',lang:'阿拉伯语 / 多语译文',url:'https://sunnah.com/',kind:'官方书目与原文链接'},
    {id:'quran',icon:'🕋',title:'古兰经与经注',ar:'القرآن والتفسير',desc:'114 章 · 原文 · 中文译文 · 经注 · 真人诵读',lang:'阿拉伯语 / 中文',url:'https://quran.com/',kind:'内置内容 + 官方 API 回退'},
    {id:'archive',icon:'🏛',title:'Internet Archive / Open Library',ar:'المكتبة المفتوحة',desc:'逐条核验权利的公版扫描本与书目',lang:'多语',url:'https://archive.org/advancedsearch.php',kind:'元数据 / 公版按需读取'}
  ];
  var HADITH = [
    {title:'صحيح البخاري · Sahih al-Bukhari',meta:'97 书 · 六大部',url:'https://sunnah.com/bukhari'},
    {title:'صحيح مسلم · Sahih Muslim',meta:'57 书 · 六大部',url:'https://sunnah.com/muslim'},
    {title:'سنن أبي داود · Sunan Abi Dawud',meta:'43 书 · 六大部',url:'https://sunnah.com/abudawud'},
    {title:'جامع الترمذي · Jami at-Tirmidhi',meta:'46 书 · 六大部',url:'https://sunnah.com/tirmidhi'},
    {title:'سنن النسائي · Sunan an-Nasa’i',meta:'52 书 · 六大部',url:'https://sunnah.com/nasai'},
    {title:'سنن ابن ماجه · Sunan Ibn Majah',meta:'37 书 · 六大部',url:'https://sunnah.com/ibnmajah'}
  ];
  function esc(s){ return typeof catEsc === 'function' ? catEsc(s) : String(s == null ? '' : s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];}); }
  function sourceById(id){ for(var i=0;i<SOURCES.length;i++) if(SOURCES[i].id===id) return SOURCES[i]; return null; }
  function sourceCards(){
    return SOURCES.map(function(s){
      return '<button class="isl-source-card' + (ISL_SOURCE===s.id?' on':'') + '" onclick="islamicPick(\''+s.id+'\')">'+
        '<span class="isl-source-icon">'+s.icon+'<\/span><span class="isl-source-copy"><b>'+esc(s.title)+'<\/b><em>'+esc(s.ar)+'<\/em><small>'+esc(s.desc)+'<\/small><i>'+esc(s.kind)+'<\/i><\/span><span class="isl-source-arrow">›<\/span><\/button>';
    }).join('');
  }
  function hadithCards(){
    return '<div class="isl-section-head"><div><b>六大部圣训<\/b><span>官方书目与原文入口<\/span><\/div><a href="https://sunnah.com/developers" target="_blank" rel="noopener">接入说明 ↗<\/a><\/div><div class="isl-hadith-grid">'+HADITH.map(function(h){return '<a class="isl-hadith-card" href="'+h.url+'" target="_blank" rel="noopener"><strong>'+esc(h.title)+'<\/strong><small>'+esc(h.meta)+'<\/small><span>打开官方阅读 ↗<\/span><\/a>';}).join('')+'<\/div>';
  }
  function quranCard(){
    return '<div class="isl-quran-card"><div class="isl-quran-mark">﷽<\/div><div><b>古兰经学习中心<\/b><span>114 章 · 原文 · 译文 · 经注 · 真人诵读 · 逐页 AI 讲解<\/span><\/div><button onclick="showQuran()">进入阅读<\/button><\/div>';
  }
  function resultCard(x){
    var title = x.title || x.name || '未命名书目';
    var desc = x.excerpt || x.description || x.meta || '';
    var url = x.url || x.link || '';
    var foot = '<span>' + esc(x.category || x.author || x.rights || '元数据') + '<\/span>';
    var link = url ? '<a href="' + esc(url) + '" target="_blank" rel="noopener">查看官方来源 ↗<\/a>' : '';
    return '<article class="isl-result"><div class="isl-result-source">' + esc(x.source_name || (sourceById(ISL_SOURCE)||{}).title || '公开来源') + '<\/div><h3>' + esc(title) + '<\/h3><p>' + esc(String(desc).split('<').join('').split('>').join('').slice(0,220)) + '<\/p><div class="isl-result-foot">' + foot + link + '<\/div><\/article>';
  }
  function renderShell(results, err){
    var body = document.getElementById('mCatBody'); if(!body) return;
    var tabs = typeof libTabs === 'function' ? libTabs() : '';
    var source = sourceById(ISL_SOURCE);
    var intro = '<section class="isl-hero"><div class="isl-kicker">مكتبة إسلامية · ISLAMIC LIBRARY<\/div><h1>伊斯兰经典图书馆<\/h1><p>按来源、学科和版本进入阅读。页面优先保留原作者、原版本与官方链接。<\/p><div class="isl-notice">公开元数据同步 · 正文按需读取 · 受保护内容只提供官方入口<\/div><\/section>';
    var filters = '<div class="isl-toolbar"><input id="islQuery" value="'+esc(ISL_QUERY)+'" placeholder="搜索书名、作者、学科…" onkeydown="if(event.key===\'Enter\')islamicSearch()"><button onclick="islamicSearch()">搜索<\/button><button class="isl-clear" onclick="islamicClear()">清除<\/button><\/div>';
    var active = source ? '<div class="isl-active"><span>'+source.icon+'<\/span><b>'+esc(source.title)+'<\/b><small>'+esc(source.lang)+' · <a href="'+source.url+'" target="_blank" rel="noopener">官方来源 ↗<\/a><\/small><\/div>' : '';
    var top = '<div class="isl-source-grid">'+sourceCards()+'<\/div>';
    var bodyHtml = intro + filters + active + top;
    if(ISL_SOURCE==='all' && !ISL_QUERY){ bodyHtml += quranCard() + hadithCards(); }
    if(err){ bodyHtml += '<div class="isl-empty">来源暂时不可访问。你仍可以从上面的官方入口打开阅读。<br><small>'+esc(err)+'<\/small><\/div>'; }
    else if(ISL_LOADING){ bodyHtml += '<div class="isl-loading">正在读取公开书目元数据…<\/div>'; }
    else if(results && results.length){ bodyHtml += '<div class="isl-section-head"><div><b>公开书目结果<\/b><span>第 '+ISL_PAGE+' 页 · 仅展示来源元数据<\/span><\/div><\/div><div class="isl-results">'+results.map(resultCard).join('')+'<\/div><div class="isl-more"><button onclick="islamicMore()">加载更多<\/button><\/div>'; }
    else if(ISL_QUERY || ISL_SOURCE==='maktabah' || ISL_SOURCE==='archive'){ bodyHtml += '<div class="isl-empty">没有找到匹配书目。换一个关键词，或打开来源官方目录继续查找。<\/div>'; }
    body.innerHTML = tabs + bodyHtml;
  }
  function load(){
    if(ISL_SOURCE==='all' && !ISL_QUERY){ renderShell([], null); return; }
    ISL_LOADING = true; renderShell([], null);
    var u = API_BASE() + '/api/islamic/search?source='+encodeURIComponent(ISL_SOURCE)+'&q='+encodeURIComponent(ISL_QUERY)+'&page='+ISL_PAGE+'&size=24';
    fetch(u).then(function(r){return r.json();}).then(function(d){ ISL_LOADING=false; renderShell(d.items||[], d.error||null); }).catch(function(e){ ISL_LOADING=false; renderShell([], String(e&&e.message||e)); });
  }
  window.showIslamicLibrary = function(){
    // 预先告知 nav：这是来源目录的首次打开，不应初始化历史书库。
    window.NUR_LIBRARY_INITIAL_TAB = 'islamic-sources';
    nav('learn');
    LIB_TAB='islamic-sources'; ISL_SOURCE='all'; ISL_QUERY=''; ISL_PAGE=1;
    var open = function(){
      if(window.NUR_ACTIVE_TAB === 'learn' && LIB_TAB === 'islamic-sources') load();
    };
    // WebKit 自动化与部分旧设备可能暂停 rAF；定时器更可靠且足够避免同步覆盖。
    setTimeout(open, 30);
  };
  window.islamicPick = function(id){ ISL_SOURCE=id; ISL_QUERY=''; ISL_PAGE=1; load(); };
  window.islamicSearch = function(){ var el=document.getElementById('islQuery'); ISL_QUERY=el?String(el.value||'').trim():''; ISL_PAGE=1; load(); };
  window.islamicClear = function(){ ISL_QUERY=''; ISL_PAGE=1; load(); };
  window.islamicMore = function(){ ISL_PAGE++; load(); };
})();
