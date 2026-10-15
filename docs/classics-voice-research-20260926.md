# 古兰经、六大圣训与自然语音接入核验

日期：2026-09-26

## 已核验现状

- 项目已有 `data/builtin_quran.js`：114 章、6236 节，含阿拉伯原文与中文译文。
- 项目已有六大部完整按书分文件：布哈里、穆斯林、奈萨仪、艾布·达乌德、伊本·马哲、提尔密济；`data/hadith/index.json` 标记合计 34,153 段。
- 项目已有多位古兰经诵读家入口和 `/api/recite` 代理。
- 项目的经注静态资源当前为空，因此经注是主要缺口。
- 普通 AI 聊天当前只显示文字；原有服务端 `/api/tts` 使用 Edge TTS，但前端文字聊天没有统一的自然人声播放控制。

## 采用的接入原则

1. 古兰经原文、中文译文、经注、真人诵读音频分开显示和建模，不把经注或译文伪装成经文原文。
2. 古兰经经注首期使用 AlQuran.Cloud 的公开 `ar.muyassar`（Tafsir al-Muyassar）按章按需请求，并保留经注来源标签；将 `ar.jalalayn` 作为可选备用版本。服务端做有限缓存和失败降级，不抓取网页。
3. 古兰经真人诵读保留现有诵读入口；普通学习对话采用 Edge TTS Natural 音色，前端明确标注为合成朗读，不称为真人录音或宗教诵读。
4. 六大部入口保留项目已有完整数据，不用未经授权的网页整站抓取替换；页面继续显示书名、编号、章节和译文/注释层级。
5. 经注、翻译、现代校订版和音频的许可分别核验。没有书面授权时，不把可访问 URL 视为可下载、离线打包或再分发许可。

## 核验来源

- https://api.alquran.cloud/v1/edition?format=text&type=tafsir&language=ar
- https://api.alquran.cloud/v1/surah/1/ar.muyassar
- https://api.alquran.cloud/v1/ayah/1:1/editions/ar.jalalayn
- https://alquran.cloud/terms-and-conditions
- https://tanzil.net/docs/text_license
- https://api-docs.quran.foundation/docs/api-reference/
- https://api-docs.quran.foundation/docs/content_apis_versioned/4.0.0/recitations/
- https://api-docs.quran.foundation/docs/content_apis_versioned/4.0.0/recitation-audio-files/
- https://everyayah.com/
- https://everyayah.com/data/recitations.js
- https://api-docs.quran.foundation/legal/developer-terms/
- https://sunnah.com/about
- https://sunnah.com/developers
- https://kitab-project.org/corpus/about
- https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis/getVoices
- https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support

## 上线标注

普通学习文本的声音是云端合成音色；设备本地声音取决于浏览器。古兰经诵读按钮使用具体诵读家的录音入口，必须单独显示诵读家和来源。AI 解释仅是学习辅助，不替代合资格学者的经注或教法意见。

## 2026-09-27 真人诵读控制回归

- Quran Foundation 的音频文档给出的逐节文件结构为 `Alafasy/mp3/001001.mp3`，并明确返回音频文件 URL；实测 `verses.quran.foundation` 与 `verses.quran.com` 的默认文件可用。原先使用的 `server8.mp3quran.net/afs/001001.mp3` 实测返回 404，因此没有继续使用该地址。
- 为保持多个诵读家的目录一致并避免伪造来源，播放器改用 EveryAyah 公布的目录清单和逐节 MP3：阿法西、苏达伊斯、舒莱姆、胡宰菲、明沙维均已逐一实测首节 HTTP 200。服务端 `/api/recite` 继续只代理允许域名，支持 Range/206，浏览器退出阅读器时停止当前逐节音频。
- 回归覆盖：手机和桌面真人诵读专项各 19/19；相关经注/逐页分析 7/7；全站手机 29/29、桌面 30/30；公网首节音频中转返回 `206 Partial Content`。音频按官方入口流式读取，不将整部录音打包为项目内置资源。
