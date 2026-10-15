# 2026-09-28 AI 阅读器性能与交互来源

## DeepSeek 官方 API

- JSON Output 指南：https://api-docs.deepseek.com/guides/json_mode/
  - 使用 `response_format: {"type":"json_object"}`。
  - Prompt 仍必须明确要求 JSON 并提供目标结构示例。
  - `max_tokens` 需要合理设置，过小会导致 JSON 被截断。
  - 官方明确提示 JSON 模式偶尔可能返回空内容，因此客户端仍需做空结果检测和可重试处理。
- Chat Completions：https://api-docs.deepseek.com/api/create-chat-completion/
  - 当前文档列出 `deepseek-flash` 与 `deepseek-v4-pro`。
  - 支持 `thinking`、`reasoning_effort`、`response_format` 和 `stream`。
  - `finish_reason=length` 表示达到 `max_tokens` 或上下文限制，需要避免把截断结果当成功。
  - 可通过 `user_id` 做用户隔离、KV cache 隔离和调度隔离。
- 限流与隔离：https://api-docs.deepseek.com/quick_start/rate_limit
  - 文档说明请求从发送到完成都占用并发连接。
  - `user_id` 不应包含隐私信息；应用应使用不可逆、非个人可识别的设备哈希。

## Apple Books 官方交互参考

- iPhone 阅读指南：https://support.apple.com/guide/iphone/read-books-iphc1af7c57/ios
  - 阅读界面支持主题、字号、竖向滚动/翻页方式、目录快速跳转、书签和高亮。
  - Apple 官方说明关闭阅读可使用关闭按钮或从顶部下滑（开启竖向滚动时有差异）。
- Mac 外观指南：https://support.apple.com/guide/books/change-a-books-appearance-ibks8923126d/mac
  - 支持 Original / Quiet / Paper 等主题、浅色/深色/自动背景、字体、粗体、间距、页边距、两栏布局和全屏阅读。

本文件仅记录交互模式与公开 API 文档，不复制 Apple 的素材或界面代码。
