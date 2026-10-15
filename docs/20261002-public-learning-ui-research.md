# 公共学习产品交互研究与燃灯同学更新依据

## 研究结论

本轮没有复制任何网站的页面、品牌、Logo、文案、图片、字体、音频或 SVG 路径。只把公开一手页面中可验证的交互关系转成燃灯同学自己的信息架构，并继续使用项目既定的米白、驼色、深棕、4px 和线性 SVG 规范。

最值得落地的共同模式有四个：

1. **索引先于内容**：主题、等级、类型、来源和学习状态先筛选，再进入文章或书页。
2. **正文是主任务**：翻译、词义、语法、音频和注释按需展开，不把所有辅助信息永久堆在正文上。
3. **阅读与复习相连**：点词或拖选后查词，结果回到原句；收藏、最近阅读、待复习和学习目标都要有清晰入口。
4. **筛选可解释**：搜索结果显示数量、当前条件、来源和许可状态，并能一键重置。

## 各站点可迁移的交互规律

### Quran.com

公开首页和章节页展示了主题/章节索引、稳定的章节深链、阿拉伯文与译文分层，以及可选的经注和学习层。[1] 官方更新页说明其音频设置把速度、朗读者、循环、自动滚动和逐词提示集中管理，而不是把所有控制散落在阅读行内。[2] 官方目标页提供 10 分钟、30 天、每日一 Juz 和自定义目标等预设。[3]

迁移到燃灯同学：继续阅读区增加“原文 / 对照 / 复习”模式，音频设置集中在一个面板，目标显示具体分钟和单元，不复制 Quran.com 的颜色或页面比例。

### Al Jazeera Learning Arabic

公开课程索引把内容按级别、内容类型和主题组织，并通过独立课文页进入目标、正文、语言点、词汇和表达。[4] 公开课文和复习页显示文本、翻译、Tashkeel/元音标记、答案显隐和上一课/下一课等状态切换。[5]

迁移到燃灯同学：为阅读区增加清晰的“辅助层”开关，优先显示正文；释义、音符、例句和学习提示按需展开。

### LingQ

公开阿拉伯语课程索引展示等级、课数、词数、主题和方言标签，课程详情页再进入编号课文列表。[6] LingQ 官方文章描述了待复习、筛选/排序、多种练习和阅读中词汇状态等流程。[7]

迁移到燃灯同学：把“标准语 / 方言 / 主题 / 难度 / 音频可用性”作为可筛选索引，把已收藏词条和阅读来源关联起来。不复制 LingQ 的颜色状态和 SRS 算法。

### Readlang

公开 Library 展示了按内容类型、难度、热度/新旧和 Read later 的索引结构。[8] 官方文章描述阅读器中的单词点击、短语选择、上下文解释、自动保存词汇、进度百分比和同步朗读高亮。[9]

迁移到燃灯同学：保持正文连续阅读，点按或选词才出现查词卡；收藏时保留原句、词形、词根和来源，不离开阅读页面。

### Tatoeba

官方搜索把词/短语、句子语言、译文语言分开，并提供长度、标签、音频、列表、排序和结果分页。[10] 结果页保留筛选条件并显示来源、音频与许可信息；下载页区分学习者句子列表和数据导出，音频许可需要逐条核验。[11]

迁移到燃灯同学：来源监测台采用关键词、类型和状态过滤；句子练习保留阿语句子、译文、音频覆盖率和来源标签，不批量镜像社区数据。

### Anki

官方手册描述 Browse 工作区的左侧筛选、右上列表、右下详情三块结构，并支持字段、标签、状态、时间、AND/OR/排除和保存搜索。[12] 复习流程先显示题面，再揭示答案，并把下一次出现时间放在反馈动作附近。[13]

迁移到燃灯同学：右侧来源记录和词条索引使用可解释筛选；新增“继续学习 / 待复习 / 已收藏”状态，而不复制 Anki 的品牌、牌组、按钮颜色或调度算法。

## 本轮实施清单

- 在主题页加入阅读模式开关：原文、对照、复习。
- 在阅读卡加入集中式音频设置：播放、速度、逐句/整段和自动跟读偏好。
- 在索引区加入学习目标预设：10 分钟、1 个单元、自定义。
- 保留来源监测台的白名单过滤，并把来源、许可和同步时间显示在结果中。
- 让查词后的词条卡保留原句和收藏动作，继续使用 `/api/dict/lookup`，不强制 AI。

## 不复制内容

不抓取登录后页面、个人数据、付费课程、整站资源或未核验音频。来源同步仍使用当前白名单、2 MiB 单响应上限和每周定时任务；本轮“同步它们的交互”指同步可解释的流程和状态，不指同步第三方网站内容。

## References

[1]: https://quran.com/al-baqarah "Quran.com Surah reading page"
[2]: https://quran.com/product-updates/simplifying-word-by-word-and-audio-settings "Quran.com audio and word-by-word settings"
[3]: https://quran.com/reading-goal "Quran.com reading goals"
[4]: https://learning.aljazeera.net/en/lessons/level/introductory "Al Jazeera Learning Arabic level index"
[5]: https://learning.aljazeera.net/en/generallanguage/%D9%81%D9%8A-%D9%85%D8%B1%D9%83%D8%B2-%D8%AA%D8%B9%D9%84%D9%8A%D9%85-%D8%A7%D9%84%D9%84%D8%BA%D8%A9-%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A%D8%A9 "Al Jazeera Arabic lesson page"
[6]: https://www.lingq.com/en/learn-arabic-online/courses/ "LingQ Arabic course index"
[7]: https://www.lingq.com/blog/reviewing-vocabulary/ "LingQ vocabulary review workflow"
[8]: https://readlang.com/library "Readlang public library"
[9]: https://blog.readlang.com/2024/12/04/context-aware-translations-and-two-other-features.html "Readlang context-aware translation"
[10]: https://en.wiki.tatoeba.org/articles/show/advanced-search "Tatoeba advanced search"
[11]: https://tatoeba.org/en/downloads "Tatoeba downloads and licensing notes"
[12]: https://docs.ankiweb.net/browsing.html "Anki Browse workspace"
[13]: https://docs.ankiweb.net/studying.html "Anki studying and review flow"
