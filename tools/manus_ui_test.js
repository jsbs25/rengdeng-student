return await (async function(){
  const results = [];
  const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
  function check(name, ok, detail){results.push({name,ok:!!ok,detail:detail||''});}
  // The existing startup/license check settles at six seconds. Do not bypass it.
  await pause(3500);
  // The app keeps a free-entry gate for fresh browser contexts; dismiss it for UI regression only.
  if(document.body.classList.contains('locked') && typeof freeEnter==='function'){ freeEnter(); await pause(120); }
  const visiblePages = () => Array.from(document.querySelectorAll('body > .page')).filter(el => getComputedStyle(el).display !== 'none');
  for(const [tab,id] of [['home','page-home'],['learn','mCat'],['search','page-search'],['me','page-me'],['home','page-home']]){
    document.querySelector('.tabbar .tb[data-tab="'+tab+'"]').click();
    await pause(150);
    const el=document.getElementById(id),r=el.getBoundingClientRect(),s=getComputedStyle(el);
    check(tab+' is the only visible page',visiblePages().length===1&&visiblePages()[0]===el,visiblePages().map(x=>x.id).join(','));
    check(tab+' fills viewport',Math.abs(r.x)<2&&r.width>=innerWidth-20&&r.height>=innerHeight-1&&s.position!=='fixed',JSON.stringify({width:r.width,height:r.height,x:r.x,y:r.y,position:s.position}));
    check(tab+' has no modal',!document.querySelector('.modal.show')&&!document.body.classList.contains('modal-open'));
  }
  nav('learn');openModal('mReader');nav('me');
  check('navigation closes reader',!document.body.classList.contains('reading')&&!document.querySelector('.modal.show'));
  openNurAI();
  const input=document.getElementById('homeAIIn'),box=document.getElementById('homeAI');
  check('AI text input visible',input.getBoundingClientRect().width>50);
  check('AI is full-page',visiblePages().length===1&&visiblePages()[0].id==='aiSec'&&document.getElementById('aiSec').getBoundingClientRect().width===innerWidth);
  const send=document.querySelector('#aiSec .ps-ai-input button:not(.ps-mic)');
  check('AI send visible',send&&send.getBoundingClientRect().width>0);
  check('AI controls stay within screen',send.getBoundingClientRect().right<=innerWidth&&input.getBoundingClientRect().width>=120);
  check('AI input above bottom navigation',input.getBoundingClientRect().bottom<=document.querySelector('.tabbar').getBoundingClientRect().top);
  // Wait past the old 4.2 / 8 second reparenting timers.
  await pause(8200);
  check('AI remains mounted and visible',document.getElementById('aiSec').parentElement===document.body&&visiblePages()[0].id==='aiSec');
  const originalFetch=window.fetch;
  window.fetch=async (url,opts)=>String(url).includes('/api/chat/message')?{ok:false,status:503,json:async()=>({error:'测试：上游暂时不可用'})}:originalFetch(url,opts);
  input.value='测试错误恢复';await homeAISend();
  check('error detail displayed',box.lastElementChild.textContent.includes('上游暂时不可用'));
  check('failure re-enables sending',!AI_BUSY&&!send.disabled&&input.value==='测试错误恢复');
  window.fetch=async (url,opts)=>String(url).includes('/api/chat/message')?{ok:true,status:200,json:async()=>({arabic:'صَبَاحُ الْخَيْرِ\n中文：早上好\nEnglish: Good morning'})}:originalFetch(url,opts);
  input.value='测试中阿完整回复';await homeAISend();
  check('Arabic and Chinese retained',box.lastElementChild.textContent.includes('中文：早上好')&&box.lastElementChild.textContent.includes('صَبَاح'));
  window.fetch=async (url,opts)=>String(url).includes('/api/chat/message')?{ok:true,status:200,json:async()=>({limited:true,reply:'今日已达上限'})}:originalFetch(url,opts);
  input.value='测试次数限制';await homeAISend();
  check('quota handling still enforced',box.lastElementChild.textContent.includes('免费对话已用完')&&!AI_BUSY);
  window.fetch=originalFetch;
  if(navigator.mediaDevices){
    const gum=navigator.mediaDevices.getUserMedia;
    navigator.mediaDevices.getUserMedia=()=>Promise.reject(new DOMException('denied','NotAllowedError'));
    if(HOME_TALK) homeAIVoice();
    homeAIVoice();await pause(100);
    check('microphone denial allows text',!HOME_TALK&&input.getBoundingClientRect().width>0);
    navigator.mediaDevices.getUserMedia=gum;
  }
  let realReply='not requested on this viewport';
  if(innerWidth>700){
    SID='manus-browser-regression-20260925';
    input.value='请把“早上好”翻译成阿拉伯语，并给出中文解释。简短回复。';
    await homeAISend();
    realReply=box.lastElementChild.textContent;
    check('real AI response',/[\u0600-\u06ff]/.test(realReply)&&!realReply.includes('⚠️'),realReply.slice(0,300));
  }
  nav('home');
  check('AI closes without leftover overlay',visiblePages().length===1&&visiblePages()[0].id==='page-home'&&!HOME_TALK);
  check('no JavaScript error',!window.__NUR_ERR,window.__NUR_ERR);
  box.innerHTML='';
  var clean=document.createElement('div');clean.className='ps-ai-msg bot';
  clean.textContent=innerWidth>700?realReply.replace('📋 复制',''):'你好，我是努尔老师。你可以输入文字提问，也可以点击麦克风练习阿拉伯语。';
  box.appendChild(clean);input.value='';
  return JSON.stringify({viewport:[innerWidth,innerHeight],build:window.__NUR_BUILD,passed:results.filter(x=>x.ok).length,total:results.length,results,realReply});
})();
