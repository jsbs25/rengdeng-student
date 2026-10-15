return await (async function(){
  var out=[],errors=[];
  function pause(ms){return new Promise(function(resolve){setTimeout(resolve,ms);});}
  function check(name,ok,detail){out.push({name:name,ok:!!ok,detail:String(detail||'')});}
  window.addEventListener('error',function(e){errors.push(String(e.message||e.error||e));});
  function visibleTabs(){return Array.from(document.querySelectorAll('.tabbar .tb')).filter(function(x){return !x.hidden;});}
  function tab(route){return document.querySelector('.tabbar .tb[data-primary-route="'+route+'"]');}
  try{
    await pause(550);
    document.body.classList.remove('locked');
    var lock = document.getElementById('mLock'); if (lock) lock.style.display = 'none';
    var home=document.getElementById('page-home');
    var shell=document.getElementById('nourProductHome');
    var bar=document.querySelector('.tabbar.nour-primary-nav');
    check('NOUR 首页工作台已挂载',!!home&&!!shell);
    check('首页标题使用图书馆定位',!!document.querySelector('.nour-product-title')&&document.querySelector('.nour-product-title').textContent.indexOf('私人图书馆')>=0);
    check('首页采用不等宽双区布局',innerWidth<761||getComputedStyle(document.querySelector('.nour-product-grid')).gridTemplateColumns.split(' ').length===2);
    check('旧首页内容仍在 DOM 中但不抢首屏',!!document.querySelector('#page-home>.feed')&&getComputedStyle(document.querySelector('#page-home>.feed')).display==='none');
    check('继续阅读区读取现有足迹',!!document.getElementById('nourContinueList'));
    var visible=visibleTabs(),labels=visible.map(function(x){return (x.querySelector('.t-nm')||{}).textContent||'';});
    check('底部仅保留五项一级导航',visible.length===5,labels.join(' / '));
    check('五项导航文案正确',JSON.stringify(labels)===JSON.stringify(['首页','阅读','词典','学习','我的']),labels.join(' / '));
    check('AI 不在一级导航',!tab('ai')&&labels.indexOf('NOUR AI')<0);
    check('搜索和生词本不在一级导航',document.querySelector('[data-tab="search"]').hidden===true&&document.querySelector('[data-tab="wordbook"]').hidden===true);
    check('保留真实业务函数',typeof window.nav==='function'&&typeof window.showWordBook==='function'&&typeof window.openSearchAll==='function'&&typeof window.openDict==='function'&&typeof window.showListen==='function');
    check('五项按钮具备无障碍标签',visible.every(function(x){return !!x.getAttribute('aria-label')||!!x.textContent.trim();}));

    var read=tab('read'); read.click(); await pause(170);
    check('阅读进入真实书库',window.NUR_ACTIVE_TAB==='learn'&&getComputedStyle(document.getElementById('mCat')).display!=='none');
    check('阅读按钮获得激活态',read.classList.contains('on')&&read.classList.contains('nour-active')&&read.getAttribute('aria-current')==='page');

    var dict=tab('dict'); dict.click(); await pause(170);
    check('词典进入真实词典面板',document.getElementById('mDict').classList.contains('show')&&document.getElementById('mDict').getBoundingClientRect().width>0);
    check('词典输入框存在并可用',!!document.getElementById('dictQ'));
    if(typeof window.closeModal==='function') window.closeModal('mDict');

    var study=tab('study'); study.click(); await pause(170);
    check('学习进入真实学习面板',document.getElementById('mLearn').classList.contains('show')&&document.getElementById('mLearn').getBoundingClientRect().width>0);
    if(typeof window.closeModal==='function') window.closeModal('mLearn');

    var me=tab('me'); me.click(); await pause(170);
    check('我的导航仍可进入个人中心',window.NUR_ACTIVE_TAB==='me'&&getComputedStyle(document.getElementById('page-me')).display!=='none');
    check('我的按钮获得激活态',me.classList.contains('on')&&me.classList.contains('nour-active')&&me.getAttribute('aria-current')==='page');

    tab('home').click(); await pause(150);
    check('返回首页后工作台保持挂载',window.NUR_ACTIVE_TAB==='home'&&getComputedStyle(shell).display!=='none');
    var searchButton=document.getElementById('nourProductSearch');
    if(searchButton) searchButton.click(); await pause(140);
    check('首页搜索按钮仍打开全局搜索',!!document.querySelector('#mSearch.show')||getComputedStyle(document.getElementById('mSearch')).display!=='none');
    if(typeof window.closeModal==='function') window.closeModal('mSearch');
    check('AI 工作区仍可由首页入口进入',!!document.querySelector('[data-open-ai]')&&!!document.getElementById('aiSec')&&typeof window.nav==='function');
    if(innerWidth<761){
      check('手机端工作台收敛为单列',getComputedStyle(document.querySelector('.nour-product-grid')).display==='block');
      check('手机端底栏避开安全区',getComputedStyle(bar).position==='fixed');
      check('手机端五项导航不溢出',bar.getBoundingClientRect().width<=innerWidth&&visible.every(function(x){return x.getBoundingClientRect().width>=44;}));
    }else{
      check('桌面端主区留有右侧索引',getComputedStyle(document.querySelector('.nour-product-grid')).gridTemplateColumns.split(' ').length===2);
    }
  }catch(e){errors.push(String(e&&e.stack||e));}
  check('无 JavaScript 错误',errors.length===0,errors.join('\n'));
  return JSON.stringify({viewport:[innerWidth,innerHeight],passed:out.filter(function(x){return x.ok;}).length,total:out.length,results:out,errors:errors});
})();
