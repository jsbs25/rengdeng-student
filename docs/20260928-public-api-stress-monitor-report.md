# 公网 8,794 本书目与 API 压力测试 / 运行监控报告

**项目：** 燃灯同学  
**域名：** `https://xn--dqry4os3s3gb.com`  
**测试时间：** 2026-09-28T20:18:24.642408+00:00 → 2026-09-28T20:19:10.040439+00:00（UTC）  
**测试原则：** 低速、有界、只读；不触碰登录、支付、会员、用户数据、管理员接口，也不触发真实 AI/TTS/ASR/媒体转码。

## 结论

- **公网服务状态：正常。** `nur.service` 与 `nur-health-monitor.service` 均为 `active`。
- **目录完整性：通过。** 8,794 条目、147 个分页全部返回；唯一 ID 8,794；缺失 ID 0；缺失标题 0。
- **API 压力结果：0 个未预期失败。** 共 233 个请求：231 个常规通过，2 个被明确识别为超大原文保护，未预期失败 0 个。
- **监控最新记录：绿色。** 公网首页和关键接口全部 200；目录总量 ≥ 8,794；六大部圣训接口返回 ≥ 6 条；本地服务健康检查 200。

## 压力测试参数

| 项目 | 值 |
|---|---:|
| 全局请求速率 | 6.0 req/s |
| 并发工作线程 | 4 |
| 目录分页大小 | 60 |
| 目录分页数量 | 147 |
| API 探测轮数 | 3 |
| 单请求超时 | 30.0 s |
| 延迟 P50 | 158.46 ms |
| 延迟 P95 | 1004.11 ms |
| 延迟 P99 | 2089.3 ms |
| 最大观测延迟 | 3873.95 ms |

## 书目与应用内原文

- 元数据分页：`8794/8794` 条目，全部返回。
- 可内置原文：`8756` 条，抽样 `16` 条。
- 抽样结果：常规 200 响应 **14** 条；超大原文保护 **2** 条。
- `openiti-b189390ada0b10e0`、`openiti-23f3107332aec56a` 返回 413，原因是服务端的 **12 MB 原文保护阈值**；这不是网络故障，避免一次请求下载过大的原文文件。
- 元数据/官方外链书目：`38` 条（例如《الرسالة》）；测试器不会把它们误送入 OpenITI 内置全文接口，应用应按其官方 BookReader/来源链接处理。

## 覆盖的安全接口类别

- 首页与健康：`/`、`/api/home_stats`
- 世界图书馆：`/api/catalog/meta`、`/api/catalog` 全 147 页、`/api/catalog/read` 原文抽样
- 伊斯兰内容：`/api/islamic/search?source=sunnah&q=`、`/api/quran/tafsir`
- 书籍与学习数据：`/api/books`、`/api/articles`、`/api/sentences`、`/api/vocab`、`/api/plans`、`/api/videos`、`/api/history`、`/api/cnbooks`、`/api/cnbook`
- 音频：`/api/audio/library`、抽取到的本地音频文件响应
- 状态查询：`/api/asr/status`、`/api/nodes`、`/api/access/status`、`/api/ai/quota`、`/api/pay/status`
- 无效载荷校验：`/api/page/analyze`、`/api/realtime/session`、`/api/chat/stream_voice`、`/api/asr` 仅发送空/无效载荷并预期 400；没有触发上游模型或扣费。

## 持续运行监控

已部署 systemd 服务：`nur-health-monitor.service`，每 **60 秒**执行一次：

- 公网首页、目录元数据、目录第一页、`/api/books`、六大部书目、古兰经经注；
- 本机 `127.0.0.1:8080/api/home_stats`；
- `nur.service` active 状态；
- VPS 负载、内存、磁盘；
- 日志写入 `/var/log/nur-monitor/health.jsonl`，当前状态写入 `/var/log/nur-monitor/latest.json`；日志超过 10 MB 自动保留最近 5,000 行。

最新监控条件：

```json
{
  "service_active": true,
  "public_http_all_200": true,
  "local_http_200": true,
  "catalog_total_8794": true,
  "sunnah_total_6": true
}
```

本轮远端回滚点：`/opt/nur/backups/20260928-public-api-monitor`。

## 明确未覆盖 / 未执行

为了避免副作用，本轮没有压测真实聊天、逐页 AI、TTS、ASR 上传、Realtime、支付/会员、登录、管理员和会写入数据的接口；也没有批量下载 8,794 部全文。压力测试验证的是完整书目索引、可内置阅读路由抽样及所有安全只读接口的稳定性。
