return await (async function(){
  const out=[]; const pause=ms=>new Promise(r=>setTimeout(r,ms));
  const check=(name,ok,detail)=>out.push({name,ok:!!ok,detail:detail||''});
  await pause(2800);
  check('fast voice mode',!!window.NourRealtime&&window.NourRealtime.mode==='speech-recognition-deepseek-stream-tts',window.NourRealtime&&window.NourRealtime.mode);
  check('gold orb',!!document.querySelector('#page-home .nour-orb'));
  check('voice HUD',!!document.getElementById('nourRealtimeHud'));
  check('text AI input',!!document.getElementById('homeAIIn'));
  check('no realtime session client',!document.documentElement.innerHTML.includes('/api/realtime/session'));
  return JSON.stringify({passed:out.filter(x=>x.ok).length,total:out.length,results:out});
})();
