/* ============================================================================
   燃灯同学 · 句子收藏视图 (Favorites v1)
   在个人中心「学习与复习」加「句子收藏」入口，点开显示所有收藏句子。
   读 nur_favorites，纯前端。
   ============================================================================ */
(function () {
  'use strict';
  function q(s) { return document.querySelector(s); }
  function qa(s) { return Array.prototype.slice.call(document.querySelectorAll(s)); }
  function favs() { try { var a = JSON.parse(localStorage.getItem('nur_favorites') || '[]'); return Array.isArray(a) ? a : []; } catch (e) { return []; } }

  function openFav() {
    var modal = q('#mFav');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'mFav';
      modal.className = 'modal';
      modal.innerHTML = '<div class="m-head"><span>⭐</span><b>句子收藏</b><button class="m-close" onclick="closeModal(\'mFav\')">✕</button></div><div class="m-body" id="mFavBody"></div>';
      document.body.appendChild(modal);
    }
    var list = favs();
    var body = q('#mFavBody');
    body.innerHTML = '';
    if (!list.length) {
      var empty = document.createElement('div');
      empty.style.cssText = 'text-align:center;padding:32px;color:#86868B;font-size:13px';
      empty.textContent = '还没有收藏句子，在句子库点 ☆ 即可收藏。';
      body.appendChild(empty);
    } else {
      list.forEach(function (txt) {
        var item = document.createElement('div');
        item.className = 'fav-item';
        var span = document.createElement('span');
        span.className = 'fav-ar';
        span.dir = 'rtl'; span.lang = 'ar';
        span.textContent = txt;
        var speak = document.createElement('button');
        speak.type = 'button'; speak.className = 's-btn'; speak.textContent = '🔊';
        speak.addEventListener('click', function () { try { ap(speak, 0, txt); } catch (e) {} });
        var rm = document.createElement('button');
        rm.type = 'button'; rm.className = 's-btn'; rm.textContent = '★';
        rm.addEventListener('click', function () { try { toggleFavWeb(txt); } catch (e) {} openFav(); });
        item.appendChild(span); item.appendChild(speak); item.appendChild(rm);
        body.appendChild(item);
      });
    }
    if (typeof openModal === 'function') openModal('mFav');
  }

  function addLink() {
    var groups = qa('#page-me .profile-group');
    var target = null;
    groups.forEach(function (g) {
      var h2 = g.querySelector('h2');
      if (h2 && h2.textContent.indexOf('学习') >= 0) target = g;
    });
    if (!target || target.querySelector('[data-fav-link]')) return;
    var btn = document.createElement('button');
    btn.className = 'profile-link';
    btn.setAttribute('data-fav-link', '1');
    btn.innerHTML = '<span>句子收藏</span><b>›</b>';
    btn.addEventListener('click', openFav);
    target.appendChild(btn);
  }

  function boot() { addLink(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
  setTimeout(boot, 1200);
})();
