# 燃灯同学 (Rengdeng Student) 页面、路由与组件清单
## UI COMPONENT INVENTORY

> 本文档完整记录当前工作区的所有前端页面、模态工作区、公共组件与现有业务函数绑定关系。重构过程中**严禁破坏以下 DOM ID 与全局 JS 函数签名**。

---

## 1. 核心构建与样式文件清单

| 文件路径 | 角色与职责 | 重构策略 |
| :--- | :--- | :--- |
| `build_home.py` | 网页单一构建脚本，汇编内联数据、HTML 结构、CSS 与 JS 并输出 `arabic_learning.html` | 保持构建管线不变，每次修改 `data/*` 后运行 `python3 build_home.py` |
| `arabic_learning.html` | 构建生成的生产单页应用入口 | 由 `build_home.py` 自动生成 |
| `data/nour-design-system.css` | **全局 Design System 唯一权威样式层**（在 `</head>` 前最后注入） | 核心升级文件：定义色彩、字体、4px 间距、深色模式与全局组件 |
| `data/nour-product-shell.js` | **产品壳层与首页挂载器**（挂载 `#nourProductHome`、五项主导航、AI 导览头） | 核心升级文件：实现编辑式四屏首页与交互绑定 |
| `data/nour-product-shell.css` | 产品壳层与首页布局样式 | 配合 `nour-design-system.css` 重构首页四屏节奏 |
| `data/nour-clarity.css` | 视觉降噪与全站页面契约层 | 升级为与 `#FFFFFF` / `#F5F5F7` 体系对齐的编辑式布局规则 |
| `data/nour-theme-enforcer.js` | 主题运行时强制同步器（监听 `data-theme` 与 DOM 变化） | 同步更新为 `#FFFFFF` / `#F5F5F7` / `#1D1D1F` / `#86868B` / `#D2D2D7` 及深色分层色板 |
| `data/nour-focus-workspace.js` | 将 `.modal` 与二级 `.page` 包装为可返回的专注工作区 | 保留并美化顶部返回胶囊 `#nourFocusBack` |

---

## 2. 顶层页面路由清单 (`.page`)

| 页面容器 ID | 路由调用方式 | 页面名称 | 关键内部节点（必须保留） |
| :--- | :--- | :--- | :--- |
| `#page-home` | `nav('home')` / `openPrimaryRoute('home')` | 首页 | `.hdr`、`#nourProductHome`、`#quote` (`#qAr`, `#qCn`)、`#studyProgress` (`#studyLearned`, `#studyBar`, `#studyStreak`)、`#hsBooks`、`#hsReadable` |
| `#aiSec` | `nav('ai')` | AI 智能助手（努尔老师） | `.ps-ai-card`、`.ps-ai-head`、`#aiQuota`、`#aiVoiceToggle`、`#homeAI`、`#homeAIChips`、`#homeAIIn`、`#homeAIFast`、`#homeMic`、`#homeAISendBtn` |
| `#mCat` | `nav('learn')` / `openPrimaryRoute('read')` | 世界图书馆 | `.m-head`、`#mCatBody`、`.lib-tabs`、`.bk-side`、`.bk-grid` |
| `#page-search` | `nav('search')` / `openSearchAll()` | 全站搜索与 AI 查词 | `#sQ`、`.search-tools`、`.srch-chips`、`#sRes` |
| `#page-me` | `nav('me')` / `openPrimaryRoute('me')` | 个人中心 | `#meBox`、`#profileActivity`、`.profile-settings` |
| `#page-civ` | `openCiv()` | 世界文明图谱 | `#civWrap` |

---

## 3. 模态框与专注工作区清单 (`.modal`)

