return await (async function(){
  var books=[
    {id:'4404',label:'الهداية في شرح بداية المبتدي',category:'14__الفقه-الحنفي'},
    {id:'1852',label:'المبسوط للسرخسي',category:'14__الفقه-الحنفي'},
    {id:'407',label:'البناية شرح الهداية',category:'14__الفقه-الحنفي'}
  ];
  var results=[],errors=[],fetchLog=[];
  function pause(ms){return new Promise(function(r){setTimeout(r,ms);});}
  var originalFetch=window.fetch;
  window.fetch=function(input,init){
    var u=String(typeof input==='string'?input:(input&&input.url)||'');
    var t=Date.now();
    return originalFetch.apply(window,arguments).then(function(r){
      if(u.indexOf('/api/read')>=0) fetchLog.push({url:u,ms:Date.now()-t,status:r.status});
      return r;
    }).catch(function(e){
      if(u.indexOf('/api/read')>=0) fetchLog.push({url:u,ms:Date.now()-t,status:'error',error:String(e)});
      throw e;
    });
  };
  window.addEventListener('error',function(e){errors.push(String(e.message||e.error||e));});
  try{
    await pause(900);
    nav('learn');
    await pause(800);
    for(var i=0;i<books.length;i++){
      var b=books[i], beforeFetch=fetchLog.length, started=Date.now();
      await openReadById(b.id,'shamela');
      await pause(140);
      var pages=window.RD_PAGES||[], total=pages.length;
      var title=(document.getElementById('mReaderTitle')||{}).textContent||'';
      var first=String(pages[0]||'').trim();
      var last=String(pages[total-1]||'').trim();
      var targets=total?[0,Math.floor((total-1)/2),total-1].filter(function(x,j,a){return a.indexOf(x)===j;}):[];
      var switches=[];
      for(var j=0;j<targets.length;j++){
        var p=targets[j],st=Date.now();
        rdJumpTo(p);
        await pause(65);
        switches.push({page:p+1,ms:Date.now()-st,rendered_page:Number(window.RD_PAGE||0)+1,chars:String((window.RD_PAGES||[])[p]||'').trim().length});
      }
      var got=fetchLog.slice(beforeFetch);
      results.push({id:b.id,label:b.label,title:title,total_pages:total,open_ms:Date.now()-started,api_fetches:got,first_chars:first.length,last_chars:last.length,switches:switches,category:b.category,ok:total>0&&first.length>0&&last.length>0&&(!switches.length||switches[switches.length-1].rendered_page===total)});
      await pause(180);
    }
    return JSON.stringify({viewport:[innerWidth,innerHeight],results:results,errors:errors,ok:results.every(function(x){return x.ok;})&&errors.length===0});
  }catch(e){errors.push(String(e&&e.stack||e));return JSON.stringify({viewport:[innerWidth,innerHeight],results:results,errors:errors,ok:false});}
})();
