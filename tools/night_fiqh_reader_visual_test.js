return await (async function(){
  var out=[],errors=[];
  function pause(ms){return new Promise(function(r){setTimeout(r,ms);});}
  function check(name,ok,detail){out.push({name:name,ok:!!ok,detail:String(detail||'')});}
  function rgb(v){var m=String(v||'').match(/rgba?\(([^)]+)\)/);if(!m)return null;var a=m[1].split(',').map(function(x){return parseFloat(x)});return {r:a[0],g:a[1],b:a[2],a:a.length>3?a[3]:1};}
  function lum(v){var c=rgb(v);if(!c)return -1;function f(x){x=x/255;return x<=.03928?x/12.92:Math.pow((x+.055)/1.055,2.4);}return .2126*f(c.r)+.7152*f(c.g)+.0722*f(c.b);}
  function info(el){if(!el)return {};var s=getComputedStyle(el),r=el.getBoundingClientRect();return {display:s.display,direction:s.direction,textAlign:s.textAlign,color:s.color,bg:s.backgroundColor,border:s.borderColor,w:Math.round(r.width),h:Math.round(r.height),lum:lum(s.color),bgLum:lum(s.backgroundColor)};}
  window.addEventListener('error',function(e){errors.push(String(e.message||e.error||e));});
  try{
    await pause(1000); setTheme('dark'); await pause(60);
    check('夜间主题已启用',document.documentElement.getAttribute('data-theme')==='dark'&&window.THEME_MODE==='dark',document.documentElement.getAttribute('data-theme'));
    nav('learn'); await pause(1700);
    var room=document.getElementById('nourFiqhReadingRoom');
    check('四学派阅读室已挂载',!!room);
    var cards=room?room.querySelectorAll('.nour-fiqh-school-card'):[];
    check('四学派横向卡片完整',cards.length===4,String(cards.length));
    var cardInfo=Array.prototype.map.call(cards,function(x){return info(x);});
    check('夜间卡片有实际暗色表面',cardInfo.length===4&&cardInfo.every(function(x){return x.w>0&&x.h>0&&x.bgLum>=0&&x.bgLum<0.25;}),JSON.stringify(cardInfo));
    var schoolArabic=room&&room.querySelector('.nour-fiqh-school-card header strong');
    var bookCopy=room&&room.querySelector('.nour-fiqh-book-copy');
    var bookMeta=room&&room.querySelector('.nour-fiqh-book-copy p');
    check('学派阿语标题保持 RTL',!!schoolArabic&&schoolArabic.getAttribute('dir')==='rtl'&&getComputedStyle(schoolArabic).direction==='rtl',schoolArabic&&JSON.stringify(info(schoolArabic)));
    check('书名区域保持 RTL',!!bookCopy&&bookCopy.getAttribute('dir')==='rtl'&&getComputedStyle(bookCopy).direction==='rtl',bookCopy&&JSON.stringify(info(bookCopy)));
    check('作者/年份区域保持 LTR',!!bookMeta&&bookMeta.getAttribute('dir')==='ltr'&&getComputedStyle(bookMeta).direction==='ltr',bookMeta&&JSON.stringify(info(bookMeta)));
    check('卡片文字夜间对比度可见',!!schoolArabic&&lum(getComputedStyle(schoolArabic).color)>0.45,schoolArabic&&getComputedStyle(schoolArabic).color);
    var quduri=room&&room.querySelector('[data-fiqh-open="fiqh-quduri"]');
    check('古都里 Shamela 入口可见',!!quduri);
    if(quduri)quduri.click();
    await pause(1900);
    var reader=document.getElementById('mReader'), body=reader&&reader.querySelector('.m-body'), page=reader&&reader.querySelector('.rd-page'), paper=reader&&reader.querySelector('.rd-paper'), analysis=document.getElementById('rdPageAnalysis');
    check('真实 Shamela 阅读器已打开',!!reader&&reader.classList.contains('show')&&document.body.classList.contains('reading'));
    check('Shamela 真实全文已加载',Array.isArray(window.RD_PAGES)&&window.RD_PAGES.length>=200,'pages='+(window.RD_PAGES&&window.RD_PAGES.length));
    var pi=info(page), bi=info(body), ai=info(analysis), ri=info(reader);
    check('Shamela 阿语正文保持 RTL 右对齐',!!page&&pi.direction==='rtl'&&(pi.textAlign==='right'||pi.textAlign==='start')&&/[\u0600-\u06ff]/.test(page.textContent||''),JSON.stringify(pi));
    check('夜间阅读舞台为深色',!!body&&bi.bgLum>=0&&bi.bgLum<0.25,JSON.stringify(bi));
    check('夜间阿语正文保持高亮文字',!!page&&pi.lum>0.45&&pi.bgLum<0.35,JSON.stringify(pi));
    check('页级 AI 卡在夜间不是浅色反差',!!analysis&&ai.bgLum>=0&&ai.bgLum<0.35&&ai.lum>0.45,JSON.stringify(ai));
    check('阅读器窗口未反向溢出',!!body&&bi.w<=innerWidth+2&&bi.h<=innerHeight+2,JSON.stringify(bi));
    if(typeof closeModal==='function')closeModal('mReader');
  }catch(e){errors.push(String(e&&e.stack||e));}
  check('无 JavaScript 错误',errors.length===0,errors.join('\n'));
  setTheme('auto');
  return JSON.stringify({viewport:[innerWidth,innerHeight],passed:out.filter(function(x){return x.ok;}).length,total:out.length,results:out,errors:errors});
})();
