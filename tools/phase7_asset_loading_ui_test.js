return await (async function(){
  const out = {checks:[], errors:[]};
  const pause = ms => new Promise(r => setTimeout(r, ms));
  const check = (name, ok, detail) => out.checks.push({name, ok:!!ok, detail:detail || null});
  await pause(1100);
  const names = () => performance.getEntriesByType('resource').map(x => x.name);
  const initial = names();
  const initialData = initial.filter(x => /data\/builtin_(sentences|books|quran|hadith|vocab|history)\.js(?:\?|$)/.test(x));
  check('lazy-loader-present', typeof window.NOUR_loadDataAsset === 'function', {version:window.NOUR_ASSET_VERSION || ''});
  check('no-large-data-requested-on-initial-page', initialData.length === 0, {resources:initialData});
  check('sentence-global-empty-before-use', !((window.BUILTIN_SENTENCES || []).length), {length:(window.BUILTIN_SENTENCES || []).length});
  check('books-global-empty-before-use', !((window.BUILTIN_BOOKS || []).length), {length:(window.BUILTIN_BOOKS || []).length});
  check('quran-global-empty-before-use', !((window.BUILTIN_QURAN || []).length), {length:(window.BUILTIN_QURAN || []).length});
  check('hadith-global-empty-before-use', !((window.BUILTIN_HADITH || []).length), {length:(window.BUILTIN_HADITH || []).length});
  check('vocab-global-empty-before-use', !((window.BUILTIN_VOCAB || []).length), {length:(window.BUILTIN_VOCAB || []).length});
  check('history-global-empty-before-use', !((window.BUILTIN_HISTORY || []).length), {length:(window.BUILTIN_HISTORY || []).length});

  async function loadAndCheck(kind, fnName, globalName, minLength){
    try{
      if(typeof window[fnName] !== 'function') throw new Error(fnName + ' missing');
      await window[fnName]();
      await pause(300);
      const resources = names().filter(x => new RegExp('builtin_' + kind + '\\.js(?:\\?|$)').test(x));
      const arr = window[globalName] || [];
      check(kind + '-requested-on-entry', resources.length >= 1, {resources:resources});
      check(kind + '-request-is-versioned', resources.some(x => /\?v=/.test(x)), {resources:resources});
      check(kind + '-data-loaded', arr.length >= minLength, {length:arr.length});
      if(kind === 'sentences'){
        const visible = document.querySelectorAll('#mSentBody .s-item').length;
        check('sentences-visible-dom-is-bounded', visible <= 80, {visible, total:arr.length});
        const more = document.querySelector('#mSentBody .s-more');
        check('sentences-has-load-more', arr.length <= 80 || !!more, {visible, total:arr.length});
        if(more){
          more.click(); await pause(80);
          check('sentences-load-more-renders-next-page', document.querySelectorAll('#mSentBody .s-item').length > visible, {before:visible, after:document.querySelectorAll('#mSentBody .s-item').length});
        }
        const needle = String(arr[arr.length - 1] && arr[arr.length - 1].a || '').slice(0, 8).toLowerCase();
        if(needle){
          const q = document.getElementById('mSentSearch'); q.value = needle; q.dispatchEvent(new Event('input', {bubbles:true})); await pause(30);
          check('sentences-search-scans-full-array', document.querySelectorAll('#mSentBody .s-item').length >= 1, {needle, visible:document.querySelectorAll('#mSentBody .s-item').length});
          q.value = ''; q.dispatchEvent(new Event('input', {bubbles:true}));
        }
      }
      return resources.length;
    }catch(e){ out.errors.push(kind + ': ' + String(e && e.stack || e)); return 0; }
  }

  await loadAndCheck('sentences','showAllSentences','BUILTIN_SENTENCES',1000);
  await loadAndCheck('books','showBooks','BUILTIN_BOOKS',1);
  await loadAndCheck('quran','showQuran','BUILTIN_QURAN',100);
  await loadAndCheck('hadith','showHadith','BUILTIN_HADITH',1);
  await loadAndCheck('vocab','showVocab','BUILTIN_VOCAB',100);
  await loadAndCheck('history','showHistory','BUILTIN_HISTORY',0);

  const beforeRepeat = names().filter(x => /builtin_(sentences|books|quran|hadith|vocab|history)\.js/.test(x));
  await window.showQuran();
  await window.showVocab();
  await window.showAllSentences();
  await pause(100);
  const afterRepeat = names().filter(x => /builtin_(sentences|books|quran|hadith|vocab|history)\.js/.test(x));
  check('loader-reuses-promises-for-loaded-assets', afterRepeat.length === beforeRepeat.length, {before:beforeRepeat.length, after:afterRepeat.length});
  return out;
})();
