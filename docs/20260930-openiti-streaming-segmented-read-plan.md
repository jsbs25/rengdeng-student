# OpenITI 超大原文流式分页与分段读取优化方案

**项目：** 燃灯同学  
**日期：** 2026-09-30  
**目标：** 修复两个 OpenITI 原文因超过当前 12 MB 全文下载保护而返回 HTTP 413 的问题，同时不放宽安全限制、不一次性下载整本书，并保持软件内阅读和逐页 AI 讲解可用。

---

## 1. 当前问题与实测事实

当前服务端实现位于 `server.py` 的 `_openiti_pages()`：

1. 用 `urllib.request.urlopen()` 下载整个 `text_url`；
2. 先写入完整 `.txt` 缓存；
3. 再读取完整文件、清理 OpenITI 头信息；
4. 最后按约 5,200 个字符生成所有页面并放入内存缓存。

当前保护逻辑：

```python
_OPENITI_MAX_BYTES = 12 * 1024 * 1024
```

因此，文件在生成第一页之前就会被拒绝。

### 两个实际受影响条目

| ID | 书名 | 原文大小 | 当前结果 |
|---|---|---:|---|
| `openiti-b189390ada0b10e0` | `شرح سنن أبي داود :: شرح سنن أبي داود لابن رسلان` | 20,041,082 bytes，约 19.1 MiB | HTTP 413 |
| `openiti-23f3107332aec56a` | `طبقات أعلام الشيعة` | 14,437,493 bytes，约 13.8 MiB | HTTP 413 |

### HTTP 能力核验

2026-09-30 对两条固定 OpenITI release 原文地址进行了只读探测：

- `HEAD` 返回 `Content-Length`；
- `Accept-Ranges: bytes`；
- `GET Range: bytes=0-1023` 返回 `206 Partial Content`；
- `Content-Range` 正确返回完整文件大小；
- 来源仍然是固定 release 的 `raw.githubusercontent.com/OpenITI/RELEASE/...` 白名单。

**结论：** 不需要放宽 12 MB 的单次下载保护，也不需要改为整本文件下载；可以改为“按字节区间读取 + 服务端增量解析 + 页面级缓存”。

---

## 2. 设计目标与非目标

### 目标

- 首次打开只读取首个小分段，首屏不等待整本书；
- 用户翻到哪一页，服务端解析到哪一页；
- 单次上游读取不超过可控分段大小；
- 断点可恢复，服务重启后不必从头下载已经缓存的分段；
- 保持现有 `/api/catalog/read?id=...&page=...` 调用兼容；
- 逐页 AI 只分析已经完整生成的当前页；
- 对超大原文、断网、Range 不支持、源文件变化提供明确状态；
- 继续限制来源白名单、请求速率、磁盘缓存和并发量。

### 非目标

- 不批量预下载 8,756 部 OpenITI 原文；
- 不在后台自动扫描整本书；
- 不绕过网站反爬、权限或版权限制；
- 不把整本原文发送给 AI；
- 不将 12 MB 限制简单改成 20 MB 或更高；
- 不承诺所有外部来源都能内置阅读。没有 `text_mode=arabic_original_link` 的书目仍保留官方 BookReader/来源链接路径。

---

## 3. 推荐总体架构

```text
用户打开第 N 页
        │
        ▼
前端 rdOpenitiFetch(N)
        │
        ▼
GET /api/catalog/read?id=...&page=N&mode=stream
        │
        ├── 页面缓存已有：立即返回 200
        │
        ├── 页面尚未生成：读取/恢复该书 manifest
        │       │
        │       ├── 读取已有 segment 文件
        │       ├── 必要时向 OpenITI 发 Range 请求
        │       ├── 增量 UTF-8 解码
        │       ├── 清理 OpenITI 元数据行
        │       ├── 按段落与 5,200 字符生成页面
        │       └── 原子写入页面索引与 segment 缓存
        │
        ├── 当前页已经生成：返回 200
        └── 当前页尚未生成但本轮预算用尽：返回 202 + progress
```

