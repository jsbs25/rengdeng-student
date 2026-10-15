# 燃灯同学 2.0 · 阶段 1 一级导航适配层计划

**日期：** 2026-10-05  
**前置状态：** 阶段 0 已完成，核心基线 171/171 通过。  
**本轮状态：** 只生成计划，没有修改代码、HTML、数据、API 或公网服务。

---

## 1. 阶段 1 的唯一目标

把当前 NOUR 的四项产品导航：

```text
首页 / 书库 / NOUR AI / 我的
```

调整为附件要求的五项一级导航：

```text
首页 / 阅读 / 词典 / 学习 / 我的
```

本阶段只负责**一级入口和旧功能适配**，不重构书库、阅读器、词典内容、学习内容或 AI 后端。

---

## 2. 当前导航基线

### 2.1 生成器中的原始底栏

`build_home.py` 当前生成 5 个原始按钮：

```text
home      首页
learn     世界图书馆
search    搜索
wordbook  生词本
me        我的
```

`nav()` 当前支持：

```text
home  → page-home
learn → mCat
search → page-search
me    → page-me
ai    → aiSec
listen → search（旧别名）
```

### 2.2 当前 NOUR 适配层行为

`data/nour-product-shell.js` 当前会：

- 隐藏 `search`。
- 隐藏 `wordbook`。
- 将 `learn` 重命名为“书库”。
- 动态加入 `ai` 按钮。
- 保留 `nav()`、`showWordBook()`、`openSearchAll()`、`openDict()` 等旧函数。
- 通过 `NUR_ACTIVE_TAB` 和 `.nour-active` 管理状态。

因此当前测试脚本中存在两套历史合同：

- `nour_product_shell_ui_test.js`：期望四项 NOUR 导航。
- `nav_wordbook_ui_test.js`：仍期望旧的“首页 / 世界图书馆 / 搜索 / 生词本 / 我的”。

阶段 1 会把这两套合同统一为五项新导航，同时保留旧函数合同。

---

## 3. 阶段 1 的目标导航映射

| 一级按钮 | 对用户显示 | 内部虚拟路由 | 现有真实入口 | 说明 |
|---|---|---|---|---|
| 1 | 首页 | `home` | `nav('home')` | 保持当前 NOUR 首页工作台 |
| 2 | 阅读 | `read` | `nav('learn')` | 进入真实书库，底层旧 tab 名暂不改 |
| 3 | 词典 | `dict` | `openDict()` | 打开现有词典面板，阶段 4 再改内容形态 |
| 4 | 学习 | `study` | `openModal('mLearn')` | 打开已有句子库/学习入口，阶段 5 再扩展为学习工作台 |
| 5 | 我的 | `me` | `nav('me')` | 保留个人、设置、生词本、跟读、账户与会员 |

### 3.1 有意隐藏但不删除的入口

以下内容从一级导航移出，但仍保留原代码和现有路径：

- `NOUR AI`：从首页按钮、阅读器上下文、选词卡或“问问燃灯”入口进入。
- 全局搜索：从首页搜索按钮、书库搜索和快捷键进入。
- 生词本：从“我的”和阅读器词卡进入。
- 听力与跟读：从“学习”和“我的”进入。
- 语法、词法、闪卡、测验、挑战：从“学习”二级内容进入。
- 古兰经、六大部、法学、经典索引：从“阅读”二级内容进入。

**隐藏入口不删除功能，不删除数据，不改变原 API。**

---

## 4. 计划修改的文件范围

### 4.1 允许修改

#### `data/nour-product-shell.js`

只修改导航适配层：

