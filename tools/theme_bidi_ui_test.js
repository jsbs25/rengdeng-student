return await (async function(){
  var out=[], errors=[];
  function pause(ms){return new Promise(function(r){setTimeout(r,ms);});}
  function check(name,ok,detail){out.push({name:name,ok:!!ok,detail:String(detail||'')});}
  window.addEventListener('error',function(e){errors.push(String(e.message||e.error||e));});
  try{
    await pause(500);
    check('theme API exists',typeof window.setTheme==='function'&&typeof window.applyTheme==='function');
    setTheme('light'); await pause(30);
    var root=document.documentElement;
    var lightBg=getComputedStyle(document.body).backgroundColor;
    check('explicit day mode applied',root.getAttribute('data-theme')==='light',root.getAttribute('data-theme'));
    check('day mode uses light surface',!/^(rgb\\(15, 15, 15\\)|#0f0f0f)/i.test(lightBg),lightBg);
    setTheme('dark'); await pause(30);
    var darkBg=getComputedStyle(document.body).backgroundColor;
    check('explicit night mode applied',root.getAttribute('data-theme')==='dark',root.getAttribute('data-theme'));
    check('night mode uses dark surface',root.getAttribute('data-theme')==='dark'&&darkBg!=='rgb(244, 241, 233)',darkBg);
    setTheme('light');
    if(typeof openModal==='function') openModal('mReader');
    window.RD_PAGES=['الاستحسان في أصول الفقه 1:1\n这一页包含中文解释与 Arabic mixed text。'];
    window.RD_PAGE=0; window.RD_ISCN=false;
    var title=document.getElementById('mReaderTitle'); if(title) title.textContent='اختبار مختلط · 第一页';
    if(typeof window.renderRead==='function') window.renderRead();
    await pause(80);
    var panel=document.getElementById('rdPageAnalysis');
    check('analysis panel mounted',!!panel);
    var mock={overview:'الاستحسان 是一种法源概念。',key_points:['哈乃斐学派重视具体论证；المالكية 需要回到原典核对。'],terms:[{ar:'الاستحسان',cn:'择善而从；需核验语境'}],school_comparison:[{school:'الحنفية',position:'哈乃斐视角：不可替代原典。',basis:'需要核对版本',status:'待核验'}],source_note:'原典说明：回到 1:1。',caution:'学习辅助，不是法特瓦。'};
    var oldFetch=window.fetch;
    window.fetch=async function(url,opts){if(String(url).indexOf('/api/page/analyze')>=0)return {ok:true,status:200,json:async function(){return {ok:true,analysis:mock};}};return oldFetch(url,opts);};
    if(typeof window.nurAnalyzeCurrentPage==='function') await window.nurAnalyzeCurrentPage(document.querySelector('.rd-page-analysis__run'));
    await pause(40);
    var b=panel&&panel.querySelector('.rd-page-analysis__bidi');
    check('mixed fields are isolated',!!panel&&panel.querySelectorAll('.rd-page-analysis__bidi').length>=5,String(panel&&panel.querySelectorAll('.rd-page-analysis__bidi').length));
    check('auto direction attributes present',!!panel&&panel.querySelectorAll('[dir="auto"]').length>=5,String(panel&&panel.querySelectorAll('[dir="auto"]').length));
    check('Arabic and Chinese remain in same field without DOM reversal',!!panel&&panel.textContent.indexOf('الاستحسان')>=0&&panel.textContent.indexOf('哈乃斐')>=0);
    var cs=b&&getComputedStyle(b); check('bidi uses plaintext isolation',!!b&&cs.unicodeBidi==='plaintext',cs&&cs.unicodeBidi);
    var paper=document.querySelector('#mReaderBody .rd-paper'); var ps=paper&&getComputedStyle(paper); check('reader bottom safe area >= nav',!!paper&&parseFloat(ps.paddingBottom)>=120,ps&&ps.paddingBottom);
    if(typeof closeModal==='function') closeModal('mReader');
    setTheme('auto');
  }catch(e){errors.push(String(e&&e.stack||e));}
  check('no JavaScript errors',errors.length===0,errors.join('\n'));
  return JSON.stringify({viewport:[innerWidth,innerHeight],passed:out.filter(function(x){return x.ok;}).length,total:out.length,results:out,errors:errors});
})();
