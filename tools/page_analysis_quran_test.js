return await (async function(){
  const out=[]; const pause=ms=>new Promise(r=>setTimeout(r,ms));
  const check=(name,ok,detail)=>out.push({name,ok:!!ok,detail:detail||''});
  await pause(1800);
  if(typeof window.showQuran === 'function') await window.showQuran();
  for(let i=0;i<80 && !(window.QURAN&&window.QURAN.length>=114) && !(window.BUILTIN_QURAN&&window.BUILTIN_QURAN.length>=114);i++) await pause(250);
  const quran=(window.QURAN&&window.QURAN.length>=114)?window.QURAN:((window.BUILTIN_QURAN&&window.BUILTIN_QURAN.length>=114)?window.BUILTIN_QURAN:[]);
  check('quran data loaded',Array.isArray(quran)&&quran.length>=114,String(quran.length));
  if(typeof window.openSurah==='function'&&quran[0]) window.openSurah(quran[0]);
  await pause(180);
  const title=document.getElementById('mReaderTitle');
  check('real quran reader opened',!!title&&title.textContent.indexOf('经典选读')>=0,title&&title.textContent);
  check('real quran page rendered',!!document.querySelector('#mReaderBody .rd-page:not(.rd-cn)'));
  check('page analysis mounted on quran',!!document.getElementById('rdPageAnalysis'));
  check('quran analysis trigger mounted',document.querySelectorAll('.rd-page-analysis-trigger').length>=1);
  const originalFetch=window.fetch;
  window.fetch=async function(url,opts){
    if(String(url).indexOf('/api/page/analyze')>=0) return {ok:true,status:200,json:async()=>({ok:true,analysis:{overview:'这是古兰经实际章节页的学习性概览。',key_points:['先读阿拉伯原文，再对照译文'],questions:['引用需回到原典核对'],practical_guidance:['跟随诵读音频复习'],quran_references:[{reference:'开端章 1:1',note:'测试相关依据',status:'直接相关'}],hadith_references:[],fiqh_context:['本页未涉及明确法学裁决。'],terms:[],source_note:'实际古兰经阅读页',caution:'学习辅助，不是法特瓦。'}})};
    return originalFetch(url,opts);
  };
  if(typeof window.nurAnalyzeCurrentPage==='function') await window.nurAnalyzeCurrentPage(document.querySelector('.rd-page-analysis__run'));
  await pause(50);
  const panel=document.getElementById('rdPageAnalysis');
  check('quran overview rendered',!!panel&&panel.textContent.indexOf('实际章节页')>=0);
  check('quran source state rendered',!!panel&&panel.textContent.indexOf('开端章 1:1')>=0);
  window.fetch=originalFetch;
  return JSON.stringify({viewport:[innerWidth,innerHeight],passed:out.filter(x=>x.ok).length,total:out.length,results:out});
})();
