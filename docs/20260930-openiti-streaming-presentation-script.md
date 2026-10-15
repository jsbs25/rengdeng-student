# “燃灯同学”OpenITI 超大原文流式分页方案
## 配套演示文稿脚本（2026-09-30）

> **用途：** 面向产品、前端、后端、内容合规和运维团队的 8–10 分钟技术演示。本文是逐页讲稿，不是把 OpenITI 全文批量下载到服务器的计划；所有演示均采用有限 Range、按需读取和可删除缓存。

## 演示目标与口径

演示结束时，观众应能确认四件事：

1. 原来因为 12 MiB 一次性原文保护而返回 413 的两部书，可以留在“燃灯同学”软件内阅读。
2. Range 分段读取不会把一个阿拉伯字符从 UTF-8 字节边界切坏；增量 decoder 的未完成字节会进入下一段。
3. 页面、分段和 decoder 状态可恢复；刷新或重启服务后不需要从零开始。
4. “正在按需读取”只对当前页工作，页面准备好后才允许 AI 逐页导读；原文、证据和模型总结仍然分层展示。

**演示口径：** OpenITI 只取固定版本的公开官方 raw 原文；不绕过反爬、付费墙，不批量下载全文，不把外部链接伪装成应用内正文。

---

## Slide 1｜从 413 到软件内可读

### 屏幕内容

- 标题：**让超大阿拉伯原文留在软件内阅读**
- 副标题：OpenITI Range + 增量 UTF-8 + 可恢复分页
- 左侧：旧流程 `整本下载 → 12 MiB 保护 → 413`
- 右侧：新流程 `HEAD/Range → 1 MiB 分段 → 5,200 字符逻辑页 → AI 逐页` 

### 演讲词

> 这次不是把 413 的限制简单放大，也不是把读者跳转到外部应用。我们把“整本下载”改成“当前页所需的最少分段”。这样读者仍然在燃灯同学内阅读，页面 AI 也仍然能看到当前页正文。

### 时间

约 40 秒。

---

## Slide 2｜问题事实：两部书为什么被保护

### 屏幕内容

| 书目 ID | 官方 Release 原文 | 实际源大小 | 旧接口结果 |
|---|---|---:|---:|
| `openiti-b189390ada0b10e0` | `SharhSunanAbiDawud...ara1` | 20,041,082 B | 413 |
| `openiti-23f3107332aec56a` | `TabaqatAclamShica...completed` | 14,437,493 B | 413 |

- 旧阈值：12 MiB 一次性原文保护
- 本轮安全上限：64 MiB 源文件
- 不承诺读取超过安全上限的源文件

### 演讲词

> 压力测试记录了两个明确的 413，它们不是普通网络错误，而是为了避免一次请求下载过大的原文。实际源站都支持 `Accept-Ranges: bytes`，第一部 HEAD 返回 20,041,082 字节，第二部返回 14,437,493 字节；它们都低于新的 64 MiB 安全上限，所以可以进入分段读取流程。

### 演示动作

在终端执行有限只读探测：

```bash
curl -sSIL "$OPENITI_URL" | grep -Ei 'HTTP/|accept-ranges|content-length'
curl -sS -D - -o /tmp/range.bin -r 0-1023 "$OPENITI_URL" \
  | grep -Ei 'HTTP/|content-range|content-length'
```

预期：`HTTP 206`、`Content-Range: bytes 0-1023/<total>`。

### 时间

约 55 秒。

---

## Slide 3｜总体架构：只读、分段、按需

### 屏幕内容

```text
读者点击 OpenITI 书卡
          │
          ▼
GET /api/catalog/read?id=...&page=0&stream=1
          │
          ├─ 校验 ID 与 raw.githubusercontent.com/OpenITI/RELEASE 白名单
          ├─ HEAD；必要时 Range 0-0 探测大小与范围能力
          ├─ 每次最多 1 MiB 分段；每个请求最多 2 MiB 预算
          ├─ UTF-8 增量 decoder + Unicode 字符级分页
          ├─ manifest / segments / pages 原子写入
          └─ 返回 200 或 202；当前页准备好才交给阅读器/AI
```

### 演讲词

> 后端核心是一个小而明确的状态机。源站元信息决定能不能读，Range 决定读哪一段，decoder 决定字节边界如何跨请求恢复，parser 决定如何形成逻辑页。所有中间状态都能落盘，但缓存是可重建的，不覆盖用户数据、会员状态或 AI 配置。

