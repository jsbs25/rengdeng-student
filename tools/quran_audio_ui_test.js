return await (async function(){
  var out=[];
  function check(name,ok,detail){out.push({name:name,ok:!!ok,detail:String(detail||'')});}
  function wait(ms){return new Promise(function(r){setTimeout(r,ms);});}
  var errors=[];
  window.addEventListener('error',function(e){errors.push(String(e.message||e.error||'error'));});
  try{
    var q=[];
    for(var i=0;i<40 && q.length<114;i++){
      q=(window.QURAN&&window.QURAN.length>=114)?window.QURAN:((window.BUILTIN_QURAN&&window.BUILTIN_QURAN.length>=114)?window.BUILTIN_QURAN:[]);
      if(q.length<114) await wait(250);
    }
    check('古兰经数据已加载',q.length>=114,q.length);
    var s=q[0];
    if(s && typeof window.openSurah==='function') window.openSurah(s);
    await wait(120);
    var reader=document.getElementById('mReader');
    check('古兰经阅读器已打开',!!reader&&getComputedStyle(reader).display!=='none',reader&&getComputedStyle(reader).display);
    check('真人诵读控制栏已显示',!!document.getElementById('rdQuranPlayBtn')&&!!document.getElementById('rdQuranRange'));
    check('逐节内容已渲染',document.querySelectorAll('.rd-qayah').length>=5,document.querySelectorAll('.rd-qayah').length);
    var initialUrl=typeof window.rdQuranAudioUrl==='function'?window.rdQuranAudioUrl(0):'';
    check('音频地址使用已验证来源',initialUrl.indexOf('everyayah.com/data/')>=0&&initialUrl.indexOf('001001.mp3')>=0,initialUrl);

    var RealAudio=window.Audio;
    function FakeAudio(){this.src='';this.paused=true;this.duration=10;this.currentTime=0;this.playbackRate=1;this._row=-1;this.readyState=4;}
    FakeAudio.prototype.load=function(){};
    FakeAudio.prototype.play=function(){this.paused=false;if(this.onloadedmetadata)this.onloadedmetadata();if(this.onplay)this.onplay();return Promise.resolve();};
    FakeAudio.prototype.pause=function(){this.paused=true;if(this.onpause)this.onpause();};
    FakeAudio.prototype.removeAttribute=function(n){if(n==='src')this.src='';};
    window.Audio=FakeAudio;

    window.rdQuranLoadRow(0,true);
    await wait(30);
    var audio=window.RD_QAUDIO;
    check('首节音频加载',!!audio&&audio.src.indexOf('/api/recite?u=')>=0&&audio.src.indexOf('everyayah.com')>=0,audio&&audio.src);
    check('播放时首节高亮',document.querySelector('.rd-qayah.is-playing[data-qrow="0"]')!==null);
    check('播放状态可见',(document.getElementById('rdQuranStatus')||{}).textContent.indexOf('正在诵读')>=0,(document.getElementById('rdQuranStatus')||{}).textContent);
    window.rdQuranSetRate(1.25);
    check('倍速已生效',audio.playbackRate===1.25,audio.playbackRate);
    window.rdQuranScrub(500);
    check('进度拖动已生效',audio.currentTime===5,audio.currentTime);

    window.rdQuranNext(); await wait(20); audio=window.RD_QAUDIO;
    check('下一节切换',audio&&audio._row===1&&audio.src.indexOf('001002.mp3')>=0,audio&&audio.src);
    check('下一节高亮',document.querySelector('.rd-qayah.is-playing[data-qrow="1"]')!==null);
    window.rdQuranPrev(); await wait(20); audio=window.RD_QAUDIO;
    check('上一节切换',audio&&audio._row===0&&audio.src.indexOf('001001.mp3')>=0,audio&&audio.src);

    window.rdQuranSetAuto(true); audio.onended(); await wait(20); audio=window.RD_QAUDIO;
    check('自动下一节',audio&&audio._row===1,audio&&audio._row);
    window.rdQuranSetAuto(false); window.rdQuranLoadRow(0,true); await wait(20); audio=window.RD_QAUDIO; audio.onended(); await wait(20);
    check('关闭自动下一节后不跳节',audio&&audio._row===0,audio&&audio._row);

    window.rdQuranLoadRow(0,true); await wait(20); audio=window.RD_QAUDIO;
    window.rdQuranToggle();
    check('暂停按钮可用',audio.paused&&((document.getElementById('rdQuranPlayBtn')||{}).textContent||'').indexOf('继续')>=0,(document.getElementById('rdQuranPlayBtn')||{}).textContent);
    window.rdQuranToggle();
    check('继续按钮可用',!audio.paused,audio.paused);
    window.rdQuranStop();
    check('停止后清除高亮',!document.querySelector('.rd-qayah.is-playing')&&!window.RD_QAUDIO);

    window.rdQuranLoadRow(0,true); await wait(20); audio=window.RD_QAUDIO;
    if(typeof window.nav==='function') window.nav('home');
    await wait(30);
    check('退出阅读器后停止音频',audio.paused&&!window.RD_QAUDIO,!!window.RD_QAUDIO);
    check('退出阅读器后无残留阅读层',!document.body.classList.contains('reading')&&(!reader||!reader.classList.contains('show')));
    window.Audio=RealAudio;
  }catch(e){check('专项脚本无异常',false,e&&e.stack||e);}
  check('无运行时错误',errors.length===0,errors.join(' | '));
  return JSON.stringify(out);
})();