关键原则是：**页是逻辑单位，Range segment 是传输单位。** 不把“5,200 个字符”错误地直接当成“5,200 个字节”，因为阿拉伯语 UTF-8 一个字符可能占多个字节，且 OpenITI 段落边界不能被破坏。

---

## 4. 服务端实现方案

### 4.1 保留并扩展现有白名单

继续复用 `_openiti_book()`，只允许：

- `openiti-[0-9a-f]{16}` ID；
- `text_mode == arabic_original_link`；
- `text_url` 使用 HTTPS；
- 域名为 `raw.githubusercontent.com`；
- 路径以 `/OpenITI/RELEASE/` 开头；
- release 与目录元数据中的固定版本一致。

不能让客户端直接传入任意 URL，也不能把 `text_url` 作为未验证的代理地址。

### 4.2 新增源文件信息探测

新增内部函数：

```python
def _openiti_head(book) -> dict:
    """返回 size、etag、last_modified、accept_ranges 等已核验元数据。"""
```

建议结果：

```json
{
  "size": 20041082,
  "accept_ranges": true,
  "etag": "...",
  "last_modified": "...",
  "content_type": "text/plain; charset=utf-8",
  "release": "v2025.1.9"
}
```

规则：

- 首选 `HEAD`；
- 若 `HEAD` 没有大小，则发一个 `Range: bytes=0-0` 的小请求；
- 若源站返回 `200` 且没有 `Content-Range`，不要自动下载完整文件；返回“当前来源不支持安全分段读取”；
- 若返回 `206`，必须校验 `Content-Range` 的起止位置和总大小；
- 将 `size`、ETag、Last-Modified 和 URL 哈希写入 manifest，源文件变化时使旧 segment 失效。

### 4.3 分段参数

建议初始配置：

```python
_OPENITI_RANGE_CHUNK_BYTES = 1024 * 1024      # 每个上游分段 1 MiB
_OPENITI_REQUEST_BUDGET_BYTES = 2 * 1024 * 1024
_OPENITI_PAGE_CHARS = 5200                    # 保持现有阅读页密度
_OPENITI_MAX_SOURCE_BYTES = 64 * 1024 * 1024  # 单本绝对保护上限
_OPENITI_PAGE_MEM_LIMIT = 96
_OPENITI_BOOK_MEM_LIMIT = 3
```

说明：

- `12 MB` 不再作为“整本文件上限”，而保留为旧的整本下载保护概念；新路径的单次请求仍最多读取约 2 MiB；
- `64 MB` 是单本绝对保护上限，超过时继续返回明确的保护性错误；
- 当前两个条目分别约 20 MB 和 14.4 MB，均在分段路径可处理范围内；
- 1 MiB 不是永久固定值，后续可按延迟和内存指标调整为 512 KiB–2 MiB。

### 4.4 每本书的磁盘状态

建议目录：

```text
data/cache/openiti/<book-id>/
├── manifest.json
├── segments/
│   ├── 000000000-001048575.part
│   ├── 001048576-002097151.part
│   └── ...
└── pages/
    ├── 000000.json
    ├── 000001.json
    └── ...
```

`manifest.json` 示例：

```json
{
  "schema": 2,
  "book_id": "openiti-b189390ada0b10e0",
  "source_url_sha256": "...",
  "release": "v2025.1.9",
  "source_size": 20041082,
  "etag": "...",
  "last_modified": "...",
  "next_byte": 2097152,
  "eof": false,
  "pages_ready": 18,
  "parser_state": {
    "pending_line": "",
    "blank_run": 0,
    "paragraph_buffer": ""
  },
  "updated_at": "2026-09-30T...Z"
}
```

实际实现可将解析状态序列化为更简洁的字段。不要把 Python 对象直接 pickle 到缓存中；使用 JSON，便于升级和清理。

