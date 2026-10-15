return await (async function(){
  var out=[], errors=[];
  function pause(ms){return new Promise(function(r){setTimeout(r,ms);});}
  function check(name,ok,detail){out.push({name:name,ok:!!ok,detail:detail||''});}
  try{
    await pause(700);
    var originalFetch=window.fetch;
    window.fetch=async function(url,opts){
      var u=String(url);
      if(u.indexOf('/api/dict/lookup')>=0){
        return {ok:true,status:200,json:async function(){return {found:true,word:'كتاب',normalized:'كِتَاب',meaning:{cn:'书；书籍',en:'book'},matches:[{w:'كاتب',cn:'作者'}],examples:[{ar:'هذا كتاب مفيد.',cn:'这是一本有益的书。'}],source:'本地词典'};}};
      }
      return originalFetch(url,opts);
    };
    document.body.classList.add('reading');
    var fake=document.createElement('span'); fake.className='rd-w'; fake.textContent='كِتَاب'; document.body.appendChild(fake);
    await rdWord({stopPropagation:function(){}},fake);
    await pause(260);
    var box=document.getElementById('rdWordBox'), ar=box&&box.querySelector('.rd-word-ar'), status=box&&box.querySelector('#rdWordStatus'), defAr=box&&box.querySelector('.dict-word-ar'), cn=box&&box.querySelector('.dict-cn');
    check('词卡真实打开',!!box&&box.getBoundingClientRect().width>300);
    check('词卡手机宽度不溢出',!!box&&box.getBoundingClientRect().right<=window.innerWidth+1&&box.getBoundingClientRect().left>=-1);
    check('阿拉伯主词保持 RTL',!!ar&&ar.getAttribute('dir')==='rtl'&&getComputedStyle(ar).direction==='rtl');
    check('词典释义阿语保持 RTL',!!defAr&&defAr.getAttribute('dir')==='rtl'&&getComputedStyle(defAr).direction==='rtl');
    check('中文释义保持 LTR',!!cn&&getComputedStyle(cn).direction==='ltr');
    check('词卡状态可读且有 live region',!!status&&status.getAttribute('aria-live')==='polite');
    check('词卡操作按钮具备无障碍标签',!!box&&!!box.querySelector('[aria-label="朗读阿拉伯语"]')&&!!box.querySelector('[aria-label="加入生词本"]')&&!!box.querySelector('[aria-label="关闭词卡"]'));
    var html=document.documentElement, oldTheme=html.getAttribute('data-theme'); html.setAttribute('data-theme','dark'); await pause(60);
    var bg=box&&getComputedStyle(box).backgroundColor; check('夜间词卡使用深色对比背景',!!box&&bg&&bg!=='rgb(246, 239, 219)'&&bg!=='rgb(255, 255, 255)');
    if(oldTheme) html.setAttribute('data-theme',oldTheme); else html.removeAttribute('data-theme');
    if(box&&box.parentNode) box.parentNode.removeChild(box); if(fake.parentNode) fake.parentNode.removeChild(fake); document.body.classList.remove('reading'); window.fetch=originalFetch;
  }catch(e){errors.push(String(e&&e.stack||e));}
  var passed=out.filter(function(x){return x.ok;}).length;
  return JSON.stringify({passed:passed,total:out.length,results:out,errors:errors});
})();