### 关键安全边界

- 只接受 `https://raw.githubusercontent.com/OpenITI/RELEASE/...`。
- 单段上限 1 MiB，单个页面请求预算 2 MiB。
- 上游并发最多 3 个。
- 源文件超过 64 MiB 返回 413，不自动改为整本下载。
- 严格校验 `Content-Range` 的起点、终点和总大小。

### 时间

约 60 秒。

---

## Slide 4｜核心：增量 UTF-8 如何保护阿拉伯字符

### 屏幕内容

```text
源字节流： ... [segment N: 0xD8] | [segment N+1: 0xA8 ...]
                         ▲
                 未完成 UTF-8 序列

segment N      → decoder.decode(bytes, final=False)
manifest       → decoder_pending_b64 + decoder_flag
segment N+1    → 恢复 decoder state，再继续 decode
页面分页       → 只在完整 Unicode 字符串上按字符切分
```

核心实现要点：

```python
decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
decoded = decoder.decode(segment, final=False)
pending, flag = decoder.getstate()
manifest["decoder_pending_b64"] = base64.b64encode(pending).decode("ascii")
manifest["decoder_flag"] = int(flag or 0)
```

### 演讲词

> 这里要区分两个边界：Range 是字节边界，阅读分页是 Unicode 字符边界。一个阿拉伯字母可能由多个 UTF-8 字节组成；如果分段恰好停在中间，decoder 不会立即输出替换字符，而是把未完成序列保存到 manifest。下一次恢复时先还原 decoder state，再接收下一段。只有完成解码后，分页器才按 Python Unicode 字符切分，因此不会切断阿拉伯字符或组合标记。

### 现场可见验证

离线 mock 测试把 Range 精确切在阿拉伯字符的 UTF-8 字节中间，重载模块后恢复 manifest，最终页面：

- 首次：`202`
- 恢复后：`200`
- 文本含阿拉伯语
- `U+FFFD` 替换字符：**0 个**

### 时间

约 75 秒。

---

## Slide 5｜分页与可恢复缓存

### 屏幕内容

```text
data/cache/openiti_stream/<book-id>/
├── manifest.json       # 源大小、ETag、next_byte、pages_ready、decoder state
├── segments/
│   └── 000000000000-000001048575.part
└── pages/
    ├── 00000000.json   # complete=true，包含正文与字节范围
    └── 00000001.json
```

- 逻辑页目标：约 5,200 个 Unicode 字符
- OpenITI `#META#` 和头部标记不作为正文展示
- 每次写入：`.part` 临时文件 → 原子替换
- 每本书独立锁，避免重复 Range 与 manifest 互相覆盖
- ETag/大小/URL hash 不匹配时，丢弃该书缓存并重新按需建立

### 演讲词

> 缓存不是“下载任务”，而是读者已经走到哪里就保存到哪里。页面 JSON 是完整页缓存，分段文件是可复用的原始字节缓存，manifest 是恢复点。服务重启只需要重新读取 manifest；已缓存的当前页不会重新请求上游。

### 演示动作

```bash
cat data/cache/openiti_stream/openiti-b189390ada0b10e0/manifest.json
ls -lh data/cache/openiti_stream/openiti-b189390ada0b10e0/{segments,pages}
```

重点指出：`next_byte`、`pages_ready`、`decoder_pending_b64` 和 `eof`。

### 时间

约 55 秒。

---

## Slide 6｜API 状态机：前端知道“等什么”

### 屏幕内容

| HTTP | 场景 | 前端动作 |
|---:|---|---|
| 200 | 当前页已就绪或页缓存命中 | 展示正文；保存单页断点缓存 |
| 202 | 当前页尚未生成，预算或分段读取尚未完成 | 展示“正在按需读取”，按 `retry_after_ms` 重试 |
| 416 | 已到 EOF 后请求超出总页数 | 显示末页/目录边界，不重试 |
| 413 | 源文件超过 64 MiB | 保留官方来源提示，不整本下载 |
| 502 | Range 不支持、范围校验失败或源站暂时错误 | 展示可理解错误，允许稍后重试 |

### 202 示例

```json
{
  "ready": false,
  "message": "正在分段读取阿拉伯原文…",
  "retry_after_ms": 500,
  "bytes_read": 3145728,
  "source_bytes": 20041082,
  "progress": 0.156964,
  "pages_ready": 437,
  "pending_page": 5000
}
```

