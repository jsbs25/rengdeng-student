return await (async function(){
  const out=[]; const pause=ms=>new Promise(r=>setTimeout(r,ms));
  const check=(name,ok,detail)=>out.push({name,ok:!!ok,detail:detail||''});
  await pause(1200);
  try{ if(typeof openModal==='function') openModal('mReader'); }catch(e){}
  window.RD_PAGES=['بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ\n这一页的阿拉伯语经典内容。'];
  window.RD_PAGE=0; window.RD_ISCN=false;
  const title=document.getElementById('mReaderTitle'); if(title) title.textContent='测试经典 · 第一页';
  check('reader render function exists',typeof window.renderRead==='function');
  renderRead(); await pause(80);
  const panel=document.getElementById('rdPageAnalysis');
  check('page analysis panel mounted',!!panel);
  check('page analysis trigger mounted',document.querySelectorAll('.rd-page-analysis-trigger').length>=1);
  check('panel is below current page',!!panel&&!!panel.closest('.rd-paper'));
  const paper=document.querySelector('#mReaderBody .rd-paper');
  if(paper){ const cs=getComputedStyle(paper); check('reader has bottom safe padding',parseFloat(cs.paddingBottom)>=100,String(cs.paddingBottom)); }
  check('analysis intro is visible',!!panel&&panel.textContent.indexOf('本页学习讲解')>=0);
  const originalFetch=window.fetch;
  window.fetch=async function(url,opts){
    if(String(url).indexOf('/api/page/analyze')>=0){
      return {ok:true,status:200,json:async()=>({ok:true,cached:false,analysis:{overview:'这一页介绍了开头的祈求与阅读重点。',key_points:['识别原文与译文的对应关系'],questions:['需要回到原典核对哪些引用？'],practical_guidance:['先朗读，再记录关键词'],quran_references:[{reference:'开端章 1:1',note:'与本页原文直接相关。',status:'直接相关'}],hadith_references:[{reference:'待核验',note:'本页没有直接列出圣训。',status:'待核验'}],fiqh_context:['本页未涉及明确法学裁决。'],terms:[{ar:'رَحْمَة',cn:'慈悯'}],source_note:'测试来源说明',caution:'这是学习辅助，不是法特瓦。',generated_at:'测试时间'}})};
    }
    return originalFetch(url,opts);
  };
  await window.nurAnalyzeCurrentPage(document.querySelector('.rd-page-analysis__run')); await pause(50);
  check('structured overview rendered',panel.textContent.indexOf('这一页介绍了开头')>=0);
  check('quran evidence rendered',panel.textContent.indexOf('开端章 1:1')>=0);
  check('hadith verification state rendered',panel.textContent.indexOf('待核验')>=0);
  check('fiqh context rendered',panel.textContent.indexOf('本页未涉及明确法学裁决')>=0);
  check('keyword rendered',panel.textContent.indexOf('رَحْمَة')>=0);
  check('analysis button remains usable',!!panel.querySelector('.rd-page-analysis__run')&&!panel.querySelector('.rd-page-analysis__run').disabled);
  window.fetch=originalFetch;
  check('no page analysis runtime error',!window.__NUR_ERR,window.__NUR_ERR||'');
  return JSON.stringify({viewport:[innerWidth,innerHeight],passed:out.filter(x=>x.ok).length,total:out.length,results:out});
})();
