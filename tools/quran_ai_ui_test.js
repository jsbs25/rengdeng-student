return await (async function(){
  var out={errors:[],states:[],analysis:null};
  function pause(ms){return new Promise(function(r){setTimeout(r,ms);});}
  window.addEventListener('error',function(e){out.errors.push(String(e.message||e.error||e));});
  function state(label){
    var panel=document.querySelector('.rd-page-analysis');
    var body=document.getElementById('mReaderBody');
    out.states.push({label:label,readerVisible:!!document.getElementById('mReader')&&getComputedStyle(document.getElementById('mReader')).display!=='none',title:(document.getElementById('mReaderTitle')||{}).textContent||'',pages:(window.RD_PAGES||[]).length,bookMeta:!!window.RD_BOOK_META,audioKind:window.RD_AUDIO&&window.RD_AUDIO.kind||'',analysisVisible:!!panel,analysisText:panel?String(panel.textContent||'').slice(0,240):'',bodyText:body?String(body.textContent||'').slice(0,240):''});
  }
  try{
    showQuran(); await pause(450); state('quran-list');
    var first=document.querySelector('#mQuranBody .s-item'); out.firstSurah=!!first;
    if(first) first.click(); await pause(1000); state('surah-open');
    var panel=document.querySelector('.rd-page-analysis'); out.analysisPanel=!!panel;
    if(typeof window.nurSetAnalysisLanguage==='function') window.nurSetAnalysisLanguage('ar');
    if(typeof window.nurSetFiqhSchool==='function') window.nurSetFiqhSchool('hanafi');
    await pause(250); state('arabic-hanafi-selected');
    var run=document.querySelector('.rd-page-analysis__run'); out.runButton=!!run;
    if(run) run.click();
    await pause(22000); state('analysis-finished-or-timeout');
    var p=document.querySelector('.rd-page-analysis'); out.analysis=p?String(p.textContent||'').slice(0,900):'';
  }catch(e){out.errors.push(String(e&&e.stack||e));}
  return out;
})();
