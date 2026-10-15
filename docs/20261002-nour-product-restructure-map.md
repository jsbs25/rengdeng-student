# NOUR / 燃灯同学产品级重构映射

**审查时间：** 2026-10-02 01:37–01:39（+03:00）  
**范围：** `build_home.py`、生成产物 `arabic_learning.html` / `v3.html`、`server.py`、`data/`、`harvest/`、`openiti_stream.py`、现有 UI 预览与测试脚本。

## 1. 重构原则

这不是一次删功能的换皮。实施采用“**新产品壳 + 旧功能适配层**”：

- 不删除既有书目、阿拉伯语原文、古兰经、圣训、词汇、句子、音频、学习记录、AI 配置和会员/用户数据。
- 不重写已经验证过的 OpenITI 流式读取、增量 UTF-8 解码、磁盘 manifest、断点缓存和 202 轮询。
- 不将外部网站页面嵌入 NOUR；公开来源只通过白名单同步、元数据、授权内容或官方链接进入站内数据层。
- 新界面只改变信息架构、导航、布局和组件呈现；核心 API、`localStorage` 键、阅读器状态变量和现有函数保留兼容。
- 任何新入口先连接已有能力；没有真实后端能力的“AI 建书”只显示明确的规划状态，不制造推荐书单假数据。

## 2. 当前能力盘点

### 数据与内容

| 领域 | 当前真实内容或能力 | 规模/证据 |
|---|---|---:|
| 伊斯兰书库 | `data/islamic_catalog.json`，包含书目、来源、分类、OpenITI 元数据与阅读字段 | 元数据对象含 `schema_version`、`meta`、`books`；既有公网目录约 8,794 部 |
| OpenITI 阅读 | 固定官方 raw 白名单、HEAD/Range 探测、1 MiB 分段、每请求预算、64 MiB 安全上限、manifest、页缓存、增量 UTF-8 解码 | `openiti_stream.py` + `/api/catalog/read` |
| 古兰经 | 114 章入口、原文、译文、诵读与逐页讲解 | `data/builtin_quran.js` 约 2.2 MB；`/api/quran/tafsir` |
| 圣训与经典 | 六大部入口、伊斯兰来源分类、经注与经典文本入口 | `data/builtin_hadith.js`、`data/hadith*.json`、`data/tafsir.json` |
| 词汇与句子 | 本地词汇、例句、分类、中文/英文释义，支持本地优先查词和 Arabic Wiktionary 有界补充 | `data/vocab_meanings.json` 295 条；`data/categorized.json` 26,689 条；`builtin_vocab.js` 约 739 KB；`builtin_sentences.js` 约 4.2 MB |
| 课程内容 | 对话、文章、语法、构词/形态、挑战练习、文明内容 | `dialogues.json` 26 个场景；`articles.json` 7 个主题；`grammar.json`、`morphology.json`、`challenge.js` |
| 音频 | 音频资料库、古兰经/朗读入口、浏览器原生阿语语音、TTS/ASR/跟读模块 | `data/audio-library.*`、`nour-voice-v2.js`、`natural-voice.js`、服务端 `/api/audio/*`、`/api/tts`、`/api/asr` |
| AI | 普通对话、流式语音、页级讲解、多语言、法学派视角、配额与登录/会员边界 | `data/ai-page.js`、`data/page-analysis.js`、`/api/page/analyze`、`/api/chat/stream_voice`、`/api/realtime/session` |
| 学习记录 | 历史、读书足迹、笔记、书签/生词本、主题/阅读偏好 | `localStorage` 既有键、`/api/history`、`/api/hnote`、个人页与设置模块 |
| 来源同步 | 受限公开来源同步、白名单缓存、类型/关键词过滤和右侧来源监测台 | `harvest/public_source_sync.py`、`data/public_source_cache/`、`/api/theme/source-feed`、systemd timer |

### 现有后端接口分组