### 4.5 增量下载与 UTF-8 解码

不能直接对每个 Range 响应调用 `chunk.decode('utf-8')` 后拼接，因为一个阿拉伯字符可能在两个字节分段之间被切开。

推荐：

```python
decoder = codecs.getincrementaldecoder('utf-8')(errors='ignore')
for raw_chunk in response:
    text_piece = decoder.decode(raw_chunk, final=False)
text_tail = decoder.decode(b'', final=True)
```

每个 Range 分段结束时保留未完成的 UTF-8 字节，或在下一次请求前重复最多 3 个字节并去重。优先使用增量 decoder，避免手工处理多字节字符。

### 4.6 增量清理和分页

现有 `_openiti_clean_text()` 是整本文本处理函数，流式版本需要拆成状态机：

1. 按换行维护 `pending_line`；
2. 丢弃 `######OpenITI#` 和 `#META#` 元数据行；
3. 连续空行压缩为段落边界；
4. 将段落加入 `paragraph_buffer`；
5. 段落超过 `_OPENITI_PAGE_CHARS` 时按字符安全切分；
6. 达到页面长度时生成页面记录；
7. Range 分段结束时保留未完成段落，不提前提交；
8. 到 EOF 时 flush 最后一个段落和最后一页。

页面记录建议包含：

```json
{
  "page": 0,
  "text": "...",
  "byte_start": 0,
  "byte_end": 1048575,
  "complete": true,
  "source_version": "v2025.1.9"
}
```

`byte_start`/`byte_end` 用于调试、缓存校验和 AI 证据锚点，不作为用户可见页码替代。

### 4.7 并发和锁

当前 `_OPENITI_LOCK` 是全局锁，会让不同书籍的读取互相阻塞。建议改为：

```python
_OPENITI_BOOK_LOCKS = {}
_OPENITI_BOOK_LOCKS_GUARD = threading.Lock()
```

每本书单独锁定，避免：

- 同一本书的两个请求同时下载同一个 Range；
- manifest 被半写入；
- 页面重复生成。

不同书籍可以并行，但仍需增加全局上游请求限速和活跃任务上限，例如：

- 同时最多 3 个 OpenITI 上游读取；
- 同一本书同时最多 1 个扫描任务；
- 同一客户端每秒最多 2 次分页请求；
- 每个 HTTP 请求最多继续读取 2 MiB，超出则返回 202。

### 4.8 原子写入和恢复

所有 segment、page 和 manifest 写入都使用：

```text
目标文件.part → fsync（可选）→ os.replace()
```

服务重启后：

- 删除未完成 `.part` 文件；
- 读取 manifest；
- 从 `next_byte` 继续；
- 如果 manifest 与 segment 校验不一致，从最后一个完整 segment 回退；
- 如果源 URL、release、文件大小或 ETag 变化，清理该书旧缓存并重新开始。

---

## 5. API 契约设计

### 5.1 兼容现有接口

继续使用：

```text
GET /api/catalog/read?id=<book_id>&page=<n>&mode=stream
```

没有 `mode=stream` 时可暂时保留旧行为，但建议在完成灰度后统一切换到流式路径。

### 5.2 页面已就绪：HTTP 200

```json
{
  "ready": true,
  "t": "openiti",
  "id": "openiti-b189390ada0b10e0",
  "page": 0,
  "total": null,
  "has_next": true,
  "text": "阿拉伯语正文…",
  "source": "OpenITI/KITAB · v2025.1.9 固定版本",
  "source_url": "https://github.com/OpenITI/RELEASE/…",
  "text_url": "https://raw.githubusercontent.com/OpenITI/RELEASE/…",
  "rights": "…",
  "streaming": true,
  "bytes_read": 1048576,
  "source_bytes": 20041082,
  "eof": false,
  "cached": true
}
```

`total` 在未到 EOF 前可以为 `null`，不能伪造总页数。前端显示“第 1 页 · 已按需读取”即可。

