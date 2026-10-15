/* 查词典限额：新用户免费 200 次（一次性）；会员 ¥15/月 不限；永久卡 ¥299 永久不限 */
(function(){
  function ready(){
    if(typeof dictSearch !== 'function') return false;
    if(dictSearch.__dl) return true;
    var orig = dictSearch;
    var fn = async function(){
      var q = ((document.getElementById('dictQ') || {}).value || '').trim();
      var box = document.getElementById('dictBody');
      if(!q){ return orig.apply(this, arguments); }
      try{
        var r = await fetch(API_BASE() + '/api/dict/use?device_id=' + encodeURIComponent(devId()) + '&token=' + encodeURIComponent((typeof webToken === 'function' ? webToken() : '')));
        var d = await r.json();
        if(d && d.ok === false && d.need_support){
          if(box) box.innerHTML = '<div style="padding:26px 18px;text-align:center;background:#fff;border:1.5px solid #d9c98f;border-radius:16px">'
            + '<div style="font-size:17px;font-weight:800;color:#0f5132;margin-bottom:10px">🔒 免费查词 200 次已用完</div>'
            + '<div style="font-size:13.5px;color:#6f7570;line-height:2">'
            +   '开通会员 → <b style="color:#0f5132">¥15 / 月 · 无限查词</b> + AI 老师<br>'
            +   '一次买断 → <b style="color:#7a5f22">¥299 永久卡 · 永久免费 不限额度</b><br><br>'
            +   '加站长微信：<b style="color:#0f5132;font-size:16px;letter-spacing:1px">YsuF0202</b><br>'
            +   '<span style="font-size:12px;color:#a8ada6">说一句「开通会员」或「买永久卡」即可</span>'
            + '</div></div>';
          return;
        }
        if(d && d.vip === true && box && box.innerHTML.indexOf('会员') >= 0){ /* 不限 */ }
      }catch(e){}
      return orig.apply(this, arguments);
    };
    fn.__dl = 1;
    try{ dictSearch = fn; }catch(e){}
    try{ window.dictSearch = fn; }catch(e){}
    return true;
  }
  var n = 0; var t = setInterval(function(){ n++; if(ready() || n > 40) clearInterval(t); }, 150);
})();