### 200 示例

```json
{
  "ready": true,
  "page": 0,
  "text": "بِسْمِ اللَّهِ ...",
  "bytes_read": 1048576,
  "source_bytes": 20041082,
  "progress": 0.052321,
  "pages_ready": 140,
  "streaming": true,
  "cached": true
}
```

### 演讲词

> 202 不是错误，也不是让浏览器空转。它带着可解释的进度、已生成页数和重试时间。前端只重试当前页，且由 AbortController 管理；离开阅读器时会中止请求和清理 timer。

### 时间

约 65 秒。

---

## Slide 7｜前端体验：像读书，不像看下载器

### 屏幕内容

- 阅读器继续使用全屏、RTL、移动横滑和 Apple Books 风格纸面
- 进度条文案：**正在按需读取阿拉伯原文…**
- 进度元信息：`已读 KB / 总 KB · 第 N 页`
- 总页数未知时显示 `第 N 页 / …`
- 当前页就绪后：正文出现、进度条显示“原文已就绪”
- 每本书最多保留 24 个最近单页 `localStorage` 缓存
- 关闭阅读器：AbortController + retry timer 全部清理

### 演示动作

1. 打开 `openiti-b189390ada0b10e0`。
2. 在网络模拟返回一次 202，指向进度条。
3. 等待轮询返回 200，指向正文和“AI”按钮。
4. 左滑下一页、右滑返回。
5. 关闭阅读器，再打开同一页，确认 localStorage 命中，不出现加载占位。

### 演讲词

> 进度条是阅读体验的一部分，不是后台日志。它告诉读者正在按需读取哪一页、已经读了多少源字节，同时不承诺一个尚未知道的总页数。缓存只限最近 24 页，避免单个大书把浏览器 localStorage 撑满。

### 时间

约 70 秒。

---

## Slide 8｜AI 逐页导读的门控与内容边界

### 屏幕内容

```text
正文状态                         AI 状态
────────────────────────────────────────────
正在载入阿拉伯原文…              不发送给 AI；显示“本页正文还没准备好”
正文载入失败                      不伪造内容；允许重试
正文已就绪                        才允许“开始讲解”
```

导读上下文继续区分：

- 原文：OpenITI 页面正文
- 证据：原典、经注、圣训或书目来源（标注直接/相关/待核验）
- 学派镜头：哈乃斐、沙斐仪等比较视角，不改变原文
- 模型总结：学习辅助，不是法特瓦或正式教法裁决

### 演讲词

> 流式读取不能把“正在载入”当成书的内容提交给 AI。现有 page-analysis 的 `usable` 保护会拒绝加载提示、失败提示和空页。只有正文 ready 后，AI 才能分析主旨、问题、依据和阿拉伯语学习重点；任何引用仍建议回到原典和合格学者处核对。

### 时间

约 45 秒。

---

## Slide 9｜测试矩阵：先证明，再发布

### 屏幕内容

| 层级 | 测试 | 实测结果 |
|---|---|---|
| UTF-8 / Range | `tools/openiti_stream_test.py`：mock Range、字节中断、恢复、EOF | **通过**：202 → 200，416，0 个替换字符 |
| 真实第一部大书 | page 0 / page 1 / page 5000 / 重复 page 1 | 200、202、200；源 20,041,082 B |
| 真实第二部大书 | page 0 / page 1 / page 5000 / 重复 page 1 | 200、202、200；源 14,437,493 B |
| 重启恢复 | 8107 服务停止/重启后读取 page 1 | **通过**：manifest 复用，页面仍 200 |
| 普通 OpenITI | `openiti-160ab550d64d62cb` page 0 | **200**，正文 5,200 字符，无替换字符 |
| 流式 UI | `openiti_stream_ui_test.js`，390×844 | **16/16** |
| 流式 UI | 同脚本，1280×900 | **16/16** |
| 全站手机 UI | `manus_ui_test.js`，390×844 | **29/29** |
| 普通手机手势 | `mobile_openiti_gesture_test.js` | **11/11** |
| 核心 API | `/api/catalog/meta`、`/api/books` | **200**；目录总量仍 ≥ 8,794 |

### 演讲词

> 我们没有用一条“看起来能读”的截图代替测试。后端有离线 Range mock 和真实官方源两层验证，前端有 202 轮询、断点缓存、取消、AI 门控和两种视口，旧的导航与普通 OpenITI 手势也重新回归。

