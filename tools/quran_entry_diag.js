(function(){
  var out={};
  function wait(ms){return new Promise(function(r){setTimeout(r,ms);});}
  return (async function(){
    nav('home'); await wait(1100);
    var k=-1,kk=window.HS_K||[]; for(var i=0;i<kk.length;i++){if(kk[i].k==='quran'){k=i;break;}}
    out.k=k; out.before=(document.getElementById('hsSecTitle')||{}).textContent||'';
    var chips=document.querySelectorAll('#tkSeg .chip'); out.chips=chips.length;
    if(chips[k]) chips[k].click();
    await wait(1000);
    out.after=(document.getElementById('hsSecTitle')||{}).textContent||'';
    out.sub=(document.getElementById('hsSecSub')||{}).textContent||'';
    out.tab=window.HS_TAB; out.books=(document.getElementById('tkBooks')||{}).innerText||'';
    out.err=window.__NUR_ERR||'';
    return JSON.stringify(out);
  })();
})()