### 5.3 本轮预算不足：HTTP 202

```json
{
  "ready": false,
  "pending_page": 18,
  "next_page": 18,
  "retry_after_ms": 500,
  "pages_ready": 18,
  "bytes_read": 2097152,
  "source_bytes": 20041082,
  "progress": 0.1046,
  "message": "正在分段读取阿拉伯原文…"
}
```

HTTP 202 表示服务正常，只是本轮没有继续读取到目标页。前端在 400–800 ms 后重试同一页，最多按 `retry_after_ms` 调度，不使用高频循环。

### 5.4 源站不支持 Range 或超过绝对上限

建议使用结构化错误：

```json
{
  "ready": false,
  "error_code": "range_unsupported",
  "error": "当前来源不支持安全分段读取",
  "fallback_url": "https://github.com/OpenITI/RELEASE/…"
}
```

或：

```json
{
  "ready": false,
  "error_code": "source_too_large",
  "error": "原文超过应用内安全读取上限，请使用官方来源查看",
  "source_bytes": 90000000,
  "fallback_url": "https://github.com/OpenITI/RELEASE/…"
}
```

HTTP 状态建议：

| 状态 | 含义 |
|---:|---|
| 200 | 当前页已经生成 |
| 202 | 正在增量读取，客户端可稍后重试 |
| 404 | ID 不存在或不是允许内置阅读的 OpenITI 条目 |
| 416 | 页码已超出已知 EOF 页数 |
| 413 | 仅用于绝对上限或明确的保护性拒绝，不再用于普通 14–20 MB 文件 |
| 502 | 上游临时网络错误，允许重试 |

---

## 6. 前端阅读器适配

现有 `rdOpenitiFetch()` 需要增加以下行为：

### 6.1 处理 200 / 202

伪代码：

```javascript
function rdOpenitiFetch(page, show, attempt) {
  // 保持现有状态校验和 req 递增
  fetch(url, {signal: state.abort && state.abort.signal})
    .then(function (r) {
      return r.json().then(function (d) {
        if (r.status === 202 && d && !d.ready) {
          return {pending: true, data: d};
        }
        if (!r.ok || d.error) throw new Error(d.error || '原文载入失败');
        return {pending: false, data: d};
      });
    })
    .then(function (result) {
      if (result.pending) {
        state.progress = result.data;
        renderRead();
        if (attempt < 120) {
          state.retryTimer = setTimeout(function () {
            rdOpenitiFetch(page, show, attempt + 1);
          }, Math.max(400, result.data.retry_after_ms || 600));
        }
        return;
      }
      // 写入 RD_PAGES[page]，保留现有 renderRead、AI 挂载和单页预取
    })
    .catch(function (e) {
      // 只把真正错误显示为错误；202 不显示失败
    });
}
```

### 6.2 UI 状态

在阅读器来源栏显示：

- `正在读取第 N 页…`；
- `已读取 2.0 MB / 19.1 MB`；
- `本页已就绪`；
- `已到达文件末尾，共 M 页`；
- `原文过大但当前页可继续按需读取`。

不要在用户看到“正在载入”时显示 AI 分析按钮；只有 `RD_PAGES[page]` 是完整正文时才允许逐页 AI。

### 6.3 总页数未知时的导航

在 EOF 之前：

- “下一页”按钮始终可用，直到请求返回 `has_next=false`；
- “上一页”按已缓存页工作；
- 目录只列出已经生成的页面，或显示“继续读取以生成目录”；
- 进度显示 `第 N 页 · 正在按需读取`，不显示伪造的 `/总页数`。

到达 EOF 后：

- manifest 写入 `eof=true`；
- API 返回稳定 `total`；
- 前端补齐最终页数和目录。

### 6.4 退出与切书

保持当前已有状态隔离逻辑，并增加：