- **内容/书库：** `/api/catalog/meta`、`/api/catalog`、`/api/catalog/read`、`/api/books`、`/api/islamic/search`、`/api/read`、`/api/cover`、`/api/coverimg`。
- **语言学习：** `/api/dict/lookup`、`/api/dict/free`、`/api/vocab`、`/api/sentences`、`/api/articles`、`/api/search`、`/api/websearch`。
- **古兰经/伊斯兰资料：** `/api/quran/proxy`、`/api/quran/tafsir`、音频相关接口。
- **AI/语音：** `/api/page/analyze`、`/api/ai/quota`、`/api/realtime/session`、`/api/chat/stream_voice`、`/api/tts`、`/api/asr`。
- **个人与账户：** `/api/auth/*`、`/api/me/usage`、`/api/history`、`/api/hnote`、`/api/access/*`、会员/授权接口。
- **运维/来源：** `/api/home_stats`、`/api/theme/source-feed`、管理员与健康监控接口。

## 3. 旧功能 → 新产品骨架

新产品只保留四项主导航：**首页 / 书库 / NOUR AI / 我的**。搜索变成全局能力；生词本、跟读、设置等进入“我的”或阅读上下文，不再占用主导航。

| 旧入口/功能 | 新归属 | 迁移策略 | 保留的核心调用 |
|---|---|---|---|
| 首页学习卡片、最近内容、学习统计 | 首页 | 改成“继续阅读 / 最近阅读 / 阅读数据 / AI 发现”四个内容区；减少按钮和卡片数量 | `updateStats()`、历史/本地记录、既有书籍打开函数 |
| 旧“世界图书馆”页 | 书库 | 书籍封面、分类、最近阅读、收藏和 AI 推荐成为主体；来源卡片移到书库内独立“来源”区域 | `nav('learn')`、`islamic-library.js`、`/api/catalog*`、`/api/books` |
| 旧搜索页 `page-search` | 全局搜索 | 保留搜索函数和结果渲染；底栏移除搜索按钮，新增顶部/快捷面板入口，支持 `⌘/Ctrl+K`、手机搜索按钮 | `doSearch()`、`doSearchAll()`、`/api/search`、本地词汇/句子查找 |
| 旧生词本底栏 | 我的 + 阅读上下文 | 从底栏移除；个人页保留入口，阅读器单词卡继续支持收藏；不迁移或重命名现有生词数据键 | `showWordBook()`、`wbAdd2()`、既有 `localStorage` 键 |
| 旧 AI 首页区 | NOUR AI | 首页不默认堆叠聊天框；AI 页改成阅读助手、阿语导师、研究助手、知识连接器四个模式 | `openNurAI()`、`data/ai-page.js`、`/api/chat/*`、配额/登录检查 |
| 页级 AI 讲解 | 阅读器右栏/底部抽屉 + NOUR AI | 在正文就绪后显示；未就绪、202 进度和错误状态不允许提交给 AI | `page-analysis.js`、`/api/page/analyze`、法学派/语言选择 |
| 书中单词点击 | 阅读器上下文工具条 | 点击单词打开轻量词卡：释义、词根/词形字段、例句、原生阿语朗读、收藏；网络补充仍是有界的非 AI 词典 | `rdWord()`、`/api/dict/lookup`、`/api/dict/free`、`dictSpeak()` |
| 古兰经入口 | 书库“经典”分类 + 阅读器 | 保持 114 章、原文、诵读、译文和经注；视觉上归入书库，不再与普通课程卡片混排 | 既有古兰经模块、`/api/quran/*` |
| 六大部圣训、经注、法学/法源 | 书库学科索引 | 以学科/系列/作者/语言过滤呈现；进入统一阅读器，页级 AI 保持证据边界 | `islamic-library.js`、`page-analysis.js`、目录接口 |
| OpenITI 大书 | 统一阅读器 | 使用现有按需分页和断点缓存；进度、已读字节、缓存页和重启恢复展示在阅读器状态条 | `openiti_stream.py`、`RD_OPENITI`、`/api/catalog/read` |
| 音频库、真人朗读、跟读 | 阅读器控制条 + 我的 | 阅读器提供当前段落朗读、速度、暂停；完整音频库进入我的/资料库；不额外制造底部导航项 | `data/audio-library.js`、`showListen()`、`/api/audio/*`、`speechSynthesis` |
| 语法、词汇、挑战 | 首页“学习计划”与书库“课程” | 作为学习路径中的模块，不作为首屏多卡片堆叠；保持本地题目与进度 | `course.js`、`challenge.js`、`belt.js`、本地进度键 |
| 来源监测与自动同步 | 书库“来源”与管理员状态 | 用户可见白名单、更新时间、过滤结果和权利说明；不展示抓取为“实时复制” | `/api/theme/source-feed`、`public_source_sync.py`、timer |
| 个人信息、外观、会员/额度 | 我的 | 统一为个人资料、阅读偏好、生词本、学习数据、账户与会员；不改权限和支付数据 | `renderMe()`、`showThemeSettings()`、`/api/me/usage`、授权接口 |

