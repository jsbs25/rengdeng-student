/* Nour Arabic Challenge — vocabulary, grammar, sentence ordering and local progress */
(function(){
  'use strict';
  var KEY = 'nur_challenge_v1';
  var META = [
    {title:'词义雷达', ar:'رادار المفردات', sub:'把高频阿语词汇变成反应力', mode:'vocab', count:5, icon:'◈', color:'gold'},
    {title:'冠词之门', ar:'بوابة التعريف', sub:'掌握 ال、太阳字母和月亮字母', mode:'grammar', count:5, icon:'☽', color:'teal'},
    {title:'词尾炼金', ar:'كيمياء الإعراب', sub:'主格、宾格、属格一眼辨认', mode:'grammar', count:5, icon:'✦', color:'violet'},
    {title:'拼句工坊', ar:'ورشة الجمل', sub:'把词块排成自然的阿拉伯语句子', mode:'sentence', count:4, icon:'⌘', color:'blue'},
    {title:'词汇闪电', ar:'برق الكلمات', sub:'限时反应，建立阿中直觉', mode:'vocab', count:6, icon:'ϟ', color:'orange'},
    {title:'混合大师', ar:'المستوى المتقدم', sub:'语法、词汇、句式综合挑战', mode:'mixed', count:6, icon:'♛', color:'red'}
  ];
  var WORDS = [
    ['كِتَاب','书','book'],['مَاء','水','water'],['بَيْت','房子','house'],['طَالِب','学生','student'],
    ['مَدْرَسَة','学校','school'],['مَكْتَبَة','图书馆','library'],['قَلَم','笔','pen'],['مُعَلِّم','老师','teacher'],
    ['صَدِيق','朋友','friend'],['سُوق','市场','market'],['طَعَام','食物','food'],['قَهْوَة','咖啡','coffee'],
    ['طَرِيق','道路','road'],['مَدِينَة','城市','city'],['جَمِيل','美丽的','beautiful'],['كَبِير','大的','big'],
    ['صَغِير','小的','small'],['جَدِيد','新的','new'],['يَوْم','一天','day'],['لَيْل','夜晚','night'],
    ['عِلْم','知识','knowledge'],['حُبّ','爱','love'],['سَلَام','和平 / 问候','peace / greeting'],['نُور','光','light'],
    ['يَقْرَأُ','他读','he reads'],['يَكْتُبُ','他写','he writes'],['يَذْهَبُ','他去','he goes'],['يَفْهَمُ','他理解','he understands']
  ];
  var GRAMMAR = [
    {ar:'الْكِتَابُ', prompt:'“这本书”是确指主格，哪一项正确？', answer:'الْكِتَابُ', options:['الْكِتَابُ','كِتَابٌ','الْكِتَابَ','كِتَابٍ'], note:'主格词尾通常是 ـُ；加 ال 后成为确指。'},
    {ar:'كِتَابٌ', prompt:'“一本书（泛指）”应该选择哪一项？', answer:'كِتَابٌ', options:['كِتَابٌ','الْكِتَابُ','كِتَابَ','الْكِتَابِ'], note:'双音符 ـٌ 表示泛指主格，前面没有 ال。'},
    {ar:'رَأَيْتُ الْكِتَابَ', prompt:'句子中的 الْكِتَابَ 是什么格？', answer:'宾格', options:['主格','宾格','属格','双数'], note:'动词 رَأَيْتُ 的宾语使用宾格，词尾是 ـَ。'},
    {ar:'بَابُ الْكِتَابِ', prompt:' الْكِتَابِ 的词尾 ـِ 表示什么？', answer:'属格', options:['主格','宾格','属格','阴性'], note:'属格常见于所有关系结构，词尾是 ـِ。'},
    {ar:'الشَّمْسُ', prompt:'الشَّمْسُ 中的 ال 应如何发音？', answer:'太阳字母：l 不发音', options:['太阳字母：l 不发音','月亮字母：l 清楚发音','完全省略 ال','读成双数'], note:'ش 是太阳字母，الشمس 读作 ash-shams。'},
    {ar:'أَنَا طَالِبٌ', prompt:'这句话为什么不需要“是”？', answer:'阿语名词句通常省略系动词', options:['必须加 هو','阿语名词句通常省略系动词','因为 طالب 是动词','因为 أنا 是复数'], note:'أنا طالب 直译为“我 学生”，意思就是“我是学生”。'},
    {ar:'كَتَبَتْ', prompt:'كَتَبَتْ 表示谁写了？', answer:'她写了', options:['他写了','她写了','他们写了','我写了'], note:'过去式词尾 ـَتْ 表示第三人称阴性单数。'},
    {ar:'أَكْتُبُ', prompt:'现在式前缀 أـ 通常提示谁？', answer:'我', options:['我','你或她','他','我们'], note:'现在式四个常见前缀：أ、ت、ي、ن。'},
    {ar:'لَا أَفْهَمُ', prompt:'如何否定现在式“我明白”？', answer:'لَا + 现在式', options:['ما + 过去式','لَا + 现在式','لَنْ + 名词','不需要否定词'], note:'现在时常用 لا，过去时常用 ما。'},
    {ar:'ذَهَبْنَا', prompt:'过去式词尾 ـنَا 表示谁？', answer:'我们', options:['我','你们','我们','他们'], note:'ـنَا 是第一人称复数“我们”的典型词尾。'},
    {ar:'طَالِبَةٌ', prompt:'词尾 ة 常常提示什么？', answer:'阴性', options:['阳性','阴性','双数','过去时'], note:'很多阴性名词以 ة 结尾，但也要结合词汇记忆。'},
    {ar:'نَذْهَبُ', prompt:'现在式前缀 نـ 表示谁？', answer:'我们', options:['我','你','他','我们'], note:'نـ 常提示第一人称复数“我们”。'}
  ];
  var SENTENCES = [
    {cn:'我学习阿拉伯语。', ar:'أَدْرُسُ الْعَرَبِيَّةَ', tokens:['أَدْرُسُ','الْعَرَبِيَّةَ']},
    {cn:'你好，早上好。', ar:'السَّلَامُ عَلَيْكُمْ، صَبَاحُ الْخَيْرِ', tokens:['السَّلَامُ','عَلَيْكُمْ،','صَبَاحُ','الْخَيْرِ']},
    {cn:'我想喝咖啡。', ar:'أُرِيدُ أَنْ أَشْرَبَ الْقَهْوَةَ', tokens:['أُرِيدُ','أَنْ','أَشْرَبَ','الْقَهْوَةَ']},
    {cn:'图书馆在哪里？', ar:'أَيْنَ الْمَكْتَبَةُ؟', tokens:['أَيْنَ','الْمَكْتَبَةُ؟']},
    {cn:'他是新学生。', ar:'هُوَ طَالِبٌ جَدِيدٌ', tokens:['هُوَ','طَالِبٌ','جَدِيدٌ']},
    {cn:'我们去市场。', ar:'نَذْهَبُ إِلَى السُّوقِ', tokens:['نَذْهَبُ','إِلَى','السُّوقِ']},
    {cn:'我不明白。', ar:'لَا أَفْهَمُ', tokens:['لَا','أَفْهَمُ']},
    {cn:'她写了作业。', ar:'كَتَبَتْ الْوَاجِبَ', tokens:['كَتَبَتْ','الْوَاجِبَ']}
  ];
  var CA = {screen:'map', stage:0, questions:[], index:0, score:0, hearts:3, wrong:[], answered:false, selected:[]};
  var STATE = loadState();
  function loadState(){ try{ var x=JSON.parse(localStorage.getItem(KEY)||'{}'); return {done:x.done||[],best:x.best||{},xp:x.xp||0}; }catch(e){ return {done:[],best:{},xp:0}; } }
  function saveState(){ try{ localStorage.setItem(KEY,JSON.stringify(STATE)); }catch(e){} }
  function esc(v){ return String(v==null?'':v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;'); }
  function shuffle(a){ var x=a.slice(); for(var i=x.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1)),t=x[i];x[i]=x[j];x[j]=t;} return x; }
  function uniq(a){ return a.filter(function(x,i){ return a.indexOf(x)===i; }); }
  function root(){ var el=document.getElementById('mChallenge'); if(el&&el.parentNode!==document.body) document.body.appendChild(el); return el; }
  function body(){ return document.getElementById('mChallengeBody'); }
  function speak(text){ if(window.speechSynthesis){ try{window.speechSynthesis.cancel();var u=new SpeechSynthesisUtterance(text);u.lang='ar-SA';u.rate=.72;window.speechSynthesis.speak(u);}catch(e){} } }
  function show(){ root(); openModal('mChallenge'); CA.screen='map'; render(); }
  window.showChallenge=show;
  function render(){ if(CA.screen==='map') renderMap(); else if(CA.screen==='finish') renderFinish(); else renderQuestion(); }
  function renderMap(){
    var b=body(); if(!b)return;
    var done=STATE.done.length, xp=STATE.xp;
    var h='<div class="ca-shell"><div class="ca-map-hero"><div><span class="ca-kicker">NOUR ARABIC QUEST · رحلة العربية</span><h2>阿拉伯语闯关练习</h2><p>每天几分钟，把“看懂”练成“会用”。选择一关开始，答题后立即看到原因。</p></div><div class="ca-xp"><b>'+xp+'</b><span>学习 XP</span></div></div><div class="ca-map-stats"><span><b>'+done+'</b> / '+META.length+' 关已完成</span><span><i class="ca-dot"></i> 词汇 · 语法 · 拼句</span><button class="ca-small-btn" data-ca-action="reset">↺ 重置进度</button></div><div class="ca-stage-grid">';
    META.forEach(function(m,i){ var n=i+1,open=(n<=2||STATE.done.indexOf(n-1)>=0),best=STATE.best[n]||0,doneNow=STATE.done.indexOf(n)>=0; h+='<button class="ca-stage-card '+(open?'open':'locked')+' '+(doneNow?'done':'')+' ca-'+m.color+'" data-ca-stage="'+n+'" type="button"><span class="ca-stage-number">'+(doneNow?'✓':('0'+n).slice(-2))+'</span><span class="ca-stage-icon">'+m.icon+'</span><span class="ca-stage-copy"><b>'+m.title+'</b><em dir="rtl">'+m.ar+'</em><small>'+m.sub+'</small><label>'+(open?(best?'最佳 '+best+'/'+m.count+' · ':'')+m.count+' 题':'完成上一关后解锁')+'</label></span><span class="ca-stage-arrow">'+(open?'›':'🔒')+'</span></button>'; });
    h+='</div><div class="ca-map-tip"><b>闯关规则</b><span>答对得 XP，答错会显示语法原因；错题会进入生词本/间隔复习。每关 60% 即可解锁下一关。</span></div></div>';
    b.innerHTML=h; bindMap();
  }
  function bindMap(){
    Array.prototype.forEach.call(document.querySelectorAll('[data-ca-stage]'),function(el){el.onclick=function(){var n=parseInt(el.getAttribute('data-ca-stage'),10);if(el.classList.contains('locked')){caToast('先完成上一关，再解锁这一关');return;}start(n);};});
    var r=document.querySelector('[data-ca-action="reset"]'); if(r)r.onclick=function(){if(confirm('确定要重置闯关进度吗？')){STATE={done:[],best:{},xp:0};saveState();renderMap();}};
  }
  function caToast(t){ var b=body(); if(!b)return; var x=document.createElement('div');x.className='ca-toast';x.textContent=t;b.appendChild(x);setTimeout(function(){if(x.parentNode)x.parentNode.removeChild(x);},1800); }
  function start(n){ CA.stage=n;var m=META[n-1];CA.screen='question';CA.questions=buildQuestions(m.mode,m.count);CA.index=0;CA.score=0;CA.hearts=3;CA.wrong=[];CA.answered=false;CA.selected=[];var h=document.getElementById('mChallengeHead');if(h)h.textContent='⚡ '+m.title;render(); }
  function choices(correct,pool){ var out=[correct].concat(shuffle(pool.filter(function(x){return x!==correct;})).slice(0,3)); return shuffle(uniq(out)); }
  function buildQuestions(mode,count){
    var out=[];
    if(mode==='vocab'||mode==='mixed'){ shuffle(WORDS).slice(0,mode==='mixed'?2:count).forEach(function(w){out.push({type:'choice',kind:'vocab',ar:w[0],prompt:'这个词是什么意思？',answer:w[1],options:choices(w[1],WORDS.map(function(x){return x[1];})),note:'词汇：'+w[2]});}); }
    if(mode==='grammar'||mode==='mixed'){ shuffle(GRAMMAR).slice(0,mode==='mixed'?2:count).forEach(function(g){out.push({type:'choice',kind:'grammar',ar:g.ar,prompt:g.prompt,answer:g.answer,options:choices(g.answer,g.options),note:g.note});}); }
    if(mode==='sentence'||mode==='mixed'){ shuffle(SENTENCES).slice(0,mode==='mixed'?2:count).forEach(function(s){out.push({type:'order',kind:'sentence',cn:s.cn,answer:s.ar,tokens:s.tokens,bank:shuffle(s.tokens),note:'先找主语/动词，再确认冠词和词尾。'});}); }
    return shuffle(out).slice(0,count);
  }
  function renderQuestion(){
    var b=body(),q=CA.questions[CA.index],m=META[CA.stage-1];if(!b||!q)return;
    var pct=Math.round((CA.index/CA.questions.length)*100), hearts='';for(var i=0;i<3;i++)hearts+=i<CA.hearts?'♥':'♡';
    var h='<div class="ca-shell ca-play"><div class="ca-play-top"><button class="ca-back-btn" data-ca-action="map">← 关卡地图</button><span class="ca-play-title">第 '+CA.stage+' 关 · '+m.title+'</span><span class="ca-hearts">'+hearts+'</span></div><div class="ca-progress-line"><i style="width:'+pct+'%"></i></div><div class="ca-qmeta"><span>题目 '+(CA.index+1)+' / '+CA.questions.length+'</span><span>得分 <b>'+CA.score+'</b></span></div>';
    if(q.type==='choice') h+='<div class="ca-question-card"><span class="ca-question-kind">'+(q.kind==='grammar'?'语法判断 · قواعد':'词汇反应 · مفردات')+'</span><div class="ca-ar-question" dir="rtl" lang="ar">'+esc(q.ar)+' <button class="ca-speak-btn" data-ca-speak="'+esc(q.ar)+'">🔊</button></div><h3>'+esc(q.prompt)+'</h3></div><div class="ca-options">'+q.options.map(function(o,i){var state='';if(CA.answered)state=o===q.answer?' correct':' wrong';return '<button type="button" class="ca-option'+state+'" data-ca-choice="'+i+'" '+(CA.answered?'disabled':'')+'><span>'+String.fromCharCode(65+i)+'</span>'+esc(o)+'</button>';}).join('')+'</div>';
    else h+='<div class="ca-question-card sentence-card"><span class="ca-question-kind">拼句工坊 · ترتيب الجملة</span><h3>'+esc(q.cn)+'</h3><div class="ca-order-answer" dir="rtl">'+(CA.selected.length?CA.selected.map(function(x,i){return '<button class="ca-selected-token" data-ca-remove="'+i+'">'+esc(x)+'</button>';}).join(''):'<span>点击下方词块，排成阿拉伯语句子</span>')+'</div></div><div class="ca-token-bank" dir="rtl">'+q.bank.map(function(x,i){var used=CA.selected.indexOf(x)>=0;return '<button type="button" class="ca-token '+(used?'used':'')+'" data-ca-token="'+i+'" '+(used||CA.answered?'disabled':'')+'>'+esc(x)+'</button>';}).join('')+'</div><div class="ca-order-actions"><button class="ca-small-btn" data-ca-action="clear-order">清空</button><button class="ca-submit-btn" data-ca-action="submit-order" '+(CA.answered||!CA.selected.length?'disabled':'')+'>检查答案</button></div>';
    if(CA.answered){var ok=CA.lastCorrect;h+='<div class="ca-feedback '+(ok?'good':'bad')+'"><b>'+(ok?'✓ 答对了！':'△ 再想一想')+'</b><span>'+(ok?'很棒，继续保持。':'正确答案：'+esc(q.answer))+'</span><small>💡 '+esc(q.note||'')+'</small><button class="ca-next-btn" data-ca-action="next">'+(CA.index+1<CA.questions.length?'下一题 →':'查看结果 →')+'</button></div>';}
    h+='</div>';b.innerHTML=h;bindQuestion(q);
  }
  function bindQuestion(q){
    var map=document.querySelector('[data-ca-action="map"]');if(map)map.onclick=function(){CA.screen='map';render();};
    Array.prototype.forEach.call(document.querySelectorAll('[data-ca-speak]'),function(x){x.onclick=function(){speak(x.getAttribute('data-ca-speak'));};});
    Array.prototype.forEach.call(document.querySelectorAll('[data-ca-choice]'),function(x){x.onclick=function(){choice(parseInt(x.getAttribute('data-ca-choice'),10));};});
    Array.prototype.forEach.call(document.querySelectorAll('[data-ca-token]'),function(x){x.onclick=function(){pickToken(parseInt(x.getAttribute('data-ca-token'),10));};});
    Array.prototype.forEach.call(document.querySelectorAll('[data-ca-remove]'),function(x){x.onclick=function(){CA.selected.splice(parseInt(x.getAttribute('data-ca-remove'),10),1);renderQuestion();};});
    var next=document.querySelector('[data-ca-action="next"]');if(next)next.onclick=function(){CA.index++;CA.answered=false;CA.selected=[];if(CA.index>=CA.questions.length){CA.screen='finish';}render();};
    var clear=document.querySelector('[data-ca-action="clear-order"]');if(clear)clear.onclick=function(){CA.selected=[];renderQuestion();};
    var submit=document.querySelector('[data-ca-action="submit-order"]');if(submit)submit.onclick=function(){submitOrder();};
  }
  function choice(i){if(CA.answered)return;var q=CA.questions[CA.index],selected=q.options[i];CA.lastCorrect=selected===q.answer;CA.answered=true;if(CA.lastCorrect)CA.score++;else{CA.hearts=Math.max(0,CA.hearts-1);CA.wrong.push(q);try{if(window.srsAdd)srsAdd('s',q.ar||q.answer);}catch(e){}};renderQuestion();}
  function pickToken(i){if(CA.answered)return;var q=CA.questions[CA.index],x=q.bank[i];if(CA.selected.indexOf(x)<0)CA.selected.push(x);renderQuestion();}
  function submitOrder(){if(CA.answered)return;var q=CA.questions[CA.index];CA.lastCorrect=CA.selected.join(' ' )===q.tokens.join(' ');CA.answered=true;if(CA.lastCorrect)CA.score++;else{CA.hearts=Math.max(0,CA.hearts-1);CA.wrong.push(q);}renderQuestion();}
  function renderFinish(){
    var b=body(),m=META[CA.stage-1],passed=CA.score>=Math.ceil(CA.questions.length*.6),best=STATE.best[CA.stage]||0;if(passed&&STATE.done.indexOf(CA.stage)<0)STATE.done.push(CA.stage);if(CA.score>best)STATE.best[CA.stage]=CA.score;STATE.xp+=CA.score*10+(passed?25:0);saveState();
    b.innerHTML='<div class="ca-shell ca-finish"><div class="ca-result-orb">'+(passed?'✦':'↻')+'</div><span class="ca-kicker">'+(passed?'LEVEL CLEARED':'KEEP GOING')+'</span><h2>'+(passed?'关卡完成！':'再试一次，你已经更接近了')+'</h2><p>'+m.title+' · <span dir="rtl">'+m.ar+'</span></p><div class="ca-score-grid"><div><b>'+CA.score+'/'+CA.questions.length+'</b><span>本关得分</span></div><div><b>'+CA.wrong.length+'</b><span>需要复习</span></div><div><b>+'+(CA.score*10+(passed?25:0))+'</b><span>获得 XP</span></div></div><div class="ca-finish-note">'+(passed?'下一关已经解锁。错题会在复习中再次出现。':'至少答对 60% 才能解锁下一关，先回看反馈再挑战一次。')+'</div><div class="ca-finish-actions"><button class="ca-submit-btn" data-ca-action="again">↻ 再战本关</button><button class="ca-small-btn" data-ca-action="map">← 返回地图</button></div></div>';
    var again=document.querySelector('[data-ca-action="again"]');if(again)again.onclick=function(){start(CA.stage);};var map=document.querySelector('[data-ca-action="map"]');if(map)map.onclick=function(){CA.screen='map';render();};
  }
  window.caOpenStage=function(n){start(n);};
})();
