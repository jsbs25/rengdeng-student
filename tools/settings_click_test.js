return await (async function(){
  const out=[]; const pause=ms=>new Promise(r=>setTimeout(r,ms));
  const check=(name,ok,detail)=>out.push({name,ok:!!ok,detail:detail||''});
  await pause(1600); nav('me'); await pause(80);
  const links=Array.from(document.querySelectorAll('#page-me .profile-link'));
  const clickText=t=>{const b=links.find(x=>x.textContent.indexOf(t)>=0); if(b){b.click(); return true;} return false;};
  check('profile links present',links.length>=5,links.length);
  check('wordbook button found',clickText('生词本')); await pause(60); check('wordbook opens',document.getElementById('mWordBook').classList.contains('show')&&document.getElementById('mWordBook').getBoundingClientRect().width>0); closeModal('mWordBook');
  check('listen button found',clickText('跟读练习')); await pause(60); check('listen opens',document.getElementById('mListen').classList.contains('show')&&document.getElementById('mListen').getBoundingClientRect().width>0); closeModal('mListen');
  check('theme button found',clickText('外观设置')); await pause(60); check('theme panel opens',document.getElementById('mTheme').classList.contains('show')&&document.querySelectorAll('.theme-settings-option').length===3); const dark=document.querySelector('.theme-settings-option[onclick*="dark"]'); if(dark) dark.click(); await pause(40); check('theme option applies',THEME_MODE==='dark'&&document.documentElement.getAttribute('data-theme')==='dark');
  return JSON.stringify({passed:out.filter(x=>x.ok).length,total:out.length,results:out});
})();
