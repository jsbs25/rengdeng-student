return await (async function(){
  var out=[],errors=[];
  function pause(ms){return new Promise(function(r){setTimeout(r,ms);});}
  function check(name,ok,detail){out.push({name:name,ok:!!ok,detail:String(detail||'')});}
  window.addEventListener('error',function(e){errors.push(String(e.message||e.error||e));});
  try{
    await pause(250);
    var root=document.querySelector('.shell'), rail=document.querySelector('.rail'), main=document.querySelector('.content');
    check('工作台页面已打开',!!root&&!!rail&&!!main);
    check('桌面采用非对称双区布局',innerWidth<761||getComputedStyle(root).gridTemplateColumns.includes('208px')&&getComputedStyle(document.querySelector('.workspace')).gridTemplateColumns.split(' ').length===2&&getComputedStyle(document.querySelector('.workspace')).columnGap==='32px');
    check('移动端隐藏侧栏并保留内容',innerWidth<761?getComputedStyle(rail).display==='none':true);
    check('指定大地色背景',getComputedStyle(document.body).backgroundColor==='rgb(248, 246, 242)');
    check('卡片圆角统一为 4px',getComputedStyle(document.querySelector('.word-panel')).borderRadius==='4px'&&getComputedStyle(document.querySelector('.top-search')).borderRadius==='4px');
    check('没有大圆角 CSS',!Array.from(document.styleSheets).some(function(ss){try{return Array.from(ss.cssRules).some(function(r){return /border-radius:\s*(?:[5-9]|[1-9]\d)px|border-radius:\s*50%/.test(r.cssText);});}catch(e){return false;}}));
    check('图标使用 SVG 线条',document.querySelectorAll('svg').length>=8&&Array.from(document.querySelectorAll('svg')).every(function(x){return x.getAttribute('viewBox')==='0 0 24 24';}));
    check('页面没有 emoji 图标',!/[\u{1F300}-\u{1FAFF}]/u.test(document.body.innerText));
    check('首页没有营销式三件套',!document.querySelector('.hero')&&!!document.querySelector('.index-list'));
    var input=document.getElementById('deskSearch');input.value='كتاب';input.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter'}));await pause(1200);
    check('真实查词接口更新工作台',document.getElementById('wordArabic').textContent.indexOf('كتاب')>=0&&document.getElementById('wordSentence').textContent.length>4);
    var savedBefore=localStorage.getItem('nour_theme_saved_words')||'';document.getElementById('saveWord').click();
    check('生词收藏写入本地索引',(localStorage.getItem('nour_theme_saved_words')||'').length>=savedBefore.length);
    var spoken=false,oldSpeak=window.speechSynthesis&&window.speechSynthesis.speak;
    if(window.speechSynthesis){window.speechSynthesis.speak=function(){spoken=true};document.getElementById('speakWord').click();await pause(80);if(oldSpeak)window.speechSynthesis.speak=oldSpeak;}
    check('阿拉伯语朗读按钮可触发',!window.speechSynthesis||spoken);
    check('来源监测台已加载',document.getElementById('sourceVisible').textContent!=='—'&&document.querySelectorAll('#sourceFeedList .source-item').length>=1);
    check('来源监测显示自动巡检说明',document.getElementById('sourceSyncLine').textContent.indexOf('自动检查')>=0&&document.querySelector('.source-policy').textContent.indexOf('白名单')>=0);
    var sourceQuery=document.getElementById('sourceQuery');sourceQuery.value='OpenITI';sourceQuery.dispatchEvent(new Event('input'));await pause(500);
    check('来源关键词过滤生效',document.querySelectorAll('#sourceFeedList .source-item').length===1&&document.querySelector('#sourceFeedList').textContent.indexOf('OpenITI')>=0);
    sourceQuery.value='';sourceQuery.dispatchEvent(new Event('input'));document.getElementById('sourceKind').value='dictionary';document.getElementById('sourceKind').dispatchEvent(new Event('change'));await pause(500);
    check('来源类型过滤生效',document.querySelectorAll('#sourceFeedList .source-item').length===1&&document.querySelector('#sourceFeedList').textContent.indexOf('词典')>=0);
    document.getElementById('sourceKind').value='all';document.getElementById('sourceKind').dispatchEvent(new Event('change'));await pause(350);document.getElementById('sourceRefresh').click();await pause(450);
    check('手动刷新保持来源记录',document.getElementById('sourceRefresh').getAttribute('aria-busy')==='false'&&document.querySelectorAll('#sourceFeedList .source-item').length>=1);
    document.querySelector('[data-reading-mode=\"compare\"]')?.click();
    check('阅读模式切换生效',document.querySelector('[data-reading-mode=\"compare\"]').classList.contains('active')&&document.getElementById('readingSupport').classList.contains('compare'));
    document.querySelector('[data-reading-mode=\"review\"]')?.click();
    check('复习模式保留阅读上下文',document.getElementById('readingSupport').classList.contains('review')&&document.getElementById('readingSupport').textContent.indexOf('原句')>=0);
    document.getElementById('readerSpeed').value='.95';
    check('阅读区提供朗读速度',document.getElementById('readerSpeed').value==='.95'&&document.getElementById('readerPlay')!==null);
    document.querySelector('[data-goal=\"unit\"]')?.click();
    check('学习目标预设可切换',document.getElementById('goalProgressText').textContent.indexOf('1 个单元')>=0&&document.querySelector('[data-goal=\"unit\"]').classList.contains('active'));
    document.querySelector('[data-goal=\"10\"]')?.click();
    document.querySelector('[data-target="reading"]').click();await pause(100);
    check('索引导航滚动到继续阅读',location.hash===''&&document.querySelector('.reading-sheet').getBoundingClientRect().top<innerHeight);
  }catch(e){errors.push(String(e&&e.stack||e));}
  check('无 JavaScript 错误',errors.length===0,errors.join('\n'));
  return JSON.stringify({viewport:[innerWidth,innerHeight],passed:out.filter(function(x){return x.ok;}).length,total:out.length,results:out,errors:errors});
})();