- 将 `mountNav()` 从 `nour-four-nav` 改为五项 `nour-primary-nav`。
- 隐藏旧 `search` 与 `wordbook` 按钮。
- 将旧 `learn` 按钮转为 `read` 虚拟按钮。
- 动态增加 `dict` 和 `study` 两个按钮。
- 将原来动态加入的 `ai` 按钮移出一级导航，但保留 `openAI()` 函数和所有 AI 入口。
- 增加统一的 `openPrimaryRoute(route)` 适配函数。
- 增加 `NOUR_PRIMARY_ROUTE` 状态，不覆盖旧 `NUR_ACTIVE_TAB` 的既有含义。
- 将 `nav('learn')` 映射到显示为“阅读”的按钮。
- 将 `nav('me')` 映射到“我的”。
- `dict` 和 `study` 使用现有真实面板，不创造新数据。
- 保留 `nav('listen')` 旧别名，不影响历史调用。

#### `data/nour-product-shell.css`

只修改导航样式：

- `.tabbar.nour-four-nav` 改为兼容性的 `.tabbar.nour-primary-nav`。
- 5 项等宽布局，保持手机 44px 以上触控热区。
- 统一线性 SVG 图标，不增加 Emoji 图标。
- 当前项使用 `aria-current`、颜色和细线状态，不用大面积发光。
- 手机保留 `env(safe-area-inset-bottom)`。
- 桌面不遮挡正文和阅读器窗口。
- 保留旧 `.nour-four-nav` 兜底选择器一个回归周期，避免旧缓存页面出现断裂。

#### `tools/nour_product_shell_ui_test.js`

更新现有产品壳合同：

- 四项改为五项。
- 断言五个标签为：首页、阅读、词典、学习、我的。
- 断言 AI 不再占据一级导航。
- 断言搜索和生词本不在一级导航，但现有入口仍存在。
- 断言主页、阅读、词典、学习、我的均有可到达路径。

#### `tools/nav_wordbook_ui_test.js`

从旧导航回归改为阶段 1 兼容回归：

- 不再断言旧的“搜索 / 生词本”底栏。
- 断言五项新导航。
- 断言“我的 → 生词本”仍打开同一个 `mWordBook`。
- 断言“我的 → 跟读练习”仍打开同一个 `mListen`。
- 断言旧 `nav('search')`、`nav('listen')`、`showWordBook()` 仍工作。

### 4.2 生成文件

源文件修改并通过测试后，按现有流程重新生成：

```bash
python3 build_home.py
cp -p arabic_learning.html v3.html
```

生成的 `arabic_learning.html` 和 `v3.html` 是构建产物，不单独手写。

### 4.3 明确不修改

本阶段不修改：

- `server.py`
- `openiti_stream.py`
- `data/islamic_catalog.json`
- `data/library/*`
- `data/users.json`
- `data/codes.json`
- `data/ai_key.txt`
- 支付、会员、授权接口
- `/api/chat/message`
- `/api/page/analyze`
- 阅读器正文和页级分析逻辑
- 词典数据和学习数据
- `localStorage` 键名
- FastAPI、Uvicorn、React、Vue、Tailwind、Bootstrap 或 CDN

---

## 5. 兼容设计

### 5.1 不重命名底层路由

用户看到“阅读”，内部仍可调用：

```javascript
nav('learn')
```

这样不影响：

- 旧首页按钮。
- 书库经典入口。
- `NUR_LIBRARY_INITIAL_TAB`。
- `showHist()`、`showCatalog()` 和伊斯兰来源预选。
- 既有 `nav('learn')` 调用者。

### 5.2 不把词典和学习伪装成新页面

阶段 1 没有新词典页和学习工作台，因此：

- “词典”先打开既有 `mDict`。
- “学习”先打开既有 `mLearn` 句子库。
- 页面标题和深层内容暂不全面重写。
- 阶段 4、阶段 5 再分别重构词典和学习页面。

这样可以先完成导航信息架构，而不伪造尚未实现的功能。

### 5.3 AI 保持二级入口

- AI 工作区 `#aiSec` 保留。
- `openAI()` 保留。
- 首页“进入阅读助手”保留。
- 阅读器页级 AI 和选词 AI 保留。
- 只移除 AI 的底部一级按钮，不删除 AI 功能。

