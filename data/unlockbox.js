/* 门禁页：解锁码输入框（在"我想拥有这款学习平台"下面） */
(function(){
  function build(){
    var lk = document.getElementById('mLock');
    if(!lk || document.getElementById('unlockBox')) return;
    var box = document.createElement('div');
    box.id = 'unlockBox';
    box.style.cssText = 'margin-top:16px;width:100%;max-width:320px;border-top:1px dashed #e5decc;padding-top:14px';
    box.innerHTML = '<div style="font-size:13px;color:#8a8f88;margin-bottom:8px">已拿到解锁码？在这里输入 👇</div>'
      + '<div style="display:flex;gap:8px">'
      + '<input id="unlockCodeIn" placeholder="输入解锁码" autocomplete="off" style="flex:1;padding:13px 14px;font-size:16px;letter-spacing:2px;text-align:center;border:1.5px solid #e5decc;border-radius:12px;background:#fff;text-transform:uppercase">'
      + '<button onclick="doUnlockClick()" style="padding:13px 18px;font-size:15px;font-weight:800;color:#fff;background:#0f5132;border:0;border-radius:12px;cursor:pointer;white-space:nowrap">解锁</button>'
      + '</div>'
      + '<div id="unlockMsg" style="margin-top:8px;font-size:12.5px;min-height:18px;color:#8a8f88"></div>';
    lk.appendChild(box);
    var el = document.getElementById('unlockCodeIn');
    if(el) el.addEventListener('keydown', function(e){ if(e.key === 'Enter') doUnlockClick(); });
  }
  function doUnlockClick(){
    var el = document.getElementById('unlockCodeIn');
    var m = document.getElementById('unlockMsg');
    var c = (el && el.value || '').trim().toUpperCase().replace(/[^A-Z0-9]/g, '');
    if(c.length === 12) c = c.slice(0,4) + '-' + c.slice(4,8) + '-' + c.slice(8);
    if(!c){ if(m){ m.style.color = '#b4553a'; m.textContent = '请输入解锁码'; } return; }
    if(m){ m.style.color = '#5a6159'; m.textContent = '验证中…'; }
    fetch(API_BASE() + '/api/vip/activate', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({code: c, device_id: devId()})})
      .then(function(r){ return r.json(); })
      .then(function(d){
        if(d && d.ok){
          if(d.token){ try{ localStorage.setItem('nur_token', d.token); }catch(e){} }
          if(m){ m.style.color = '#0f5132'; m.textContent = '✅ ' + (d.msg || '解锁成功'); }
          setTimeout(function(){ try{ unlockApp(); }catch(e){} }, 600);
        }else{
          if(m){ m.style.color = '#b4553a'; m.textContent = '❌ ' + ((d && d.msg) || '解锁码无效'); }
        }
      })
      .catch(function(){ if(m){ m.style.color = '#b4553a'; m.textContent = '⚠️ 网络错误，请重试'; } });
  }
  window.doUnlockClick = doUnlockClick;
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function(){ setTimeout(build, 900); });
  else setTimeout(build, 900);
  setTimeout(build, 2000);
  setTimeout(build, 4000);
})();

/* 清理门禁页上的历史遗留按钮（只留：标题 + 我想拥有 + 解锁码输入）*/
(function(){
  var KEEP_HINT = ['我想拥有这款学习平台', '输入解锁码', '解锁', '进入需要解锁码', '燃灯同学', '设备码', '复制设备码'];
  function clean(){
    var lk = document.getElementById('mLock');
    if(!lk) return;
    Array.prototype.forEach.call(lk.querySelectorAll('button, input[type=button], a, .chip, .cat-tab'), function(el){
      var t = (el.textContent || el.placeholder || '').trim();
      if(el.id === 'unlockCodeIn' || el.id === 'lockWxId') return;
      if(KEEP_HINT.some(function(k){ return t.indexOf(k) >= 0; })) return;
      el.style.display = 'none';
    });
    // 隐藏二维码/收款图
    Array.prototype.forEach.call(lk.querySelectorAll('img'), function(im){
      im.style.display = 'none';
    });
  }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function(){ setTimeout(clean, 1000); });
  else setTimeout(clean, 1000);
  setTimeout(clean, 2500);
  setTimeout(clean, 5000);
})();