- `clearTimeout(state.retryTimer)`；
- `AbortController.abort()`；
- 不让旧书的 202 重试覆盖新书阅读器；
- 关闭阅读器时不继续推进上游 Range 读取。

### 6.5 预取策略

继续只预取下一页一次，不递归下载整本：

```text
当前页 ready → 延迟 150–300 ms → 读取下一页一次
```

预取也必须受每次 2 MiB 预算限制，并且不能改变当前页、页码或 AI 当前上下文。

---

## 7. 逐页 AI 联动

流式阅读不会改变 `/api/page/analyze` 的安全边界：

1. 只发送已经完成的当前页文本；
2. 不发送尚未完成的 `202` 占位文本；
3. 请求中携带稳定的 `book_id`、逻辑页码和 `byte_start`/`byte_end` 锚点；
4. 缓存键加入 `source_version` 和页面 byte 区间；
5. 如果页面仍在读取，AI 按钮显示“本页载入完成后可讲解”；
6. 原文来源、版本和页码不确定时，AI 必须继续显示“待核验”提示。

建议缓存键增加：

```text
book_id + release + source_size + byte_start + byte_end + page_text_hash + language + fiqh_school
```

这样即使 OpenITI release 更新，也不会复用旧版本页面讲解。

---

## 8. 失败与降级策略

| 场景 | 行为 |
|---|---|
| HEAD 成功、Range 成功 | 启用流式分页 |
| HEAD 失败但 Range 探测成功 | 使用 Range 元数据继续 |
| Range 返回 200 全文 | 拒绝完整下载，显示官方来源链接 |
| 206 的 Content-Range 不匹配 | 丢弃该分段，返回 502 并允许重试 |
| UTF-8 分段切断字符 | 增量 decoder 处理，不显示乱码 |
| 上游超时 | 保留已完成 segment，返回 502；下次从断点继续 |
| 磁盘空间不足 | 停止写缓存，保留内存当前页并提示稍后重试 |
| 超过单本绝对上限 | 返回 `source_too_large`，不继续读取 |
| manifest 损坏 | 回退到最后完整 segment，重建 manifest |
| 源文件版本变化 | 清理旧 page index，保留可审计日志后重新按需读取 |
| 用户快速切页 | 取消旧重试，只保留最新请求；已缓存页面继续可用 |

---

## 9. 测试计划

### 9.1 单元测试

建立 `tools/test_openiti_streaming.py`，使用本地 Range 模拟服务器测试：

- `Content-Range` 校验；
- 206 与 200 降级；
- UTF-8 多字节字符跨分段；
- `######OpenITI#`、`#META#` 行清理；
- 段落跨 Range 边界；
- 超过页面长度时的切分；
- EOF 与最终总页数；
- manifest 原子写入与断点恢复；
- manifest 与源大小变化时缓存失效；
- 同一本书并发请求只发一个 Range；
- 不同书可并行。

### 9.2 两个真实条目验收

对以下两个 ID 进行应用内测试：

```text
openiti-b189390ada0b10e0
openiti-23f3107332aec56a
```

每本至少验证：

1. `HEAD` 得到大小；
2. 第 0 页首次返回 200，不再返回 413；
3. 第 1、2、10 页能够通过 200/202 最终得到正文；
4. 刷新服务后可以从 manifest 继续；
5. 下一页预取只读取一页；
6. 退出阅读器后不再产生新 Range 请求；
7. 当前页 AI 按钮只在正文 ready 后出现；
8. 目录、RTL、字体、底部安全区没有回归；
9. 服务器不会出现整本 14–20 MB 文件单次读入内存。

### 9.3 压力与监控回归

更新 `tools/public_api_stress.py`：

- 将 `413 oversize_source_protection` 改为流式路径的最终 200 或中间 202；
- 增加 `stream_read_samples`；
- 记录 `range_requests`、`bytes_read`、`pages_ready`、`eof`；
- 不把 202 视为失败；
- 对无 Range 的模拟源仍必须验证安全拒绝。

