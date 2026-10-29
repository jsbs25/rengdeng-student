# NOUR 每日健康检查与增量备份

日期：2026-10-18

## 已启用

线上服务器已安装并启用：

- 服务：`nur-daily-health-backup.service`
- 定时器：`nur-daily-health-backup.timer`
- 脚本：`/usr/local/sbin/nur-daily-health-backup.sh`
- 定时：每天 `03:30 UTC`，允许最多 10 分钟随机延迟
- 当前服务器时区：UTC
- `Persistent=true`：服务器错过触发时间后恢复时会补跑

换算为：北京时间每天 11:30 左右；东三区每天 06:30 左右。

## 每次执行内容

脚本先检查：

- `nur.service` 是否 active
- `nur-health-monitor.service` 是否 active
- 本机首页 `http://127.0.0.1:8080/`
- `/api/sentences/daily`
- `/api/nodes`
- `/api/catalog/meta`，目录总数至少 8,794
- 公网 `/api/sentences/daily`
- 今日一句字段和小响应边界

通过后使用 `rsync --link-dest` 创建增量快照，并保留最近 14 个每日快照。每个快照都包含代码、公开数据、构建产物和 systemd 配置副本；相同文件使用硬链接，减少重复占用。

## 排除范围

备份不会复制或覆盖：

- `/opt/nur/backups/`
- `/opt/nur/releases/`
- cache、日志、部署恢复目录和旧备份目录
- `.env`、AI key、用户、支付、解锁、兑换码等敏感文件
- 监控日志和测试结果目录

当前备份是服务器本地增量快照。没有绑定第三方对象存储或 GitHub 作为异地目的地，因此不会未经授权上传用户、支付或运行数据。

## 首次验证

首次手动执行已成功：

- systemd service：`Result=success`
- `ExecMainStatus=0`
- 健康状态：`ok`
- 备份状态：`ok`
- 快照：`/var/backups/nur-daily/20261018T170532Z`
- 快照占用：约 5.3G
- 文件数量：19,897
- 敏感文件扫描：空
- `nur.service`：active
- `nur-health-monitor.service`：active
- timer：enabled

最新状态文件：

```text
/var/lib/nur-daily-health-backup/latest.json
```

最新快照软链接：

```text
/var/backups/nur-daily/latest
```

## 恢复方式

恢复前先停止应用并确认目标快照：

```bash
systemctl stop nur.service
rsync -a /var/backups/nur-daily/<TIMESTAMP>/app/ /opt/nur/
systemctl start nur.service
systemctl status nur.service nur-health-monitor.service
```

只恢复公开代码或页面时，应按文件粒度恢复，避免覆盖用户、支付、解锁、密钥和缓存数据。
