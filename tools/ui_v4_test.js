return await (async function(){
  const out=[]; const pause=ms=>new Promise(r=>setTimeout(r,ms));
  const check=(name,ok,detail)=>out.push({name,ok:!!ok,detail:detail||''});
  await pause(1700); if(typeof nav==='function') nav('ai'); await pause(220);
  const input=document.getElementById('homeAIIn'), compose=document.querySelector('.home-ai-compose'), send=document.getElementById('homeAISendBtn'), mic=document.getElementById('homeMic'), count=document.getElementById('homeAICount');
  check('AI compose exists',!!compose); check('magic mounted',compose&&compose.dataset.magicMounted==='1'); check('send exists',!!send); check('mic exists',!!mic);
  if(compose){compose.dispatchEvent(new PointerEvent('pointermove',{bubbles:true,clientX:compose.getBoundingClientRect().left+20,clientY:compose.getBoundingClientRect().top+12}));}
  check('compose tracks pointer',compose&&getComputedStyle(compose).getPropertyValue('--spot-x').trim()!=='50%');
  if(send){const r=send.getBoundingClientRect(); send.dispatchEvent(new PointerEvent('pointermove',{bubbles:true,clientX:r.left+r.width*.8,clientY:r.top+r.height*.2}));}
  check('send has magnetic offset',send&&getComputedStyle(send).getPropertyValue('--mag-x').trim()!=='0px');
  if(input){input.value='极致交互测试'; input.dispatchEvent(new Event('input',{bubbles:true}));}
  await pause(60);
  check('text state visible',compose&&compose.classList.contains('has-text'));
  check('counter active',count&&/\d+\s*字/.test(count.textContent),count&&count.textContent);
  check('send ready',send&&send.classList.contains('is-ready'));
  if(send){send.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,clientX:send.getBoundingClientRect().left+10,clientY:send.getBoundingClientRect().top+10}));}
  check('press state immediate',send&&send.classList.contains('is-pressed'));
  await pause(200); check('press state resets',send&&!send.classList.contains('is-pressed'));
  if(input){input.value=''; input.dispatchEvent(new Event('input',{bubbles:true}));}
  check('within viewport',input&&input.getBoundingClientRect().right<=innerWidth+1&&send&&send.getBoundingClientRect().right<=innerWidth+1);
  check('no startup error',!window.__NUR_ERR,window.__NUR_ERR||'');
  return JSON.stringify({passed:out.filter(x=>x.ok).length,total:out.length,results:out});
})();