### 5.4 状态与无障碍

计划使用：

```text
window.NOUR_PRIMARY_ROUTE = home | read | dict | study | me
window.NUR_ACTIVE_TAB     = 现有底层 tab 状态
```

按钮必须保留：

- `aria-label`
- `aria-current="page"`
- 键盘可达
- 44px 以上手机触控区域
- 模态打开后焦点进入相应输入框

---

## 6. 阶段 1 测试计划

### 6.1 静态与构建检查

```bash
python3 -m py_compile server.py build_home.py
python3 build_home.py
cp -p arabic_learning.html v3.html
```

由于当前桌面没有 Node，不把 Node 当作必要依赖；使用真实浏览器运行时回归验证 JavaScript。

### 6.2 手机 390×844

检查：

- 五项导航完整可见。
- 标签不溢出、不重叠。
- 安全区不遮挡最后一项。
- 点击“阅读”进入书库。
- 点击“词典”打开 `mDict` 并自动聚焦。
- 点击“学习”打开 `mLearn`。
- 点击“我的”进入 `page-me`。
- 生词本和跟读仍从“我的”打开。
- 搜索仍能从首页入口打开。
- AI 仍能从首页/阅读器入口打开。

### 6.3 桌面 1280×900

检查：

- 五项导航不漂移。
- 不遮挡三栏阅读工作区。
- 书库和阅读器显示为主内容。
- 词典/学习面板不会让底部导航重复出现。
- 当前项状态和返回路径正确。

### 6.4 兼容回归

至少运行：

- `tools/nour_product_shell_ui_test.js`
- `tools/nav_wordbook_ui_test.js`
- `tools/nour_reader_window_ui_test.js`
- `tools/nour_word_context_ui_test.js`
- `tools/theme_bidi_ui_test.js`
- `tools/page_analysis_quran_test.js`
- `tools/classics_library_ui_test.js`

阶段 0 的 171/171 作为回归基线，阶段 1 不能降低既有通过率。

---

## 7. 发布与回滚计划

### 发布前

1. 备份当前远端：
   `/opt/nur/backups/20261005-phase1-primary-navigation`
2. 上传最小文件：
   - `data/nour-product-shell.js`
   - `data/nour-product-shell.css`
   - `arabic_learning.html`
   - `v3.html`
3. 远端 staging 预检。
4. 校验 HTML 包含五项导航和产品壳版本标记。
5. 不上传用户、会员、支付、缓存和 AI 密钥。

### 发布后

- 重启 `nur.service`。
- 检查 `nur.service` 和 `nur-health-monitor.service`。
- 检查 `/api/catalog/meta` 仍为 8,794。
- 运行公网手机/桌面导航回归。
- 打开真实书库、词典、学习入口和个人中心。

### 回滚

只恢复：

- `data/nour-product-shell.js`
- `data/nour-product-shell.css`
- `arabic_learning.html`
- `v3.html`

不回滚或覆盖任何数据文件。

---

## 8. 阶段 1 完成标准

阶段 1 只有在以下全部满足时才算完成：

- 一级导航严格为：首页 / 阅读 / 词典 / 学习 / 我的。
- AI、搜索、生词本不作为一级按钮，但仍可访问。
- 旧 `nav()`、生词本、跟读、阅读器和搜索函数继续可用。
- 词典真实打开 `mDict`，学习真实打开 `mLearn`，没有假页面。
- 手机和桌面回归全部通过。
- 阶段 0 的核心 API 和数据基线不变。
- 不引入 FastAPI、Uvicorn 或新的前端框架。
- 远端服务和健康监控保持 active。

**阶段 1 不包含首页五区重排、阅读器重构、词典内容重构、学习工作台重构或 AI 后端修改。**这些分别留到后续阶段。
