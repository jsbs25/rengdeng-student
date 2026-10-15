return await (async function(){
  const pause=ms=>new Promise(r=>setTimeout(r,ms)); await pause(1700); if(typeof nav==='function') nav('ai'); await pause(180);
  const input=document.getElementById('homeAIIn'); if(input){input.value='请解释这句阿拉伯语的词根和语法'; input.dispatchEvent(new Event('input',{bubbles:true})); input.focus();}
  const compose=document.querySelector('.home-ai-compose'); if(compose){const r=compose.getBoundingClientRect(); compose.dispatchEvent(new PointerEvent('pointermove',{bubbles:true,clientX:r.left+r.width*.72,clientY:r.top+r.height*.35}));}
  await pause(300); return JSON.stringify({textState:!!(compose&&compose.classList.contains('has-text')),sendReady:!!document.getElementById('homeAISendBtn')?.classList.contains('is-ready')});
})();
