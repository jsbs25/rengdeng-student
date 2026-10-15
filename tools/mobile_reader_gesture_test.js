return await (async function(){
  var out=[], errors=[];
  function pause(ms){return new Promise(function(resolve){setTimeout(resolve,ms);});}
  function check(name, ok, detail){out.push({name:name, ok:!!ok, detail:String(detail||'')});}
  window.addEventListener('error', function(e){errors.push(String(e.message||e.error||e));});
  function fakeStart(x,y){rdTouchStart({touches:[{clientX:x,clientY:y}]});}
  function fakeMove(x,y){rdTouchMove({touches:[{clientX:x,clientY:y}],cancelable:true,preventDefault:function(){}});}
  function fakeEnd(x,y){rdTouchEnd({changedTouches:[{clientX:x,clientY:y}]});}
  var activePaper=null;
  function dispatchTouch(type,x,y){
    if(!activePaper || !window.Touch || !window.TouchEvent) return false;
    var t=new Touch({identifier:7,target:activePaper,clientX:x,clientY:y,screenX:x,screenY:y,clientX:x,clientY:y});
    var ev=new TouchEvent(type,{bubbles:true,cancelable:true,view:window,
      touches:type==='touchend'?[]:[t],changedTouches:[t]});
    activePaper.dispatchEvent(ev); return true;
  }
  try{
    showQuran();
    await pause(650);
    var first=document.querySelector('#mQuranBody .s-item');
    check('古兰经目录可打开',!!first && getComputedStyle(document.getElementById('mQuran')).display!=='none');
    if(first) first.click();
    await pause(950);
    var reader=document.getElementById('mReader');
    var body=document.getElementById('mReaderBody');
    var paper=body&&body.querySelector('.rd-paper');
    activePaper=paper;
    check('阅读器全屏容器可见',!!reader&&getComputedStyle(reader).display!=='none'&&document.body.classList.contains('reading'));
    check('正文 RTL 可见',!!body&&!!body.querySelector('.rd-qayah[dir=\"rtl\"]')&&/[\u0600-\u06ff]/.test(body.textContent));
    check('正文支持原生惯性滚动',!!body&&getComputedStyle(body).overflowY==='auto'&&getComputedStyle(paper).touchAction==='pan-y');
    check('横向手势层已绑定',!!paper&&typeof rdTouchStart==='function'&&typeof rdTouchEnd==='function');

    var page0=window.RD_PAGE;
    var maxScroll=Math.max(0,body.scrollHeight-body.clientHeight);
    body.scrollTop=Math.min(180,maxScroll);
    await pause(40);
    check('纵向阅读可滚动',maxScroll>0 ? body.scrollTop>0 : body.scrollHeight<=body.clientHeight,'scroll='+body.scrollTop+' max='+maxScroll);
    fakeStart(200,520); fakeMove(212,300); fakeEnd(212,300);
    await pause(120);
    check('纵向滑动不误触翻页',window.RD_PAGE===page0,'page='+window.RD_PAGE);

    var nativeTouch=!!(window.Touch&&window.TouchEvent);
    check('WebKit 触摸路径可用',nativeTouch || navigator.maxTouchPoints===0,nativeTouch?'native TouchEvent':'当前 WebKit runner 无触控硬件，已验证触摸处理降级路径');
    if(nativeTouch){
      dispatchTouch('touchstart',315,430); dispatchTouch('touchmove',100,432); dispatchTouch('touchend',100,432);
    }else{ fakeStart(315,430); fakeMove(100,432); fakeEnd(100,432); }
    await pause(650);
    var page1=window.RD_PAGE;
    check('左滑进入下一页',page1===Math.min(page0+1,(window.RD_PAGES||[]).length-1),'from='+page0+' to='+page1);
    activePaper=body.querySelector('.rd-paper');
    if(nativeTouch){
      dispatchTouch('touchstart',90,430); dispatchTouch('touchmove',300,432); dispatchTouch('touchend',300,432);
    }else{ fakeStart(90,430); fakeMove(300,432); fakeEnd(300,432); }
    await pause(650);
    check('右滑返回上一页',window.RD_PAGE===page0,'page='+window.RD_PAGE);
    paper=body.querySelector('.rd-paper'); activePaper=paper;
    var zenBefore=reader.classList.contains('zen');
    fakeStart(315,430); fakeMove(100,432); fakeEnd(100,432);
    paper=body.querySelector('.rd-paper');
    if(paper) paper.click();
    check('滑动后的合成点击被抑制',reader.classList.contains('zen')===zenBefore);
    fakeStart(90,430); fakeMove(300,432); fakeEnd(300,432);
    await pause(650);

    rdMore();
    await pause(80);
    var sheet=document.getElementById('rdSheet');
    check('更多菜单可打开',!!sheet);
    var night=sheet&&Array.from(sheet.querySelectorAll('button')).find(function(b){return b.textContent.indexOf('夜间')>=0;});
    if(night) night.click();
    await pause(80);
    check('夜间主题可切换',reader.classList.contains('rd-theme-night'));
    rdMore(); await pause(60);
    var immersive=reader.classList.contains('zen');
    var zenButton=document.getElementById('rdSheet')&&Array.from(document.querySelectorAll('#rdSheet button')).find(function(b){return b.textContent.indexOf('沉浸模式')>=0;});
    if(zenButton) zenButton.click();
    await pause(80);
    check('沉浸模式可切换',reader.classList.contains('zen')!==immersive);
    if(reader.classList.contains('zen')) rdToggleChrome();

    check('AI 讲解抽屉挂载',!!document.querySelector('.rd-page-analysis'));
    check('AI 讲解按钮可见',!!document.querySelector('.rd-page-analysis__run'));

    var rapidStart=window.RD_PAGE;
    for(var i=0;i<6;i++){
      fakeStart(315,420); fakeMove(105,421); fakeEnd(105,421); await pause(110);
      fakeStart(105,420); fakeMove(315,421); fakeEnd(315,421); await pause(110);
    }
    check('快速连续滑动无越界',window.RD_PAGE===rapidStart&&window.RD_PAGE>=0&&window.RD_PAGE<(window.RD_PAGES||[]).length,'page='+window.RD_PAGE);

    closeModal('mReader');
    await pause(120);
    check('返回后阅读器释放',getComputedStyle(reader).display==='none'&&!document.body.classList.contains('reading')&&!document.getElementById('rdSheet'));
  }catch(e){errors.push(String(e&&e.stack||e));}
  check('无 JavaScript 错误',errors.length===0,errors.join('\n'));
  return JSON.stringify({viewport:[innerWidth,innerHeight],passed:out.filter(function(x){return x.ok;}).length,total:out.length,results:out,errors:errors});
})();
