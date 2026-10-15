# NOUR 节点异步刷新与今日一句有界加载发布报告

- 发布日期：2026-10-07
- 线上域名：<https://xn--dqry4os3s3gb.com/>
- 发布目录：`/opt/nur/releases/20261007-nodes-daily-sentences-1538UTC/`
- 回滚目录：`/opt/nur/releases/20261007-nodes-daily-sentences-1538UTC/backup/`

## 本轮改动

### `/api/nodes` 与 `/sub`

- 请求路径只读取最近一次成功的订阅 YAML 缓存。
- 冷缓存、过期缓存请求都会立即返回，不等待第三方源和 TCP 测速。
- 使用线程锁和单飞 daemon worker，多个并发请求不会重复触发刷新。
- 外部源 HTTP 超时收紧到 2 秒，单节点 TCP 测速收紧到 1.2 秒。
- 测速最多处理前 64 个候选，避免刷新耗时随源规模无限增长。
- 刷新失败保留旧缓存；冷启动失败返回 HTTP 200 与 `proxies: []` 的可识别临时 YAML。
- `/api/nodes` 增加 `refreshing`、`stale`、`age_seconds`、`last_success`、`last_error` 状态字段。
- `/sub` 增加 `X-Nour-Sub-Refreshing`、`X-Nour-Sub-Stale` 响应头。

### 今日一句

- 新增 `GET /api/sentences/daily`。
- 返回真实句子 `{a,e,c,cat}`、日期、稳定索引和总数；按日期选择，同一天结果稳定。
- 公网实测响应 **178 bytes**，远低于 10KB 上界。
- 旧 `GET /api/sentences` 完整分类合同保留，供主动句子库、兼容入口和其他客户端继续使用。
- 首页改为请求 `/api/sentences/daily`；完整 `builtin_sentences.js` 只在用户主动打开句子库、闪卡或跟读时按需加载。
- 产品壳增加 `MutationObserver`，确保异步摘要返回后首页主卡与今日一句卡同步。

## 本地验证

- `python3 -m py_compile server.py build_home.py openiti_stream.py tools/public_api_stress.py tools/nodes_daily_api_test.py`：通过。
- `git diff --check`：通过。
- `tools/nodes_daily_api_test.py`：通过；真实句子总量 30,298，摘要 278 bytes；冷缓存失败保持空缓存且立即返回。
- 本地首页：手机 390×844 **13/13**；桌面 1280×900 **13/13**。
- 按需数据加载：首屏无大资源请求；主动进入句子库后加载版本化 `builtin_sentences.js`，真实数据 30,298 条。
- 目录回归：8,794 条目录、8,756 条可读项、法源学/学派筛选和站内原文阅读通过。
- 词典：**10/10**。
- Apple 风格阅读器：**21/21**。
- 主题与 RTL/LTR：**12/12**。
- 古兰经入口：**8/8**。
- OpenITI 流式阅读：**16/16**。
- 本地有界只读压测：182/182 通过；目录 8,794/8,794，daily 278 bytes，nodes 最大 1.61ms。

## 公网验收

### 接口实测

| 接口 | HTTP | 延迟 | 响应大小 | 结果 |
|---|---:|---:|---:|---|
| `/api/nodes` 冷缓存 | 200 | 363.4ms | 175 bytes | `refreshing=true, stale=true`，立即返回 |
| `/api/nodes` 第二次 | 200 | 109.85ms | 175 bytes | 立即返回，无同步触网 |
| `/sub` | 200 | 112.59ms | 40 bytes | 临时 YAML 立即返回，后台刷新 |
| `/api/sentences/daily` | 200 | 297.77ms | 178 bytes | 真实句子、日期、索引、总数合同通过 |
| `/api/sentences` | 200 | 867.35ms | 2,741,819 bytes | 完整旧合同保留 |
| `/api/catalog/meta` | 200 | 878.21ms | 7,216 bytes | 总目录 8,794 |

公网节点后台刷新完成后，压测中的热请求为 **110.21ms**，状态为 `refreshing=false, stale=false`。之前约 35 秒超时的同步阻塞已消除。

### 公网回归

- 首页手机 390×844：**13/13**，无 JavaScript 错误、无横向溢出、无首页全量句子请求。
- 首页桌面 1280×900：**13/13**，今日一句与主卡同步。
- 按需数据加载：所有检查通过；首屏没有完整句子资源，主动入口才加载句子资源。
- 部署后公网有界只读压测：**182/182** 通过。
  - 目录：8,794/8,794 唯一条目，无缺 ID、无缺标题。
  - 可读：8,756；元数据-only：38。
  - `sentences_daily`：178 bytes，合同通过。
  - `nodes_async`：110.21ms，合同通过。
  - 4 个预期无效 POST 返回 400，未触发 AI、支付、写入或媒体任务。

> 公网当前 `categorized.json` 的既有真实句子总数为 20,164；本轮没有上传、覆盖或删改该数据文件。daily 与公网保留的完整 `/api/sentences` 统计一致。构建机本地源为 30,298 条，未用本地数据覆盖线上用户数据。

## 发布安全

- 发布前已检查 `nur.service` 与 `nur-health-monitor.service` 均 active。
- 只替换：`server.py`、`build_home.py`、`arabic_learning.html`、`v3.html`、`data/nour-product-shell.js`。
- 未上传 58MB 原始压测数据，未覆盖 `ai_key`、users/payments/unlocks/cache/monitor 配置和用户数据。
- 发布后：`nur.service` active，`nur-health-monitor.service` active，`NRestarts=0`。
- 发布文件 SHA256：

```text
362a83fd021db79f64d8dc3db86503b96bef0254fefc1e4ca18b7687f0d8c182  server.py
242556937c4345bbb91abc077ee613b58782cea180758a9493df16d9aef3e21c  build_home.py
77a84b65abef156d7bd36c08151e4566bb8b945431a4d237e8431594a7462b1e  arabic_learning.html
77a84b65abef156d7bd36c08151e4566bb8b945431a4d237e8431594a7462b1e  v3.html
5732fa8daa2a7dd12fad8c1625d22ed4df360483e613927d3ddcfa444c494c36  data/nour-product-shell.js
```

## 回滚

如需回滚，在服务器上执行：

```bash
cd /opt/nur
R=/opt/nur/releases/20261007-nodes-daily-sentences-1538UTC/backup
for f in server.py build_home.py arabic_learning.html v3.html; do
  install -o root -g root -m 0644 "$R/$f" "/opt/nur/.rollback-$f"
  mv -Tf "/opt/nur/.rollback-$f" "/opt/nur/$f"
done
if test -f "$R/data/nour-product-shell.js"; then
  install -o root -g root -m 0644 "$R/data/nour-product-shell.js" /opt/nur/data/nour-product-shell.js
fi
systemctl restart nur.service
systemctl is-active nur.service nur-health-monitor.service
```
