#!/bin/bash
# 0 点爬虫巡检 + 自动重建（一次性后台任务）
sleep 3600  # 等到 ~00:20（从 23:20 开始）
cd /Users/mafucheng/Desktop/arabic-learning

echo "=== $(date +%H:%M:%S) 0 点巡检 ==="
python3 -c "
import json, os, time
p = 'data/categorized.json'
print('categorized 更新:', time.strftime('%H:%M:%S', time.localtime(os.path.getmtime(p))))
d = json.load(open(p, encoding='utf-8'))
missing = sum(1 for it in d if not it.get('en','').strip() or not it.get('cn','').strip())
from collections import Counter
c = Counter(it.get('cat','other') for it in d)
jn = sum(1 for k in c if k.startswith('jordan'))
print('句数:', len(d), '| 缺翻译:', missing, '| jordan:', jn, '| 分类:', len(c))
"

# 数据变了则重建 + 同步 + 打包
python3 rebuild.py 2>&1 | tail -3
cp arabic_learning.html ~/Desktop/arabic_learning.html

APP="/Users/mafucheng/Desktop/Nur Al-Arabiyya.app/Contents/Resources/app/electron"
cp build_home.py "$APP/"
cp data/categorized.json data/data.json data/dialogues.json data/history.json data/hadith.json data/tafsir.json data/books.json data/articles.json data/quotes.json data/vocab_meanings.json "$APP/data/"
cd "$APP" && python3 build_home.py dist/index.html 2>&1 | tail -1
codesign --force --deep --sign - "/Users/mafucheng/Desktop/Nur Al-Arabiyya.app" 2>&1 | tail -1

cd /Users/mafucheng/Desktop/arabic-learning/app
~/Library/gradle-8.13/bin/gradle --stop 2>/dev/null
rm -rf "$TMPDIR"/metro-* node_modules/.cache android/.gradle android/app/build/generated android/app/build/intermediates/assets 2>/dev/null
cd android
export JAVA_HOME=$HOME/Library/Java/jdk-17.0.2.jdk/Contents/Home
export ANDROID_HOME=$HOME/Android/sdk
export PATH=$JAVA_HOME/bin:$ANDROID_HOME/platform-tools:$PATH
~/Library/gradle-8.13/bin/gradle assembleRelease --console=plain 2>&1 | tail -2
cp app/build/outputs/apk/release/app-release.apk ~/Desktop/燃灯者_حامل_المصباح_v1.3.apk

cd /tmp && node test_web_jsdom.js 2>&1 | tail -1
echo "=== 0 点巡检完成 $(date +%H:%M:%S) ==="
