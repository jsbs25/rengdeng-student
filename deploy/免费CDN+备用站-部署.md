# 燃灯同学 · 免费 CDN + 免费备用站 部署指南

## 主站（已在跑 ✓）
- VPS：`152.239.115.147`（Hostinger KVM1 · AlmaLinux9 · 法兰克福）
- 域名：`燃灯同学.com` → A 记录指向 VPS ✓
- SSL：Let's Encrypt ✓ 自动续期 ✓
- 服务：`systemctl restart nur` · 代码 `/opt/nur`

## ① 免费 CDN + 免费 SSL：Cloudflare（推荐，10 分钟）
1. 注册 https://dash.cloudflare.com （免费 ✓）
2. Add site → 输入 `燃灯同学.com` → 选 Free 计划
3. Cloudflare 给两个 NS（如 `xxx.ns.cloudflare.com`）→ 到 **Hostinger → DNS → 更改域名服务器** 改成这两个
4. Cloudflare 里加 A 记录：`@` → `152.239.115.147`（橙云=代理 ✓）
5. SSL/TLS → 模式选 **Full (strict)** ✓（自动免费证书 ✓）
6. 开 **Auto Minify** + **Brotli** + **Caching: Standard** ✓
效果：全球加速 ✓ 免费 SSL ✓ 抗 DDoS ✓ 源站隐藏 ✓ 月流量免费 ✓

⚠️ 注意：改了 NS 后，Hostinger 的 DNS 就不再生效 ✓ 所有记录都在 Cloudflare 管 ✓

## ② 免费备用站（静态镜像）：三选一
本项目 `dist/` 目录已经是**可静态部署的完整站**（HTML + 数据 + 字体 ✓）。
（说明：AI 对话 / 全站搜索 / 封面抓取需要主站 API ✓ 静态镜像会自动调主站接口 ✓ 已开 CORS ✓）

### 方案 A：Cloudflare Pages（推荐 ✓ 免费 ✓ 自带 SSL ✓ 可绑域名）
1. https://dash.cloudflare.com → Workers & Pages → Create → Pages → Upload assets
2. 把 `dist/` 整个文件夹拖进去 → Deploy ✓
3. 得到一个 `xxx.pages.dev` 网址 ✓（可再绑 `beifen.燃灯同学.com`）

### 方案 B：Netlify（同样免费 ✓）
1. https://app.netlify.com/drop → 拖 `dist/` 进去 ✓ 秒得网址 ✓

### 方案 C：Vercel / GitHub Pages（免费 ✓）
- Vercel：拖 `dist/` ✓
- GitHub Pages：建仓库 → 上传 `dist/` → Settings → Pages ✓

## ③ 免费 VPS（开源/免费额度，需要注册）
| 平台 | 免费额度 | 说明 |
|---|---|---|
| Oracle Cloud Always Free | 2×AMD/4×ARM 永久免费 | 最强 ✓ 但要信用卡验证 ✓ |
| Fly.io | 小额度免费 | 支持 Python ✓ |
| Koyeb | 1 个免费实例 | 支持 Python ✓ |
| Render | 免费 Web Service | 会休眠 ✗ |
| Railway | 试用额度 | 之后收费 ✗ |

**建议**：备用站用 **Cloudflare Pages（静态镜像）** 就够了 ✓
（真正的动态备用再上 Oracle Always Free ✓ 我可以帮你写部署脚本 ✓）

## ④ 一键同步脚本（本地）
```bash
cd ~/Desktop/arabic-learning
python3 build_home.py            # 重新生成页面
bash tools/sync_dist.sh          # 同步到 dist/（静态镜像）
# 然后把 dist/ 拖到 Cloudflare Pages 即可
```
