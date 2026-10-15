# 右侧来源监测台发布记录

## 公网地址

<https://xn--dqry4os3s3gb.com/theme_workbench.html>

## 功能

右侧“来源记录”升级为“来源监测台”，从服务器上的白名单同步缓存读取真实状态：

- 显示最近同步时间、当前记录数、可用来源数、需复核数。
- 关键词过滤：来源名称、许可摘要、读取动作。
- 类型过滤：词典、例句、典籍、阅读、语音。
- 状态过滤：可用、需复核、待同步。
- 手动刷新只重新读取缓存，不从浏览器发起任意网站抓取。
- 每条记录显示中文名、原名、类型、状态、最近读取时间和许可说明。
- 有最新词典样例时显示一段受限样例，不复制整站内容。

## 后端边界

新增只读接口：`GET /api/theme/source-feed`。

接口读取 `data/public_source_cache/status.json` 和 `wiktionary-sample.json`，不执行网络请求，不接受用户传入 URL。实际来源同步仍由已有 `nur-public-source-sync.timer` 每周运行，保留：

- 官方白名单来源。
- 单请求 2 MiB 上限。
- 请求间隔 1.1 秒。
- 不下载整库。
- 不覆盖用户、会员、充值或 AI 数据。

## 当前公网结果

- `ar-wiktionary`：可用
- `tatoeba`：可用
- `openiti-release`：可用
- `arabic-wikipedia`：可用
- `common-voice-mdc`：可用
- 最近同步：2026-09-30 16:56:53 UTC

## 验收

- 本地 API 默认：5 条、5 条可用。
- 本地手机 UI：19/19。
- 本地桌面 UI：19/19。
- 公网手机 UI：19/19。
- 公网桌面 UI：19/19。
- 公网 `OpenITI` 关键词过滤：1 条。
- 公网“词典”类型过滤：1 条。
- 首页 HTTP 200。
- `/api/catalog/meta`：8794。
- `/api/books`：HTTP 200。
- `nur.service`、`nur-health-monitor.service`、`nur-public-source-sync.timer`：active。

## 回滚

本轮回滚点：`/opt/nur/backups/20261001-source-monitor`。

回滚需要恢复该目录中的 `server.py` 和 `theme_workbench.html`，再重启 `nur.service`。不会触碰 `data/public_source_cache`、用户数据、会员信息或 AI 配置。
