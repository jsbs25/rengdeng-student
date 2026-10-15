return await (async function(){
  const out=[]; const pause=ms=>new Promise(r=>setTimeout(r,ms));
  const check=(name,ok,detail)=>out.push({name,ok:!!ok,detail:detail||''});
  await pause(3500);
  check('chain voice state exists',!!window.NourRealtime&&window.NourRealtime.mode==='asr-deepseek-tts',window.NourRealtime&&window.NourRealtime.mode);
  check('gold orb still exists',!!document.querySelector('#page-home .nour-orb'));
  check('chain status HUD exists',!!document.getElementById('nourRealtimeHud'));
  check('not using OpenAI Realtime client',!document.documentElement.innerHTML.includes('/api/realtime/session'));
  check('text AI input still exists',!!document.getElementById('homeAIIn'));
  return JSON.stringify({passed:out.filter(x=>x.ok).length,total:out.length,results:out});
})();
