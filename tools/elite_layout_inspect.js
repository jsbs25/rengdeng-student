(function(){
  var ids=['page-home','nourMission','quote','studyProgress','nourFocusToggle','nourPaletteOpen'];
  var out={}; ids.forEach(function(id){var e=document.getElementById(id); if(!e){out[id]=null;return;} var r=e.getBoundingClientRect(),s=getComputedStyle(e);out[id]={display:s.display,opacity:s.opacity,order:s.order,rect:{x:r.x,y:r.y,w:r.width,h:r.height},parent:e.parentElement&&e.parentElement.id};});
  return JSON.stringify(out);
})();
