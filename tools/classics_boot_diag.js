(function(){
  var o={};
  try{o.err=window.__NUR_ERR||'';}catch(e){o.err='errread:'+e;}
  try{o.nav=typeof window.nav;o.tafsir=typeof window.showTafsir;o.voice=typeof window.nourSpeakReply;o.quran=typeof window.showQuran;o.hs=typeof window.hsGo;}catch(e){o.state='state:'+e;}
  try{o.body=(document.body&&document.body.innerText||'').slice(0,180);}catch(e){o.body='body:'+e;}
  return JSON.stringify(o);
})()
