return await (async function(){
  var out=[], errors=[];
  function pause(ms){return new Promise(function(r){setTimeout(r,ms);});}
  function check(name,ok,detail){out.push({name:name,ok:!!ok,detail:String(detail||'')});}
  function now(){return (performance&&performance.now)?performance.now():Date.now();}
  async function waitFor(fn,ms){var start=now(); while(now()-start<ms){try{if(fn())return now()-start;}catch(e){} await pause(8);} return -1;}
  function themeOption(mode){return document.querySelector('#mTheme .theme-settings-option[onclick*="'+mode+'"]');}
  window.addEventListener('error',function(e){errors.push(String(e.message||e.error||e));});
  try{
    await pause(1000);
    if(typeof nav==='function') nav('me');
    await pause(180);
    var links=Array.from(document.querySelectorAll('#page-me .profile-link'));
    var settings=links.find(function(x){return x.textContent.indexOf('外观设置')>=0;});
    check('外观设置入口存在',!!settings, String(links.length));
    if(settings) settings.click();
    await pause(80);
    var modal=document.getElementById('mTheme');
    check('外观设置面板打开',!!modal&&modal.classList.contains('show'),modal&&getComputedStyle(modal).display);
    check('三种模式可见',document.querySelectorAll('#mTheme .theme-settings-option').length===3);
    var initial=window.THEME_MODE;
    var dark=themeOption('dark');
    check('深色模式按钮可点击',!!dark);
    var t=now(); if(dark) dark.click();
    var darkMs=await waitFor(function(){return window.THEME_MODE==='dark'&&document.documentElement.getAttribute('data-theme')==='dark';},1000);
    var darkStored=localStorage.getItem('nur_theme2');
    check('深色模式状态切换完成',darkMs>=0,'响应 '+(darkMs<0?'超时':darkMs.toFixed(1)+'ms'));
    check('深色模式持久化写入',darkStored==='dark',darkStored);
    var darkBg=getComputedStyle(document.body).backgroundColor;
    var light=themeOption('light');
    check('浅色模式按钮可点击',!!light);
    t=now(); if(light) light.click();
    var lightMs=await waitFor(function(){return window.THEME_MODE==='light'&&document.documentElement.getAttribute('data-theme')==='light';},1000);
    var lightStored=localStorage.getItem('nur_theme2');
    check('浅色模式状态切换完成',lightMs>=0,'响应 '+(lightMs<0?'超时':lightMs.toFixed(1)+'ms'));
    check('浅色模式持久化写入',lightStored==='light',lightStored);
    var lightBg=getComputedStyle(document.body).backgroundColor;
    check('深浅背景实际不同',darkBg!==lightBg,'dark='+darkBg+'; light='+lightBg);
    check('当前选中态同步',!!document.querySelector('#mTheme .theme-settings-option.on[onclick*="light"]'));
    // The page bootstrap and the settings layer use the same storage key.
    check('刷新初始化读取同一持久化键',document.documentElement.innerHTML.indexOf('nur_theme2')>=0&&localStorage.getItem('nur_theme2')==='light');
    if(typeof closeModal==='function') closeModal('mTheme');
    if(typeof setTheme==='function') setTheme('auto');
  }catch(e){errors.push(String(e&&e.stack||e));}
  check('无 JavaScript 错误',errors.length===0,errors.join('\n'));
  return JSON.stringify({viewport:[innerWidth,innerHeight],initial:initial||'',darkMs:darkMs,lightMs:lightMs,passed:out.filter(function(x){return x.ok;}).length,total:out.length,results:out,errors:errors});
})();
