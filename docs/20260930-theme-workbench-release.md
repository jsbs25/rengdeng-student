# 纸页索引工作台主题发布记录

## 访问地址

- 公网：<https://xn--dqry4os3s3gb.com/theme_workbench.html>
- 本地：`http://127.0.0.1:8110/theme_workbench.html`

本次作为独立主题页发布，未替换燃灯同学现有首页，便于比较和回退。

## 设计主题

**纸页索引工作台 / Arabic Study Desk**。

页面不是营销式 Hero，而是一个长文档式的学习索引：左侧固定目录、中央词条与阅读记录、右侧学习统计和来源记录。桌面端使用 236px 侧栏 + 不等宽主/侧内容区；手机端折叠侧栏，保持词条、阅读和索引顺序。

## 约束落实

- 米白 `#F8F6F2`、驼色 `#C4A484`、深棕 `#3C2F2F` 为主色。
- 没有蓝紫色渐变，也没有 CSS gradient。
- 所有交互面板和按钮使用 4px 圆角；没有 50% 或 999px 大圆角。
- 图标全部为线条 SVG，没有 emoji 图标。
- 没有大面积阴影，没有 hover 放大；仅使用细边框、留白和颜色变化建立层级。
- 文案使用具体记录：42 分钟、8 个词条、页 68 / 142、3 天连续学习、8,794 条书目。
- 交互：真实调用 `/api/dict/lookup`，支持本地优先查词；调用浏览器 `speechSynthesis` 朗读；收藏写入 localStorage；索引导航滚动到对应章节。

## 验收

- 手机 390×844：14/14 通过。
- 桌面 1280×900：14/14 通过。
- 公网手机 390×844：14/14 通过。
- 公网桌面 1280×900：14/14 通过。
- 公网文件 SHA-256：`681d020d8de51d876a05ecf0fd7eb7b5ed9ebfd583334f4ec5cf063aa625d480`。
- `nur.service`、`nur-health-monitor.service`、`nur-public-source-sync.timer` 均 active。

## 回滚

独立主题页回滚点：`/opt/nur/backups/20260930-theme-workbench`。

删除或替换 `/opt/nur/theme_workbench.html` 即可，不需要重启服务，也不会影响用户数据、会员状态、AI 配置、OpenITI 缓存或现有首页。
