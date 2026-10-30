# 燃灯同学 (Rengdeng Student) 全站 UI/UX 重构路线图
## UI REDESIGN ROADMAP

> **核心目标**：在不破坏任何现有后端业务逻辑、API 接口、离线数据包与用户学习记录的前提下，将「燃灯同学」升级为具备 Apple 级视觉层次、独立文化底蕴与完整知识生态的国际化 AI 教育产品。

---

## 一、现有项目架构审查总结 (Phase 1 Audit)

1. **前端技术栈**：
   - **Web 主站（核心单一来源）**：由 `build_home.py` 编译生成 `arabic_learning.html`，配合 `data/*.css` 与 `data/*.js` 模块化样式/脚本层运行。
   - **多端复用**：`app/`（Expo React Native + Electron 桌面壳）与 `miniprogram/`（微信小程序）均围绕同一套服务端 API（`server.py`）与数据模型构建。
2. **页面路由与视图机制**：
   - 顶层页面容器（`.page`）：
     - `#page-home`：首页（由 `data/nour-product-shell.js` 挂载 `#nourProductHome` 产品壳层）。
     - `#aiSec`：AI 对话工作区（努尔老师 `NOUR AI`，支持阅读助手、阿语导师、研究助手三模式及语音交互）。
     - `#mCat` (`nav('learn')`)：世界图书馆主页面（精选书籍、OpenITI 阿拉伯语典籍、伊斯兰经典、中文古籍）。
     - `#page-search` (`nav('search')`)：全站搜索与 AI 查词/句法分析页。
     - `#page-me` (`nav('me')`)：个人中心与设置页。
     - `#page-civ` (`openCiv()`)：世界文明图谱页。
   - 专注工作区弹窗（`.modal` + `nour-focus-workspace.js`）：
     - `#mReader`：Apple Books 风格沉浸式阅读器（含逐词查词、AI 页面导读、多学派视角对比）。
     - `#mLearn`：阿拉伯语学习工作台（3.4 万句分类句子库）。
     - `#mDict`：阿拉伯语词典（词根、近反义词、例句、Wiktionary 补充）。
     - `#mQuran`：古兰经 114 章选读与音频诵读。
     - `#mVocab` / `#mWordBook` / `#mFlash` / `#mQuiz` / `#mChallenge` / `#mGrammar` / `#mAlphabet` / `#mListen` / `#mDialog`：完整阿语习得闭环。

---

## 二、十阶段执行计划 (10-Phase Execution Plan)

### 第一阶段：架构审查与文档基线（已完成）
- [x] 盘点前端构建链路（`build_home.py` → `arabic_learning.html`）、所有 `.page` 路由与 `.modal` 工作区。
- [x] 梳理历史 CSS 注入顺序，定位最后裁决层：`data/nour-design-system.css`、`data/nour-clarity.css` 与 `data/nour-theme-enforcer.js`。
- [x] 建立 `DESIGN_SYSTEM.md`、`UI_REDESIGN_ROADMAP.md`、`UI_COMPONENT_INVENTORY.md`。

### 第二阶段：建立全局 Design System（当前执行）
- [x] 重构 `data/nour-design-system.css`，严格落地 `#FFFFFF` 主背景、`#F5F5F7` 次背景、`#1D1D1F` 主文字、`#86868B` 次文字、`#D2D2D7` 分割线，以及橄榄绿 (`#1B4D3E`) + 哑光金 (`#B08D40`) 品牌色规范。
- [x] 同步更新 `data/nour-theme-enforcer.js`，使内联主题执行器与新色彩体系（浅色 + 深色独立分层）完全一致，消除旧深蓝/暖黄杂色残留。
- [x] 统一 4px 间距系统、中英阿三语字体栈、RTL 连字保护与十大公共组件样式。

### 第三阶段：首页编辑式四屏重构（当前优先交付）
严格按照 Apple 官网编辑式节奏重构 `#nourProductHome`（`data/nour-product-shell.js` + `data/nour-product-shell.css` + `data/nour-design-system.css`）：
- **第一屏（品牌与主视觉 Hero）**：
  - 品牌：**燃灯同学**（配阿文书法标识 `حامل المصباح`）
  - 副标题：**让学习成为一种探索。**
  - 介绍：**在语言、经典与人工智能之间，建立属于自己的知识世界。**
  - 两个核心主入口：**开始学习**（Primary 橄榄绿实心胶囊按钮）、**探索 AI**（Secondary 精致描边胶囊按钮），附带轻量全局搜索入口，首屏绝不堆砌杂乱入口。
- **第二屏（继续学习 Continue Learning）**：
  - 非对称编辑布局展示：**最近学习的课程**、**最近阅读的书籍**（真实阅读足迹）、**今日学习进度与今日一句**、**最近的 AI 对话入口**。
- **第三屏（探索知识 Explore Knowledge）**：
  - 四个具有独立视觉性格与尺寸节奏的大型专题内容区域（非等大重复卡片）：
    1. **阿拉伯语学习**（旗舰大画布：句子、词汇、语法、发音体系）
    2. **AI 智能助手**（智能交互面板：阅读伴读、语法拆解、跨语种问答）
    3. **古兰经**（典雅文化专区：114 章原文、译文、名家诵读与逐词解析）
    4. **世界图书馆**（宽幅书架专题：23,000+ 世界典籍、史书与中文古籍）
- **第四屏（个人学习统计 Personal Learning Analytics）**：
  - 简洁克制的数据看板：展示 **学习时间 / 连续天数**、**单词记忆**、**阅读进度** 与可折叠的工具索引。

### 第四阶段：AI 对话系统重构
- 桌面端采用「左侧会话/模式与快捷指令栏 + 中间宽幅 Markdown/中阿混排对话流 + 底部精致胶囊输入框」多栏布局。
- 移动端采用抽屉/折叠式模式切换，聊天流占据核心视口，输入框固定在底部安全区之上。
- 100% 保留现有 `homeAISend`、`homeAIVoice`、快答切换与阅读器上下文注入逻辑。

### 第五阶段：世界图书馆与 Apple Books 阅读器升级
- 图书馆首页突出「最近阅读、我的书架、推荐阅读、分类浏览、搜索」，弱化传统后台表格感。
- 阅读器（`#mReader`）强化舒适阅读宽度、中阿双语字体、字号调节、纸张/深色背景切换与 AI 段落导读。

### 第六阶段：阿拉伯语学习系统重构
- 重构学习工作台（`#mLearn`），突出「今日学习任务、单词记忆、课程学习、语法学习、句子训练、错题/闪卡复习」，一进入即明确下一步行动。

### 第七阶段：古兰经与个人中心重构
- 古兰经（`#mQuran`）强化经文排版、章节检索与诵读体验。
- 个人中心（`#page-me`）采用 iOS 设置式清晰分组结构（个人资料、学习记录、收藏/生词、账户设置、AI 偏好、外观设置、语言与备份）。

### 第八阶段：移动端与平板响应式精修
- 针对 `<768px`（手机）、`768px–1023px`（平板）、`>=1024px`（桌面）逐一精修留白、触控热区（`>=44px`）与底部导航避让。

### 第九阶段：深色模式深度调校
- 检查所有页面、弹窗、阅读器、代码块与阿语金色强调在 `html[data-theme="dark"]` 下的对比度与层次。

### 第十阶段：全站测试、性能优化与文档归档
- 运行 `python3 build_home.py` 重新生成生产 HTML，启动本地服务并通过浏览器实际预览检验视觉与控制台零报错。
