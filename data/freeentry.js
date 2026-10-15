/* 门禁页（无解锁码）：只做"自己维护、请支持"的提醒 + 免费进入 */
(function(){
  function build(){
    var lk = document.getElementById('mLock');
    if(!lk || document.getElementById('freeGoBox')) return;
    var box = document.createElement('div');
    box.id = 'freeGoBox';
    box.style.cssText = 'margin-top:12px;width:100%;max-width:330px;text-align:center';
    box.innerHTML =
        '<div style="background:#fff;border:1px solid #efe6d2;border-radius:16px;padding:16px 16px 14px;margin-bottom:12px">'
      +   '<div style="font-size:15px;font-weight:800;color:#0f5132;margin-bottom:8px">🪔 燃灯同学 · 阿拉伯学习平台</div>'
      +   '<div style="font-size:13px;color:#6f7570;line-height:1.95;text-align:left">'
      +     '本站由站长<b>个人自费维护</b><br>'
      +     '服务器 · 域名 · AI 接口 每月都要花钱<br>'
      +     '免费试用：<b>查词 200 次</b> · 书库 / 句子 / 听力 随便用<br>'
      +     '想无限用：<b>会员 ¥15/月</b> · <b>永久卡 ¥299</b><br>'
      +   '</div>'
      +   '<div style="margin-top:12px;font-size:13px;color:#0f5132;font-weight:700">找站长：YsuF0202</div>'
      +   '<div style="font-size:11.5px;color:#a8ada6;margin-top:4px">加的时候说一句「支持燃灯同学」</div>'
      + '</div>'
      + '<button onclick="freeEnter()" style="width:100%;padding:14px;font-size:15.5px;font-weight:800;color:#fff;background:#0f5132;border:0;border-radius:14px;cursor:pointer">🚪 进入学习（免费）</button>'
      + '<div style="font-size:11.5px;color:#b0b5af;margin-top:8px">不支持下也能进 ✓ 只是希望你能记得它</div>';
    lk.appendChild(box);
    // 清掉旧的门禁按钮（解锁码/我想拥有等）
    Array.prototype.forEach.call(lk.querySelectorAll('button'), function(b){
      var t = (b.textContent || '').trim();
      if(b.parentNode && b.parentNode.id === 'freeGoBox') return;
      if(t.indexOf('进入学习') >= 0) return;
      b.style.display = 'none';
    });
    Array.prototype.forEach.call(lk.querySelectorAll('input'), function(i2){ i2.style.display = 'none'; });
  }
  function freeEnter(){
    try{
      localStorage.setItem('nur_free_enter', String(Date.now()));
      if(typeof unlockApp === 'function') unlockApp();
      var lk = document.getElementById('mLock');
      if(lk) lk.style.display = 'none';
      document.body.classList.remove('locked');
    }catch(e){}
  }
  window.freeEnter = freeEnter;
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function(){ setTimeout(build, 1000); });
  else setTimeout(build, 1000);
  setTimeout(build, 2400); setTimeout(build, 4500);
})();

/* 清掉门禁页上的旧文案（"进入需要解锁码""付费后即可进入"等） */
(function(){
  function fix(){
    var lk = document.getElementById('mLock');
    if(!lk) return;
    // 1) 隐藏含旧关键词的元素（允许有子元素）
    Array.prototype.forEach.call(lk.querySelectorAll('*'), function(e){
      var t = (e.textContent || '').trim();
      if(!t) return;
      if(e.id === 'freeGoBox' || (e.closest && e.closest('#freeGoBox'))) return;
      if(t.indexOf('进入需要解锁码') >= 0 || t.indexOf('付费后即可进入') >= 0 || t.indexOf('付费进入后') >= 0 || t.indexOf('最低 ¥10') >= 0 || t.indexOf('全部内容与') >= 0){
        e.style.display = 'none';
      }
    });
    // 2) 兜底：把 mLock 里所有大字旧标题行藏掉
    Array.prototype.forEach.call(lk.children, function(el){
      if(el.id === 'freeGoBox') return;
      var t = (el.textContent || '').trim();
      if(t.indexOf('🔥') >= 0 || t.indexOf('立即解锁') >= 0){ el.style.display = 'none'; }
    });
  }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function(){ setTimeout(fix, 1200); });
  else setTimeout(fix, 1200);
  setTimeout(fix, 2600); setTimeout(fix, 5000);
})();
