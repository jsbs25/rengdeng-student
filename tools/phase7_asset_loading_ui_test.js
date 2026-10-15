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
