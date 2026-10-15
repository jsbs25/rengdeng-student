return await (async function(){
  var out=[];
  function check(name,ok,detail){out.push({name:name,ok:!!ok,detail:String(detail||'')});}
  function pause(ms){return new Promise(function(r){setTimeout(r,ms);});}
  var errors=[];
  window.addEventListener('error',function(e){errors.push(String(e.message||e.error||'error'));});
  await pause(900);
  check('页面启动无空白',!!document.querySelector('#page-home,.page'),document.body.innerText.slice(0,80));
  check('自然语音模块已注册',typeof window.nourSpeakReply==='function'&&typeof window.nourToggleAutoVoice==='function',typeof window.nourSpeakReply);
  if(typeof window.nav==='function') window.nav('ai');
  await pause(180);
  var ai=document.getElementById('aiSec'), toggle=document.getElementById('aiVoiceToggle'), inp=document.getElementById('homeAIIn');
  check('AI 页面可进入',!!ai&&getComputedStyle(ai).display!=='none',ai&&getComputedStyle(ai).display);
  check('AI 人声开关可见',!!toggle, toggle&&toggle.textContent);
  if(toggle) toggle.click();
  await pause(80);
  check('AI 人声开关可切换',toggle&&toggle.getAttribute('aria-pressed')==='true',toggle&&toggle.textContent);
  check('AI 输入框可用',!!inp&&!inp.disabled,inp&&inp.getBoundingClientRect().width);
  if(typeof window.nav==='function') window.nav('home');
  await pause(1000);
  var k=-1, kk=window.HS_K||[]; for(var ki=0;ki<kk.length;ki++){if(kk[ki].k==='quran'){k=ki;break;}}
  check('书架有古兰经入口',k>=0,k);
  if(k>=0){ var chips=document.querySelectorAll('#tkSeg .chip'); if(chips[k]) chips[k].click(); else if(typeof window.hsGo==='function') window.hsGo(k,null); }
  await pause(500);
  check('经典中心已打开',(document.getElementById('hsSecTitle')||{}).textContent==='古兰经与经注',(document.getElementById('hsSecTitle')||{}).textContent||'');
  if(typeof window.showTafsir==='function') window.showTafsir(1);
  await pause(2300);
  var tf=document.getElementById('tfList'), qbody=document.getElementById('mQuranBody');
  var qm=qbody, qp=qbody; while(qp&&qp.parentNode&&qp.parentNode!==document.body){if((' '+(qp.parentNode.className||'')+' ').indexOf(' modal ')>=0){qm=qp.parentNode;break;}qp=qp.parentNode;}
  check('经注面板打开',!!qbody&&getComputedStyle(qm||qbody).display!=='none',qbody&&qbody.innerText.slice(0,90));
  check('经注按节加载',!!tf&&tf.querySelectorAll('.tf-item').length>=1,tf&&tf.querySelectorAll('.tf-item').length);
  check('经注来源已标注',!!document.querySelector('.tf-source')&&document.querySelector('.tf-source').textContent.indexOf('AlQuran.Cloud')>=0,document.querySelector('.tf-source')&&document.querySelector('.tf-source').textContent);
  check('无运行时错误',errors.length===0,errors.join(' | '));
  return JSON.stringify(out);
})();
