## Design Concept
本演示为技术复盘与管理汇报场景。视觉锚点结合“学术图书馆”的克制排版与“高管级汇报”的数据严谨性，借用前者大量留白与衬线标题的典雅，以及后者以数据为核心、结论先行的模块化信息密度。色彩体系摒弃了技术总结滥用的“霓虹科技蓝”陈词滥调，严格遵循NOUR品牌契约：色温偏暖，以象牙白（Ivory）作为全局背景营造纸质阅读体验，深墨绿（Ink Green）作为主色及文字色提供沉稳的骨架，哑光金（Matte Gold）作为点缀色仅用于核心数据高亮与图表强调。字体策略采用经典的衬线与无衬线搭配，标题使用 Noto Serif SC 传递学术级的严谨与权威感，正文与数据使用 Noto Sans SC 确保屏幕显示的极致清晰度。

## Visual Language
*   **Imagery**: 绝对无照片、无装饰性配图。全盘采用系统架构图、流程图与真实监控数据图表，确保每寸像素均服务于信息传递。
*   **Containers**: 留白优先（Whitespace-first）。拒绝厚重的实色卡片，采用极细的墨绿或灰白单线边框（1px solid）来划分信息区块，维持页面通透感。
*   **Icons**: 极简风格（Minimal），仅在健康检查通过、警告等状态指示时使用实心小尺寸图标，禁止使用大尺寸装饰性图标。
*   **Dataviz**: 表格采用学术期刊规范（仅保留顶线、底线与表头下线，无垂直分割线）。图表（Chart.js）配色以哑光金为当前波次/核心指标，深墨绿为对比基线/次要指标。
*   **Motif**: “哑光金方块”（■）。在每页标题左侧放置一个 8x8px 的哑光金小方块，作为视觉锚点与品牌印记，确保页页连贯。

## Layout Directives
*   **Global**: 页面边距统一为 48px。左对齐排版为主，页面底部固定包含页码与极为隐蔽的机密性/来源说明。采用严格的网格对齐。
*   **Cover**: 极简学术排版，大面积象牙白留白，标题居中偏上，深墨绿衬线体，下方紧跟一行哑光金副标题。
*   **Table of Contents**: （本大纲无目录页）。
*   **Section Dividers**: （本大纲无过渡页）。
*   **Closing**: （本大纲无传统致谢页，以 Roadmap 收尾替代）。
*   **Slide Map**:

| id | pattern | image | density |
| :--- | :--- | :--- | :--- |
| cover | 居中大标题与留白 | none | low |
| health | 结论先行 + 极简状态表格 | none | medium |
| singleflight | 架构对比图 + 核心机制说明 | none | medium |
| latency | 核心数据指标 + 多系列柱状图 | none | high |
| optimization | 阶段流程图 + 逐项优化列表 | none | high |
| experience | 双端对比清单 + 交互日志代码块 | none | medium |
| ui | 全局契约细则 + 矩阵式规格表 | none | high |
| roadmap | 路线图时间轴 + 里程碑数据点 | none | medium |

## Design Tokens
*   **Colors**:

| token | hex | usage |
| :--- | :--- | :--- |
| brand-ivory-bg | #FAF8F5 | 全局页面背景，提供温和纸质感 |
| brand-ink-primary | #1A3629 | 主标题、强调性边框、核心结构线 |
| brand-gold-accent | #C1A673 | 核心数据高亮、图表主系列、Motif方块 |
| text-primary | #2C3E35 | 正文主体文字，略浅于主色以区分层级 |
| text-secondary | #5C6E64 | 辅助说明、图表标签、表头提示词 |
| surface-tint | #F0EFEA | 局部代码块或次要信息底色，微弱对比 |
| border-subtle | #D9D6CE | 表格横线、区块分割线 |
| chart-series-2 | #4A6B58 | 图表中作为基线或次要指标的辅助绿色 |

*   **Text Roles**:

| role | family | size (px) | applies_to |
| :--- | :--- | :--- | :--- |
| display | Noto Serif SC | 48 | 封面主标题 |
| heading | Noto Serif SC | 32 | 每页顶部结论性标题 |
| metric | Noto Sans SC | 40 | 核心监控数据（如并发数、P95延迟） |
| body | Noto Sans SC | 18 | 段落正文、列表项 |
| caption | Noto Sans SC | 14 | 图例、表格注脚、页码 |

## Guardrails
*   **禁止使用任何照片或插图**：严格遵守无照片要求，用数据与图表填补视觉重心。
*   **禁止使用任何动画效果或过渡动效**：维持极度克制、静态的审阅体验。
*   **禁止使用圆角与阴影**：所有容器与图表元素必须使用直角（0px border-radius），彻底抛弃互联网卡片化阴影。
*   **禁止出现科技蓝或渐变色**：严格锁死墨绿与哑光金的纯色搭配。
*   **字号底线**：正文绝对不可小于 18px，图表内坐标轴标签与图例不可小于 12px。
