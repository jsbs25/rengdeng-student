return await (async function(){
  var out=[], errors=[];
  function check(name,ok,detail){out.push({name:name,ok:!!ok,detail:String(detail||'')});}
  function wait(ms){return new Promise(function(r){setTimeout(r,ms);});}
  window.addEventListener('error',function(e){errors.push(String(e.message||e.error||'error'));});
  try{
    check('音频资料库入口存在',typeof window.showAudioLibrary==='function',typeof window.showAudioLibrary);
    window.showAudioLibrary(); await wait(250);
    var modal=document.getElementById('mAudioLibrary');
    check('音频资料库全屏打开',!!modal&&modal.classList.contains('show'),modal&&getComputedStyle(modal).display);
    var r=await fetch((typeof window.API_BASE==='function'?window.API_BASE():'')+'/api/audio/library?limit=240');
    var d=await r.json();
    check('音频目录接口成功',r.ok&&!!d&&!d.error,d&&d.error);
    check('音频文件已列出',Array.isArray(d&&d.items)&&d.items.length>0,d&&d.items&&d.items.length);
    check('目录声明支持 FLAC',!!(d&&d.supported_formats&&d.supported_formats.indexOf('flac')>=0),(d&&d.supported_formats)||'');
    check('目录包含宣礼音频',!!(d&&d.items&&d.items.some(function(x){return x.category==='宣礼与礼拜'})),'');
    check('目录包含应用生成音频',!!(d&&d.items&&d.items.some(function(x){return x.category==='AI 生成与语音'})),'');
    check('页面播放器已挂载',document.querySelectorAll('.audio-library-player').length>0,document.querySelectorAll('.audio-library-player').length);
    var search=document.getElementById('audioLibrarySearch');
    check('音频搜索框可用',!!search,'');
    check('本机音频导入控件可用',!!document.getElementById('audioLibraryImport'),'');
    if(search){search.value='m4a';search.dispatchEvent(new Event('input',{bubbles:true}));await wait(30);check('格式搜索可过滤',document.querySelectorAll('.audio-library-card').length>=1,document.querySelectorAll('.audio-library-card').length);}
    var flac=Array.isArray(d&&d.items)&&d.items.find(function(x){return String(x.ext).toLowerCase()==='flac';});
    check('FLAC 条目使用应用内文件接口',!flac||String(flac.url).indexOf('/api/audio/file?')>=0,flac&&flac.url||'当前无 FLAC 文件但接口已支持');
    var p=document.querySelector('.audio-library-player');
    if(p){p.dispatchEvent(new Event('play'));check('播放器为原生 audio 控件',p.tagName==='AUDIO',p.tagName);}
    window.closeAudioLibrary(); await wait(30);
    check('关闭后无音频资料库残留层',!modal.classList.contains('show'),modal.className);
  }catch(e){check('专项脚本无异常',false,e&&e.stack||e);}
  check('无运行时错误',errors.length===0,errors.join(' | '));
  return JSON.stringify(out);
})();
