return await (async function(){
  const out=[],errors=[];
  const pause=ms=>new Promise(r=>setTimeout(r,ms));
  const check=(name,ok,detail)=>out.push({name,ok:!!ok,detail:detail||''});
  window.addEventListener('error',e=>errors.push(String(e.message||e.error||e)));
  await pause(650);
  document.body.classList.remove('locked');
  var lock = document.getElementById('mLock'); if (lock) lock.style.display = 'none';
  const allButtons=()=>Array.from(document.querySelectorAll('.tabbar .tb'));
  const navButtons=()=>allButtons().filter(b=>!b.hidden);
  const visiblePages=()=>Array.from(document.querySelectorAll('body > .page')).filter(el=>getComputedStyle(el).display!=='none');
  const labels=()=>navButtons().map(b=>(b.textContent||'').trim());
  const tabs=()=>navButtons().map(b=>b.getAttribute('data-primary-route'));
  const byRoute=r=>document.querySelector('.tabbar .tb[data-primary-route="'+r+'"]');
  check('底栏显示五项',navButtons().length===5,JSON.stringify(labels()));
  check('底栏文案统一',JSON.stringify(labels())===JSON.stringify(['首页','阅读','词典','学习','我的']),JSON.stringify(labels()));
  check('底栏没有重复我的',labels().filter(x=>x==='我的').length===1,JSON.stringify(labels()));
  check('底栏包含阅读词典学习',tabs().indexOf('read')>=0&&tabs().indexOf('dict')>=0&&tabs().indexOf('study')>=0,JSON.stringify(tabs()));
  check('旧搜索与生词本按钮保留但隐藏',!!document.querySelector('[data-tab="search"]')&&!!document.querySelector('[data-tab="wordbook"]')&&document.querySelector('[data-tab="search"]').hidden&&document.querySelector('[data-tab="wordbook"]').hidden);

  byRoute('me').click(); await pause(120);
  check('我的路径打开个人中心',document.getElementById('page-me')&&getComputedStyle(document.getElementById('page-me')).display!=='none');
  check('个人中心有生词本入口',!!Array.from(document.querySelectorAll('#page-me .profile-link')).find(x=>(x.textContent||'').includes('生词本')));
  const wordbook=Array.from(document.querySelectorAll('#page-me .profile-link')).find(x=>(x.textContent||'').includes('生词本'));
  if(wordbook) wordbook.click(); await pause(120);
  const wb=document.getElementById('mWordBook');
  check('个人中心生词本打开统一面板',!!wb&&wb.classList.contains('show')&&wb.getBoundingClientRect().width>0,wb?wb.id:'missing');
  check('生词本搜索框存在',!!document.getElementById('mWbSearch'));
  if(typeof closeModal==='function') closeModal('mWordBook'); await pause(60);

  const listen=Array.from(document.querySelectorAll('#page-me .profile-link')).find(x=>(x.textContent||'').includes('跟读练习'));
  if(listen) listen.click(); await pause(120);
  const lm=document.getElementById('mListen');
  check('个人中心跟读打开统一面板',!!lm&&lm.classList.contains('show')&&lm.getBoundingClientRect().width>0,lm?lm.id:'missing');
  if(typeof closeModal==='function') closeModal('mListen'); await pause(60);

  byRoute('read').click(); await pause(120);
  check('阅读路径打开真实书库',window.NUR_ACTIVE_TAB==='learn'&&getComputedStyle(document.getElementById('mCat')).display!=='none');
  byRoute('dict').click(); await pause(120);
  check('词典路径打开真实词典',document.getElementById('mDict').classList.contains('show'));
  if(typeof closeModal==='function') closeModal('mDict');
  byRoute('study').click(); await pause(120);
  check('学习路径打开真实句子库',document.getElementById('mLearn').classList.contains('show'));
  if(typeof closeModal==='function') closeModal('mLearn');

  nav('search'); await pause(110);
  check('旧 nav(search) 仍打开查词页',document.getElementById('page-search')&&getComputedStyle(document.getElementById('page-search')).display!=='none');
  check('搜索页是唯一可见页面',visiblePages().length===1&&visiblePages()[0].id==='page-search',visiblePages().map(x=>x.id).join(','));
  nav('listen'); await pause(110);
  check('旧 listen 别名仍兼容',document.getElementById('page-search')&&getComputedStyle(document.getElementById('page-search')).display!=='none');
  check('旧 showWordBook 函数仍存在',typeof window.showWordBook==='function');
  nav('me'); await pause(100);
  check('返回我的仍打开个人中心',document.getElementById('page-me')&&getComputedStyle(document.getElementById('page-me')).display!=='none');
  check('无前端错误',errors.length===0,errors.join('\n'));
  return JSON.stringify({viewport:[innerWidth,innerHeight],build:window.__NUR_BUILD,passed:out.filter(x=>x.ok).length,total:out.length,results:out,errors:errors});
})();
