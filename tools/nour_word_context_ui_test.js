return await (async function(){
  var out=[], errors=[], originalFetch=window.fetch, captured=null;
  function pause(ms){return new Promise(function(r){setTimeout(r,ms);});}
  function check(name,ok,detail){out.push({name:name,ok:!!ok,detail:String(detail||'')});}
  window.addEventListener('error',function(e){errors.push(String(e.message||e.error||e));});
  try{
    await pause(700);
    var id='openiti-word-context-test';
    var book={id:id,t:'كتاب اختبار سياق الكلمة',a:'OpenITI',source:'OpenITI/KITAB',text_mode:'arabic_original_link',text_url:'https://raw.githubusercontent.com/OpenITI/RELEASE/v2025.1.9/test'};
    window.NUR_ISLAMIC_BOOKS=window.NUR_ISLAMIC_BOOKS||{}; window.NUR_ISLAMIC_BOOKS[id]=book;
    window.fetch=async function(url,opts){
      var u=String(url);
      if(u.indexOf('/api/catalog/read')>=0){
        var m=u.match(/[?&]page=(\d+)/), page=m?Number(m[1]):0;
        return {ok:true,status:200,json:async function(){return {ready:true,text:page?'في الصفحة الثانية ننتقل إلى مثال آخر في العربية.':'الحمد لله، هذه صفحة عربية للتجربة وفيها كلمة التوجيه والإرشاد.',page:page,total:2,has_next:page<1,progress:1,bytes_read:2048,source_bytes:2048,pages_ready:2,eof:true,source:'OpenITI/KITAB',source_url:'https://openiti.org/'}}};
      }
      if(u.indexOf('/api/dict/lookup')>=0){
        return {ok:true,status:200,json:async function(){return {found:true,word:'التوجيه',normalized:'التوجيه',meaning:{cn:'指导、指引',en:'guidance'},examples:[],source:'本地固定词库'}}};
      }
      if(u.indexOf('/api/chat/message')>=0){
        try{captured=JSON.parse((opts&&opts.body)||'{}');}catch(e){captured=null;}
        return {ok:true,status:200,json:async function(){return {arabic:'已收到选词上下文，并完成词根与语境分析。'}}};
      }
      return originalFetch(url,opts);
    };
    openIslamicBook(id); await pause(520);
    var modal=document.getElementById('mReader'), first=modal&&modal.querySelector('.rd-w');
    check('测试书籍已打开',!!modal&&modal.classList.contains('show')&&!!first);
    var target=Array.from(modal.querySelectorAll('.rd-w')).find(function(e){return e.textContent.trim()==='التوجيه'})||first;
    await rdWord({stopPropagation:function(){}},target); await pause(260);
    var ctx=window.NOUR_AI_CONTEXT||{}, card=document.getElementById('rdWordBox'), aiButton=card&&card.querySelector('.rd-word-ai');
    check('点击阿语词后自动写入选词字段',ctx.selected==='التوجيه'&&ctx.selection==='التوجيه','selected='+String(ctx.selected||''));
    check('词卡显示交给 NOUR AI 分析按钮',!!aiButton&&aiButton.textContent.indexOf('交给 NOUR AI 分析')>=0);
    check('AI 工作区语境卡显示选中词',!!document.querySelector('.nour-reader-context__selection')&&document.querySelector('.nour-reader-context__selection').textContent.indexOf('التوجيه')>=0);
    if(aiButton)aiButton.click();
    await pause(900);
    check('按钮关闭词卡并切换到 NOUR AI',!document.getElementById('rdWordBox')&&window.NUR_ACTIVE_TAB==='ai');
    check('AI 输入已经提交选词问题',!!captured&&String(captured.message||'').indexOf('التوجيه')>=0);
    check('AI 请求包含选词上下文标记',!!captured&&String(captured.message||'').indexOf('【用户选中的阿拉伯语词或短语】')>=0);
    check('AI 请求保留当前书页语境',!!captured&&String(captured.message||'').indexOf('كتاب اختبار سياق الكلمة')>=0&&String(captured.message||'').indexOf('الحمد لله')>=0);
    check('AI 请求包含词根分析意图',!!captured&&/词根|词形|词性/.test(String(captured.message||'')));
    nav('home'); await pause(100); openIslamicBook(id); await pause(320); rdGo(1); await pause(180);
    var next=window.NOUR_AI_CONTEXT||{};
    check('翻页后旧选词不会串入下一页',!next.selected&&!next.selection&&next.page===2);
    closeModal('mReader');
  }catch(e){errors.push(String(e&&e.stack||e));}
  window.fetch=originalFetch;
  check('无 JavaScript 错误',errors.length===0,errors.join('\n'));
  return JSON.stringify({viewport:[innerWidth,innerHeight],passed:out.filter(function(x){return x.ok;}).length,total:out.length,results:out,errors:errors,captured:captured?{message:String(captured.message||'').slice(0,900)}:null});
})();
