# NOUR AI 工作区视觉升级发布记录

**时间：** 2026-10-03（+03:00）  
**公网：** <https://xn--dqry4os3s3gb.com/>  
**范围：** 仅优化 NOUR AI 工作区视觉层与响应式布局，不删除或替换既有 AI 请求逻辑。

## AI 接入说明

- 普通聊天运行时已核验为 `https://api.deepseek.com/chat/completions`，模型 `deepseek-chat`。
- 逐页导读调用同一 DeepSeek 兼容链路；代码默认模型为 `deepseek-flash`，可由远端 `NUR_PAGE_AI_MODEL` 环境变量覆写。
- 实时语音是独立分支，代码默认使用 OpenAI Realtime `gpt-realtime-2.1`，语音 `marin`。
- 本报告不记录任何 API key、用户数据或会员信息。

## 本轮改动

- 新增 `data/nour-ai-polish.css`，将 AI 页从旧的全屏纵向表单改为安静的阅读助手工作区：
  - 桌面：左侧问题入口与模式区，右侧正文消息区，底部输入行；
  - 手机：标题、消息、快捷问题、输入区按单列排列；
  - 深墨绿、暖白、哑光金，细边界和 8px 卡片圆角；
  - 输入框聚焦、发送按钮 ready 状态和快捷问题保持原有业务行为。
- 追加与旧 `app-pages.css` 高优先级规则兼容的覆盖层，解决旧样式强制 `flex/0px` 覆盖新工作区的问题。
- `build_home.py` 末端注入精修层；生成 `arabic_learning.html` 和 `v3.html`。
- 未修改 `server.py`、AI endpoint、用户/会员数据、OpenITI 数据或健康监控逻辑。

## 测试结果

### 本地

- Python 编译：通过。
- AI 工作区手机 390×844：14/14。
- AI 工作区桌面 1280×900：14/14。
- NOUR 产品壳桌面：18/18。
- Apple Books 式阅读器与上下文桥接：18/18。
- OpenITI 流式阅读手机回归：16/16。
- 古兰经逐页 AI：分析请求完成，原文、阿拉伯语正文、分析面板和语言切换状态正常。

### 公网

- 手机 AI 工作区：14/14。
- 桌面 AI 工作区：14/14。
- `/`：200。
- `/api/catalog/meta`：200。
- `/api/books`：200。
- `/api/dict/lookup`：200。
- `/api/quran/tafsir`：200。
- 两部此前返回 413 的 OpenITI：流式首页均 200。

## 发布与回滚

- 远端服务：`nur.service` active。
- 健康监控：`nur-health-monitor.service` active。
- 独立回滚点：`/opt/nur/backups/20261003-ai-polish`。
- 发布方式：暂存目录校验、原子移动文件、重启服务、源站和公网回归。
- 本轮没有创建新的自动爬取任务，也没有扩大来源同步范围。
