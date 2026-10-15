return await (async function(){
  const out=[]; const pause=ms=>new Promise(r=>setTimeout(r,ms));
  const check=(name,ok,detail)=>out.push({name,ok:!!ok,detail:String(detail||'')});
  await pause(1200); if(typeof nav==='function') nav('ai'); await pause(250);
  const input=document.getElementById('homeAIIn'), send=document.getElementById('homeAISendBtn');
  check('ai page visible',!!document.querySelector('#aiSec.ai-page'));
  check('input usable',!!input && input.getBoundingClientRect().width>100 && getComputedStyle(input).pointerEvents!=='none');
  check('send usable',!!send && send.getBoundingClientRect().width>40 && getComputedStyle(send).pointerEvents!=='none');
  if(input){input.value='请用一句中文回复：你好'; input.dispatchEvent(new Event('input',{bubbles:true})); input.focus();}
  check('send ready',!!(send&&send.classList.contains('is-ready')));
  if(send) send.click();
  await pause(12000);
  const msgs=[...document.querySelectorAll('#homeAI .ps-ai-msg')].map(x=>({cls:x.className,text:(x.textContent||'').slice(0,300)}));
  const last=msgs[msgs.length-1]||{};
  check('request finished',typeof AI_BUSY==='boolean'&&!AI_BUSY,'AI_BUSY='+String(typeof AI_BUSY==='boolean'?AI_BUSY:'missing'));
  check('response rendered',msgs.length>=2 && !!last.text && !/正在连接|正在查资料/.test(last.text),JSON.stringify(last));
  check('no visible error',!last.text || !/无法连接|服务未启动|HTTP |出错/.test(last.text),last.text);
  return JSON.stringify({passed:out.filter(x=>x.ok).length,total:out.length,results:out,messages:msgs});
})();
