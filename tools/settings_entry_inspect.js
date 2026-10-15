(function(){
  var out=[]; function snap(name,fn){try{var r=fn()||{};out.push({name:name,ok:true,data:r});}catch(e){out.push({name:name,ok:false,error:String(e)})}}
  function parentInfo(id){var e=document.getElementById(id),r=e&&e.getBoundingClientRect(),s=e&&getComputedStyle(e),p=e&&e.parentElement;return {exists:!!e,show:!!(e&&e.classList.contains('show')),rect:r&&{x:r.x,y:r.y,w:r.width,h:r.height},display:s&&s.display,parent:p&&{id:p.id,tag:p.tagName,display:getComputedStyle(p).display}};}
  if(typeof nav==='function') nav('me');
  snap('me page',function(){var e=document.getElementById('page-me'),r=e.getBoundingClientRect();return {display:getComputedStyle(e).display,w:r.width,h:r.height}});
  snap('wordbook',function(){showWordBook();return parentInfo('mWordBook')});
  closeModal('mWordBook');
  snap('listen',function(){showListen();return parentInfo('mListen')});
  closeModal('mListen');
  snap('theme before',function(){return {theme:THEME_MODE,html:document.documentElement.getAttribute('data-theme')}});
  snap('theme toggle',function(){var old=THEME_MODE;setTheme(old==='dark'?'light':'dark');return {before:old,after:THEME_MODE,html:document.documentElement.getAttribute('data-theme')}});
  return JSON.stringify(out);
})()
