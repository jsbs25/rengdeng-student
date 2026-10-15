# NOUR 阶段 7A-0：性能基线报告

**测量时间：** 2026-10-06 19:08 UTC  
**公网：** `https://xn--dqry4os3s3gb.com`  
**范围：** 只读；未调用 AI、登录、支付、TTS、ASR 或任何写接口

## 结论

公网关键请求全部返回 200，当前服务可用；但已经看到三个明确的性能治理目标：

1. **首页响应仍为无缓存策略。** 公网首页压缩后约 543 KB、单次测量约 721 ms；响应头是 `no-store, no-cache`，没有 ETag 或 Last-Modified。
2. **三个大内置脚本仍会被页面启动阶段请求。** 句子、书籍、古兰经脚本压缩传输合计约 2.42 MB；它们并非所有首页用户都立即需要。
3. **静态资源缓存头互相冲突。** 大脚本同时出现 `no-store, no-cache, max-age=0` 和 `max-age=604800`；浏览器通常会优先按 no-store 处理，因此“七天缓存”没有稳定生效。

本地查词函数本身的 Python 热路径已经很快，但公网 `/api/dict/lookup` 的一次测量为 **173.58 ms**，下一步仍应将句子例句索引化，并在真实冷启动/公网重复测试中确认收益。

## 公网 API 测量

| 请求 | 状态 | 压缩后字节 | 延迟 |
|---|---:|---:|---:|
| `/` | 200 | 543,483 | 720.83 ms |
| `/api/home_stats` | 200 | 258 | 1,016.43 ms |
| `/api/catalog/meta` | 200 | 2,507 | 135.95 ms |
| `/api/catalog?page=1&size=60` | 200 | 11,021 | 127.82 ms |
| `/api/library/classics?size=5` | 200 | 1,721 | 127.02 ms |
| `/api/library/fiqh-schools?size=5` | 200 | 15,174 | 148.49 ms |
| `/api/dict/lookup?w=كتاب` | 200 | 774 | 173.58 ms |

这是单次有界测量，不是 SLA；首页和 `home_stats` 的延迟需要在多轮低速测量中复核。

## 静态资源测量

| 资源 | 压缩后字节 | 延迟 | 当前缓存头摘要 |
|---|---:|---:|---|
| `builtin_sentences.js` | 1,152,452 | 695.42 ms | `no-store...max-age=0, max-age=604800` |
| `builtin_books.js` | 644,648 | 988.85 ms | `no-store...max-age=0, max-age=604800` |
| `builtin_quran.js` | 619,297 | 612.05 ms | `no-store...max-age=0, max-age=604800` |
| `builtin_vocab.js` | 115,217 | 301.24 ms | `no-store...max-age=0, max-age=604800` |
| `views2.js` | 11,832 | 114.88 ms | `no-store...max-age=0` |
| `upgrade2.css` | 3,384 | 311.73 ms | `no-store...max-age=0` |
| `library2.css` | 3,690 | 122.61 ms | `no-store...max-age=0` |
| `paper-v3.css` | 1,649 | 333.37 ms | `no-store...max-age=0` |

所有上表资源均为 200；大资源均启用了 gzip。测量脚本从生成 HTML 的 `src/href` 中提取资源，因此反映的是当前真实构建产物，而不是手工猜测。

## 本地查词测量

测试读取真实 `vocab_meanings.json` 和 `data.json`，没有发起外部词典或模型请求。

| 情况 | 样本数 | P50 | 最大值 |
|---|---:|---:|---:|
| 同一进程暖缓存 | 25 | 2.501 ms | 48.559 ms |
| 每次新进程冷启动 | 8 | 25.101 ms | 26.694 ms |

暖缓存第一次命中会触发本地数据载入，后续查词较快；当前函数仍会在例句查找阶段扫描内存中的句子列表。索引化的价值主要是降低数据规模继续增长后的尾延迟和内存重复风险，而不是宣称当前查词已经不可用。

## 阶段 7A-1 的第一处改动

基于本次结果，下一轮只做一个低风险切片：

- 给静态资源增加内容版本标识；
- 将带版本的 JS/CSS 设为可缓存；
- 保持 HTML 和所有用户/支付/AI 状态接口不缓存；
- 修正 `no-store` 与 `max-age` 同时出现的冲突；
- 先只迁移一个大资源到按需加载，并验证旧全局变量和离线兜底；
- 不同时修改词典 UI、AI prompt、阅读器或数据文件。

完成后用手机和桌面浏览器复测冷启动、二次刷新、首页、书库、古兰经和旧导航。若任一旧功能失败，先回滚性能切片，再继续词典索引。

## 测试产物

- 原始聚合数据：`docs/20261006-phase7-performance-baseline.json`
- 执行脚本：`tools/performance_baseline.py`
- 总体执行计划：`docs/20261006-phase7-performance-dictionary-plan.md`
