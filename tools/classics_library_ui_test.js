return await (async function(){
  var checks=[], errors=[], originalFetch=window.fetch, originalOpen=window.openReadById, opened=null, calls=[];
  function pause(ms){return new Promise(function(r){setTimeout(r,ms);});}
  function check(name,ok,detail){checks.push({name:name,ok:!!ok,detail:String(detail||'')});}
  var sample={
    meta:{total:1820,counts:{quran:158,hadith:441,fiqh:283,usul:26,language:251,history:178,aqida:217,literature:266}},
    reading_paths:[{id:'fiqh-evidence',title:'法学入门 → 法源学 → 学派比较',ar:'من الفقه إلى أصوله ومقارنته',summary:'学习性路径',collections:['fiqh','usul','language'],steps:['伊斯兰法学','法源学','语言与论证']}],
    items:[
      {id:'2237',title_ar:'آكام المرجان في أحكام الجان',collection:'fiqh',collection_label:'伊斯兰法学',source_url:'https://shamela.ws/book/2237',rt:'shamela',readable:true},
      {id:'4134',title_ar:'شذا العرف في فن الصرف',collection:'language',collection_label:'阿拉伯语言与修辞',source_url:'https://shamela.ws/book/4134',rt:'shamela',readable:true},
      {id:'4407',title_ar:'معجم المسائل النحوية والصرفية الواردة في القرآن الكريم',collection:'quran',collection_label:'古兰经学与经注',source_url:'https://shamela.ws/book/4407',rt:'shamela',readable:true}
    ]
  };
  window.addEventListener('error',function(e){errors.push(String(e.message||e.error||e));});
  window.fetch=async function(url,opts){
    var u=String(url);
    if(u.indexOf('/api/library/classics')>=0){
      calls.push(u);
      var query=u.indexOf('collection=fiqh')>=0;
      return {ok:true,status:200,json:async function(){return {ok:true,total:query?1:3,page:0,size:18,items:query?[sample.items[0]]:sample.items,reading_paths:sample.reading_paths,meta:sample.meta};}};
    }
    return originalFetch(url,opts);
  };
  window.openReadById=function(id,rt){opened={id:String(id),rt:String(rt)};};
  try{
    await pause(720);
    nav('learn');
    await pause(1100);
    var panel=document.getElementById('nourClassicPanel');
    check('经典发现面板已挂载',!!panel);
    check('经典计数来自 API',!!panel&&panel.textContent.indexOf('1,820')>=0);
    check('阅读路径已显示',!!panel&&panel.querySelectorAll('.nour-path-card').length>=1);
    check('分类筛选可见',!!panel&&panel.querySelectorAll('[data-classic-collection]').length>=8);
    check('真实 Shamela 来源链接带安全属性',!!panel&&panel.querySelector('a[href="https://shamela.ws/book/2237"][target="_blank"][rel="noopener"]'));
    var read=panel&&panel.querySelector('[data-classic-read]'); if(read) read.click();
    check('书卡点击复用站内阅读入口',!!opened&&opened.id==='2237'&&opened.rt==='shamela');
    var fiqh=panel&&panel.querySelector('[data-classic-collection="fiqh"]'); if(fiqh) fiqh.click();
    await pause(450);
    check('学科筛选请求有界',calls.some(function(x){return x.indexOf('collection=fiqh')>=0&&x.indexOf('size=18')>=0}));
    var path=panel&&panel.querySelector('[data-classic-path]'); if(path) path.click();
    await pause(200);
    var input=document.getElementById('homeAIIn');
    check('阅读路径可交给 NOUR AI',!!input&&input.value.indexOf('法学入门')>=0&&input.value.indexOf('不要编造')>=0);
    check('无 JavaScript 错误',errors.length===0,errors.join('\n'));
  }catch(e){errors.push(String(e&&e.stack||e));}
  window.fetch=originalFetch; window.openReadById=originalOpen;
  return JSON.stringify({viewport:[innerWidth,innerHeight],passed:checks.filter(function(x){return x.ok;}).length,total:checks.length,results:checks,errors:errors,calls:calls.slice(-4)});
})();
