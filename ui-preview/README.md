# 燃灯同学四屏 UI 预览

这是可继续开发的 React + Tailwind CSS 项目。桌面画板以 2×2 手机界面呈现首页、世界图书馆、搜索与个人页；每台手机的底部导航都可以在四个页面间切换。

本机开发：`npm install` 后运行 `npm run dev`。项目入口为 `main.jsx`，页面组件在 `App.jsx`，视觉规则在 `style.css` 与 `tailwind.config.cjs`。

线上静态预览使用项目根目录的 `design-preview.html`。真实网站继续由 `../build_home.py` 生成，预览样例数据不会覆盖真实书库和学习记录。
