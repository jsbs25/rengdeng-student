return await (async function(){
  const out=[]; const check=(name,ok,detail)=>out.push({name,ok:!!ok,detail:detail||''});
  const pause=ms=>new Promise(r=>setTimeout(r,ms));
  await pause(3500);
  nav('learn');
  await pause(1800);
  const card=document.querySelector('#mCatBody .bk-grid .bk-card');
  check('Arabic library has cards',!!card);
  if(card){
    card.click();
    await pause(3500);
    const body=document.getElementById('mReaderBody');
    const text=(body&&body.innerText)||'';
    check('reader modal opened',!!document.querySelector('#mReader.show')||document.body.classList.contains('reading'));
    check('Arabic book text loaded',text.length>120 && /[\u0600-\u06ff]/.test(text),text.slice(0,120));
  }
  return JSON.stringify({passed:out.filter(x=>x.ok).length,total:out.length,results:out});
})();
