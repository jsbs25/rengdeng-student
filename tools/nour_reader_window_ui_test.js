return await (async function(){
  var out=[], errors=[], originalFetch=window.fetch, id='openiti-b189390ada0b10e0', captured=null;
  function pause(ms){return new Promise(function(r){setTimeout(r,ms);});}
  function check(name,ok,detail){out.push({name:name,ok:!!ok,detail:String(detail||'')});}
  window.addEventListener('error',function(e){errors.push(String(e.message||e.error||e));});
  try{
    await pause(650);
    var book={id:id,t:'ديوان أبو طالب · Apple Books reader',a:'OpenITI',source:'OpenITI/KITAB',text_mode:'arabic_original_link',text_url:'https://raw.githubusercontent.com/OpenITI/RELEASE/v2025.1.9/test'};
    window.NUR_ISLAMIC_BOOKS=window.NUR_ISLAMIC_BOOKS||{}; window.NUR_ISLAMIC_BOOKS[id]=book;
    window.fetch=async function(url,opts){
      var u=String(url);
      if(u.indexOf('/api/catalog/read')>=0){
        var m=u.match(/[?&]page=(\d+)/), page=m?Number(m[1]):0;
        return {ok:true,status:200,json:async function(){return {ready:true,text:page?'الصفحة الثانية من النص العربي، وفيها سياق يكفي للتحليل.':'بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ\n\nهذه صفحة عربية داخل نافذة القراءة، وسيصل سياقها إلى المساعد.',page:page,total:2,has_next:page<1,progress:1,bytes_read:2048,source_bytes:2048,pages_ready:2,eof:true,source:'OpenITI/KITAB',source_url:'https://openiti.org/'}}};
      }
      return originalFetch(url,opts);
    };
    openIslamicBook(id); await pause(420);
    var modal=document.getElementById('mReader'), head=modal&&modal.querySelector('.m-head'), body=modal&&modal.querySelector('.m-body'), paper=modal&&modal.querySelector('.rd-paper'), page=modal&&modal.querySelector('.rd-page');
    var mr=modal&&modal.getBoundingClientRect(), hr=head&&head.getBoundingClientRect(), br=body&&body.getBoundingClientRect(), pr=paper&&paper.getBoundingClientRect();
    check('站内阅读器已打开',!!modal&&modal.classList.contains('show')&&document.body.classList.contains('reading'));
    check('默认不是全屏模式',!!modal&&!modal.classList.contains('full'));
    check('阅读器保留标题栏',!!head&&getComputedStyle(head).display!=='none');
    var bars=Array.from(modal.querySelectorAll('.m-body>.rd-bar')).filter(function(x){return getComputedStyle(x).display!=='none';});
    check('阅读器只显示一个主工具条',bars.length===1);
    check('工具条提供本地书签',!!modal.querySelector('.rd-bookmark'));
    var beforeBookmark=localStorage.getItem('nur_reader_bookmarks')||'{}';
    if(modal.querySelector('.rd-bookmark')) modal.querySelector('.rd-bookmark').click();
    await pause(60);
    check('书签状态可持久化',Object.keys(JSON.parse(localStorage.getItem('nur_reader_bookmarks')||'{}')).length>=1);
    localStorage.setItem('nur_reader_bookmarks',beforeBookmark);
    check('Mac 阅读窗口有外部留白',innerWidth<800||!!hr&&hr.width < innerWidth-40,'head='+ (hr&&hr.width) +' viewport='+innerWidth);
    check('阅读窗口高度低于视口',innerWidth<800||!!br&&br.height < innerHeight-50,'body='+ (br&&br.height) +' viewport='+innerHeight);
    check('正文纸页位于阅读舞台内',!!page&&!!paper&&pr.width<=br.width+1&&pr.width < innerWidth-30,'paper='+ (pr&&pr.width) +' body='+ (br&&br.width));
    var pageNow=modal&&modal.querySelector('.rd-page');
    check('正文保持阿拉伯 RTL 排版',!!pageNow&&getComputedStyle(pageNow).direction==='rtl'&&/بِسْم|هذه/.test(pageNow.textContent||''));
    check('正文下方保留本页 AI 分析挂点',!!document.getElementById('rdPageAnalysis'));
    check('阅读上下文已同步',!!window.NOUR_AI_CONTEXT&&window.NOUR_AI_CONTEXT.title.indexOf('ديوان أبو طالب')>=0&&window.NOUR_AI_CONTEXT.page===1);
    await pause(80);
    var aiContext=document.getElementById('nourReaderContext');
    check('AI 工作区显示当前页语境',!!aiContext&&!aiContext.hidden&&aiContext.textContent.indexOf('当前阅读语境已连接')>=0);
    // 进入 AI 工作区并验证现有聊天 API 仅被追加当前上下文，不改动业务函数签名。
    nav('ai'); await pause(180);
    var inp=document.getElementById('homeAIIn'); if(inp){inp.value='解释这一页的核心意思';}
    window.fetch=function(url,opts){
      var u=String(url);
      if(u.indexOf('/api/chat/message')>=0){try{captured=JSON.parse(opts.body);}catch(e){} return Promise.resolve({ok:true,status:200,json:async function(){return {arabic:'已根据当前页回答。'};}});}
      return originalFetch(url,opts);
    };
    await homeAISend(); await pause(100);
    check('NOUR AI 请求保留原问题',!!captured&&captured.message.indexOf('解释这一页的核心意思')>=0);
    check('NOUR AI 请求包含书名上下文',!!captured&&captured.message.indexOf('ديوان أبو طالب')>=0);
    check('NOUR AI 请求包含当前页正文',!!captured&&captured.message.indexOf('هذه صفحة عربية داخل نافذة القراءة')>=0);
    check('AI 语境状态在工作区可见',!!document.getElementById('nourReaderContext')&&!document.getElementById('nourReaderContext').hidden);
    // 返回阅读器，确认默认仍是窗口模式，并测试翻页后上下文更新。
    window.fetch=originalFetch;
    openIslamicBook(id); await pause(260); rdGo(1); await pause(180);
    check('翻页后上下文页码更新',!!window.NOUR_AI_CONTEXT&&window.NOUR_AI_CONTEXT.page===2&&window.NOUR_AI_CONTEXT.text.indexOf('الصفحة الثانية')>=0);
    check('翻页后仍保持窗口模式',!!document.getElementById('mReader')&&!document.getElementById('mReader').classList.contains('full'));
    closeModal('mReader');
    check('关闭后窗口和阅读状态清理',document.querySelectorAll('.modal.show').length===0&&!document.body.classList.contains('reading'));
  }catch(e){errors.push(String(e&&e.stack||e));}
  window.fetch=originalFetch;
  check('无 JavaScript 错误',errors.length===0,errors.join('\n'));
  return JSON.stringify({viewport:[innerWidth,innerHeight],passed:out.filter(function(x){return x.ok;}).length,total:out.length,results:out,errors:errors,captured:captured?{message:String(captured.message||'').slice(0,500)}:null});
})();