### 时间

约 70 秒。

---

## Slide 10｜发布、回滚与运行监控

### 屏幕内容

### 发布顺序

1. 远端预检：服务状态、磁盘空间、当前版本和健康监控。
2. 创建独立回滚目录：`/opt/nur/backups/20260930-openiti-streaming`。
3. 备份 `server.py`、`build_home.py`、`arabic_learning.html`、`v3.html`、相关 CSS 和现有配置引用。
4. 临时目录上传 `openiti_stream.py`、服务端、构建产物和 `data/openiti-stream.css`。
5. 原子替换最少必要文件，重启 `nur.service`。
6. 公网只做有限验证：两个指定 ID 的 HEAD/Range、page 0、普通 OpenITI、核心 API、手机/桌面 UI。
7. 确认 `nur-health-monitor.service` 仍为 active。

### 回滚条件

- 任意核心 API 非预期 5xx。
- OpenITI 普通书籍回归失败。
- 阅读器出现跨页面或 AI 将加载提示送出的错误。
- 缓存增长不受控或 manifest 校验异常。

### 回滚动作

```bash
cp -a /opt/nur/backups/20260930-openiti-streaming/* /opt/nur/
systemctl restart nur.service
systemctl is-active nur.service nur-health-monitor.service
```

> 仅回滚代码与生成页面；不删除用户数据、不覆盖会员/充值状态、不打印或替换 AI 密钥。

### 演讲词

> 这一轮的安全原则是最少文件、独立回滚点、发布后有限验证。健康监控继续只读检查；本轮没有创建新的“每小时自动爬取和自动升级”任务，也不会把当前功能包装成未获权限的自动化。

### 时间

约 60 秒。

---

## 结尾页｜一句话总结

### 屏幕内容

> **不是把 413 阈值放大，而是把“整本原文”改造成“可验证、可恢复、可解释的按需阅读”。**

三项验收：

- **字符正确：** UTF-8 decoder state 跨 Range 恢复，阿拉伯字符不被截断。
- **体验正确：** 进度条、有限断点缓存、RTL 全屏阅读、AI 只分析已就绪正文。
- **运维正确：** 固定官方来源、有限带宽、原子缓存、清晰状态码、可回滚。

### 结束语

> 下一步上线前仍要再做一次远端备份和公网有限回归；在此之前，本地实现和测试已完成，公网旧版本不应被描述为已经包含本轮流式能力。

---

## 附录 A｜现场演示命令清单

```bash
# 1. 构建与语法
python3 -m py_compile openiti_stream.py server.py build_home.py
python3 build_home.py
cp -p arabic_learning.html v3.html

# 2. 离线核心测试
python3 tools/openiti_stream_test.py

# 3. 临时服务
NUR_PORT=8107 python3 server.py

# 4. 两部大书的有限 API 读取
curl -i 'http://127.0.0.1:8107/api/catalog/read?id=openiti-b189390ada0b10e0&page=0&stream=1'
curl -i 'http://127.0.0.1:8107/api/catalog/read?id=openiti-23f3107332aec56a&page=0&stream=1'

# 5. 浏览器 UI（测试脚本会模拟一次 202，避免把 UI 回归变成无界上游下载）
/tmp/manus_web_test http://127.0.0.1:8107 390 844 \
  tools/openiti_stream_ui_test.js /tmp/openiti-ui-mobile/result.json
/tmp/manus_web_test http://127.0.0.1:8107 1280 900 \
  tools/openiti_stream_ui_test.js /tmp/openiti-ui-desktop/result.json
```

## 附录 B｜文件变更清单

- `openiti_stream.py`：Range、分段缓存、增量 UTF-8、Unicode 分页、202 状态。
- `server.py`：`/api/catalog/read?...&stream=1` 优先走流式模块，保留旧逻辑作为兼容回退。
- `build_home.py`：流式阅读器、进度条、202 轮询、AbortController、24 页 localStorage 缓存。
- `data/openiti-stream.css`：RTL、Apple 风格和移动端进度条样式。
- `tools/openiti_stream_test.py`：离线核心专项测试。
- `tools/openiti_stream_ui_test.js`：浏览器 UI 专项测试。
- `docs/20260930-openiti-streaming-presentation-script.md`：本演示脚本。

**当前状态：** 本地构建、真实源有限读取和 UI 回归已完成；远端备份、上传、重启和公网发布仍需在本地全部绿色后单独执行。
