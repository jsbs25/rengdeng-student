/* NOUR focus workspace adapter.
 * Makes a feature click feel like entering a dedicated screen while delegating
 * every business action to the existing nav/openModal/closeModal functions.
 */
(function(){
  'use strict';
  if(window.__NOUR_FOCUS_WORKSPACE__) return;
  window.__NOUR_FOCUS_WORKSPACE__ = true;
  var PAGE_IDS = { 'page-search':'搜索', 'page-me':'我的', 'mCat':'书库', 'aiSec':'NOUR AI' };
  var MODAL_IDS = {
    /* mReader intentionally stays a centered Apple Books window. */
    mDict:1, mGrammar:1, mLearn:1, mWordBook:1, mSentences:1,
    mListen:1, mVocab:1, mFlash:1, mChallenge:1, mAlphabet:1, mQuran:1,
    mHadith:1, mH6:1, mHistory:1, mLibrary:1, mTalk:1, mRead:1,
    mExplain:1, mDialog:1, mPrayer:1, mBelt:1, mMusic:1, mImage:1,
    mAudioLibrary:1
  };
  var UTILITY_IDS = {mTheme:1,mLogin:1,mPay:1,mDonate:1,mInstall:1,mLock:1,mSearch:1};
  function q(s,r){return (r||document).querySelector(s);}
  function qa(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s));}
  function call(name){var a=[].slice.call(arguments,1);try{if(typeof window[name]==='function')return window[name].apply(window,a);}catch(e){} }
  function ensureBack(){
    var b=q('#nourFocusBack');
    if(!b){
      b=document.createElement('button'); b.id='nourFocusBack'; b.type='button'; b.setAttribute('aria-label','返回首页');
      b.innerHTML='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5 8 12l7 7"/><path d="M8 12h12"/></svg><span>返回</span>';
      b.addEventListener('click',function(){
        var r=window.__NOUR_FOCUS_ROUTE__;
        if(r && r.type==='modal'){call('closeModal',r.id);} else {call('nav','home');}
        clearFocus();
      });
      document.body.appendChild(b);
    }
    return b;
  }
  function setFocus(kind,id,label){
    ensureBack();
    window.__NOUR_FOCUS_ROUTE__={type:kind,id:id,label:label||''};
    document.body.classList.add('nour-focus-active');
    document.documentElement.classList.add('nour-focus-active');
    var back=q('#nourFocusBack'); if(back){var s=q('span',back);if(s)s.textContent='返回'+(label?' · '+label:'');}
  }
  function clearFocus(){
    document.body.classList.remove('nour-focus-active');
    document.documentElement.classList.remove('nour-focus-active');
    window.__NOUR_FOCUS_ROUTE__=null;
    var back=q('#nourFocusBack'); if(back) back.style.display='none';
    qa('.nour-focus-page').forEach(function(el){el.classList.remove('nour-focus-page');});
    qa('.nour-focus-modal').forEach(function(el){el.classList.remove('nour-focus-modal');el.removeAttribute('data-focus-kind');});
  }
  function markPage(el){
    if(!el) return;
    var label=PAGE_IDS[el.id]||'工作区';
    el.classList.add('nour-focus-page');
    setFocus('page',el.id,label);
  }
  function markModal(el){
    if(!el) return;
    var label=(q('.m-head b',el)||{}).textContent||'功能';
    el.classList.add('nour-focus-modal');
    if(UTILITY_IDS[el.id]) el.setAttribute('data-focus-kind','utility');
    setFocus('modal',el.id,String(label).trim());
  }
  function observe(){
    if(!window.MutationObserver) return;
    var ob=new MutationObserver(function(){
      var activePage=q('body>.page[aria-hidden="false"],body>.page[style*="display: block"]');
      if(activePage && PAGE_IDS[activePage.id] && !activePage.classList.contains('nour-focus-page')) markPage(activePage);
      var activeModal=q('.modal.show');
      if(activeModal && (MODAL_IDS[activeModal.id]||UTILITY_IDS[activeModal.id])){
        if(MODAL_IDS[activeModal.id]&&!activeModal.classList.contains('nour-focus-modal')) markModal(activeModal);
      }
      if(!activePage && !activeModal && document.body.classList.contains('nour-focus-active')) clearFocus();
    });
    ob.observe(document.body,{subtree:true,childList:true,attributes:true,attributeFilter:['class','style','aria-hidden']});
    window.__NOUR_FOCUS_OBSERVER__=ob;
  }
  function wrap(){
    if(window.__NOUR_FOCUS_WRAPPED__) return;
    window.__NOUR_FOCUS_WRAPPED__=true;
    if(typeof window.nav==='function'){
      var nav0=window.nav;
      window.nav=function(tab){
        var result=nav0.apply(this,arguments);
        setTimeout(function(){
          var id=tab==='learn'?'mCat':tab==='ai'?'aiSec':tab==='search'?'page-search':tab==='me'?'page-me':'page-home';
          var el=document.getElementById(id);
          if(id==='page-home'){clearFocus();return;}
          if(el) markPage(el);
        },0);
        return result;
      };
    }
    if(typeof window.openModal==='function'){
      var open0=window.openModal;
      window.openModal=function(id){
        var result=open0.apply(this,arguments);
        setTimeout(function(){var el=document.getElementById(id);if(el&&MODAL_IDS[id])markModal(el);},0);
        return result;
      };
    }
    if(typeof window.closeModal==='function'){
      var close0=window.closeModal;
      window.closeModal=function(id){
        var result=close0.apply(this,arguments);
        setTimeout(function(){
          var el=document.getElementById(id);
          if(el) el.classList.remove('nour-focus-modal');
          var nextModal=document.querySelector('.modal.show');
          if(nextModal && MODAL_IDS[nextModal.id]) markModal(nextModal);
          else {
            var nextPage=document.querySelector('body>.page[aria-hidden="false"]');
            if(nextPage && PAGE_IDS[nextPage.id]) markPage(nextPage);
            else clearFocus();
          }
        },0);
        return result;
      };
    }
  }
  function boot(){wrap();ensureBack();observe();}
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',boot); else setTimeout(boot,0);
})();
