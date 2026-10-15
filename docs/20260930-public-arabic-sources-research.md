# 公开阿拉伯语来源核验（2026-09-30）

## 结论

本项目采用“自有学习界面 + 后端白名单同步 + 可追溯来源字段”的方式，不 iframe 外站，也不把“公开可见”当作“可以整站复制”。查词优先使用本地固定数据；没有本地释义时，才以低频、可缓存的 Arabic Wiktionary API 做公开词典补充。

自动更新只同步最小必要字段。每条内容保存 `source_id`、`source_url`、`license`、`revision/version`、`retrieved_at` 和 `modified`。提供来源/许可证页、纠错和下架机制。

## 来源核验

### Arabic Wiktionary

- 官方 API：<https://ar.wiktionary.org/w/api.php>
- 查询规范：<https://www.mediawiki.org/wiki/API:Query>
- 使用规范：<https://www.mediawiki.org/wiki/API:Etiquette>
- Wikimedia API 指南：<https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_API_Usage_Guidelines>
- 复用条款：<https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use>

页面正文通常按 CC BY-SA 4.0 与 GFDL 框架复用，但具体页面、导入文本和音频可能有额外条件。API 客户端应使用可识别 User-Agent、串行请求、缓存、gzip、`maxlag` 和指数退避。生产策略：默认保存词条标题、页面 ID、revision、URL 和少量经许可文本；音频默认只保存文件描述页链接，不复制音频。

### Kaikki / Wiktextract

- Arabic 数据页：<https://kaikki.org/dictionary/Arabic/>
- rawdata 说明：<https://kaikki.org/dictionary/rawdata.html>
- Wiktextract：<https://github.com/tatuylonen/wiktextract>
- Wiktionary 版权页：<https://en.wiktionary.org/wiki/Wiktionary:Copyrights>

可作为批量词形、词性、IPA 和形态索引来源，但 Arabic 后处理 JSONL 页面标为 DEPRECATED，不能假设存在稳定 API。数据源自 Wiktionary，通常需要 CC BY-SA/GFDL 署名和 ShareAlike/GFDL 条件；第三方引文、音频、图片必须逐项核验。建议周度或更低频率条件检查，只在版本变化时下载，流式解析，不把大整包放到线上请求路径。

### Tatoeba

- 官方站：<https://tatoeba.org/en/>
- Downloads：<https://tatoeba.org/en/downloads>
- API：<https://api.tatoeba.org/>
- OpenAPI：<https://api.tatoeba.org/openapi>
- 条款：<https://tatoeba.org/en/terms_of_use>

文本句子通常为 CC BY 2.0 France，也有 CC0；必须按句子保存作者、句子 ID、语言、许可证、原文 URL 和修改时间。翻译可能是衍生作品。音频许可证与文本不同，许可证为空时不得站外复用。官方 Downloads 每周六 06:30 UTC 更新；建议每周低频同步或按需短 TTL 缓存，串行/低并发并退避，不抓 UI、不复制评论和用户资料。

### Mozilla Common Voice

- 官方入口：<https://commonvoice.mozilla.org/>
- MDC 数据集：<https://mozilladatacollective.com/datasets/cmu5wom3z00ceo107guxtg4xa>
- MDC API：<https://mozilladatacollective.com/api-reference>
- 条款：<https://commonvoice.mozilla.org/en/terms>
- CC0：<https://creativecommons.org/publicdomain/zero/1.0/>

Arabic Scripted Speech 数据标为 CC0，但 Mozilla 条款同时要求不要在其他平台发布、分发或镜像 Common Voice 数据集全部或部分。因此不能直接把整套音频搬到本网站 CDN。默认只保存数据集 ID、版本、许可和官方链接；若必须使用音频，先获得明确授权，或做受控、最小、不可枚举的内部缓存。不要保存贡献者人口统计等不必要字段。

### OpenITI RELEASE

- RELEASE：<https://github.com/OpenITI/RELEASE>
- KITAB 文档：<https://kitab-project.org/docs/openITI>
- 固定版本 DOI：<https://doi.org/10.5281/zenodo.3082463>
- CC BY-NC-SA 4.0：<https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.en>

OpenITI RELEASE 使用 CC BY-NC-SA 4.0，允许非商业条件下的复制/改编并要求署名、原 URI、版本、修改说明和 ShareAlike。商业网站、广告、订阅或付费课程不能仅凭该许可复制全文，应取得商业书面授权或只保存书目、URI、摘要和官方链接。生产环境固定 tag/commit/DOI，按需流式读取，低频检查版本，不下载整库。

### Arabic Wikimedia / Wikipedia feeds

- MediaWiki API：<https://www.mediawiki.org/wiki/API:Main_page>
- Arabic Wikipedia API：<https://ar.wikipedia.org/w/api.php>
- 内容复用：<https://www.mediawiki.org/wiki/Wikimedia_APIs/Content_reuse>
- 机器人规范：<https://wikitech.wikimedia.org/wiki/Robot_policy>
- Terms：<https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use>

可用于发现阿拉伯语阅读素材和元数据。正文通常为 CC BY-SA 4.0，但外部导入、模板、图片和音频需要逐项核验。安全策略是保存标题、URL、revision、时间、少量摘要和许可证信息，不轮询整站全文；用 ETag/Last-Modified、单队列、低并发和退避。全文再分发必须署名、给许可证链接、标记修改并满足 ShareAlike；许可不明时只保存链接或自写摘要。

## 产品内署名策略

1. 原文、第三方来源和自有教学说明分层保存，禁止把来源内容伪装成原创。
2. 每条可见外部内容旁显示来源、原文页、版本/revision、许可证和抓取时间。
3. 不使用 iframe，不把外站页面直接嵌入产品；由本地组件重新排版，保留可点击原始来源。
4. 受许可证不明、音频许可为空、商业条件冲突或撤回影响的内容只保留链接/元数据，支持下架。
5. 自动任务只处理白名单来源，限制大小、超时、并发和每日新增量，失败时保留上一个可用数据集，不覆盖用户数据、会员状态或 AI 密钥。
