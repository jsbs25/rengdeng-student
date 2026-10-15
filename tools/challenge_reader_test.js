return await (async function(){
  const out=[]; const pause=ms=>new Promise(r=>setTimeout(r,ms));
  const check=(name,ok,detail)=>out.push({name,ok:!!ok,detail:detail||''});
  await pause(1600);
  showChallenge(); await pause(80);
  const modal=document.getElementById('mChallenge');
  check('challenge modal opens',!!modal&&modal.classList.contains('show')&&modal.getBoundingClientRect().width>=380);
  check('six stage cards render',document.querySelectorAll('.ca-stage-card').length===6);
  check('stage 1 open',!!document.querySelector('.ca-stage-card[data-ca-stage="1"].open'));
  const stage=document.querySelector('.ca-stage-card[data-ca-stage="1"]'); if(stage) stage.click(); await pause(70);
  check('question screen renders',!!document.querySelector('.ca-question-card')&&document.querySelectorAll('.ca-option').length===4);
  const qpage=document.querySelector('.ca-question-card'); check('arabic question uses RTL',!!qpage&&getComputedStyle(qpage.querySelector('.ca-ar-question')).direction==='rtl');
  const first=document.querySelector('.ca-option'); if(first) first.click(); await pause(60);
  check('answer feedback appears',!!document.querySelector('.ca-feedback'));
  const next=document.querySelector('[data-ca-action="next"]'); if(next) next.click(); await pause(50);
  check('next question advances',document.querySelector('.ca-qmeta')&&document.querySelector('.ca-qmeta').textContent.indexOf('题目 2')>=0);
  // Reader typography and word sheet, using a short deterministic local page.
  RD_PAGES=['السَّلَامُ عَلَيْكُمْ\nأَنَا طَالِبٌ']; RD_PAGE=0; window.RD_ISCN=false; document.getElementById('mReaderTitle').textContent='测试阿语书'; renderRead(); await pause(30);
  const rp=document.querySelector('.rd-page:not(.rd-cn)'); check('reader Arabic page renders',!!rp); if(rp){const cs=getComputedStyle(rp);check('reader direction RTL',cs.direction==='rtl');check('reader line spacing',parseFloat(cs.lineHeight)>2);check('Arabic words are tappable',rp.querySelectorAll('.rd-w').length>=2);}
  const fake=document.createElement('span');fake.className='rd-w';fake.textContent='كِتَاب';document.body.appendChild(fake); rdWord({stopPropagation:function(){}},fake); await pause(80);
  const wb=document.getElementById('rdWordBox'); check('word explanation sheet opens',!!wb&&wb.getBoundingClientRect().width>300); if(wb){const cs=getComputedStyle(wb);check('word sheet above safe bottom',parseFloat(cs.bottom)>=70);check('word sheet has actions',wb.querySelectorAll('button').length===3);check('Arabic word is RTL',wb.querySelector('.rd-word-ar')&&wb.querySelector('.rd-word-ar').getAttribute('dir')==='rtl');}
  return JSON.stringify({passed:out.filter(x=>x.ok).length,total:out.length,results:out});
})();
