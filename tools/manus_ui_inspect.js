(function(){
  function desc(el){if(!el)return null;var s=getComputedStyle(el),r=el.getBoundingClientRect();return {id:el.id,cls:el.className,parent:el.parentElement&&el.parentElement.id,display:s.display,position:s.position,width:Math.round(r.width),height:Math.round(r.height),x:Math.round(r.x),y:Math.round(r.y),z:s.zIndex,transform:s.transform,maxWidth:s.maxWidth};}
  var out={title:document.title,build:window.__NUR_BUILD,error:window.__NUR_ERR,viewport:[innerWidth,innerHeight],nav:typeof nav==='function'?nav.toString():'missing',api:typeof API_BASE==='function'?API_BASE():'missing',screens:[]};
  ['home','learn','listen','me'].forEach(function(tab){try{nav(tab);out.screens.push({tab:tab,bodyClass:document.body.className,pages:Array.from(document.querySelectorAll('.page')).map(desc),overlays:Array.from(document.querySelectorAll('.modal,.ov,.overlay,.m-overlay,[role="dialog"]')).filter(function(e){return getComputedStyle(e).display!=='none';}).map(desc)});}catch(e){out.screens.push({tab:tab,error:String(e)});}});
  nav('home'); return JSON.stringify(out);
})();
