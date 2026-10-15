# 燃灯同学 / NOUR 2.0 阶段 7A-2：剩余大数据按需加载发布记录

**发布日期：** 2026-10-06  
**公网：** https://xn--dqry4os3s3gb.com/  
**状态：** 已发布并完成公网验收  
**回滚点：** `/opt/nur/backups/20261006-phase7a2-lazy-data-modules`

## 本轮目标

在不删除既有功能和数据的前提下，把首屏仍会请求的内置大数据模块改为“进入功能时才加载”：

- 精选书籍：`builtin_books.js`
- 古兰经：`builtin_quran.js`
- 圣训数据：`builtin_hadith.js`
- 词汇：`builtin_vocab.js`
- 历史文章：`builtin_history.js`
- 句子库：延续 7A-1 已完成的按需加载

保留原有全局变量、入口函数、数据格式、阅读器和 AI 上下文桥接。没有改动 AI prompt、DeepSeek 配置、用户/会员/支付、密钥、OpenITI/Shamela 正文缓存或健康监控。

## 实现

`build_home.py` 现在内联一个统一的 `NOUR_loadDataAsset(kind)` Promise 加载器：

- 资源文件使用 `NOUR_ASSET_VERSION` 查询参数。
- 同一资源的并发或重复入口复用同一个 Promise，不重复插入 `<script>`。
- 首屏只初始化空数组；数据脚本不再作为启动阶段 `<script defer>` 标签下载。
- 书籍、古兰经、圣训、词汇、历史和句子入口在实际打开前等待对应资源。
- 全局搜索的句子、词汇和古兰经筛选，以及单词闪卡，均会在使用前等待资源。
- 首页古兰经与入门词汇视图同步使用同一加载器。

历史模块在当前项目真实数据文件中是空数组（`window.BUILTIN_HISTORY=[]`），本轮只保证请求、初始化和入口路径正常，没有制造历史内容。

## 真实性能基线

数据见：[`docs/20261006-phase7a2-performance-baseline.json`](20261006-phase7a2-performance-baseline.json)。这是一次有界只读测量，不是 SLA，也未调用 AI、认证、支付、TTS、ASR 或写接口。

| 指标 | 7A-2 公网实测 |
|---|---:|
| 首页状态 / 压缩传输 | `200` / 约 `544,008 B` |
| 首页单次延迟 | `748.46 ms` |
| 启动阶段资源 | `13` 项 |
| 延后资源 | `6` 项 |
| `/api/catalog/meta` | `200` / `136.42 ms` |
| `/api/catalog?page=1&size=60` | `200` / `112.94 ms` |
| `/api/library/classics?size=5` | `200` / `112.78 ms` |
| `/api/dict/lookup?w=كتاب` | `200` / `194.46 ms` |
| 词典本地暖缓存 P50 | `2.544 ms` |
| 词典本地冷启动 P50 | `26.361 ms` |

与 7A-1 相比，首屏版本化资源清单从 **18 项降至 13 项**；书籍、古兰经、圣训、词汇、历史和句子共 **6 项**转为真正的 deferred 资源。它们仍可通过真实公网 URL 加载，且服务器返回 `public, max-age=604800, immutable` 与 ETag。

公网延后资源实测：

| 资源 | 状态 | 传输字节 |
|---|---:|---:|
| `builtin_sentences.js` | 200 | `1,550,866` |
| `builtin_books.js` | 200 | `644,648` |
| `builtin_quran.js` | 200 | `619,297` |
| `builtin_vocab.js` | 200 | `138,006` |
| `builtin_hadith.js` | 200 | `747` |
| `builtin_history.js` | 200 | `54` |

## 回归结果

### 本地 127.0.0.1:8139

- 按需资源合同：手机/桌面均无失败项；每类资源均按入口请求、带版本参数、复用 Promise。
- 句子：`29,740` 条真实数据加载。
- 书籍：`4` 条真实内置数据加载；服务器书库 API 仍作为后续数据源。
- 古兰经：`114` 章真实数据加载。
- 圣训：`2` 条当前内置数据加载。
- 词汇：`26,386` 条真实数据加载。
- 历史：真实空数组加载，不以假数量代替。
- 首页：手机 `11/11`、桌面 `11/11`。
- 一级导航：手机 `25/25`。
- 阅读器：手机 `21/21`、桌面 `21/21`。
- 学习工作台：手机 `10/10`。
- 主题与中阿混排：手机 `12/12`。
- 教法证据链：手机/桌面均 `10/10`。
- 经典索引：`1820` 条、无重复、全部有 Shamela 阅读路径。
- 古兰经页级导读：`7/7`。
- OpenITI 流式离线回归：通过。

### 公网 `https://xn--dqry4os3s3gb.com/`

- `/api/catalog/meta`：`200`，`total=8794`。
- `/api/library/classics?size=2`：`200`。
- `/api/library/fiqh-schools?size=2`：`200`。
- `/api/read?t=shamela&id=8220`：`200`，保留《مختصر القدوري》真实全文路径。
- 按需资源合同：手机与桌面均无失败项。
- 古兰经页级入口：手机 `7/7`。
- 首页：手机 `11/11`。
- Apple 风格阅读器：手机 `21/21`。

## 保护与回滚

本轮没有删除书籍、词汇、经文、圣训、音频、AI、学习记录或用户数据，也没有覆盖 `data/ai_key.txt`、支付、用户、充值、解锁或缓存正文。

如需回滚，恢复上述独立备份中的文件后重启：

```bash
systemctl restart nur.service
systemctl is-active nur.service
systemctl is-active nur-health-monitor.service
```

健康监控配置没有纳入替换范围，发布后 `nur.service` 与 `nur-health-monitor.service` 均为 `active`。

## 本轮交付文件

- `build_home.py`
- `arabic_learning.html`
- `v3.html`
- `data/views2.js`
- `data/builtin_*.js`
- `tools/phase7_asset_loading_ui_test.js`
- `tools/page_analysis_quran_test.js`
- `tools/performance_baseline.py`
- `docs/20261006-phase7a2-performance-baseline.json`
