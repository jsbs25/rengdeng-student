# 燃灯同学 (Rengdeng Student · حامل المصباح) 全局设计系统规范
## DESIGN SYSTEM v2.0

> **产品定位**：安静、简洁、优雅、智能、专业、有文化底蕴的国际化知识与 AI 教育产品。
> **设计哲学**：参考 Apple 官网的编辑式视觉层次、macOS 的克制交互、iOS 的原生触控体验、Apple Books 的沉浸式排版与 Apple Intelligence 的自然协同——借鉴设计哲学，保持「燃灯同学」独立的橄榄绿与哑光金品牌识别。

---

## 1. 色彩体系 (Color System)

### 1.1 浅色模式 (Light Mode — 默认主视觉)

| 语义令牌 (CSS Variable) | 色值 | 用途与规范 |
| :--- | :--- | :--- |
| `--ds-bg` | `#FFFFFF` | 主背景（首屏、编辑式画布、阅读纸面） |
| `--ds-bg-secondary` / `--ds-surface-2` | `#F5F5F7` | 次背景（分屏交替底色、模块容器、输入框静止底色、分组背景） |
| `--ds-surface` | `#FFFFFF` | 卡片、浮层、导航栏与弹窗主体表面 |
| `--ds-surface-elevated` | `rgba(255, 255, 255, 0.88)` | 粘性顶栏/底栏毛玻璃表面（配合 `backdrop-filter: blur(20px)`） |
| `--ds-ink` | `#1D1D1F` | 主文字（标题、正文、核心数据） |
| `--ds-ink-2` | `#86868B` | 次文字（副标题、说明文案、元数据、辅助标签） |
| `--ds-ink-3` | `#AEAEB2` | 弱化文字（占位符、禁用态、时间戳） |
| `--ds-line` | `#D2D2D7` | 标准分割线、边框、表格线 |
| `--ds-line-subtle` | `#E8E8ED` | 列表内部分割细线、轻量化卡片边界 |

### 1.2 品牌色与功能色 (Brand & Semantic Accents)

> **使用铁律**：品牌色只用于**重要主按钮、当前选中状态、阅读焦点和极少量视觉强调**。严禁使用大面积品牌色背景铺满整屏或堆砌高饱和度渐变卡片。

| 语义令牌 | 浅色模式 | 深色模式 | 用途 |
| :--- | :--- | :--- | :--- |
| `--ds-brand` (燃灯橄榄墨绿) | `#1B4D3E` | `#3CA680` | 主操作按钮 (Primary CTA)、激活导航态、核心阿语强调 |
| `--ds-brand-hover` | `#143B2F` | `#4FC097` | 主按钮悬停/按压态 |
| `--ds-brand-soft` | `rgba(27, 77, 62, 0.08)` | `rgba(60, 166, 128, 0.14)` | 选中胶囊底色、焦点轻提示背景 |
| `--ds-gold` (哑光典籍金) | `#B08D40` | `#D1B062` | 文化徽章、古兰经/典籍腰封细线、键盘焦点环、收藏星标 |
| `--ds-gold-soft` | `rgba(176, 141, 64, 0.12)` | `rgba(209, 176, 98, 0.16)` | 书签高亮、重点词根标注底色 |
| `--ds-danger` | `#D70015` | `#FF453A` | 错误提示、生词删除、危险操作 |
| `--ds-success` | `#248A3D` | `#30D158` | 拼句正确、打卡完成、跟读达标 |
| `--ds-warning` | `#B25000` | `#FF9F0A` | 复习到期提醒、网络离线提示 |

### 1.3 深色模式 (Dark Mode — 独立分层重设计)

不能简单将白色反转为纯黑，必须通过灰度海拔（Elevation）建立层次：

| 语义令牌 | 色值 | 层级说明 |
| :--- | :--- | :--- |
| `--ds-bg` | `#0B0C0E` | 基础深邃背景（Level 0） |
| `--ds-bg-secondary` / `--ds-surface-2` | `#141619` | 次级区块背景（Level 1） |
| `--ds-surface` | `#1C1E22` | 卡片、列表容器表面（Level 2） |
| `--ds-surface-elevated` | `rgba(28, 30, 34, 0.86)` | 悬浮导航、模态框表面（Level 3） |
| `--ds-ink` | `#F5F5F7` | 主文字（高可读暖白，避免刺眼纯白 `#FFF`） |
| `--ds-ink-2` | `#A1A1A6` | 次文字（副标题、译文辅助说明） |
| `--ds-ink-3` | `#6E6E73` | 占位符与次要编号 |
| `--ds-line` | `#2C2E33` | 容器边框与主分割线 |
| `--ds-line-subtle` | `#222428` | 列表内部分割线 |

---

## 2. 字体与多语言排版体系 (Typography & BiDi System)

### 2.1 字体栈 (Font Stacks)

