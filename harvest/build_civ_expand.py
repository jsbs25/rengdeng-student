#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扩展「伊斯兰文明」条目：按中文维基分类批量抓取。"""
import json, time, urllib.parse, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'data' / 'civ.json'
ZH = 'https://zh.wikipedia.org/w/api.php'
CATS = {
 'dynasties': ['伊斯兰王朝','哈里发国','阿拉伯帝国','穆斯林王朝','伊斯兰教国家','伊斯兰帝国'],
 'scholars': ['伊斯兰教神学家','穆斯林学者','阿拉伯科学家','伊斯兰哲学家','阿拉伯数学家','阿拉伯天文学家',
              '阿拉伯医学家','伊斯兰教法学家','伊斯兰哲学家','阿拉伯语学者','圣训学家','古兰经注家',
              '伊斯兰教史学家','穆斯林科学家'],
 'cities': ['伊斯兰教圣地','阿拉伯城市','伊斯兰教城市','中东古城','奥斯曼帝国城市','伊朗城市','伊拉克城市','叙利亚城市'],
 'events': ['伊斯兰教历史','穆斯林征服','伊斯兰教战争','十字军东征','蒙古帝国战争','伊斯兰教战役','阿拉伯帝国战役'],
}
def get(u):
    for i in range(3):
        try:
            rq=urllib.request.Request(u,headers={'User-Agent':'nur/1.0'})
            with urllib.request.urlopen(rq,timeout=45) as r: return json.loads(r.read().decode())
        except Exception: time.sleep(1+i)
    return {}
def members(cat,limit=120):
    out=[];cont=None
    while len(out)<limit:
        u=ZH+'?action=query&list=categorymembers&cmtitle='+urllib.parse.quote('Category:'+cat)+'&cmnamespace=0&cmlimit=500&format=json'
        if cont: u+='&cmcontinue='+cont
        d=get(u); out+=[m['title'] for m in d.get('query',{}).get('categorymembers',[])]
        cont=d.get('continue',{}).get('cmcontinue')
        if not cont: break
        time.sleep(0.25)
    return out[:limit]
def extracts(titles):
    res={}
    for i in range(0,len(titles),20):
        u=(ZH+'?action=query&prop=extracts|langlinks&explaintext=1&exintro=1&exlimit=20&lllang=ar&redirects=1&format=json&titles='
           +urllib.parse.quote('|'.join(titles[i:i+20])))
        d=get(u)
        for p in d.get('query',{}).get('pages',{}).values():
            t=(p.get('extract') or '').strip()
            if len(t)<80: continue
            ar=''
            for ll in (p.get('langlinks') or []):
                if ll.get('lang')=='ar': ar=ll.get('*') or ''; break
            res[p.get('title')]={'name':p.get('title'),'ar':ar,'text':t[:1500]}
        time.sleep(0.25)
    return res
def main():
    data=json.loads(OUT.read_text(encoding='utf-8')) if OUT.exists() else {}
    for kind,cats in CATS.items():
        have={x['name'] for x in data.get(kind,[])}
        titles=[]
        for c in cats:
            for t in members(c):
                if t not in have and t not in titles: titles.append(t)
        if not titles:
            print(' -',kind,'无新增'); continue
        got=extracts(titles)
        add=[dict(v,kind=kind) for v in got.values()]
        data[kind]=data.get(kind,[])+add
        print(f'  {kind}: +{len(add)}（共 {len(data[kind])}）')
        OUT.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    data['counts']={k:len(v) for k,v in data.items() if isinstance(v,list)}
    OUT.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print('✅',data['counts'])
if __name__=='__main__': main()

