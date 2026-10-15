/* Nour Page Analysis — on-demand, cached, evidence-aware page explanations */
(function(){
  'use strict';
  var cache = {};
  var inflight = {};
  var baseRender = window.renderRead;
  var maxText = 6500;
  var requestTimeoutMs = 35000;

  function esc(v){
    v = String(v == null ? '' : v);
    if(typeof window.catEsc === 'function') return window.catEsc(v);
    return v.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
  }
  function arr(v){
    if(Array.isArray(v)) return v;
    if(v == null || v === '') return [];
    return [v];
  }
  function text(v){ return String(v == null ? '' : v).trim(); }
  // Mixed Arabic/Chinese strings are isolated per field so punctuation, numbers
  // and Chinese fragments do not inherit one global RTL direction.
  function bidi(v, cls){
    var value = text(v);
    if(!value) return '';
    return '<span class=\"rd-page-analysis__bidi' + (cls ? ' ' + cls : '') + '\" dir=\"auto\">' + esc(value) + '</span>';
  }
  function bidiBlock(v, cls){
    var value = text(v);
    if(!value) return '';
    return '<div class=\"rd-page-analysis__bidi rd-page-analysis__bidi--block' + (cls ? ' ' + cls : '') + '\" dir=\"auto\">' + esc(value) + '</div>';
  }
  var SCHOOL_OPTIONS = {
    compare:{label:'综合对比视角',ar:'مقارنة المذاهب',hint:'先识别原文与作者所属传统，再并列说明哈乃斐、马立克、沙斐仪和汉百里视角；不把任何一派写成唯一共识。'},
    hanafi:{label:'哈乃斐学派',ar:'الحنفية',hint:'优先解释哈乃斐术语、证据层级与内部意见；跨学派内容只作有来源的比较，不把哈乃斐表达扩写成作者原话。'},
    maliki:{label:'马立克学派',ar:'المالكية',hint:'优先关注马立克传统中的圣训、麦地那实践、公共利益与学派传承；具体归属必须回到原文、传本和版本。'},
    shafii:{label:'沙斐仪学派',ar:'الشافعية',hint:'优先解释沙斐仪法源论证、文本说明、圣训规范性与类比；区分沙斐仪本人、后世学派和其他学派观点。'},
    hanbali:{label:'汉百里学派',ar:'الحنابلة',hint:'优先关注汉百里传统对经文、圣训、先贤传述和推理的处理；不把后世学派总结倒写成原文或普遍共识。'}
  };
  var LANGUAGE_OPTIONS = {
    'zh-CN':{label:'中文讲解',ar:'شرح بالصينية'},
    'ar':{label:'阿拉伯语讲解',ar:'شرح بالعربية'},
    'en':{label:'英语讲解',ar:'Explanation in English'}
  };
  function safeSchool(v){ return SCHOOL_OPTIONS[v] ? v : 'compare'; }
  function safeLanguage(v){ return LANGUAGE_OPTIONS[v] ? v : 'zh-CN'; }
  function currentSchool(){
    var v = '';
    try{ v = window.NUR_FIQH_SCHOOL || window.localStorage.getItem('nur_fiqh_school') || ''; }catch(e){}
    return safeSchool(v);
  }
  function currentLanguage(){
    var v = '';
    try{ v = window.NUR_ANALYSIS_LANGUAGE || window.localStorage.getItem('nur_analysis_language') || ''; }catch(e){}
    return safeLanguage(v);
  }
  function schoolLabel(v){ return (SCHOOL_OPTIONS[safeSchool(v)] || SCHOOL_OPTIONS.compare).label; }
  function languageLabel(v){ return (LANGUAGE_OPTIONS[safeLanguage(v)] || LANGUAGE_OPTIONS['zh-CN']).label; }
  function classifyMeta(meta){
    var hint = [meta && meta.t,meta && meta.c,meta && meta.c_ar,meta && meta.discipline,meta && meta.tags,meta && meta.schools,meta && meta.ai_profile].join(' ');
    if(/经注|تفسير|tafsir/i.test(hint)) return 'tafsir';
    if(/圣训|حديث|hadith|سنة|布哈里|穆斯林/i.test(hint)) return 'hadith';
    if(/法学|法源|فقه|أصول|fiqh|usul/i.test(hint)) return 'fiqh';
    return 'book';
  }
  function current(){
    var page = (typeof window.RD_PAGE === 'number') ? window.RD_PAGE : (window.RD_PAGE || 0);
    var pages = window.RD_PAGES || [];
    var raw = text(pages[page] || '');
    var titleEl = document.getElementById('mReaderTitle');
    var title = text(titleEl && titleEl.textContent) || '经典阅读';
    var total = pages.length || 1;
    var kind = 'book', surah = 0, surahName = '', bookMeta = null;
    try{
      if(window.RD_AUDIO && window.RD_AUDIO.kind === 'quran'){
        kind = 'quran';
        if(window.currentSurah){ surah = parseInt(window.currentSurah.id || 0,10) || 0; surahName = text(window.currentSurah.n || window.currentSurah.tz || ''); }
      }else if(title.indexOf('经注') >= 0 || title.indexOf('تفسير') >= 0){ kind = 'tafsir'; }
      else if(/圣训|حديث|Hadith|穆斯林|布哈里/.test(title)){ kind = 'hadith'; }
      else if(/法学|法源|فقه|أصول|Fiqh|Usul/.test(title)){ kind = 'fiqh'; }
      if(window.RD_BOOK_META){
        bookMeta = window.RD_BOOK_META;
        // 只有独立书目导读页才是 catalog；已打开的 OpenITI 正文必须按正文页解释。
        kind = window.RD_ISLAMIC_GUIDE ? 'catalog' : classifyMeta(bookMeta);
      }
    }catch(e){}
    var school = currentSchool(), language = currentLanguage();
    return {page:page + 1,total:total,text:raw.slice(0,maxText),title:title,kind:kind,surah:surah,surah_name:surahName,book_meta:bookMeta,fiqh_school:school,fiqh_school_label:schoolLabel(school),response_language:language,response_language_label:languageLabel(language)};
  }
  function compact(v,n){ return text(v).slice(0,n || 900); }
  function compactList(v,n,count){
    return Array.isArray(v) ? v.slice(0,count || 5).map(function(x){ return compact(typeof x === 'object' ? (x.text || x.explanation || x.title || '') : x, n || 480); }).join('；') : compact(v,n || 900);
  }
  function analysisMeta(b){
    if(!b || typeof b !== 'object') return null;
    var g = b.ai_guide || {};
    var sourceInput = Array.isArray(b.sources) ? b.sources : (Array.isArray(g.sources) ? g.sources : []);
    if(!sourceInput.length && (b.u || b.url)) sourceInput = [{title:b.source || '官方来源',url:b.u || b.url,why:[b.access,b.rights].filter(Boolean).join('；')}];
    var sources = sourceInput.slice(0,8).map(function(x){
      if(!x || typeof x !== 'object') return null;
      return {title:compact(x.title || x.label,180),url:text(x.url).slice(0,600),why:compact(x.why || x.note,520)};
    }).filter(function(x){ return x && (x.title || x.url); });
    return {id:b.id,t:b.t,a:b.a,y:b.y,c:b.c,c_ar:b.c_ar,discipline:b.discipline,u:b.u,source:b.source,access:b.access,rights:b.rights,level:b.level,intro:b.intro,
      fiqh_schools:Array.isArray(b.fiqh_schools) ? b.fiqh_schools.slice(0,4) : [],
      fiqh_school_labels:Array.isArray(b.fiqh_school_labels) ? b.fiqh_school_labels.slice(0,4) : [],
      fiqh_school_evidence:b.fiqh_school_evidence || {},
      fiqh_school_inference:compact(b.fiqh_school_inference,500),source_evidence:sources,
      ai_profile:compact(g.ai_profile || b.ai_profile,900),ai_guide_version:b.ai_guide_version,guide_summary:compact(g.summary,1100),guide_background:compact(g.historical_context,1100),guide_objectives:compactList(g.study_objectives,420,5),guide_terms:compactList(g.key_terms,300,8),guide_focus:compactList(g.comparative_focus,420,4),guide_boundary:compact(g.evidence_boundary,1000)};
  }
  function key(c){ return [c.kind,c.title,c.book_meta && c.book_meta.id || '',c.book_meta && c.book_meta.ai_guide_version || '',c.fiqh_school,c.response_language,c.page,c.text.slice(0,240),c.text.length].join('|'); }
  function supportsSchool(c){
    if(!c) return false;
    if(c.kind === 'fiqh') return true;
    if(c.kind !== 'catalog') return false;
    var meta = c.book_meta || {};
    return /法学|法源|فقه|أصول|Fiqh|Usul/i.test([c.title,meta.c,meta.c_ar,meta.discipline].join(' '));
  }
  function schoolControl(c){
    if(!supportsSchool(c)) return '';
    var active = safeSchool(c.fiqh_school), h = '<div class="rd-page-analysis__school"><div class="rd-page-analysis__school-copy"><strong>法学派视角</strong><small>切换后重新分析；只改变解释镜头，不改变原文和证据。</small></div><select class="rd-page-analysis__school-select" aria-label="选择法学派视角" onchange="window.nurSetFiqhSchool(this.value)">';
    Object.keys(SCHOOL_OPTIONS).forEach(function(k){ var x=SCHOOL_OPTIONS[k]; h += '<option value="' + esc(k) + '"' + (k === active ? ' selected' : '') + '>' + esc(x.label + ' · ' + x.ar) + '</option>'; });
    return h + '</select></div>';
  }
  function languageControl(c){
    var active = safeLanguage(c.response_language), h = '<div class="rd-page-analysis__language"><div class="rd-page-analysis__school-copy"><strong>讲解语言</strong><small>切换语言后重新生成，原文与证据不变。</small></div><select class="rd-page-analysis__language-select" aria-label="选择 AI 讲解语言" onchange="window.nurSetAnalysisLanguage(this.value)">';
    Object.keys(LANGUAGE_OPTIONS).forEach(function(k){ var x=LANGUAGE_OPTIONS[k]; h += '<option value="' + esc(k) + '"' + (k === active ? ' selected' : '') + '>' + esc(x.label + ' · ' + x.ar) + '</option>'; });
    return h + '</select></div>';
  }
  function currentPanel(){ return document.getElementById('rdPageAnalysis'); }
  function usable(c){
    var v = text(c && c.text);
    return v.length >= 6 && !/^(正在载入|尚未载入|原文载入失败|（本页没有可显示)/.test(v);
  }
  function panelOpen(){ var p=currentPanel(); return !!(p && p.dataset && p.dataset.open === '1'); }
  function panelClass(){ return 'rd-page-analysis' + (panelOpen() ? ' is-open' : ''); }
  function openPanel(){
    var p=currentPanel(); if(!p) return;
    p.dataset.open='1'; p.className='rd-page-analysis is-open';
    try{ setTimeout(function(){ p.scrollIntoView({behavior:'smooth',block:'nearest'}); },30); }catch(e){ try{ p.scrollIntoView(); }catch(e2){} }
  }
  function renderUnavailable(message){
    var p=currentPanel(); if(!p) return;
    p.dataset.open='1'; p.className='rd-page-analysis is-open';
    p.innerHTML='<div class="rd-page-analysis__head"><div class="rd-page-analysis__mark">…</div><div class="rd-page-analysis__title"><strong>本页正文还没准备好</strong><small>不会把加载提示当成书籍内容发送给 AI。</small></div><button class="rd-page-analysis__run" type="button" onclick="event.stopPropagation();window.nurAnalyzeCurrentPage(this)">再检查</button></div><div class="rd-page-analysis__body"><div class="rd-page-analysis__error">'+esc(message || '请等正文加载完成后再试。')+'</div></div>';
  }
  function renderError(message){
    var p=currentPanel(); if(!p) return;
    p.dataset.open='1'; p.className='rd-page-analysis is-open';
    p.innerHTML='<div class="rd-page-analysis__head"><div class="rd-page-analysis__mark">!</div><div class="rd-page-analysis__title"><strong>本页讲解暂时没有生成</strong><small>原文仍可继续阅读；不会把不完整结果当成可靠结论。</small></div><button class="rd-page-analysis__run" type="button" onclick="event.stopPropagation();window.nurAnalyzeCurrentPage(this)">再试一次</button></div><div class="rd-page-analysis__body"><div class="rd-page-analysis__error">'+esc(message || '网络或 AI 服务暂时不可用，请稍后重试。')+'</div></div>';
  }
  function renderList(items){
    var a = arr(items).filter(function(x){ return text(typeof x === 'object' ? (x.text || x.point || x.note || x.title) : x); });
    if(!a.length) return '';
    return '<ul class="rd-page-analysis__list">' + a.map(function(x){
      var v = typeof x === 'object' ? (x.text || x.point || x.note || x.title || '') : x;
      return '<li>' + bidi(v) + '</li>';
    }).join('') + '</ul>';
  }
  function renderRefs(items){
    var a = arr(items).filter(function(x){ return typeof x === 'object' ? text(x.reference || x.citation || x.title || x.label) : text(x); });
    if(!a.length) return '';
    return '<div class="rd-page-analysis__refs">' + a.map(function(x){
      var ref = typeof x === 'object' ? (x.reference || x.citation || x.title || x.label || '') : x;
      var note = typeof x === 'object' ? (x.note || x.relevance || x.explanation || '') : '';
      var status = typeof x === 'object' ? (x.status || x.confidence || '需核对原典') : '需核对原典';
      var url = typeof x === 'object' && /^https?:\/\//i.test(text(x.url)) ? text(x.url).slice(0,700) : '';
      return '<div class="rd-page-analysis__ref"><strong>' + bidi(ref) + '</strong>' + (note ? '<span>' + bidi(note) + '</span>' : '') + '<span class="rd-page-analysis__badge">' + bidi(status) + '</span>' + (url ? '<a class="rd-page-analysis__link" href="' + esc(url) + '" target="_blank" rel="noopener noreferrer">打开核验页面</a>' : '') + '</div>';
    }).join('') + '</div>';
  }
  function renderSchoolComparison(items){
    var a = arr(items).filter(function(x){ return x && typeof x === 'object' && text(x.school || x.label || x.name); }).slice(0,4);
    if(!a.length) return '';
    return '<div class="rd-page-analysis__school-grid">' + a.map(function(x){
      var school = x.school || x.label || x.name || '';
      var position = x.position || x.view || x.summary || '未提供明确立场';
      var basis = x.basis || x.evidence || x.reason || '';
      var status = x.status || x.confidence || '待核验';
      return '<article class="rd-page-analysis__school-card"><div class="rd-page-analysis__school-card-head"><strong>' + bidi(school) + '</strong><span class="rd-page-analysis__badge">' + bidi(status) + '</span></div><div>' + bidi(position) + '</div>' + (basis ? '<small>依据线索：' + bidi(basis) + '</small>' : '') + '</article>';
    }).join('') + '</div>';
  }
  function renderSourceEvidence(meta){
    if(!meta || typeof meta !== 'object') return '';
    var sourceRaw = arr(meta.source_evidence);
    if(!sourceRaw.length && (meta.u || meta.url)) sourceRaw = [{title:meta.source || '官方来源',url:meta.u || meta.url,why:[meta.access,meta.rights].filter(Boolean).join('；')}];
    var sources = sourceRaw.filter(function(x){ return x && typeof x === 'object' && (text(x.title) || text(x.url)); }).slice(0,8);
    var html = '';
    if(sources.length){
      html += '<div class="rd-page-analysis__source-list">' + sources.map(function(x){
        var title = x.title || '官方来源';
        var why = x.why || '';
        var url = /^https?:\/\//i.test(text(x.url)) ? text(x.url).slice(0,700) : '';
        return '<div class="rd-page-analysis__source"><strong>' + bidi(title) + '</strong>' + (why ? '<span>' + bidi(why) + '</span>' : '') + (url ? '<a class="rd-page-analysis__link" href="' + esc(url) + '" target="_blank" rel="noopener noreferrer">打开官方来源</a>' : '') + '</div>';
      }).join('') + '</div>';
    }
    if(meta.id && typeof window.nourOpenCatalogBook === 'function') html += '<button type="button" class="rd-page-analysis__inapp" onclick="event.stopPropagation();window.nourOpenCatalogBook(' + JSON.stringify(String(meta.id)) + ')">在 NOUR 内打开这部原文</button>';
    return html;
  }
  function renderTerms(items){
    var a = arr(items).filter(function(x){ return typeof x === 'object' ? text(x.ar || x.term || x.word) : text(x); });
    if(!a.length) return '';
    return '<div class="rd-page-analysis__terms">' + a.map(function(x){
      var ar = typeof x === 'object' ? (x.ar || x.term || x.word || '') : x;
      var cn = typeof x === 'object' ? (x.cn || x.meaning || x.note || '') : '';
      return '<div class="rd-page-analysis__term"><b dir=\"auto\">' + esc(ar) + '</b>' + (cn ? '<span dir="auto">' + esc(cn) + '</span>' : '') + '</div>';
    }).join('') + '</div>';
  }
  function section(title, body){ return body ? '<section class="rd-page-analysis__section"><h4>' + esc(title) + '</h4>' + body + '</section>' : ''; }
  function renderAnalysis(a){
    var p = currentPanel(); if(!p) return;
    a = a || {};
    var c = current();
    var catalogNote = c.kind === 'catalog' ? '<div class="rd-page-analysis__catalog-note">当前为<strong>书目级 AI 导读</strong>：模型只基于本卡公开元数据、导览与当前导读页工作，不等于已取得或核验整本正文。</div>' : '';
    var schoolNote = supportsSchool(c) ? '<div class="rd-page-analysis__school-note"><b>当前视角：' + esc(c.fiqh_school_label) + '</b><span>' + esc((SCHOOL_OPTIONS[c.fiqh_school] || SCHOOL_OPTIONS.compare).hint) + '</span></div>' : '';
    var html = '<div class="rd-page-analysis__head"><div class="rd-page-analysis__mark">✦</div><div class="rd-page-analysis__title"><strong>' + (c.kind === 'catalog' ? '书目 AI 导读' : '本页学习讲解') + '</strong><small>先看原文，再看结构、问题与依据；这是学习辅助，不是教法裁决。</small></div><button class="rd-page-analysis__run" type="button" onclick="event.stopPropagation();window.nurAnalyzeCurrentPage(this)">重新分析</button></div><div class="rd-page-analysis__body">' + catalogNote + languageControl(c) + schoolControl(c) + schoolNote;
    html += section('这一页讲了什么', '<div class="rd-page-analysis__text">' + bidiBlock(a.overview || '暂时没有摘要。') + '</div>');
    html += section('核心内容', renderList(a.key_points || a.main_points));
    html += section('需要想清楚的问题', renderList(a.questions || a.issues));
    html += section('怎么理解或落实', renderList(a.practical_guidance || a.guidance || a.solutions));
    html += section('古兰经依据', renderRefs(a.quran_references || a.quran_evidence));
    html += section('圣训依据', renderRefs(a.hadith_references || a.hadith_evidence));
    html += section('文本结构与论证', renderList(a.text_structure || a.structure));
    html += section('法学与学术背景', renderList(a.fiqh_context || a.fiqh));
    html += section('四学派比较（学习视角）', renderSchoolComparison(a.school_comparison || a.madhhab_comparison));
    html += section('阿拉伯语学习要点', renderList(a.language_notes || a.language_learning));
    html += section('关键词', renderTerms(a.terms));
    var sourceEvidence = renderSourceEvidence(c.book_meta);
    if(sourceEvidence) html += section('原典、版本与来源', sourceEvidence);
    if(a.source_note) html += '<div class="rd-page-analysis__footer">来源说明：' + bidi(a.source_note, 'rd-page-analysis__bidi--block') + '</div>';
    var inference = c.book_meta && c.book_meta.fiqh_school_inference ? '<div class="rd-page-analysis__footer">学派归属说明：' + bidi(c.book_meta.fiqh_school_inference, 'rd-page-analysis__bidi--block') + '</div>' : '';
    html += '<div class="rd-page-analysis__notice">' + bidi(a.caution || '引用、传述和法学观点需要回到原典、可靠经注与合格学者处核对；本页 AI 不发布法特瓦，也不替代正式教法咨询。', 'rd-page-analysis__bidi--block') + '</div>' + inference;
    html += '<div class="rd-page-analysis__footer">AI 生成时间：' + esc(a.generated_at || '本次阅读') + ' · 引用标注为“直接/相关/待核验”时，请优先核对原典。</div></div>';
    p.innerHTML = html;
    p.dataset.open = '1';
    p.className = 'rd-page-analysis is-open';
  }
  function renderLoading(){
    var p = currentPanel(); if(!p) return;
    var c = current();
    p.dataset.open = '1';
    p.className = 'rd-page-analysis is-open';
    p.innerHTML = '<div class="rd-page-analysis__head"><div class="rd-page-analysis__mark">✦</div><div class="rd-page-analysis__title"><strong>正在分析本页</strong><small>会结合页面内容整理主旨、问题、依据和法学背景。</small></div><button class="rd-page-analysis__run" type="button" disabled>分析中…</button></div><div class="rd-page-analysis__body">' + languageControl(c) + schoolControl(c) + '<div class="rd-page-analysis__loading"><i class="rd-page-analysis__spinner"></i><span>正在生成「' + esc(c.response_language_label || '中文讲解') + ' · ' + esc(c.fiqh_school_label || '综合对比视角') + '」学习笔记；经典原文不会被修改。</span></div></div>';
  }
  function renderIntro(){
    var p = currentPanel(); if(!p) return;
    var c = current();
    var title = c.kind === 'catalog' ? '书目 AI 导读' : '本页学习讲解';
    var small = c.kind === 'catalog' ? '基于公开书目元数据生成；正文请以官方版本为准。' : '针对当前页正文生成主旨、重点、问题、依据和阿拉伯语学习提示。';
    var intro = c.kind === 'catalog' ? '点击“开始讲解”，AI 会围绕作者、时代、学科、版本、官方来源和阿拉伯语学习重点生成导读；它不会把目录信息伪装成原文或法特瓦。' : '点击“开始讲解”，AI 会只分析当前页，区分原文、作者观点、学派解释和模型归纳；未经核验的引用会明确标为“待核验”。';
    p.className = panelClass();
    p.innerHTML = '<div class="rd-page-analysis__head"><div class="rd-page-analysis__mark">✦</div><div class="rd-page-analysis__title"><strong>' + title + '</strong><small>' + small + '</small></div><button class="rd-page-analysis__run" type="button" onclick="event.stopPropagation();window.nurAnalyzeCurrentPage(this)">开始讲解</button></div><div class="rd-page-analysis__body">' + languageControl(c) + schoolControl(c) + '<div class="rd-page-analysis__intro">' + intro + '</div></div>';
  }
  function mount(){
    if(!document.getElementById('mReaderBody')) return;
    var bars = document.querySelectorAll('#mReaderBody .rd-bar');
    for(var i=0;i<bars.length;i++){
      if(bars[i].querySelector('.rd-page-analysis-trigger')) continue;
      var b = document.createElement('button');
      b.type='button'; b.className='rd-page-analysis-trigger rd-ic'; b.title='本页 AI 讲解'; b.setAttribute('aria-label','本页 AI 讲解'); b.textContent='AI';
      b.onclick=function(ev){ if(ev) ev.stopPropagation(); openPanel(); window.nurAnalyzeCurrentPage(this); };
      var more = bars[i].querySelector('.rd-ic[title="更多"]');
      if(more && more.parentNode) more.parentNode.insertBefore(b, more); else bars[i].appendChild(b);
    }
    var paper = document.querySelector('#mReaderBody .rd-paper');
    if(!paper) return;
    var p = document.getElementById('rdPageAnalysis');
    if(!p){
      p = document.createElement('section'); p.id='rdPageAnalysis'; p.className='rd-page-analysis'; p.setAttribute('onclick','event.stopPropagation()');
      paper.appendChild(p);
    }
    var c=current(), k=key(c);
    if(cache[k] && !cache[k].retryable) renderAnalysis(cache[k]); else if(usable(c)) renderIntro(); else renderUnavailable('请等正文加载完成后再试。');
  }
  window.nourOpenCatalogBook = function(id){
    try{
      if(!id) return;
      if(typeof window.openIslamicBook === 'function') return window.openIslamicBook(id);
      if(typeof window.openBookById === 'function') return window.openBookById(id);
    }catch(e){}
  };
  window.nurSetFiqhSchool = function(v){
    var school = safeSchool(v);
    try{ window.NUR_FIQH_SCHOOL = school; window.localStorage.setItem('nur_fiqh_school', school); }catch(e){ window.NUR_FIQH_SCHOOL = school; }
    openPanel(); renderIntro();
  };
  window.nurSetAnalysisLanguage = function(v){
    var language = safeLanguage(v);
    try{ window.NUR_ANALYSIS_LANGUAGE = language; window.localStorage.setItem('nur_analysis_language', language); }catch(e){ window.NUR_ANALYSIS_LANGUAGE = language; }
    openPanel(); renderIntro();
  };
  function fetchWithTimeout(url, options, ms){
    var timer;
    var timeout=new Promise(function(_,reject){ timer=setTimeout(function(){ reject(new Error('AI 讲解等待超过35秒，请点击“再试一次”')); },ms); });
    return Promise.race([fetch(url,options),timeout]).then(function(v){ clearTimeout(timer); return v; },function(e){ clearTimeout(timer); throw e; });
  }
  window.nurAnalyzeCurrentPage = async function(btn){
    openPanel();
    var c=current();
    if(!usable(c)){ renderUnavailable(c.text ? '当前页正在加载或没有足够正文，请稍后再试。' : '当前页没有足够正文可供分析。'); return; }
    var k=key(c);
    if(cache[k] && !cache[k].retryable){ renderAnalysis(cache[k]); return; }
    if(inflight[k]){ renderLoading(); return; }
    inflight[k]=true;
    renderLoading();
    try{
      var payload={book_title:c.title,book_kind:c.kind,book_meta:analysisMeta(c.book_meta),fiqh_school:c.fiqh_school,fiqh_school_label:c.fiqh_school_label,response_language:c.response_language,response_language_label:c.response_language_label,page_number:c.page,page_total:c.total,text:c.text,surah:c.surah,surah_name:c.surah_name,device_id:(typeof window.devId==='function'?window.devId():''),token:(typeof window.webToken==='function'?window.webToken():'')};
      var r=await fetchWithTimeout((typeof window.API_BASE==='function'?window.API_BASE():'')+'/api/page/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)},requestTimeoutMs);
      var d=await r.json();
      if(!r.ok || !d.ok) throw new Error((d&&d.error)||'分析服务暂时不可用');
      var result=d.analysis || {};
      if(!d.retryable && !result.retryable) cache[k]=result;
      renderAnalysis(result);
    }catch(e){ renderError(e && e.message ? e.message : '网络或 AI 服务暂时不可用'); }
    finally{ delete inflight[k]; }
  };
  if(typeof baseRender === 'function'){
    window.renderRead=function(){
      var r=baseRender.apply(this,arguments);
      try{ setTimeout(mount,0); }catch(e){ mount(); }
      return r;
    };
  }
  document.addEventListener('DOMContentLoaded',function(){ setTimeout(mount,0); });
  window.nurPageAnalysis={mount:mount,clear:function(){cache={};mount();}};
})();