```css
:root {
  /* 中文与英文 UI：Apple 系统字体优先，跨平台优雅回退 */
  --ds-font-sans: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text",
                  "PingFang SC", "Hiragino Sans GB", "HarmonyOS Sans SC",
                  "Microsoft YaHei", "Noto Sans SC", system-ui, sans-serif;

  /* 中文长文阅读（古籍、译文、深度导读） */
  --ds-font-serif-cn: "Songti SC", "STSong", "Noto Serif SC", "Source Han Serif SC", serif;

  /* 阿拉伯语 UI 与短句（清晰现代、音符防碰撞） */
  --ds-font-ar-ui: "SF Arabic", "DubaiNur", "AmiriNur", "Geeza Pro", "Noto Naskh Arabic", serif;

  /* 阿拉伯语经典与长文阅读（古兰经、圣训、OpenITI 典籍） */
  --ds-font-ar-read: "ScheherazadeNur", "AmiriQuranNur", "AmiriNur", "SF Arabic", serif;

  /* 等宽字体（代码块、词根编号、快捷键） */
  --ds-font-mono: ui-monospace, "SF Mono", Menlo, Monaco, Consolas, monospace;
}
```

### 2.2 字号与行高阶梯 (Type Scale)

| 级别 | 令牌 | 字号 | 行高 | 字重 | 适用场景 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Hero Display** | `--ds-fs-hero` | `clamp(36px, 5vw, 56px)` | `1.08` | `700` (`-0.03em`) | 首页第一屏主标题「燃灯同学」 |
| **Section Title** | `--ds-fs-h1` | `clamp(28px, 3.4vw, 40px)` | `1.15` | `650` (`-0.02em`) | 首页大屏分节标题、频道主标题 |
| **Title 2** | `--ds-fs-h2` | `clamp(21px, 2.2vw, 28px)` | `1.24` | `600` (`-0.015em`) | 内容大区标题、模块副标题 |
| **Title 3** | `--ds-fs-h3` | `18px` | `1.35` | `600` | 卡片主标题、设置分组标题 |
| **Body Large** | `--ds-fs-lede` | `clamp(17px, 1.5vw, 20px)` | `1.65` | `400` | 首屏导语、专题引言 |
| **Body** | `--ds-fs-body` | `16px` | `1.65` | `400` | 标准中文正文、AI 对话正文 |
| **Subhead** | `--ds-fs-sub` | `14px` | `1.55` | `500` | 列表摘要、次级按钮、导航文字 |
| **Caption** | `--ds-fs-cap` | `12px` | `1.4` | `500` | 标签、眉题 (Kicker)、脚注、快捷键 |
| **Arabic Reader** | `--ds-fs-ar-read` | `clamp(22px, 2.6vw, 30px)` | `2.05` | `400` | 带完整音符 (Tashkeel) 的阿拉伯语原文 |

### 2.3 阿拉伯语 RTL 与中阿混排黄金准则

1. **零字距原则**：任何包含阿拉伯语的元素严禁设置非零 `letter-spacing`（必须强制 `letter-spacing: 0 !important`），防止阿拉伯字母连字（Ligatures）断裂。
2. **充足音符行高**：带音符（Fatha / Kasra / Damma / Shadda）的阿语文本，行高不得低于 `1.9`（阅读器中设为 `2.0 ~ 2.2`），避免上下行音符重叠裁切。
3. **双向文字隔离 (BiDi Isolation)**：
   - 独立阿语段落必须声明 `dir="rtl" lang="ar"`。
   - 中阿混排容器（如 AI 对话、语法解释、词典释义）中的阿语词组使用 `unicode-bidi: isolate`（`.nour-bidi`），段落使用 `unicode-bidi: plaintext`（`.nour-bidi-plaintext`），防止标点符号与括号错位。

---

## 3. 间距与栅格体系 (4px Spacing & Layout Grid)

### 3.1 4px 基础间距令牌

| 令牌 | 像素值 | 倍数 | 典型用途 |
| :--- | :--- | :--- | :--- |
| `--ds-sp-1` | `4px` | 1x | 图标与角标微距、行内标签内边距 |
| `--ds-sp-2` | `8px` | 2x | 紧凑按钮组间距、标题与副标题微距 |
| `--ds-sp-3` | `12px` | 3x | 表单控件内边距、列表项内部间距 |
| `--ds-sp-4` | `16px` | 4x | 移动端页面水平安全边距、标准卡片内边距 |
| `--ds-sp-5` | `20px` | 5x | 桌面端中等卡片内边距 |
| `--ds-sp-6` | `24px` | 6x | 模块内部网格间距、卡片外边距 |
| `--ds-sp-8` | `32px` | 8x | 大型内容卡片内边距、分栏间距 |
| `--ds-sp-10` | `40px` | 10x | 区块标题与内容区垂直间距 |
| `--ds-sp-12` | `48px` | 12x | 移动端大屏分节上下内边距 |
| `--ds-sp-16` | `64px` | 16x | 桌面端编辑式大屏分节垂直内边距 |
| `--ds-sp-20` | `80px` | 20x | 首屏 Hero 与重点章节呼吸留白 |

