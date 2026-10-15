/* 一带一路 · 中阿合作（数据来自服务器每小时爬虫：data/beltroad.json） */
function showBelt(){
  openModal('mBelt');
  var box = document.getElementById('mBeltBody');
  if(!box) return;
  box.innerHTML = '<div style="padding:30px;text-align:center;color:#8a8f88;font-size:13px">正在读取最新数据…</div>';
  fetch(API_BASE() + '/data/beltroad.json?t=' + Date.now())
    .then(function(r){ return r.json(); })
    .then(function(d){ beltRender(d); })
    .catch(function(){ box.innerHTML = '<div style="padding:30px;text-align:center;color:#b4553a;font-size:13px">数据读取失败，请稍后重试</div>'; });
}

function beltRender(d){
  var box = document.getElementById('mBeltBody');
  if(!box) return;
  var items = (d && d.items) || [];
  var h = '<div class="belt-head">'
    + '<div class="belt-ttl">中阿合作 · 实时资讯</div>'
    + '<div class="belt-sub">共 ' + items.length + ' 条 · 更新于 ' + ((d && d.updated) || '—') + ' · 每小时自动更新</div>'
    + '</div>';
  if(!items.length){
    h += '<div style="padding:26px;text-align:center;color:#8a8f88;font-size:13px">暂无数据（服务器正在抓取）</div>';
    box.innerHTML = h; return;
  }
  h += items.map(function(x, i){
    var ar = x.ar ? '<div class="belt-ar" dir="rtl">' + x.ar + '</div>' : '';
    var link = x.link ? '<a class="belt-link" href="' + x.link + '" target="_blank" rel="noopener noreferrer">原文 ›</a>' : '';
    return '<div class="belt-card">'
      + '<div class="belt-n">' + (i + 1) + '</div>'
      + '<div class="belt-b">'
      + '<div class="belt-cn">' + x.title + '</div>'
      + ar
      + '<div class="belt-meta">' + (x.source || '') + (x.pub ? (' · ' + x.pub) : '') + ' ' + link + '</div>'
      + '</div></div>';
  }).join('');
  box.innerHTML = h;
}
