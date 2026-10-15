# 📖 阿拉伯语学习 · 燃灯者 (حامل المصباح)

> 无声却引人归途 —— 网页版 + 手机 App + 桌面 App 三端，全部离线可用。

## 🚀 一键启动

```bash
bash run.sh        # 启动服务器（AI 对话 / 语音识别 / 数据 API）
```

- 网页版：[arabic_learning.html](arabic_learning.html)（双击即用 / http://localhost:8080）
- 手机 App：`app/` 下打包的 APK（Android），iOS 需 eas build
- 桌面 App：`燃灯者 - Nur Al-Arabiyya.app`（自带服务器 + 爬虫，双击即用）

> AI 对话 / 单词拆解 / 语音识别（唤醒、跟读评测）需要服务器运行；其余全部离线可用（数据已内嵌）。

## ✨ 功能总览

### 📚 学习内容
- **2500+ 句阿拉伯语**（23 分类，完整音符），中英翻译全齐 + 🔊 朗读 + 🗣 音译
- **旅途 200 句**（约旦留学生场景，10 个分类，方言口语 + 音译）
- **词汇表**：4000+ 高频词（词频 + 中英释义），AI 语法分析
- **古兰经**：114 章 6236 节（Tanzil 标准文本）+ 中文翻译 + 3 位诵读家音频 + AI 逐字分解
- **图书馆**：13 篇文章 + **5 本公版整书** 149 万字（卡里来和笛木乃 / 辛巴达 / 哈里里玛卡梅 / 宽恕书 / 一千零一夜）+ AI 写文章
- **💬 日常对话**：30 个留学生场景 × 5 轮有来有往，**每天自动轮换 10 场景 = 100 句**

### 🧠 学习系统
- **📅 间隔复习（SRS）**：闪卡答题自动进入遗忘曲线（1/3/7/15/30 天），到期提醒条
- **📕 生词本**：一键收词，随时复习
- **🃏 闪卡**：句子卡 / 单词卡 / 间隔复习三模式
- **📝 测验**：10 题闯关（阿语→中文）
- **🔤 字母入门**：28 字母四种书写形式 + 认读测验
- **🎯 每日目标**：自定义每日单词目标，进度环联动
- **🔥 打卡 / 连续天数 / 学习计时 / 7 天曲线**

### 🎙 AI 与语音
- **🤖 AI 老师**：DeepSeek 对话（阿/中/英三段式），打字机 + 朗读
- **🎙 语音唤醒**：喊「马晓梅」唤醒 AI，语音对话（本地 Whisper 识别，离线）
- **🎯 跟读评测**：录音 → Whisper 阿语识别 → 词级比对打分
- **🔔 每日提醒**：本地通知（App）
- **💾 数据备份**：导出/导入 JSON（网页版 + App）

## 📁 文件结构

```
arabic-learning/
├── arabic_learning.html   ← 网页版（单文件 ~6MB，双击即用，全部数据内嵌）
├── server.py              ← 服务器（AI 对话 + 语音识别 /api/asr + 数据 API）
├── build_home.py          ← 网页构建脚本
├── scraper_hourly.py      ← 每小时爬虫（新句子 → 自动翻译 → 重建页面）
├── translate_fix.py       ← 批量 AI 翻译补全（DeepSeek）
├── gen_dialogues.py       ← 留学生日常对话数据生成（30 场景）
├── rebuild.py             ← 一键重建 App 数据 + 网页版
├── data/                  ← categorized.json（句子）/ dialogues.json（对话）/ books.json 等
└── app/                   ← Expo App（src/ 全部模块）
```

## 🔧 开发

- 改网页：编辑 `build_home.py` → `python3 build_home.py` → 刷新
- 数据变更后一键重建：`python3 rebuild.py`
- 新句子自动翻译：爬虫每小时自动做（限 60 句）；手动全量：`python3 translate_fix.py`
- App 打包：`cd app/android && gradle assembleRelease`（newArchEnabled=false）
- 语音识别：faster-whisper small 模型（首次使用自动下载 ~460MB，之后离线）
