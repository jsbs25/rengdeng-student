# 服务器 SSH 与公网访问超时诊断

**检查时间：** 2026-10-02 02:29–02:36（本地设备时区 +03:00）  
**域名：** `xn--dqry4os3s3gb.com`  
**源站：** `152.239.115.147`

## 结论

当前故障位于**源站主机或源站网络栈/防火墙层**，不是本地项目代码、域名解析或 SSH 私钥问题。

源站的 TCP 端口 22、80、443 都可以快速建立连接，但连接建立后完全没有处理应用层数据：

- SSH 不发送服务端 banner；
- HTTP 不返回任何响应首字节；
- HTTPS 不完成 TLS ServerHello；
- Cloudflare 边缘 TLS 正常，但发送 GET 后也一直等不到回源结果。

这符合主机卡死、sshd/nginx/systemd 全部失去调度、云主机网络层异常，或上游防火墙接受连接后丢弃 payload 的特征。单纯重启 `nur.service` 无法从当前状态执行，因为 SSH 在认证前就已经卡住。

## 实测证据

### DNS

域名解析正常并由 Cloudflare 代理：

- `A 172.67.223.1`
- `A 104.21.17.65`
- `AAAA 2606:4700:3033::ac43:df01`
- `AAAA 2606:4700:3034::6815:1141`

本地路由正常，源站通过网关 `192.168.1.1`、接口 `en0` 发送。

### 源站 TCP

四次重复连接均能快速成功：

| 端口 | TCP 建连 |
|---:|---|
| 22 | 4/4 成功，约 0.08–0.10 秒 |
| 80 | 4/4 成功，约 0.09–0.10 秒 |
| 443 | 4/4 成功，约 0.09–0.10 秒 |

### SSH

SSH 详细日志停止在：

```text
Connection established.
Local version string SSH-2.0-OpenSSH_10.3
Connection timed out during banner exchange
Connection to 152.239.115.147 port 22 timed out
```

本地 ED25519 公钥存在并被正确加载，故障发生在服务端发送 SSH banner 之前，还没有进入用户名、密钥认证或权限判断阶段。

### 源站 HTTP/TLS

对源站直连的原始 socket 探针结果：

- 80：发送 `GET /` 或 `HEAD /` 后 6–15 秒无任何字节；
- 443：TCP 建连成功，但 TLS 握手在 6–8 秒内超时；
- 22：连接后等待 6–8 秒无 banner。

因此不是单个 `nur.service` 路由错误。即使 HTTP 代理或应用进程异常，443 的 TLS 握手和 22 的 SSH banner 也不应同时完全无响应。

### Cloudflare

Cloudflare 两个 IPv4 边缘地址都能完成 TLS：

- TLS 版本：`TLSv1.2`
- cipher：`ECDHE-ECDSA-CHACHA20-POLY1305`
- 证书 CN：`xn--dqry4os3s3gb.com`

但向两个边缘地址发送 HTTP GET 后均在 12 秒内无响应。使用 `curl` 等待 75 秒仍未收到 HTTP 头或响应体，说明边缘正在等待或无法完成回源；本次探针未等到 Cloudflare 生成错误页。

## 当前不能做的操作

由于 SSH banner 阶段就超时，当前无法安全执行：

- `systemctl status/restart nur.service`
- 读取 `journalctl`、内存、磁盘和负载
- 创建本轮远端备份
- 上传或原子替换网站文件
- 从服务端验证 Cloudflare 回源配置

没有进行盲目重启、上传或替换，避免在无法读取远端回滚点时扩大故障。

## 建议恢复顺序

1. 在 VPS/云厂商控制台查看实例状态、CPU、内存、磁盘、网络和安全组。
2. 如果控制台显示实例卡死或无响应，执行一次**软重启**；软重启无效时再使用云控制台的强制重启。
3. 重启后先测试：

   ```bash
   ssh -4 -o ConnectTimeout=15 root@152.239.115.147 'date -Is; systemctl is-active nur.service; systemctl is-active nur-health-monitor.service'
   ```

4. SSH 恢复后先读取服务日志和监听状态，再创建独立回滚目录：

   ```bash
   systemctl --failed
   journalctl -u nur.service -b --no-pager -n 120
   ss -ltnp
   df -h
   free -h
   ```

5. 只有确认主机稳定、`nur.service` 正常后，才继续部署本地待发布的 NOUR 产品壳变更。
6. 最后从公网验证首页、`/api/catalog/meta`、词典、古兰经、两个 OpenITI 大书和 AI。

## 安全边界

- 本次仅做只读网络诊断。
- 未读取或修改 AI 密钥。
- 未触碰用户数据、会员/充值状态或远端缓存。
- 未创建新的自动重启或自动抓取任务。
