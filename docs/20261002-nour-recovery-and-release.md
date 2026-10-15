# NOUR / 燃灯同学源站恢复与上线记录

**执行时间：** 2026-10-02 02:37–02:51（本地设备时区 +03:00）  
**公网：** <https://xn--dqry4os3s3gb.com/>  
**源站：** `root@152.239.115.147`

## 故障根因

SSH、HTTP 和 HTTPS 曾经可以建立 TCP 连接，但应用层不返回数据。源站恢复 SSH 后，主机证据显示：

- 3.6GiB 内存、无 swap；
- `nur-health-monitor.service` 反复增长到约 600MB，并被 OOM killer 终止；
- 内核记录两次 OOM，分别杀死健康监控和主应用 Python 进程；
- 旧监控每分钟请求完整 `/api/books` 大响应；
- 旧日志轮转使用 `read_text().splitlines()`，在 `health.jsonl` 增长到 104MB 后会把整文件载入内存；
- 这导致 load average 一度约 `68 / 90 / 85`，随后出现 SSH banner、TLS 和 HTTP 超时。

## 已实施修复

### 1. 健康监控降载

修改并发布 `/opt/nur/monitor/nur_health_monitor.py`：

- 移除每分钟的完整 `/api/books` 探测；
- 圣训探测限制为 `page=1&size=6`；
- 单个响应读取上限从 64KiB 降为 16KiB；
- 请求增加 `Connection: close`；
- 每轮结束执行垃圾回收；
- 日志轮转只从文件尾读取最多 4MiB，不再把整个历史日志读入内存；
- 保留目录总量、OpenITI 元数据、古兰经经注、圣训、本地服务和公网状态检查。

### 2. 主机内存保护

- 创建并启用 `/swapfile`，大小 2GiB；
- 写入 `/etc/fstab`，重启后仍然有效；
- 新增 `/etc/systemd/system/nur-health-monitor.service.d/recovery-memory.conf`：

```ini
[Service]
MemoryHigh=192M
MemoryMax=256M
OOMPolicy=stop
```

- 监控服务仍设置为自动重启，但不再允许它挤压主站服务。

### 3. NOUR 产品壳上线

已通过临时目录和原子替换发布：

- `server.py`
- `build_home.py`
- `arabic_learning.html`
- `v3.html`
- `openiti_stream.py`
- `data/nour-product-shell.css`
- `data/nour-product-shell.js`
- 修复后的 `monitor/nur_health_monitor.py`

未覆盖用户数据、书籍数据、会员状态或 AI 配置。

## 远端回滚点

```text
/opt/nur/backups/20261002-nour-product-shell-recovery
```

该目录保存了上线前的网页产物、服务端代码、OpenITI 模块、监控脚本和 systemd 配置。

## 上线后验证

| 检查项 | 结果 |
|---|---:|
| `nur.service` | active |
| `nur-health-monitor.service` | active |
| 监控健康条件 | 全部 true |
| `catalog_total` | 8794 |
| `/` | HTTP 200 |
| `/api/catalog/meta` | HTTP 200 |
| `/api/books` | HTTP 200 |
| `/api/dict/lookup` | HTTP 200 |
| `/api/quran/tafsir` | HTTP 200 |
| 两部超大 OpenITI 流式首页 | ready=true，无 U+FFFD |
| NOUR 手机产品壳 | 19/19 |
| NOUR 桌面产品壳 | 18/18 |
| 古兰经手机入口 | 8/8 |
| 伊斯兰图书馆手机入口 | 8/8 |
| OpenITI 流式手机阅读器 | 16/16 |

一轮约 60 秒的稳定性窗口后：

- 监控进程 RSS 约 22MB；
- `MemoryMax=256MB`；
- `NRestarts=0`；
- `health.jsonl` 约 4.2MB；
- 修复之后没有新增 OOM 记录；
- 可用内存约 2.0GiB；
- 网站关键接口保持 HTTP 200。

## 当前状态

网站已恢复并上线。之前的 SSH/公网超时属于源站 OOM 与监控日志内存峰值问题，不是 Cloudflare DNS 或本地 SSH 密钥故障。
