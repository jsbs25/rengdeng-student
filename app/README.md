# نور العربية · Nur Al-Arabiyya · 阿拉伯语之光

专业跨平台阿拉伯语学习 APP（React Native + Expo，支持 iOS / Android / Web）。

## 项目结构

```
app/
├── App.js                    # APP 入口 + 底部5导航
├── app.json                  # Expo 配置 (iOS/Android 标识)
├── assets/icon.png           # APP 图标（深绿+金拱门）
├── src/
│   ├── config.js             # API 地址配置（Web=localhost / 真机=局域网IP）
│   ├── theme.js              # 主题（深绿/金/米白）
│   ├── data.js               # 学习数据（13分类·1743句·离线可用）
│   ├── articlesData.js       # 内置13篇文章（图书馆离线可用）
│   ├── api.js                # 数据层：服务器优先 + 离线降级 + 本地词频表
│   ├── store.js              # 本地持久化（收藏/学习/复习/统计/连续天数/订阅）
│   ├── components.js         # 玻璃卡片/拱门/圆环/句子卡/分类
│   ├── LibraryModal.js       # 图书馆（文章阅读 + AI 写文章）
│   ├── WordModal.js          # 单词表（词汇表 + 单词拆解 + AI 词义解释）
│   └── screens/
│       ├── HomeScreen.js     # 首页（真实统计 + 全部入口）
│       ├── LearnScreen.js    # 学习（句子表：分类/搜索/收藏/复习/已学）
│       ├── ListenScreen.js   # 听力（慢速/正常/听写模式/跟读录音+评分）
│       ├── AIScreen.js       # AI老师（DeepSeek，有上下文记忆+自动朗读）
│       └── ProfileScreen.js  # 我的（统计/会员）
└── dist/                     # Web 构建产物
```

## 运行

```bash
cd ~/Desktop/arabic-learning/app

# 1. 启动数据服务（AI对话/文章需要）
cd ~/Desktop/arabic-learning && python3 server.py

# 2. Web 预览
cd app && npx expo start --web

# 3. 真机测试（Expo Go）
npx expo start
# 手机装 Expo Go，同一WiFi扫码即可
```

**真机连不上服务器？** 编辑 `src/config.js` 里的 `LAN_IP`，改成电脑的局域网 IP（`ipconfig getifaddr en0` 查看），手机和电脑需在同一 WiFi。

## 打包发布

### 安卓 APK（免费，云打包）
```bash
cd ~/Desktop/arabic-learning/app
npm install -g eas-cli
eas login        # 用 Expo 账号登录（免费注册）
eas build --platform android --profile preview
# 生成 APK，下载安装；正式发布用 production profile 生成 AAB 上传 Google Play
```

### 苹果 IPA（需 Apple Developer 账号）
```bash
eas build --platform ios
# 云端生成 IPA；或用 Xcode:
# npx expo prebuild --platform ios && open ios/*.xcworkspace
# 需 Apple Developer 账号 (99美元/年) + Xcode 签名
```

### 免账号测试
- **iOS**: 用 Expo Go 扫码（免费）
- **Android**: `eas build -p android --profile preview` 直接出 APK

### 真机 AI 连不上？
1. 手机和电脑连**同一个 WiFi**
2. 电脑先启动服务：`cd ~/Desktop/arabic-learning && python3 server.py`
3. 确认电脑 IP 与 `src/config.js` 里的 `LAN_IP` 一致（终端 `ipconfig getifaddr en0` 查看）
4. 已配置 iOS 允许 HTTP（ATS）+ 局域网权限说明、Android 明文流量许可，独立安装包可直接连本地服务

## 功能清单

- [x] 首页：拱门 Header / 今日学习圆环（真实进度）/ 数据卡 / 功能入口 / 分类 / 每日一句
- [x] 句子表（学习页）：13 分类 / 搜索 / 🔊阿语·🇬🇧英语朗读（自动记已学）/ ⭐收藏 / 📌复习 / ✅已学筛选
- [x] 单词表：3314 个词频词 + 搜索 + 发音 + 🤖AI 逐词解释（词义/词性/例句）+ 句子逐词拆解
- [x] 听力：慢速 0.5 / 正常 0.7 / 🙈听写模式（隐藏翻译）/ 🎤跟读录音（真实时长评分：语速+完整度）
- [x] AI老师：中文/阿语提问 / 阿语回答+中文 / 有上下文记忆 / 自动朗读（可开关）/ 纠错 / 写文章
- [x] 图书馆：13 篇内置文章（离线可用）/ 🔊朗读全文 / ✨AI 写文章
- [x] 我的：学习统计（连续天数/今日分钟/已学/收藏）/ 会员预留
- [ ] 登录系统（Apple/Google/手机号）— 预留
