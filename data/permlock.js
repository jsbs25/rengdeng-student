/* 门禁页最上面：永久解锁码输入框（¥299 永久 · 不限额度） */
(function(){
  function build(){
    var lk = document.getElementById('mLock');
    if(!lk || document.getElementById('permBox')) return;
    var box = document.createElement('div');
    box.id = 'permBox';
    box.style.cssText = 'width:100%;max-width:330px;margin-bottom:14px';
    box.innerHTML =
        '<div style="background:#fff;border:1.5px solid #d9c98f;border-radius:16px;padding:14px">'
      +   '<div style="font-size:13px;font-weight:800;color:#7a5f22">🔑 永久解锁码（¥299 · 永久免费 · 不限额度）</div>'
      + '<div style="font-size:12px;color:#a08a4a;margin:5px 0 9px">👉 需要联系站长购买 · 微信：<b style="color:#0f5132">YsuF0202</b>（说一句「买永久卡」）</div>'
      +   '<div style="display:flex;gap:8px">'
      +     '<input id="permCodeIn" placeholder="输入解锁码" autocomplete="off" style="flex:1;padding:12px 12px;font-size:15px;letter-spacing:2px;text-align:center;border:1.5px solid #e5decc;border-radius:11px;background:#fff;text-transform:uppercase">'
      +     '<button onclick="doPermUnlock()" style="padding:12px 16px;font-size:14.5px;font-weight:800;color:#fff;background:#7a5f22;border:0;border-radius:11px;cursor:pointer;white-space:nowrap">解锁</button>'
      +   '</div>'
      +   '<div id="permMsg" style="margin-top:7px;font-size:12.5px;min-height:16px;color:#8a8f88"></div>'
      + '</div>';
    lk.insertBefore(box, lk.firstChild);
    var el = document.getElementById('permCodeIn');
    if(el) el.addEventListener('keydown', function(e){ if(e.key === 'Enter') doPermUnlock(); });
  }
  function doPermUnlock(){
    var el = document.getElementById('permCodeIn');
    var m = document.getElementById('permMsg');
    var c = ((el && el.value) || '').trim().toUpperCase().replace(/[^A-Z0-9]/g, '');
    if(c.length === 12) c = c.slice(0,4) + '-' + c.slice(4,8) + '-' + c.slice(8);
    if(!c){ if(m){ m.style.color = '#b4553a'; m.textContent = '请输入解锁码'; } return; }
    if(m){ m.style.color = '#5a6159'; m.textContent = '验证中…'; }
    fetch(API_BASE() + '/api/vip/activate', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({code: c, device_id: devId()})})
      .then(function(r){ return r.json(); })
      .then(function(d){
        if(d && d.ok){
          if(m){ m.style.color = '#0f5132'; m.textContent = '✅ ' + (d.msg || '解锁成功，永久有效'); }
          try{ localStorage.setItem('nur_perm', '1'); }catch(e){}
          setTimeout(function(){ try{ if(typeof unlockApp === 'function') unlockApp(); }catch(e){} var l = document.getElementById('mLock'); if(l) l.style.display = 'none'; document.body.classList.remove('locked'); }, 700);
        }else{
          if(m){ m.style.color = '#b4553a'; m.textContent = '❌ ' + ((d && d.msg) || '解锁码无效'); }
        }
      })
      .catch(function(){ if(m){ m.style.color = '#b4553a'; m.textContent = '⚠️ 网络错误，请重试'; } });
  }
  window.doPermUnlock = doPermUnlock;
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function(){ setTimeout(build, 1000); });
  else setTimeout(build, 1000);
  setTimeout(build, 2300); setTimeout(build, 4400);
})();

/* 首页：解锁码框放在「支持燃灯同学」下面、「学阿拉伯语」上面 */
(function(){
  function homeBox(){
    try{
      if(document.getElementById('permBoxHome')) return true;
      var home = document.getElementById('page-home');
      if(!home) return false;
      var sup = document.getElementById('hsSupTop') || document.querySelector('.sup-card');
      var hero = document.querySelector('.tk-hero');
      var box = document.createElement('div');
      box.id = 'permBoxHome';
      box.style.cssText = 'max-width:1100px;margin:12px auto 4px;padding:0 18px';
      box.innerHTML =
          '<div style="background:#fff;border:1.5px solid #d9c98f;border-radius:16px;padding:14px;display:flex;gap:10px;align-items:center;flex-wrap:wrap">'
        +   '<div style="flex:1;min-width:180px">'
        +   '<div style="font-size:13px;font-weight:800;color:#7a5f22">🔑 永久解锁码（¥299 · 永久免费 · 不限额度）</div>'
        +   '<div style="font-size:12px;color:#a08a4a;margin-top:4px">👉 需要联系站长购买 · 微信：<b style="color:#0f5132">YsuF0202</b>（说一句「买永久卡」）</div>'
        +   '</div>'
        +   '<input id="permCodeHome" placeholder="输入解锁码" autocomplete="off" style="flex:0 0 190px;padding:12px;font-size:15px;letter-spacing:2px;text-align:center;border:1.5px solid #e5decc;border-radius:11px;text-transform:uppercase">'
        +   '<button onclick="doPermHome()" style="padding:12px 18px;font-size:14.5px;font-weight:800;color:#fff;background:#7a5f22;border:0;border-radius:11px;cursor:pointer">解锁</button>'
        +   '<div id="permMsgHome" style="flex:1 0 100%;font-size:12.5px;color:#8a8f88"></div>'
        + '</div>';
      if(sup && sup.parentNode){ sup.parentNode.insertBefore(box, sup.nextSibling); }
      else if(hero && hero.parentNode){ hero.parentNode.insertBefore(box, hero); }
      else { home.insertBefore(box, home.firstChild); }
      var el = document.getElementById('permCodeHome');
      if(el) el.addEventListener('keydown', function(e){ if(e.key === 'Enter') doPermHome(); });
      return true;
    }catch(e){ return false; }
  }
  function doPermHome(){
    var el = document.getElementById('permCodeHome');
    var m = document.getElementById('permMsgHome');
    var c = ((el && el.value) || '').trim().toUpperCase().replace(/[^A-Z0-9]/g, '');
    if(c.length === 12) c = c.slice(0,4) + '-' + c.slice(4,8) + '-' + c.slice(8);
    if(!c){ if(m){ m.style.color='#b4553a'; m.textContent='请输入解锁码'; } return; }
    if(m){ m.style.color='#5a6159'; m.textContent='验证中…'; }
    fetch(API_BASE() + '/api/vip/activate', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({code: c, device_id: devId()})})
      .then(function(r){ return r.json(); })
      .then(function(d){
        if(d && d.ok){ if(m){ m.style.color='#0f5132'; m.textContent='✅ ' + (d.msg || '解锁成功'); } try{ localStorage.setItem('nur_perm','1'); }catch(e){} }
        else { if(m){ m.style.color='#b4553a'; m.textContent='❌ ' + ((d && d.msg) || '解锁码无效'); } }
      })
      .catch(function(){ if(m){ m.style.color='#b4553a'; m.textContent='⚠️ 网络错误'; } });
  }
  window.doPermHome = doPermHome;
  var n = 0; var t = setInterval(function(){ n++; if(homeBox() || n > 40) clearInterval(t); }, 200);
  setTimeout(homeBox, 1500); setTimeout(homeBox, 3500);
})();
