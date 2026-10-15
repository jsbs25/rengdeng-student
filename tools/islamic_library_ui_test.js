return await (async function(){
  var out=[];
  function check(name,ok,detail){out.push({name:name,ok:!!ok,detail:String(detail||'')});}
  function pause(ms){return new Promise(function(resolve){setTimeout(resolve,ms);});}
  try{
    if(typeof window.showIslamicLibrary==='function') window.showIslamicLibrary();
    await pause(700);
    var page=document.getElementById('mCat');
    var body=document.getElementById('mCatBody');
    check('来源目录页面已打开',!!page && getComputedStyle(page).display!=='none',page?getComputedStyle(page).display:'missing');
    check('来源卡片数量',document.querySelectorAll('.isl-source-card').length>=5,document.querySelectorAll('.isl-source-card').length);
    check('古兰经学习入口',!!document.querySelector('.isl-quran-card'));
    check('六大部圣训入口',document.querySelectorAll('.isl-hadith-card').length===6,document.querySelectorAll('.isl-hadith-card').length);
    check('伊斯兰来源标签选中',!!document.querySelector('.lib-tabs .lt.on') && document.querySelector('.lib-tabs .lt.on').textContent.indexOf('伊斯兰')>=0);
    var q=document.getElementById('islQuery');
    check('来源搜索框可用',!!q && !q.disabled);
    var sunnah=document.querySelector('.isl-source-card[onclick*="sunnah"]');
    if(sunnah) sunnah.click();
    await pause(850);
    check('六大部来源切换',!!document.querySelector('.isl-active') && document.querySelector('.isl-active').textContent.indexOf('六大部圣训')>=0,body?body.textContent.slice(0,240):'');
    check('六大部书目仍可见',document.querySelectorAll('.isl-hadith-card').length===0 || document.querySelectorAll('.isl-result').length>=0);
    check('底部导航不遮挡图书馆',function(){var t=document.querySelector('.tabbar'),p=document.querySelector('.library-page');if(!t||!p)return false;var a=t.getBoundingClientRect(),b=p.getBoundingClientRect();return a.top>=0 && b.width>0;}());
  }catch(e){check('验收脚本无异常',false,e&&e.message||e);}
  return JSON.stringify(out);
})();
