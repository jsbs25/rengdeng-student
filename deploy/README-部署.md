# 燃灯者 · 网页版上线部署指南

## 一、先准备三样东西

| 需要 | 推荐 | 说明 |
|---|---|---|
| **服务器** | Vultr / 阿里云轻量 / 腾讯云轻量（2核2G 起） | 国外机房**免备案**；国内机房要 ICP 备案 |
| **域名**（可选但强烈建议） | 任意注册商 | 没有也能用 IP 直接访问 |
| **HTTPS** | Let's Encrypt 免费证书 | **麦克风/口语陪练必须 HTTPS**，否则 iPhone 上不给用麦克风 |

> 关键点：这个 App 是「标准库 Python 服务 + 静态文件」，**不需要 Flask/FastAPI**，部署很轻。

## 二、一键部署（Ubuntu 22.04 为例）

```bash
# 1. 在服务器上装好基础环境
sudo apt update && sudo apt install -y python3 python3-pip nginx certbot python3-certbot-nginx

# 2. 把项目传上去（在你自己电脑上执行）
rsync -av --exclude 'harvest/cn/daizhige' --exclude 'app/node_modules' \
  ~/Desktop/arabic-learning/ root@你的服务器IP:/opt/nur/

# 3. 在服务器上启动
cd /opt/nur
sudo bash deploy/setup.sh          # 装 systemd 服务 + nginx 反代
```

## 三、域名 + HTTPS

```bash
# 把域名 A 记录指向服务器 IP 后：
sudo certbot --nginx -d your-domain.com
```
certbot 会自动改好 nginx 并续期。

## 四、目录与端口

- 服务监听 `127.0.0.1:8080`（只对本机开放，由 nginx 对外）
- 页面：`/opt/nur/arabic_learning.html`
- 数据：`/opt/nur/data/`（伊斯兰书目 8MB、圣训 42MB、中国古籍、经注、图谱）
- AI 密钥：`/opt/nur/data/ai_key.txt`（**只放服务器，别提交到公开仓库**）

## 五、体积说明（上传前可裁剪）

| 目录 | 体积 | 是否必须 |
|---|---|---|
| `arabic_learning.html` | 12MB | ✅ 必须 |
| `data/islamic_catalog.json` | 8MB | ✅ |
| `data/hadith/*.json` | ~42MB | ✅（六大部全文） |
| `data/cn_books/t/*.txt` | ~4GB | ⚠️ 可只传 `index.json`，正文按需 |
| `data/history`, `data/tafsir.json`, `data/civ*.json` | <1MB | ✅ |
| `assets/imgs` | 660KB | ✅ |

## 六、安全建议

1. **务必开 HTTPS**（否则麦克风、PWA 都用不了）
2. 给 `/api/chat/message` 加**限流**（防别人盗刷你的 AI 额度）
3. `data/ai_key.txt` 权限设 `600`，且不要进 git
4. 想更强：在 nginx 加 `limit_req` 限速

## 七、上线后

- 手机 Safari 打开 `https://你的域名/` → **分享 → 添加到主屏幕** = 得到一个全屏 App（PWA）
- 有 Xcode 的电脑上跑 `bash tools/build_ipa.sh` 可以再打 iOS 安装包
