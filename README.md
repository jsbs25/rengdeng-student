# 📖 燃灯同学 · 阿拉伯语学习与 AI 阅读平台 (حامل المصباح)

> 无声却引人归途 —— 网页版 + 微信小程序 + 手机 App。

## 🚀 一键启动

```bash
bash run.sh        # 启动服务器（AI 对话 / 语音识别 / 数据 API / 静态网页）
```

- 网页版：http://localhost:8080 （生产：https://燃灯同学.com）
- 微信小程序：`miniprogram/`（原生 WXML/WXSS，对接 `/api/*`）
- 手机 App：`app/`（Expo + WebView 壳，连局域网电脑服务）

> AI 对话 / 全站搜索 / 图书馆正文 / 语音识别需要服务器运行；句子库等核心数据已内嵌离线可用。

## ✨ 功能总览

### 📚 学习内容
- **3 万+ 句阿拉伯语**（23 分类，完整音符），中英翻译 + 朗读 + 音译
- **词汇表**：2 万+ 高频词，AI 语法分析
- **古兰经**：114 章 6236 节 + 中文翻译 + 诵读家音频 + AI 逐字分解
- **图书馆**：精选整书 + 世界图书馆（伊斯兰书目 8000+）+ 中国古籍
- **日常对话**：留学生场景，每日自动轮换

### 🧠 学习系统
- 间隔复习（SRS）、生词本、闪卡、测验、字母入门、每日目标、打卡/连续天数/计时

### 🎙 AI 与语音
- AI 老师（DeepSeek 对话）、语音唤醒、跟读评测、每日提醒、数据备份

## 🎨 设计系统

- 浅色「暖纸 + 墨绿 + 哑金」/ 深色「暖炭黑 + 金」双主题
- 阿拉伯语 RTL 一等公民（Amiri / Scheherazade 阅读字体）
- 统一设计令牌 + 主题执行器（`data/nour-design-system.css` + `data/nour-theme-enforcer.js`）

## 🔒 安全

- 敏感文件服务端封堵、管理密码轮换、接口限流
- SECRET 走环境变量 / `data/secret.txt`（自动生成，gitignore）
- `verify_web.py` 自动体检 + GitHub Actions CI 门禁

## 📁 文件结构

```
arabic-learning/
├── arabic_learning.html   ← 网页版（由 build_home.py 生成，约 1.9MB + 外链 data/*.js）
├── server.py              ← 后端（AI / 语音 / 数据 API / 静态服务，约 5300 行）
├── build_home.py          ← 网页构建脚本
├── data/                  ← 内容数据 + 前端脚本 + 设计系统
├── miniprogram/           ← 微信小程序（原生）
├── app/                   ← Expo App（WebView 壳）
├── tools/verify_web.py    ← 网页自动体检（CI 门禁）
└── deploy/                ← 部署脚本（systemd / nginx / Apache / cloudflared）
```

## 🔧 开发

- 改网页：编辑 `build_home.py` 或 `data/*.css` → `python3 build_home.py` → 刷新
- 自动体检：`python3 tools/verify_web.py`
- 数据变更后一键重建：`python3 rebuild.py`
- 新句子自动翻译：`scraper_hourly.py`（每小时，限 60 句）
