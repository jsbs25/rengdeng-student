return await (async function(){
  var out=[], errors=[];
  function pause(ms){return new Promise(function(r){setTimeout(r,ms);});}
  function check(name,ok,detail){out.push({name:name,ok:!!ok,detail:String(detail||'')});}
  function visible(el){return !!el && getComputedStyle(el).display!=='none' && el.getBoundingClientRect().width>0;}
  function focusState(){return document.body.classList.contains('nour-focus-active') && !!document.getElementById('nourFocusBack');}
  window.addEventListener('error',function(e){errors.push(String(e.message||e.error||e));});
  try{
    await pause(900);
    check('首页默认不进入焦点模式',!document.body.classList.contains('nour-focus-active'));
    check('全屏返回控件已准备',!!document.getElementById('nourFocusBack'));
    nav('search'); await pause(100);
    var search=document.getElementById('page-search');
    check('搜索进入焦点模式',focusState()&&search&&search.classList.contains('nour-focus-page'));
    check('搜索页面覆盖视口',!!search&&search.getBoundingClientRect().width>=innerWidth-2&&search.getBoundingClientRect().height>=innerHeight-2);
    check('焦点模式隐藏底部导航',!!document.querySelector('.tabbar')&&getComputedStyle(document.querySelector('.tabbar')).display==='none');
    nav('home'); await pause(80);
    check('返回首页退出焦点模式',!document.body.classList.contains('nour-focus-active'));
    openDict(); await pause(160);
    var dict=document.getElementById('mDict'), dr=dict&&dict.getBoundingClientRect();
    check('词典进入全屏功能工作区',visible(dict)&&dict.classList.contains('nour-focus-modal')&&focusState());
    check('词典工作区覆盖视口',!!dr&&dr.width>=innerWidth-2&&dr.height>=innerHeight-2);
    check('词典保留标题栏和输入区',!!dict&&visible(dict.querySelector('.m-head'))&&!!dict.querySelector('#dictQ'));
    closeModal('mDict'); await pause(80);
    check('关闭词典恢复首页',!document.body.classList.contains('nour-focus-active')&&!document.querySelector('.modal.show'));
    showWordBook(); await pause(120);
    var wb=document.getElementById('mWordBook');
    check('生词本进入全屏功能工作区',visible(wb)&&wb.classList.contains('nour-focus-modal')&&focusState());
    closeModal('mWordBook'); await pause(60);
    openModal('mGrammar'); await pause(100);
    var gram=document.getElementById('mGrammar');
    check('语法课进入全屏功能工作区',visible(gram)&&gram.classList.contains('nour-focus-modal'));
    closeModal('mGrammar'); await pause(60);
    nav('learn'); await pause(120);
    openDict(); await pause(100); closeModal('mDict'); await pause(100);
    check('关闭书库内功能后仍停留在书库工作区',document.body.classList.contains('nour-focus-active')&&document.getElementById('mCat').classList.contains('nour-focus-page')&&window.__NOUR_FOCUS_ROUTE__&&window.__NOUR_FOCUS_ROUTE__.id==='mCat');
    nav('home'); await pause(80);
    nav('ai'); await pause(100);
    var ai=document.getElementById('aiSec');
    check('NOUR AI 进入页面级全屏工作区',focusState()&&ai&&ai.classList.contains('nour-focus-page'));
    check('AI 输入仍可见',!!document.getElementById('homeAIIn')&&visible(document.getElementById('homeAIIn')));
    nav('home'); await pause(80);
    check('核心业务函数仍存在',typeof openModal==='function'&&typeof closeModal==='function'&&typeof nav==='function'&&typeof openDict==='function');
  }catch(e){errors.push(String(e&&e.stack||e));}
  check('无 JavaScript 错误',errors.length===0,errors.join('\n'));
  return JSON.stringify({viewport:[innerWidth,innerHeight],passed:out.filter(function(x){return x.ok;}).length,total:out.length,results:out,errors:errors});
})();
