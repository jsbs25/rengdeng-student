# 燃灯同学 / NOUR 2.0 阶段 7A-1：缓存策略与句子库按需加载发布记录

**发布日期：** 2026-10-06  
**公网：** https://xn--dqry4os3s3gb.com/  
**状态：** 已发布并完成公网验收  
**回滚点：** `/opt/nur/backups/20261006-phase7a1-cache-lazy-assets`

## 本轮目标

针对阶段 7A-0 发现的三个问题做低风险切片：

- HTML 继续实时验证，不给页面壳和用户状态使用长期缓存。
- 带构建版本号的 JS/CSS/静态资源使用长期缓存、ETag、Last-Modified 和条件请求。
- 把 4.6 MB 的句子库从首屏脚本标签改为首次进入句子库、查找句子、听力或闪卡时按需加载。

没有更换 Python 服务栈，没有修改 AI prompt、阅读器协议、目录数据、用户/会员/支付、AI 密钥、缓存正文或监控配置。

## 实现摘要

### 1. 版本化资源

`build_home.py` 每次构建生成 `4.1.0-YYYYMMDDHHMMSS` 版本标识，并将其用于外链 CSS 和非句子数据模块。句子库使用同一版本标识由 `NOUR_loadDataAsset('sentences')` 加载。

### 2. 静态响应头

`server.py` 现在为静态文件提供：

- `ETag`
- `Last-Modified`
- `304 Not Modified`
- `Vary: Accept-Encoding`
- 版本化资源：`public, max-age=31536000, immutable`（公网 CDN 当前呈现为 7 天 immutable）
- HTML、API 和未版本化数据：继续重新验证或 `no-store`
- 大文本 gzip 传输和已有压缩缓存逻辑保持不变

公网实测的版本化 `builtin_books.js` 返回 `200`，并在相同 ETag 条件请求下返回 `304`；Cloudflare 对外呈现 `public, max-age=604800, immutable`。

### 3. 句子库兼容性

保留 `BUILTIN_SENTENCES` 全局变量和原有入口函数。初始页面只创建空数组与 Promise 加载器，用户进入句子库后再请求：

```text
data/builtin_sentences.js?v=4.1.0-20261006230559
```

加载完成后真实数据量为 **29,740 句**，原分类、搜索、听力、跟读和闪卡继续使用原函数与数据结构。

## 公网验收

| 项目 | 结果 |
|---|---:|
| `/api/catalog/meta` | `200`，`total=8794` |
| `/api/library/classics?size=5` | `200`，索引总数 `1820` |
| `/api/library/fiqh-schools?size=5` | `200`，四学派数据可用 |
| `/api/read?t=shamela&id=8220` | `200`，`239` 页 |
| 只读性能基线 API | `7/7` 返回 `200` |
| 版本化静态资源 | `18` 项被基线工具采样 |
| 首页 | `200`，HTML 继续 `no-cache, must-revalidate` |
| `nur.service` | `active` |
| `nur-health-monitor.service` | `active` |

公网单次性能测量（非 SLA）：

- 首页压缩后约 **544,087 bytes**，约 **776 ms**。
- `/api/catalog/meta` 约 **133 ms**。
- `/api/catalog?page=1&size=60` 约 **129 ms**。
- 版本化 `builtin_books.js`：约 **644,648 bytes** 线上传输记录，gzip，约 **110 ms**。
- 句子库不再出现在首屏版本化模块清单；它只在句子入口测试中请求。
- 本地词典暖缓存 P50 **2.628 ms**，冷启动 P50 **26.401 ms**。

### 浏览器回归

公网手机 `390×844` 与桌面 `1280×900` 均通过：

- 按需资源合同：手机 **10/10**，桌面 **10/10**
- 首页：手机 **11/11**，桌面 **11/11**
- 一级导航：手机 **25/25**，桌面 **23/23**
- Apple 风格阅读器：手机 **21/21**，桌面 **21/21**
- 主题与中阿混排：手机 **12/12**
- 古兰经页级入口：手机 **7/7**
- OpenITI 流式离线回归：通过
- 经典索引完整性：`1820` 条、无重复、全部具备 Shamela 阅读路径

## 保护与回滚

本轮未删除任何既有功能、书籍、词汇、经文、圣训、音频、AI 或用户数据。生产发布只替换了服务端缓存逻辑、构建产物和必要的前端数据模块，并在替换前创建独立备份。

若需要回滚，可从：

```text
/opt/nur/backups/20261006-phase7a1-cache-lazy-assets
```

恢复本轮替换文件后重启 `nur.service`；`nur-health-monitor.service` 不在替换范围内。

## 测试工具

- `tools/phase7_asset_loading_ui_test.js`
- `tools/performance_baseline.py`
- `docs/20261006-phase7-performance-baseline.json`
- 阶段 7A-0 基线：`docs/20261006-phase7-performance-baseline.md`
