# 阶段 0 保护性基线回归报告

**日期：** 2026-10-05
**状态：** 完成；未修改业务代码、数据、API 或生产服务。

## 离线检查

| 检查 | 结果 |
|---|---|
| Python 语法：`server.py`、`build_home.py`、`openiti_stream.py` 与专项脚本 | 通过 |
| OpenITI 流式与增量 UTF-8 | 通过：202/200/416、无阿语替换字符、manifest 可恢复 |
| 经典索引完整性 | 通过：1,820 条、ID 唯一、Shamela 可读、4 条阅读路径 |

## 浏览器回归

| 模块 | 手机 | 桌面 |
|---|---:|---:|
| NOUR 产品壳 | 19/19 | 18/18 |
| Apple 风格阅读器窗口 | 18/18 | 18/18 |
| 日夜主题与中阿混排 | 12/12 | 12/12 |
| 古兰经页级入口 | 7/7 | 7/7 |
| 教法证据链 | 10/10 | 10/10 |
| 选词与阅读上下文 | 11/11 | 11/11 |
| 经典索引与阅读路径 | 9/9 | 9/9 |

**浏览器合计：171/171，通过项无 JavaScript 运行时错误。**

## 公网 API 基线

- `/api/catalog/meta`：HTTP 200，目录总数 **8,794**。
- `/api/catalog?size=1`：HTTP 200，分页返回 1 条。
- `/api/library/classics?size=1`：HTTP 200，返回真实阅读入口和 4 条路径。
- `/api/library/fiqh-schools?size=1`：HTTP 200。
- `/api/dict/lookup?w=ذهب`：HTTP 200，词典接口合同正常。
- `/api/quran/tafsir?surah=1`：HTTP 200。
- `/api/read?t=shamela&id=8220`：HTTP 200，真实 **239 页**。
- 首页 HTTP 200。
- `nur.service`：`active`。
- `nur-health-monitor.service`：`active`。

## 环境限制

连接的桌面终端没有 `node` 可执行文件，因此没有执行 `node --check`。没有因此安装依赖或更换技术栈；页面 JavaScript 已由真实浏览器回归执行并全部通过。

## 阶段 0 结论

阶段 0 通过。下一阶段仍需单独确认后才开始；阶段 1 只允许修改一级导航适配层，不修改后端、数据、阅读器业务逻辑和账户/会员状态。