## 4. 目标桌面信息架构

### Mac / 宽屏

- **左侧 220–260 px：** 书库树、最近阅读、收藏、学科筛选。
- **中间弹性主区：** 首页内容、书库网格/索引或阅读正文。
- **右侧 320–380 px：** NOUR AI、页级解释、词汇卡、来源/笔记；没有上下文时收起，避免持续占据屏幕。
- 搜索以顶部命令面板打开，不改变当前主视图。

### iPad

- 书库列表与正文二选一主视图。
- AI 作为可拖拽/可关闭的侧栏或底部抽屉。
- 书中选词先显示紧凑词卡，再由用户选择“解释这一段”进入 AI。

### iPhone

- 四项底部导航：首页、书库、NOUR AI、我的。
- 阅读器全屏，工具条按需出现；正文保持 RTL、字号/行距和横滑翻页。
- 全局搜索从顶部按钮或系统级快捷入口进入。
- AI、词卡、来源信息使用全屏抽屉，不能遮挡正文底部和系统安全区。

## 5. 视觉重构约束

- 视觉参考是安静的数字图书馆，不复制 Apple 的具体界面、图标或文案。
- 主色：墨黑、深墨绿、象牙白、暖灰，少量哑光金作为状态强调。
- 书封面通过真实书目字段生成可识别的学科封面体系；禁止用静态图片伪装不可用功能。
- 内容优先，减少玻璃拟态、统一大圆角、过多阴影和重复边框。
- 动画 300–500 ms，阅读器打开淡入与轻微位移即可；不使用夸张发光、缩放悬停和霓虹渐变。
- 阿拉伯语正文和词卡使用现有阿语字体资源，`dir="rtl"` 与中文辅助文本分层处理。

## 6. 实施顺序与回滚点

1. **先建兼容壳：** 增加四项导航、全局搜索按钮、工作区容器和右侧上下文面板，不删除旧页面节点。
2. **再迁移首页：** 只调整首页可见层级，把原有内容挂到“继续阅读/最近阅读/阅读数据/AI 发现”区域。
3. **再迁移书库：** 以真实书目和封面为主，复用原卡片打开函数和 OpenITI 阅读器。
4. **再收拢 AI：** 将首页 AI 入口改为明确的 NOUR AI 工作台，正文 AI 由阅读上下文触发。
5. **再改阅读器：** 复用 `RD_*` 状态和页级分析，补工具条、书签、搜索与响应式布局。
6. **再迁移我的：** 保留生词本、跟读、主题、数据和账户入口，统一路径。
7. **本地回归后发布：** 先保存源码与生成 HTML 的独立远端备份，再原子替换；用户数据、会员/充值状态、AI 密钥和缓存不在替换范围。

每一步都保留旧页面节点和旧函数至少一个回归周期。若新壳发生问题，可以恢复导航/可见性层而不用回滚数据文件。

## 7. 不做的事情

- 不批量复制第三方网站全文，不绕过反爬、付费墙或登录。
- 不把“AI 建书”做成假推荐。第一版只连接现有目录搜索和来源监测，无法验证的推荐明确标注为待研究。
- 不删除 AI，只让 AI 从默认首页退到用户主动打开的阅读工作区。
- 不把 `/api/books` 的精选列表误称为完整书库；完整目录仍以目录元数据接口和书库数据为准。
- 不触碰支付、会员、用户隐私、管理员密钥和既有健康监控。
