return await (async function(){
  const out={initial:{q:typeof window.QURAN,bq:typeof window.BUILTIN_QURAN,qLen:(window.QURAN||[]).length,bLen:(window.BUILTIN_QURAN||[]).length,err:window.__NUR_ERR||''},scripts:Array.from(document.scripts).filter(s=>String(s.src).indexOf('builtin_quran')>=0).map(s=>({src:s.src,defer:s.defer,async:s.async,ready:s.readyState||''}))};
  try{const r=await fetch('data/builtin_quran.js');const t=await r.text();out.fetch={status:r.status,bytes:t.length,head:t.slice(0,40)};try{(0,eval)(t);out.afterEval={bq:typeof window.BUILTIN_QURAN,bLen:(window.BUILTIN_QURAN||[]).length};}catch(e){out.evalError=String(e);}}catch(e){out.fetchError=String(e);}
  return JSON.stringify(out);
})();