建议压力测试保持低速：

```text
workers=4
全局约 6 req/s
每个超大书最多 2 个并发会话
不执行整库正文预取
```

监控增加：

- Range 上游错误数；
- 202 平均重试次数；
- 413 绝对保护次数；
- 分段缓存命中率；
- 当前活跃扫描数；
- `/opt/nur/data/cache/openiti` 占用空间。

---

## 10. 分阶段实施与发布顺序

### 阶段 A：兼容层与数据结构

- 新增 Range HEAD/206 校验函数；
- 新增 manifest、segment、page cache 目录；
- 保留旧函数作为 feature flag fallback；
- 增加两个条目的本地模拟测试。

### 阶段 B：流式解析器

- 将整本 `_openiti_clean_text()` 拆成增量 parser；
- 加入 UTF-8 incremental decoder；
- 实现页面生成、EOF 和 manifest 恢复；
- 先不改前端，只用 API 集成测试验证。

### 阶段 C：API 与前端 202 状态

- `/api/catalog/read?mode=stream` 返回 200/202 结构；
- `rdOpenitiFetch()` 处理 pending、进度、取消与重试；
- 总页数未知时的导航和来源栏；
- AI 按钮与 ready 状态绑定。

### 阶段 D：灰度发布

建议 feature flag：

```text
OPENITI_STREAMING=1
OPENITI_STREAMING_IDS=openiti-b189390ada0b10e0,openiti-23f3107332aec56a
```

先只对两个 413 条目启用：

1. 备份 `/opt/nur/server.py`、页面、目录和用户/AI 数据；
2. 上传服务端与前端；
3. 重启 `nur.service`；
4. 验证两个条目首屏、翻页、AI、退出；
5. 查看 5–10 分钟监控；
6. 失败时关闭 flag 或恢复本轮回滚点。

### 阶段 E：扩大到全部 OpenITI

两个大文件稳定后，再将 `OPENITI_STREAMING_IDS` 扩大到所有 `openiti-*` 条目。仍然只在用户打开或翻页时读取，绝不主动扫描全库。

---

## 11. 回滚方案

保留现有旧路径，并提供三个回滚层级：

1. **配置回滚：** `OPENITI_STREAMING=0`，恢复旧逻辑；
2. **文件回滚：** 从 `/opt/nur/backups/<timestamp>/` 恢复 `server.py` 和生成页面；
3. **缓存回滚：** 删除或隔离 `data/cache/openiti/<book-id>/`，不影响用户数据、AI 密钥、会员状态和其他书库。

流式缓存目录不应与旧的单文件缓存共用同一个命名空间，避免旧版本误读新格式。

---

## 12. 验收标准

只有满足以下条件才认为优化完成：

- 两个指定 ID 首次打开不再因 14–20 MB 文件返回 413；
- 单个 HTTP 请求不读取超过配置的 Range 分段预算；
- 页面按需生成，未翻到的页面不会被整本预生成；
- 服务重启后能从 manifest 继续；
- 断网不会丢失已经完成的分段；
- 源站不支持 Range 时不会退化为整本下载；
- 202 进度状态不被前端误报成失败；
- AI 只接收 ready 的当前页；
- 现有 8,794 条目录、古兰经、六大部、RTL、手势和底部导航回归通过；
- 监控服务保持 active，未出现内存、磁盘或上游请求异常；
- 真实压力测试中不再出现未分类的 413/404；
- 压力测试与本方案报告能区分：正常 200、处理中 202、来源保护和真正失败。

---

## 13. 推荐下一步

下一轮直接按 **阶段 A → B** 实现服务端流式核心，并只对两个已知 413 条目启用灰度；完成 API 集成测试后，再改前端 202 状态。这样可以先解决真实阻塞点，同时把风险控制在两个固定 OpenITI 条目内，不影响当前 8,794 本目录和现有阅读器。
