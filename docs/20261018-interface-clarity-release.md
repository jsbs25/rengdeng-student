# NOUR 界面清晰度更新记录

日期：2026-10-18

## 本轮目标

在不删除旧功能、不改变数据接口、不触碰阅读器业务逻辑的前提下，降低首页视觉噪声。首页现在按“标题 → 继续阅读 → 今日一句 → NOUR AI → 更多工具”组织，功能入口仍然存在。

## 实现内容

- 新增 `data/nour-clarity.css`，作为独立、可回滚的最后视觉层。
- 任务条由发光卡片改为细线索引条；四个既有动作仍然可点击。
- 移除首页发光环和顶部快捷装饰按钮的视觉占位，不删除快捷指令逻辑。
- 继续阅读、AI 发现、阅读数据、工具索引改用分隔线与留白，减少嵌套卡片和阴影。
- 今日一句改为纸面式左侧金线，不改变 `/api/sentences/daily` 或完整句子库加载逻辑。
- 首页 AI 保留原输入、上下文和发送逻辑，仅去掉额外仪表盘框架。
- 移动端统计区改为两行两列，保留四个真实统计值。
- 底部导航改为小型实体导航条，保留原有导航路径和安全区。
- `build_home.py` 增加 `nour-clarity` 最高优先级样式注入。

## 本地验证

- `python3 -m py_compile server.py build_home.py openiti_stream.py`：通过。
- `python3 build_home.py`：通过，生成首页约 1.9 MB。
- `git diff --check`：通过。
- 手机首页回归：13/13 通过。
- 桌面首页回归：13/13 通过。
- 主题/RTL/夜间模式：12/12 通过。
- 古兰经入口：8/8 通过。
- Mac Apple Books 阅读窗口：21/21 通过。

## 线上发布

发布回滚目录：`/opt/nur/releases/20261018-interface-clarity-1625UTC`

仅替换：

- `/opt/nur/build_home.py`
- `/opt/nur/arabic_learning.html`
- `/opt/nur/v3.html`
- `/opt/nur/data/nour-clarity.css`

没有替换用户、会员、支付、AI 密钥、缓存或监控配置。

## 公网验收

- `/`：HTTP 200，约 1,956,172 bytes，包含 `nour-clarity`。
- `/api/sentences/daily`：HTTP 200，199 bytes，真实今日句子存在，响应小于 10 KB。
- `/api/catalog/meta`：HTTP 200，目录总数 8,794。
- `/api/nodes`：HTTP 200，199 bytes，快速返回并显示后台刷新状态。
- 公网手机首页：13/13 通过。
- 公网桌面首页：13/13 通过。
- `nur.service`：active，`NRestarts=0`。
- `nur-health-monitor.service`：已恢复为 `enabled` 且 `active`。

## 回滚

恢复 `/opt/nur/releases/20261018-interface-clarity-1625UTC/` 中的三个旧页面/构建文件；若要完全移除本轮样式，删除 `/opt/nur/data/nour-clarity.css` 并恢复旧页面产物即可。服务重启后旧版本恢复。
