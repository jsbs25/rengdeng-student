# 燃灯同学 · 微信小程序

原生小程序（WXML / WXSS / JS），对接现有 `server.py` 的 `/api/*`，与网页版共用同一套「纸感 + 墨绿 + 哑金」设计令牌与 RTL 排版。

## 目录结构

```
miniprogram/
├── app.js / app.json / app.wxss      # 全局：入口 / 页面注册+tabBar / 设计令牌
├── config.js                          # API 地址（生产域名）
├── project.config.json                # 开发者工具项目配置（appid 待填）
├── sitemap.json
├── utils/api.js                       # 请求封装（对接 /api/*）
└── pages/
    ├── home/      首页（今日一句 + 学习数据 + 入口）
    ├── learn/     学习（句子库分类）
    ├── library/   世界图书馆（精选书 + 全站搜索）
    ├── ai/        AI 老师（对话）
    └── me/        我的（数据 + 设备登录）
```

## 本地运行

1. 安装并打开「微信开发者工具」，导入本 `miniprogram/` 目录。
2. `project.config.json` 里的 `appid` 目前是 `touristappid`（游客模式），换成你的小程序 AppID。
3. 本地开发：`config.js` 指向 `https://xn--dqry4os3s3gb.com`；开发者工具里勾选「不校验合法域名」即可调试。

## 上线前必须完成（微信平台要求）

1. **request 合法域名**：在微信公众平台 → 开发 → 开发设置 → 服务器域名，把 `https://xn--dqry4os3s3gb.com` 加入 request 合法域名。
2. **HTTPS**：域名必须 HTTPS（已具备 Let's Encrypt 证书）。
3. **ICP 备案**：正式发布要求域名已备案（当前为海外 Hostinger，需完成备案或改用境内备案域名）。
4. **域名校验文件**：若用 web-view 需上传校验文件（本方案未用 web-view，可跳过）。
5. **appid**：替换 `touristappid` 为正式 AppID，并在 `app.json` 填正确信息。

## 说明

- AI 对话、全站搜索、图书馆正文等依赖后端 `/api/*`（已具备，CORS `*`）。
- 图书馆「整书正文」目前在小程序内只展示书目信息，完整阅读请在网页版进行（后续可接入分页接口）。
- 小程序请求不走 cookie，设备登录用 `X-Token` 头传递（`utils/api.js` 已处理）。