### 3.2 版心与响应式断点

- **最大编辑版心 (`--ds-max-width`)**：`1200px`（居中，两侧自适应安全留白 `clamp(16px, 4vw, 48px)`）。
- **最佳阅读版心 (`--ds-read-width`)**：`720px`（保证中文每行 34~42 字、阿拉伯语每行 55~70 字符的黄金视觉跨度）。
- **断点定义**：
  - **Mobile (`< 768px`)**：单栏流式布局 + 固定底部毛玻璃导航栏（避让 `env(safe-area-inset-bottom)`）。
  - **Tablet (`768px – 1023px`)**：双栏编辑网格 + 抽屉/分栏自适应。
  - **Desktop (`>= 1024px`)**：非对称编辑式多栏布局、左侧持久化导航/会话面板、居中宽幅阅读器。

---

## 4. 圆角、阴影与动效体系 (Shape, Elevation & Motion)

### 4.1 圆角阶梯
- `--ds-r-xs`: `6px`（键盘快捷键 `<kbd>`、小徽章）
- `--ds-r-sm`: `10px`（次要按钮、列表悬浮态、下拉菜单项）
- `--ds-r-md`: `14px`（输入框、搜索框、常规列表卡片）
- `--ds-r-lg`: `20px`（大型编辑式特性面板、模态弹窗）
- `--ds-r-xl`: `28px`（首页重点专题画布）
- `--ds-r-pill`: `999px`（主行动按钮、分段胶囊、底部悬浮导航）

### 4.2 阴影准则
摒弃廉价发光与厚重黑影，主要依靠 `#FFFFFF` 与 `#F5F5F7` 的背景色差及 `1px solid var(--ds-line)` 表达层级：
- `--ds-shadow-sm`: `0 1px 3px rgba(0, 0, 0, 0.04)`（轻微浮起卡片）
- `--ds-shadow-md`: `0 8px 24px rgba(0, 0, 0, 0.06), 0 1px 2px rgba(0, 0, 0, 0.04)`（悬浮工具栏、下拉菜单）
- `--ds-shadow-lg`: `0 20px 48px rgba(0, 0, 0, 0.12), 0 2px 6px rgba(0, 0, 0, 0.06)`（模态窗口、Apple Books 阅读器窗口）

### 4.3 自然动效与无障碍
- 缓动函数：`--ds-ease: cubic-bezier(0.22, 1, 0.36, 1)`（Apple 风格自然阻尼减速）。
- 时长：微交互 `160ms`，面板过渡 `260ms`。
- 完整支持 `@media (prefers-reduced-motion: reduce)`，开启后禁用一切位移动画。

---

## 5. 十大核心公共组件规范 (Component System)

1. **按钮 (Buttons)**：
   - Primary CTA：底色 `--ds-brand` (`#1B4D3E`)，文字 `#FFFFFF`，圆角 `999px`，最小触控高度 `44px`。
   - Secondary Action：底色 `#F5F5F7`（或透明带 `1px solid #D2D2D7`），文字 `#1D1D1F`，圆角 `999px`。
   - Text Link：无边框，文字 `--ds-brand`，附带微距右箭头 `›`。
2. **输入框 (Inputs & Textareas)**：高度 `>= 44px`，底色 `--ds-surface`，边框 `1px solid #D2D2D7`，聚焦时边框切换为 `--ds-brand` 并带 `3px` 柔和焦点环。
3. **导航栏 (Navigation)**：
   - 顶部品牌栏：安静呈现「燃灯同学 · حامل المصباح」与简洁快捷操作（搜索、主题切换、语言切换）。
   - 底部主导航：精致毛玻璃胶囊栏（首页、阅读、词典、学习、我的），当前项以橄榄绿高亮。
4. **弹窗与工作区 (Modals & Sheets)**：桌面端居中圆角工作台，移动端贴合手势习惯的 Sheet 视图，统一粘性头部 `.m-head`。
5. **下拉菜单与分段器 (Segmented Controls & Menus)**：采用 iOS/macOS 分段控制器风格（`#F5F5F7` 槽底 + `#FFFFFF` 滑块卡片）。
6. **编辑式内容区域与卡片 (Editorial Blocks & Cards)**：拒绝千篇一律的等大网格卡片，采用主次分明的主推大卡 + 紧凑列表项 + 专题长卷。
7. **标签与徽章 (Badges & Chips)**：克制使用哑光金与浅灰底色，仅承载分类、词性与学习状态。
8. **加载动画与骨架屏 (Skeletons & Loading)**：移除突兀旋转图标，统一使用柔和呼吸脉冲骨架条。
9. **提示信息 (Toast & Inline Notices)**：顶部/底部居中轻量胶囊提示，2.6 秒自动消隐。
10. **全局搜索框 (Spotlight Search)**：支持 `⌘K` / 点击呼出，集查词、句子、古兰经、世界图书馆于一体的极简搜索入口。
