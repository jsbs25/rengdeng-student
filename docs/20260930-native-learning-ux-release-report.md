# 燃灯同学：自然学习界面与公开来源同步发布报告

发布时间：2026-09-30（本地构建时间 19:54，公网验收随后完成）

## 已完成

### 1. 首页改成“先学习、后工具”

- 首页不再强制展示金色 AI 光球和 AI 对话卡。
- 首屏改成三个清晰入口：**查一个词、听一遍、练一题**。
- 底部默认文案改为“练习室”，日常口语卡改为场景对话；AI 页面仍保留为用户主动进入的可选工具，不再是学习主路径。
- 视觉使用轻量 CSS、RTL 字体和移动/桌面响应式卡片，没有引入外站 iframe 或不可维护的图片装饰。

### 2. 站内查词与阿语发音

- 新增只读接口：`GET /api/dict/lookup?w=...`。
- 查词顺序：本地固定词库和句子库 → Arabic Wiktionary 公开词典补充。
- 支持带或不带阿拉伯语音符的输入；服务端会有限搜索带音符词条，避免“كتاب”查不到正式词条。
- 结果包含阿拉伯语例句、中文/英文字段（本地有则直接展示）、来源标记和公开词典链接。
- 朗读使用设备原生 `speechSynthesis`，选择可用的 `ar-*` 声音；语音输入使用浏览器 `SpeechRecognition`，不可用时明确提示手动输入。
- 阅读器单词卡复用同一条本地优先查词链路，支持朗读、收藏和关闭；不会把 AI 占位塞进普通查词流程。

### 3. 公开来源自动更新

新增 `harvest/public_source_sync.py` 和 systemd timer：

- 白名单来源：Arabic Wiktionary、Tatoeba、OpenITI RELEASE、Arabic Wikipedia API、Mozilla Data Collective Common Voice 元数据页。
- 单队列、请求间隔约 1.1 秒、单响应 2 MiB 上限、超时、原子 JSON 写入。
- 只写 `data/public_source_cache/`，不覆盖用户、会员、充值状态、AI 配置或 OpenITI 原文缓存。
- 不下载整库、不镜像 Common Voice 音频、不复制许可证不明的音频；OpenITI 在商业网站上默认只保留书目、URI、版本和官方链接，全文仍受 CC BY-NC-SA 和商业使用边界约束。
- 本地和远端首次执行均为 5/5 白名单来源可达，并生成 Wiktionary “سلام” 样例与状态文件。
- 远端 timer：`nur-public-source-sync.timer`，每周日 03:30 UTC，带 30 分钟随机延迟；首次成功执行后下一次计划时间为 2026-10-04 03:56 UTC 左右。

来源和许可证核验见：[公开阿拉伯语来源研究文档](20260930-public-arabic-sources-research.md)。

### 4. 保留上一轮 OpenITI 流式能力

- 两部原先返回 413 的书：`openiti-b189390ada0b10e0`、`openiti-23f3107332aec56a`。
- 公网首页请求均从 413 变为 HTTP 200 流式响应：分别读取 1 MiB 分段，返回源大小约 20,041,082 和 14,437,493 字节。
- 返回正文含阿拉伯字符、没有 `U+FFFD` 替换字符；前端 202 轮询、有限页缓存、AbortController、断点缓存和移动横滑保持通过。

## 验收结果

| 范围 | 结果 |
| --- | --- |
| Python 语法：server/build/source-sync/OpenITI | 通过 |
| 本地手机自然学习 UI | 17/17 |
| 本地桌面自然学习 UI | 17/17 |
| 本地手机 OpenITI 流式 UI | 16/16 |
| 本地桌面 OpenITI 流式 UI | 16/16 |
| 伊斯兰图书馆综合 UI | 通过 |
| 古兰经入口与首章 RTL 阅读 | 通过 |
| 全站手机导航/可选 AI 页面 | 29/29 |
| 公网手机自然学习 UI | 17/17 |
| 公网桌面自然学习 UI | 17/17 |
| 公网手机 OpenITI 流式 UI | 16/16 |
| 公网桌面 OpenITI 流式 UI | 16/16 |
| 公网目录元数据 | `total=8794`，`openiti_arabic_works=8756` |
| 公网 `nur.service` | active |
| 公网健康监控 | active |
| 公网来源同步 timer | active |

注：`/api/books` 是精选书籍接口，返回 4 条并不代表完整目录数量；完整目录数量以 `/api/catalog/meta` 的 `total=8794` 为准。

## 发布与回滚

- 远端回滚点：`/opt/nur/backups/20260930-native-learning-ux`
- 原子发布临时目录：`/opt/nur/.deploy-native-learning-ux-20260930`
- 本轮发布没有删除或覆盖用户数据、会员状态、充值状态、AI 密钥和既有健康监控。
- 如需回滚，停止来源 timer（如需要），从上述回滚点原子恢复 `server.py`、`build_home.py`、`arabic_learning.html`、`v3.html` 和 `data/openiti-stream.css`，再重启 `nur.service`；来源同步脚本/单元可单独禁用，不影响阅读器。

## 已知边界

- 浏览器原生语音识别和阿拉伯语声音依赖设备/浏览器是否安装 `ar-*` voice；网站已提供手动输入和公开词典补充。
- 公开来源字段和正文的许可证按来源、页面、句子或音频文件逐项处理；没有把 Common Voice 整套音频或 OpenITI 整库复制到公网。
- 本轮把 AI 从默认主路径移除，但没有删除原有 AI 页面；这样保留已有逐页导读能力，同时让基础查词、例句、朗读和练习不依赖 AI。
- 未创建“每小时爬取并自动改版”的任务；本轮只部署了合规、低频、白名单的每周来源元数据刷新。
