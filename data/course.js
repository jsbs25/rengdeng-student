/* 课程中心：语法课 + 词法课（统一版式） */
function showGrammar(id, tab){ openModal('mGrammar'); renderGrammar(id || 0, tab || 'grammar'); }
function showMorph(id){ openModal('mGrammar'); renderGrammar(id || 0, 'morph'); }

function renderGrammar(id, tab){
  tab = tab || 'grammar';
  var G = window.BUILTIN_GRAMMAR || [];
  var M = window.BUILTIN_MORPH || [];
  var isM = (tab === 'morph');
  var d = isM ? M : G;
  var box = document.getElementById('mGramBody');
  if(!box) return;
  var head = document.getElementById('mGramHead');
  if(head) head.textContent = (isM ? '词法课' : '语法课') + ' · 共 ' + d.length + ' 课';

  var h = '<div class="gtabs">'
    + '<div class="gtab' + (isM ? '' : ' on') + '" id="gtabG">语法课 · ' + G.length + '</div>'
    + '<div class="gtab' + (isM ? ' on' : '') + '" id="gtabM">词法课 · ' + M.length + '</div>'
    + '</div>';

  if(!id){
    h += '<div class="ghint">一课一个主题：先读「要点」，再点 🔊,跟着念一遍。</div>';
    h += d.map(function(x, i){
      var n = (x.points || []).length;
      return '<div class="gcard" data-gid="' + x.id + '">'
        + '<div class="gcard-n">' + (i + 1) + '</div>'
        + '<div class="gcard-b"><b>' + x.title + '</b><span class="gcard-ar">' + (x.title_ar || '') + '</span>'
        + '<div class="gcard-in">' + x.intro + '</div>'
        + '<div class="gcard-m">' + n + ' 个要点 · 逐条发音 · 附记忆口诀</div></div>'
        + '<div class="gcard-arrow">›</div></div>';
    }).join('');
    box.innerHTML = h;
  } else {
    var x = null;
    for(var i = 0; i < d.length; i++){ if(String(d[i].id) === String(id)){ x = d[i]; break; } }
    if(!x){ box.innerHTML = h + '<div class="ghint">没有找到这一课。</div>'; return; }
    if(head) head.textContent = x.title + ' · ' + (x.title_ar || '');
    h += '<div class="gdetail">'
      + '<div class="gtitle"><b>' + x.title + '</b><span class="gcard-ar">' + (x.title_ar || '') + '</span></div>'
      + '<div class="gintro">' + x.intro + '</div>'
      + '<div class="gsec">要点对照</div>'
      + '<table class="gtable">';
    (x.points || []).forEach(function(p){
      h += '<tr><td class="gar">' + p.ar + '</td>'
        + '<td class="gcn">' + p.cn + (p.note ? '<div class="gnote">' + p.note + '</div>' : '') + '</td>'
        + '<td class="gsp"><button class="s-btn gspk" onclick="ap(this,0,&quot;' + p.ar + '&quot;)">🔊</button></td></tr>';
    });
    h += '</table>';
    if(x.tip){ h += '<div class="gsec">记忆要点</div><div class="gtip">💡 ' + x.tip + '</div>'; }
    h += '<div class="gnav"><button class="act-btn gback">‹ 返回课程目录</button></div></div>';
    box.innerHTML = h;
  }
  bindGrammar(tab);
}

function bindGrammar(tab){
  var a = document.getElementById('gtabG'), b = document.getElementById('gtabM');
  if(a) a.onclick = function(){ renderGrammar(0, 'grammar'); };
  if(b) b.onclick = function(){ renderGrammar(0, 'morph'); };
  var back = document.querySelector('.gback');
  if(back) back.onclick = function(){ renderGrammar(0, tab); };
  Array.prototype.forEach.call(document.querySelectorAll('.gcard'), function(c){
    c.onclick = function(){ renderGrammar(c.getAttribute('data-gid'), tab); };
  });
}
