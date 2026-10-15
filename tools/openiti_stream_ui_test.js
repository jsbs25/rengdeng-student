return await (async function(){
  var out=[],errors=[];
  function pause(ms){return new Promise(function(r){setTimeout(r,ms);});}
  function check(name,ok,detail){out.push({name:name,ok:!!ok,detail:String(detail||'')});}
  function fs(x,y){rdTouchStart({touches:[{clientX:x,clientY:y}]});}
  function fm(x,y){rdTouchMove({touches:[{clientX:x,clientY:y}],cancelable:true,preventDefault:function(){}});}
  function fe(x,y){rdTouchEnd({changedTouches:[{clientX:x,clientY:y}]});}
  window.addEventListener('error',function(e){errors.push(String(e.message||e.error||e));});
  var id='openiti-b189390ada0b10e0';
  var originalFetch=window.fetch, calls={}, abortSeen=false;
  var book={id:id,t:'شرح سنن أبي داود · 流式 UI 测试',a:'OpenITI',source:'OpenITI/KITAB',text_mode:'arabic_original_link',text_url:'https://raw.githubusercontent.com/OpenITI/RELEASE/v2025.1.9/test'};
  try{
    localStorage.removeItem('nur_openiti_page_v2:'+id+':0');
    window.NUR_ISLAMIC_BOOKS=window.NUR_ISLAMIC_BOOKS||{};
    window.NUR_ISLAMIC_BOOKS[id]=book;
    window.fetch=async function(url,opts){
      var u=String(url), m=u.match(/[?&]page=(\d+)/), page=m?Number(m[1]):0;
      if(u.indexOf('/api/catalog/read')>=0){
        calls[page]=(calls[page]||0)+1;
        if(page===0 && calls[page]===1){
          return {ok:false,status:202,json:async function(){return {ready:false,message:'正在按需读取阿拉伯原文…',retry_after_ms:80,progress:0.05,bytes_read:1048576,source_bytes:20041082,pages_ready:0,page:0};}};
        }
        var texts={
          0:'بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ\n\nهذه صفحة عربية تجريبية بعد إكمال القراءة.',
          1:'الصفحة الثانية: نص عربي داخل القارئ مع شرح قابل للتحليل.'
        };
        return {ok:true,status:200,json:async function(){return {ready:true,text:texts[page]||texts[0],page:page,total:2,has_next:page<1,progress:0.12,bytes_read:3145728,source_bytes:20041082,pages_ready:2,eof:false,source:'OpenITI/KITAB',source_url:'https://openiti.org/'}}};
      }
      return originalFetch(url,opts);
    };
    openIslamicBook(id);
    await pause(70);
    var state=window.RD_OPENITI, body=document.getElementById('mReaderBody');
    check('流式书在软件内全屏打开',!!state&&!!document.body.classList.contains('reading')&&!!document.querySelector('#mReader.show'));
    check('202 时显示按需读取进度',!!document.getElementById('rdOpenitiProgress')&&document.getElementById('rdOpenitiProgressLabel').textContent.indexOf('按需读取')>=0);
    check('202 时正文仍是加载占位',String(window.RD_PAGES[0]||'').indexOf('正在载入')>=0);
    await pause(650);
    check('轮询后正文就绪',!!window.RD_OPENITI.loaded[0]&&/[\u0600-\u06ff]/.test(String(window.RD_PAGES[0]||''))&&!String(window.RD_PAGES[0]||'').includes('�'));
    check('就绪进度条显示原文已就绪',document.getElementById('rdOpenitiProgressLabel').textContent.indexOf('已就绪')>=0);
    check('页面断点缓存写入',!!localStorage.getItem('nur_openiti_page_v2:'+id+':0'));
    var analysis=document.querySelector('.rd-page-analysis');
    check('正文就绪后 AI 面板可用',!!analysis&&!!analysis.querySelector('.rd-page-analysis__run')&&!analysis.querySelector('.rd-page-analysis__run').disabled);
    // 第二页已经由阅读器预取；显式翻页仍应留在原阅读器内。
    await pause(250);
    rdGo(1); await pause(120);
    check('阅读器前进到下一页',window.RD_PAGE===1&&/[\u0600-\u06ff]/.test(String(window.RD_PAGES[1]||'')));
    rdGo(-1); await pause(120);
    check('阅读器返回上一页',window.RD_PAGE===0);
    // 取消一个尚未完成的请求，验证 closeModal 会 abort 并清理重试计时器。
    var saved=window.RD_OPENITI;
    var originalPageTotal=saved.total; saved.total=3;
    window.fetch=function(url,opts){
      if(String(url).indexOf('/api/catalog/read')>=0 && String(url).indexOf('page=2')>=0){
        return new Promise(function(){
          if(opts&&opts.signal) opts.signal.addEventListener('abort',function(){abortSeen=true;});
        });
      }
      return originalFetch(url,opts);
    };
    rdOpenitiFetch(2,true); await pause(80);
    closeModal('mReader'); await pause(80);
    check('退出阅读器会 abort 未完成请求',abortSeen);
    check('退出后取消状态与计时器已清理',saved.cancelled===true&&Object.keys(saved.controllers||{}).length===0&&Object.keys(saved.retryTimers||{}).length===0);
    // 重新打开短模拟书并验证移动横滑不产生悬浮弹层。
    window.fetch=originalFetch;
    book.text_url='https://raw.githubusercontent.com/OpenITI/RELEASE/v2025.1.9/test';
    window.fetch=async function(url,opts){
      if(String(url).indexOf('/api/catalog/read')>=0){
        var m=String(url).match(/[?&]page=(\d+)/),p=m?Number(m[1]):0;
        return {ok:true,status:200,json:async function(){return {ready:true,text:p?'الصفحة الثانية':'بِسْمِ اللَّهِ صفحة أولى',page:p,total:2,has_next:p<1,progress:1,bytes_read:20041082,source_bytes:20041082,pages_ready:2,eof:true,source:'OpenITI/KITAB'}}};
      }
      return originalFetch(url,opts);
    };
    openIslamicBook(id); await pause(300);
    var p0=window.RD_PAGE;
    fs(320,420); fm(100,422); fe(100,422); await pause(180);
    check('手机左滑下一页',window.RD_PAGE===Math.min(p0+1,1),'from='+p0+' to='+window.RD_PAGE);
    fs(90,420); fm(300,422); fe(300,422); await pause(180);
    check('手机右滑返回上一页',window.RD_PAGE===p0);
    check('阅读器保持唯一前台弹层',document.querySelectorAll('.modal.show').length===1&&document.querySelector('#mReader.show'));
    closeModal('mReader');
    check('关闭后无残留弹层',document.querySelectorAll('.modal.show').length===0&&!document.body.classList.contains('reading'));
  }catch(e){errors.push(String(e&&e.stack||e));}
  window.fetch=originalFetch;
  check('无 JavaScript 错误',errors.length===0,errors.join('\n'));
  return JSON.stringify({viewport:[innerWidth,innerHeight],passed:out.filter(function(x){return x.ok;}).length,total:out.length,results:out,errors:errors,calls:calls});
})();
