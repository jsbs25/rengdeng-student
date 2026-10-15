# 燃灯同学 / NOUR 2.0 阶段 1：一级导航适配发布记录

**发布日期：** 2026-10-05  
**公网：** https://xn--dqry4os3s3gb.com/  
**回滚点：** `/opt/nur/backups/20261005-phase1-primary-navigation-v1`

## 本阶段目标

在不删除旧页面、旧函数或旧数据的前提下，将产品壳的一级导航收敛为五项：

> 首页 · 阅读 · 词典 · 学习 · 我的

搜索和生词本仍保留原有 DOM 与业务函数，作为全局/个人中心入口；NOUR AI 继续由首页工作台和阅读语境入口进入，不占用底部一级导航。

## 实现范围

- `data/nour-product-shell.js`
  - 新增 `home/read/dict/study/me` 路由适配状态和 `aria-current`。
  - “阅读”调用既有 `nav('learn')`，不替换书库逻辑。
  - “词典”调用既有 `openDict()`。
  - “学习”先复用既有 `detachModal('mLearn')`，再打开 `mLearn`，避免它留在隐藏父级中出现零尺寸。
  - “我的”调用既有 `nav('me')`。
  - 保留原 `nav()`、搜索、生词本、跟读、AI 和阅读器函数。
- `data/nour-product-shell.css`
  - 为五项导航提供固定底栏、触控尺寸、焦点态和手机安全区样式。
  - 保留旧 `nour-four-nav` 选择器作为缓存安全回退，不删除历史样式。
- `arabic_learning.html`、`v3.html`
  - 由既有 `python3 build_home.py` 重新生成并同步。
- `tools/nour_product_shell_ui_test.js`
  - 增加五项导航、真实书库/词典/学习/个人中心、首页搜索与手机/桌面布局合同。
- `tools/nav_wordbook_ui_test.js`
  - 验证生词本、跟读练习、旧搜索和旧 `nav()` 别名仍可进入原有面板。

## 验收结果

### 本地

- Python 编译：通过（`server.py`、`build_home.py` 及相关测试脚本）。
- 经典索引完整性：通过，1,820 条、无重复、均有 Shamela 可读入口。
- OpenITI 流式核心：通过，包含增量 UTF-8、Range、EOF 和断点续读断言。
- 浏览器回归：**216/216 通过**，覆盖 390×844 与 1280×900：
  - 一级导航/旧入口：五项脚本合同全部通过。
  - 经典索引、教法证据链、四学派阅读室：通过。
  - 日夜主题、中阿混排、苹果式阅读器、古兰经页级导读：通过。
- 桌面终端没有 `node` 可执行文件，`node --check` 返回环境状态 127；生成 HTML 已被真实浏览器成功加载并执行，相关 JavaScript 合同回归无运行时错误。

### 公网

- `/api/catalog/meta`：`total=8794`，未改变既有目录基线。
- `/api/library/classics?collection=fiqh`：真实法学索引返回 `total=283`。
- `/api/library/fiqh-schools`：四个学派入口均返回。
- `/api/read?t=shamela&id=8220`：真实《مختصر القدوري》返回 **239 页**，首屏正文 `body` 非空。
- 公网浏览器回归：**129/129 通过**，覆盖手机/桌面产品壳、兼容入口、经典索引、四学派阅读室、真实 Shamela 阅读器和古兰经入口。
- `nur.service=active`；`nur-health-monitor.service=active`。

## 数据与安全边界

本次发布未覆盖或迁移：

- `data/ai_key.txt`
- 用户、会员、充值、支付、解锁数据
- 词典、经文、圣训、OpenITI、Shamela 缓存
- 8,794 条既有目录和 1,820 条经典索引
- 监控配置和 systemd 服务定义

生产替换前已完成远端独立备份；若需回滚，恢复上述回滚点中的四个文件后重启 `nur.service` 即可。

## 阶段状态

阶段 1 一级导航适配已完成并上线。下一阶段仍应在当前稳定版本上增量推进，继续复用真实数据和旧业务路径，不进行全量技术栈迁移。
