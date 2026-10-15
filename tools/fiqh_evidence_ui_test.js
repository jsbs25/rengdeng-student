return await (async function(){
  var checks=[], errors=[], originalFetch=window.fetch, captured=null;
  function pause(ms){return new Promise(function(r){setTimeout(r,ms);});}
  function check(name,ok,detail){checks.push({name:name,ok:!!ok,detail:String(detail||'')});}
  window.addEventListener('error',function(e){errors.push(String(e.message||e.error||e));});
  try{
    await pause(700);
    var id='fiqh-quduri';
    var book={id:id,t:'مختصر القدوري · 法学原典',a:'古都里',c:'法学',c_ar:'فقه',discipline:'法学',u:'https://catalog.hathitrust.org/Record/102709712',source:'HathiTrust · 书目页',access:'按版本核验',rights:'不把 Full View 误当全球公版',fiqh_schools:['hanafi'],fiqh_school_labels:['哈乃斐学派'],fiqh_school_evidence:{hanafi:['القدوري']},fiqh_school_inference:'从书名、作者和公开元数据推断；不是作者自证或教法裁决',text_mode:'arabic_original_link'};
    window.NUR_ISLAMIC_BOOKS=window.NUR_ISLAMIC_BOOKS||{}; window.NUR_ISLAMIC_BOOKS[id]=book;
    window.fetch=async function(url,opts){
      var u=String(url);
      if(u.indexOf('/api/catalog/read')>=0){
        return {ok:true,status:200,json:async function(){return {ready:true,text:'بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ\n\nهذا نص عربي في مسألة فقهية، ويصل إلى مساعد القراءة.',page:0,total:1,has_next:false,progress:1,bytes_read:2048,source_bytes:2048,pages_ready:1,eof:true,source:'HathiTrust',source_url:book.u};}};
      }
      if(u.indexOf('/api/page/analyze')>=0){
        try{captured=JSON.parse(opts.body);}catch(e){}
        return {ok:true,status:200,json:async function(){return {ok:true,cached:false,analysis:{overview:'本页区分规则文本、作者表达和学习者需要核验的依据。',key_points:['把原文与后世解释分开'],questions:['证据是否能在原典页码中复核？'],practical_guidance:['打开官方版本逐项核对'],quran_references:[{reference:'待核验的相关经文',note:'只作线索',status:'待核验',url:'https://quran.com/'}],hadith_references:[{reference:'待核验的圣训来源',note:'不能据此提高等级',status:'待核验'}],fiqh_context:['这是学习性比较，不是法特瓦'],school_comparison:[{school:'哈乃斐学派',position:'以当前书目传统作学习性概括',basis:'书目元数据：القدوري',status:'直接相关'},{school:'马立克学派',position:'当前页未提供直接主张',basis:'待核验',status:'待核验'},{school:'沙斐仪学派',position:'当前页未提供直接主张',basis:'待核验',status:'待核验'},{school:'汉百里学派',position:'当前页未提供直接主张',basis:'待核验',status:'待核验'}],language_notes:['观察术语和条件句'],terms:[{ar:'فَرْض',cn:'义务；需回到词典和原典核对'}],source_note:'来源需回到官方版本',caution:'学习辅助，不是法特瓦。'}};}}
        }
    return originalFetch(url,opts);
    };
    openIslamicBook(id); await pause(600);
    check('书内阿拉伯正文已打开',!!document.getElementById('mReaderBody')&&/هذا نص عربي/.test(document.getElementById('mReaderBody').textContent||''));
    var run=document.querySelector('.rd-page-analysis__run'); if(run) run.click(); await pause(500);
    var panel=document.getElementById('rdPageAnalysis');
    check('四学派比较卡已渲染',!!panel&&panel.querySelectorAll('.rd-page-analysis__school-card').length===4);
    check('官方来源卡已渲染',!!panel&&panel.querySelectorAll('.rd-page-analysis__source').length>=1);
    check('经文核验链接可点击',!!panel&&panel.querySelector('a[href="https://quran.com/"]'));
    check('站内原文入口已渲染',!!panel&&!!panel.querySelector('.rd-page-analysis__inapp'));
    check('证据状态明确显示',!!panel&&/待核验/.test(panel.textContent||''));
    check('payload 保留学派证据字典',!!captured&&captured.book_meta&&typeof captured.book_meta.fiqh_school_evidence==='object'&&!Array.isArray(captured.book_meta.fiqh_school_evidence));
    check('payload 保留来源线索',!!captured&&captured.book_meta&&Array.isArray(captured.book_meta.source_evidence)&&captured.book_meta.source_evidence.length>=1);
    check('阅读器保持 RTL',!!document.querySelector('.rd-page')&&getComputedStyle(document.querySelector('.rd-page')).direction==='rtl');
    check('无 JavaScript 错误',errors.length===0,errors.join('\n'));
  }catch(e){errors.push(String(e&&e.stack||e));}
  window.fetch=originalFetch;
  return JSON.stringify({viewport:[innerWidth,innerHeight],passed:checks.filter(function(x){return x.ok;}).length,total:checks.length,results:checks,errors:errors});
})();
