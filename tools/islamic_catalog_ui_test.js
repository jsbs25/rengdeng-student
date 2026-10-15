return await (async function(){
  var out=[];
  function check(name,ok,detail){out.push({name:name,ok:!!ok,detail:String(detail||'')});}
  function pause(ms){return new Promise(function(resolve){setTimeout(resolve,ms);});}
  try{
    if(typeof window.nav==='function') window.nav('learn');
    await pause(120);
    if(typeof window.libTab==='function') window.libTab('islamic');
    await pause(850);
    var page=document.getElementById('mCat'), body=document.getElementById('mCatBody');
    check('世界图书馆页面已打开',!!page && getComputedStyle(page).display!=='none',page?getComputedStyle(page).display:'missing');
    check('统一书库标签已显示',!!document.querySelector('.lib-tabs') && document.body.textContent.indexOf('世界图书馆')>=0);
    check('五个核心学科导航',document.querySelectorAll('.bk-cat-discipline').length>=5,document.querySelectorAll('.bk-cat-discipline').length);
    check('大规模阿拉伯书目已接入',!!window.CAT_META && Number(window.CAT_META.total||0)>=8000,window.CAT_META&&window.CAT_META.total);
    check('目录总量与分类已显示',!!document.getElementById('catCount') && document.querySelectorAll('#catGrid .bk-card').length>0,document.getElementById('catCount')&&document.getElementById('catCount').textContent);
    check('专题标签索引已显示',document.querySelectorAll('.bk-cat-tag').length>=8,document.querySelectorAll('.bk-cat-tag').length);
    var tagButton=document.querySelector('.bk-cat-tag');
    if(tagButton) tagButton.click();
    await pause(3000);
    check('专题标签可筛选',!!tagButton && document.querySelectorAll('#catGrid .bk-card').length>0,document.getElementById('catCount')&&document.getElementById('catCount').textContent);
    var schoolButton=document.querySelector('.bk-cat-school');
    check('法学派作品索引已显示',document.querySelectorAll('.bk-cat-school').length>=4,document.querySelectorAll('.bk-cat-school').length);
    if(schoolButton) schoolButton.click();
    await pause(3000);
    check('法学派索引可筛选',!!schoolButton && document.querySelectorAll('#catGrid .bk-card').length>0,document.getElementById('catCount')&&document.getElementById('catCount').textContent);
    var usul=[].slice.call(document.querySelectorAll('.bk-cat-discipline')).find(function(x){return x.textContent.indexOf('法源学')>=0;});
    if(usul) usul.click();
    await pause(3000);
    check('法源学分类可筛选',document.querySelectorAll('#catGrid .bk-card').length>=7,document.querySelectorAll('#catGrid .bk-card').length);
    check('书卡显示来源与 AI 导读',document.querySelectorAll('#catGrid .bk-source').length>=7 && document.querySelectorAll('#catGrid .bk-card-actions .bk-in').length>=7);
    check('阿拉伯原文入口已显示',document.querySelectorAll('#catGrid .bk-original').length>=1,document.querySelectorAll('#catGrid .bk-original').length);
    var original=document.querySelector('#catGrid .bk-original');
    if(original) original.click();
    await pause(2600);
    check('原文在软件内阅读器打开',!!window.RD_OPENITI && !!document.querySelector('.rd-inapp-source') && getComputedStyle(document.getElementById('mReader')).display!=='none',window.RD_OPENITI&&window.RD_OPENITI.id);
    check('原文首屏已加载',!!window.RD_OPENITI && window.RD_OPENITI.loaded[0]===true && document.querySelector('#mReader .rd-page') && document.querySelector('#mReader .rd-page').textContent.indexOf('正在载入')<0);
    check('原文页挂载逐页 AI 注解',!!document.getElementById('rdPageAnalysis') && !!document.querySelector('.rd-page-analysis-trigger'));
    var beforePage=window.RD_PAGE;
    if(window.RD_OPENITI && window.RD_OPENITI.total>1 && typeof window.rdGo==='function'){ window.rdGo(1); await pause(500); }
    check('软件内原文可翻页',!window.RD_OPENITI || window.RD_OPENITI.total<2 || window.RD_PAGE===beforePage+1,window.RD_OPENITI&&window.RD_OPENITI.total);
    if(typeof window.closeModal==='function') window.closeModal('mReader');
    await pause(120);
    var ai=document.querySelector('#catGrid .bk-card-actions .bk-in');
    if(ai) ai.click();
    await pause(850);
    check('书目 AI 导读阅读页打开',!!document.querySelector('#mReader') && getComputedStyle(document.querySelector('#mReader')).display!=='none',document.getElementById('mReaderTitle')&&document.getElementById('mReaderTitle').textContent);
    check('书目导读显式标注元数据边界',document.body.textContent.indexOf('书目级 AI 导读')>=0 || document.body.textContent.indexOf('书目 AI 导读')>=0);
    check('书目导读入口可追踪',!!window.RD_BOOK_META && !!window.RD_BOOK_META.u,window.RD_BOOK_META&&window.RD_BOOK_META.id);
    check('详细导读主卡已渲染',!!document.querySelector('.rd-guide') && document.querySelectorAll('.rd-guide__section').length>=6,document.querySelectorAll('.rd-guide__section').length);
    check('导读包含历史背景与学习路径',document.body.textContent.indexOf('历史与文本背景')>=0 && document.body.textContent.indexOf('建议阅读路径')>=0);
    check('导读包含阿拉伯语术语',document.querySelectorAll('.rd-guide__term').length>=3,document.querySelectorAll('.rd-guide__term').length);
    check('导读来源链接已显示',document.querySelectorAll('.rd-guide__source').length>=2,document.querySelectorAll('.rd-guide__source').length);
    check('导读包含证据边界',document.body.textContent.indexOf('证据边界与核验提醒')>=0 && document.body.textContent.indexOf('不是法特瓦')>=0);
    var school=document.querySelector('.rd-page-analysis__school-select');
    check('法学派视角选择器已显示',!!school,school&&school.value);
    if(school){ school.value='hanafi'; school.dispatchEvent(new Event('change',{bubbles:true})); await pause(120); }
    check('哈乃斐视角可切换',!school || document.body.textContent.indexOf('哈乃斐学派')>=0,school&&school.value);
  }catch(e){check('验收脚本无异常',false,e&&e.message||e);}
  return JSON.stringify(out);
})();