| 模态框 ID | 触发函数 | 功能模块 | 关键内部节点（必须保留） |
| :--- | :--- | :--- | :--- |
| `#mReader` | `openBook()` / 馆藏点击 | Apple Books 阅读器 | `#mReaderTitle`、`#mReaderBody`、`.rd-paper`、`.rd-bar`、`.rd-page`、`.rd-page-analysis` |
| `#mLearn` | `openModal('mLearn')` | 阿拉伯语学习工作台 | `#studyWorkspaceLearned`、`#studyWorkspaceStreak`、`.cat-scroll`、`.s-card` |
| `#mDict` | `openDict()` | 阿拉伯语词典 | `#dictQ`、`#dictBody`、`dictSearch()`、`dictVoice()` |
| `#mQuran` | `openModal('mQuran')` / `showQuran()` | 古兰经 114 章选读 | `#mQuranSearch`、`#mQuranBody`、`#mQuranCount` |
| `#mGrammar` | `showGrammar()` | 阿拉伯语语法课 | `#mGramHead`、`#mGramBody` |
| `#mVocab` | `showVocab()` | 8.5 万高频词汇表 | `#mVocabSearch`、`#mVocabBody`、`#mVocabCount` |
| `#mFlash` | `showFlashcard()` | SRS 间隔重复闪卡 | `#mFlashHead`、`#mFlashBody`、`#flashBadge` |
| `#mWordBook` | `showWordBook()` | 个人生词本 | `#mWbSearch`、`#mWordBookBody`、`#mWordBookCount`、`#wbCount` |
| `#mListen` | `showListen()` | 听力与跟读评测 | `#mListenHead`、`#mListenBody` |
| `#mChallenge` | `showChallenge()` | 词汇/语法/拼句闯关 | `#mChallengeHead`、`#mChallengeBody` |
| `#mQuiz` | `showQuiz()` | 阿拉伯语随机测验 | `#mQuizHead`、`#mQuizBody` |
| `#mAlphabet` | `showAlphabet()` | 28 字母发音与写法课 | `#mAlphabetHead`、`#mAlphabetBody` |
| `#mDialog` | `showDialog()` | 30 场景日常口语对话 | `#mDialogHead`、`#mDialogBody` |
| `#mSentences` | `showAllSentences()` | 全部句子检索 | `#mSentSearch`、`#mSentBody`、`#mSentCount` |
| `#mH6` / `#mHadith` | `showH6()` | 哲人哲言 / 圣训库 | `#mH6Body`、`#mHadithBody` |
| `#mHistory` | `openModal('mHistory')` | 世界历史文献库 | `#mHistoryBody` |
| `#mTheme` | `showThemeSettings()` | 外观设置（浅色/深色） | `#mThemeBody` |
| `#mLogin` / `#mPay` | `openModal('mLogin')` / `openPay()` | 账户登录与会员额度 | `#lUser`、`#lPass`、`#payMine`、`#payPlans` |

---

## 4. 公共 UI 组件映射表

| 组件类别 | 统一 CSS 类名体系 | 现有兼容类名 |
| :--- | :--- | :--- |
| **按钮 (Buttons)** | `.ds-btn`, `.ds-btn-primary`, `.ds-btn-secondary`, `.ds-btn-ghost`, `.nour-product-action` | `.act-btn`, `.s-btn`, `.hbb-b` |
| **输入框 (Inputs)** | `.ds-input`, `.nour-product-search` | `#dictQ`, `#sQ`, `#homeAIIn`, `.srch-big` |
| **导航栏 (Nav)** | `.hdr`, `.tabbar.nour-primary-nav`, `#nourFocusBack` | `.tabbar`, `.tb` |
| **卡片与专题块 (Cards)** | `.nour-hero-stage`, `.nour-continue-card`, `.nour-World-card`, `.nour-stat-card` | `.card`, `.profile-card`, `.bkcard`, `.s-card` |
| **标签与胶囊 (Chips)** | `.ds-chip`, `.ds-badge` | `.chip`, `.cat-tab`, `.lt`, `.nour-ai-mode` |
| **弹窗 (Modals)** | `.modal`, `.m-head`, `.m-body` | `.modal.show`, `.nour-focus-modal` |
