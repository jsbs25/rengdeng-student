/* 门禁页：点"我想拥有这款学习平台" → 显示站长微信号 */
var OWNER_WECHAT = 'YsuF0202';   /* ← 站长微信号，告诉我我改这里 */
window.__OWNER_WX__ = window.__OWNER_WX__ || '';

function lockContact(){
  try{
    var id = window.__OWNER_WX__ || OWNER_WECHAT;
    var box = document.getElementById('lockContactBox');
    if(!box){
      box = document.createElement('div');
      box.id = 'lockContactBox';
      box.style.cssText = 'margin-top:14px;width:100%;max-width:320px;background:#fff;border:1px solid #efe6d2;border-radius:16px;padding:16px;text-align:center';
      var host = document.getElementById('mLock');
      if(host) host.appendChild(box);
    }
    box.innerHTML = '<div style="font-size:13px;color:#8a8f88;margin-bottom:8px">加站长微信，开通学习平台 👇</div>'
      + '<div id="lockWxId" style="font-size:20px;font-weight:800;color:#0f5132;letter-spacing:.5px;word-break:break-all">' + id + '</div>'
      + '<button onclick="lockCopyWx()" style="margin-top:12px;padding:11px 20px;font-size:14px;font-weight:700;color:#fff;background:#0f5132;border:0;border-radius:12px;cursor:pointer">📋 复制微信号</button>'
      + '<div style="margin-top:10px;font-size:12px;color:#a8ada6;line-height:1.7">加的时候说一句「开通学习平台」<br>站长看到会马上帮你开通</div>';
    try{ box.scrollIntoView({behavior:'smooth', block:'center'}); }catch(e){}
  }catch(e){}
}
function lockCopyWx(){
  try{
    var id = window.__OWNER_WX__ || OWNER_WECHAT;
    var b = (typeof event !== 'undefined' && event && event.target) ? event.target : null;
    navigator.clipboard.writeText(id).then(function(){ if(b) b.textContent = '✓ 已复制'; }).catch(function(){ if(b) b.textContent = id; });
  }catch(e){}
}
