# NOUR 全站界面与稳定性升级记录

日期：2026-10-18

## 范围

本轮按“全站审计 → 页面契约 → 稳定性修复 → 本地回归 → 最小发布 → 公网验收”执行。没有引入 React、Vue、jQuery、Bootstrap 或 Tailwind，没有删除既有 API、数据文件、用户逻辑、AI、阅读器、词典、古兰经、圣训和学习入口。

## 页面层升级

新增并继续使用 `data/nour-clarity.css` 作为最后的可回滚视觉层。书库、搜索、我的和 AI 页面统一使用米白纸面、深橄榄绿、哑光金和细分隔线；书库卡片保留视觉化书籍封面，但取消高亮放大、重阴影和深色玻璃表面。搜索和个人中心统一为单列内容区。普通功能弹窗统一标题栏、背景、边界和按钮圆角，`mReader` 与焦点阅读器被明确排除，保留 Apple Books 风格的沉浸窗口。

本轮没有删除任何入口。底部导航、世界图书馆、搜索、我的、AI、词典、古兰经、六大部、书目导读、主题设置、生词本和学习工具仍由原有真实函数驱动。

## 稳定性修复

`data/nour-focus-workspace.js` 原先通过 `setTimeout(0)` 延迟添加焦点工作区状态，打开 AI 或页面时会出现一个短暂的输入区与底部导航重叠帧。现在导航和普通工作区弹窗在原函数返回后同步标记焦点状态，MutationObserver 仍保留为兜底。AI 全屏工作区不再出现打开瞬间跳动。

完整句子库此前虽然按需加载真实资源，但会在 `renderAllS()` 中把约 3.4 万条句子一次性创建为 DOM 节点，导致移动浏览器卡顿并让回归测试超时。现在 `build_home.py` 保留完整 `ALL_SENTENCES` 数组和全量搜索，只渲染首批 80 条；用户点击“加载更多”后按每批 80 条追加。搜索仍扫描完整数组，不会只搜索当前可见批次。新增 `.s-more` 样式，按钮符合全站纸面契约。

## 本地回归

构建与静态检查通过：

- `python3 -m py_compile server.py build_home.py openiti_stream.py tools/nodes_daily_api_test.py tools/public_api_stress.py`
- `python3 build_home.py`
- `git diff --check`

页面回归结果：

| 区域 | 结果 |
|---|---:|
| 首页手机 | 13/13 |
| 首页桌面 | 13/13 |
| 产品壳与导航 | 25/25 |
| 焦点工作区 | 17/17 |
| 阅读器手机 | 21/21 |
| 主题与 RTL | 12/12 |
| AI 视觉工作区 | 14/14 |
| 词典 | 10/10 |
| 按需资源和句子库 | 31/31 |

按需资源专项验证了首屏不加载大数据、主动入口按需加载版本化资源、句子数组真实载入、可见 DOM 不超过首批 80 条、加载更多能渲染下一批、搜索能命中完整数组，以及重复打开会复用已加载 Promise。

## 公网发布

线上回滚目录：`/opt/nur/releases/20261018-fullsite-clarity-bounded-1950UTC`

本次仅替换以下运行文件：

- `/opt/nur/build_home.py`
- `/opt/nur/arabic_learning.html`
- `/opt/nur/v3.html`
- `/opt/nur/data/nour-clarity.css`
- `/opt/nur/data/nour-focus-workspace.js`

没有替换线上已有的句子、词典、古兰经、书目或用户数据资产；本地数据资产与线上版本存在差异，本轮按最小发布边界保留线上数据。

## 公网验收

- `/`：HTTP 200，约 1,965,699 bytes。
- `/api/sentences/daily`：HTTP 200，199 bytes，真实今日句子存在且小于 10 KB。
- `/api/nodes`：HTTP 200，175 bytes，后台刷新状态快速返回。
- `/api/catalog/meta`：HTTP 200，目录总数 8,794。
- 公网手机首页：13/13。
- 公网桌面首页：13/13。
- 公网按需资源与句子库：31/31。
- `nur.service`：active，`NRestarts=0`。
- `nur-health-monitor.service`：active，enabled。

## 回滚

恢复 `/opt/nur/releases/20261018-fullsite-clarity-bounded-1950UTC/` 中的 `build_home.py`、`arabic_learning.html`、`v3.html`、`data/nour-clarity.css` 和 `data/nour-focus-workspace.js` 即可回到发布前版本。回滚后执行 `systemctl restart nur.service`。本轮句子库有界渲染的本地备份位于 `.manus-backups/20261018-sentence-bounded-render/build_home.py`。
