# 伊斯兰经典与图书来源核验

日期：2026-09-27

本记录只保存公开来源和接入边界。产品默认采用“元数据同步、正文按需、官方外链优先”，不绕过登录、验证码、robots、速率限制或版权保护。

## Maktabah Salafiyyah

- 官方主页：https://maktabahsalafiyyah.org/
- Books 分类：https://maktabahsalafiyyah.org/category/books/
- WordPress REST API：https://maktabahsalafiyyah.org/wp-json/
- 书籍分类 API：https://maktabahsalafiyyah.org/wp-json/wp/v2/categories?parent=31&per_page=100
- 书籍文章示例：https://maktabahsalafiyyah.org/wp-json/wp/v2/posts?categories=31&per_page=5
- robots：https://maktabahsalafiyyah.org/robots.txt
- 版权页：https://maktabahsalafiyyah.org/rights-of-publication/

该站公开提供 WordPress 书籍文章、分类、搜索和部分 PDF 外链。重点学科包括 Aqidah/Manhaj、Fiqh、Hadith、Tafsir、Manners、Refutation、Zuhd、Sirah 等。未发现逐项开放许可证，因此产品只同步标题、作者、分类、摘要、详情 URL 和 PDF 外链；默认不下载、镜像或重新托管 PDF。

## Shamela

- 官方主页：https://shamela.ws/
- 官方 MCP：https://shamela.ws/mcp
- 支持说明：https://shamela.ws/page/support
- 条款：https://shamela.ws/page/terms
- 隐私：https://shamela.ws/page/privacy
- 圣训分类示例：https://shamela.ws/category/6
- 书籍与逐页示例：https://shamela.ws/book/1546/171

Shamela 的公开网页和只读 MCP 可用于书目、搜索、目录和按页阅读。涉及法学、法源学、经注、圣训、信仰、传记、语言等学科。官网没有把全库统一声明为开放许可；推荐只保存元数据和官方逐页链接，获得明确授权后再考虑缓存正文。

## Sunnah.com 六大部

- Bukhari：https://sunnah.com/bukhari
- Muslim：https://sunnah.com/muslim
- Abu Dawud：https://sunnah.com/abudawud
- Tirmidhi：https://sunnah.com/tirmidhi
- Nasa'i：https://sunnah.com/nasai
- Ibn Majah：https://sunnah.com/ibnmajah
- Developers/API：https://sunnah.com/developers
- About：https://sunnah.com/about

六大部页面公开展示书、章节、Reference、In-book reference、阿拉伯原文、译文和部分等级。官方 About 明确禁止 scraping 和大规模再发布整本书/整套合集；API 需要申请 key，离线 dump 尚不可用。因此本站只做六部书目和官方链接目录；没有 API 授权时不抓取圣训全文。

## Quran.com 与 AlQuran.Cloud

- Quran Foundation 开发者文档：https://api-docs.quran.foundation/docs/quickstart/
- Content API：https://api-docs.quran.foundation/docs/content_apis_versioned/4.0.0/content-apis/
- Search API：https://api-docs.quran.foundation/docs/search_apis_versioned/1.0.0/quran-foundation-search-api/
- Quran.com 条款：https://quran.com/terms-and-conditions
- AlQuran.Cloud API：https://alquran.cloud/api
- AlQuran.Cloud editions：https://api.alquran.cloud/v1/edition
- AlQuran.Cloud CDN：https://alquran.cloud/cdn
- AlQuran.Cloud 条款：https://alquran.cloud/terms-and-conditions

Quran.com Content API 提供章节、经文、译文、经注、逐词、诵读等结构化内容，但需要服务端凭据；不能抓取网页替代 API。AlQuran.Cloud 提供免 key 的逐节 API 和音频 CDN，可作为现有古兰经的按需回退。原文、译文、经注和诵读应分层记录 edition/resource/reciter 与来源，音频默认流式外链，不批量镜像。

## Internet Archive / Open Library

- IA Advanced Search：https://archive.org/advancedsearch.php
- IA Metadata API：https://blog.archive.org/2013/07/04/metadata-api/
- Open Library API：https://openlibrary.org/developers/api
- Open Library 数据：https://openlibrary.org/data
- 借阅说明：https://openlibrary.org/help/faq/borrow

Internet Archive 的单个条目可能明确标注 Public Domain 并提供 OCR/PDF；但权利必须逐条检查。Open Library 适合书目发现和借阅外链，不把借阅文件当公开下载。默认缓存 metadata、rights、licenseurl、file format 和官方详情链接；明确公版后才按需读取公开文件。

## 产品接入原则

1. 书库按“来源 → 学科 → 书目 → 官方详情/阅读”组织。
2. Maktabah Salafiyyah 使用公开 WordPress GET API 做低频书目同步。
3. Shamela 使用官方 MCP/官方网页按需读取，默认不全库爬取。
4. Sunnah.com 六大部先做书目目录和官方链接；API key 获得后再实现服务端小范围代理。
5. Quran.com 使用官方 Content/Search API；AlQuran.Cloud 作为免 key 的逐节和音频回退。
6. Internet Archive/Open Library 只收录逐条核验过权利的书籍，借阅内容只外链。
7. 页面展示来源、版本、作者、译者、诵读者、抓取时间和版权提示，AI 分析不得把学习性归纳写成法特瓦。

## 2026-09-27 五学科世界图书馆扩展

本轮新增统一书目文件 `data/islamic_catalog.json`，共 38 部：伊斯兰法学 6 部、法源学 7 部、圣训学 7 部、古兰经学 5 部、阿拉伯修辞学 6 部、古兰经与经注馆内入口 1 个、六大部圣训馆内入口 6 个。每条记录至少包含：原文题名/作者、时代或版本、中文学科与阿拉伯语学科、难度、来源说明、官方 URL、访问方式、权利提示、学习导览和 AI 分析画像。

已核验并用于目录导航的公开入口包括：

- 法学/法源学：OpenITI/KITAB 文档与 release、Arabic Collections Online、Waqfeya、HathiTrust、Internet Archive、WorldCat/高校研究指南；外部正文按官方版本打开，不把开放元数据扩展成全文许可。
- 圣训学：Shamela 圣训学分类与逐章阅读、Waqfeya 书目分类、Internet Archive 单条 BookReader、OpenITI 机器可读版本；圣训学术语分析不自动判定某条圣训的真伪或现实可用性。
- 古兰经学：Library of Congress 数字馆藏/IIIF、Arabic Collections Online、Royal Aal al-Bayt Institute、Gibb Memorial Trust、Quranic Arabic Corpus、Corpus Coranicum、OpenITI；手稿图像、OCR、经注、译文和第三方材料逐项区分权利。
- 修辞学：Arabic Collections Online、Internet Archive 单条 BookReader/元数据 API、OpenITI 和 NYU Press Library of Arabic Literature；“三科”是后世教学映射，不强行改写早期 adab 文本的历史结构。

### AI 注解边界

1. 每张书目卡均提供“AI 导读”，但外部目录默认是**书目级元数据导读**，不声称模型读过整本书，也不复制受保护正文。
2. 书目导读页面把题名、作者、时代、学科、官方来源、访问方式和权利状态送入 `/api/page/analyze`；服务端缓存键包含书目 ID 和学科，防止不同书籍的分析串线。
3. AI 输出继续分开显示：页面摘要、核心内容、问题、学习建议、古兰经依据、圣训依据、法学/学术背景、阿语术语、来源说明和固定安全提示。
4. 书目级导读要求没有明确证据时将经文/圣训依据留空或标记“待核验”，不得因为书名属于宗教或法学学科就补造引文、编号、页码、作者观点或教法结论。
5. 原文、译文、经注/注释、学者观点和模型归纳必须独立标记；固定声明为“AI 注解仅用于文本理解和学习辅助，不是法特瓦，不替代合资格学者、教师或当地法律意见”。
6. 要实现某部外部书的真正逐页 AI 注解，下一阶段必须先核验该版本的授权/公版状态，再按官方页码或 IIIF/BookReader 锚点按需接入；本轮不做未经许可的全库下载、OCR 镜像或反爬。


## 2026-09-27 核心法学/法源学书目 AI 导读核验来源

本轮对 13 部核心书目分别核验至少 2 个实际打开的官方馆藏、官方书页或学术机构来源。完整结构化字段已合并入 `data/islamic_catalog.json` 的 `ai_guide`；以下保留来源 URL 以便版本和论证复核。

### الرسالة · al-Risāla（`fiqh-risala`）
- [Internet Archive：《Imam Shafi's Risalah》条目](https://archive.org/details/imamshafirisalah)：实际打开并核对目录指定的官方 BookReader 条目，支持题名、作者、阿拉伯语扫描、OCR及馆藏元数据；条目对具体校订版交代有限，因此不能把它当作唯一版本。
- [阿拉伯文学图书馆：《法源理论书信》官方书页](https://www.libraryofarabicliterature.org/books/9780814769980/the-epistle-on-legal-theory/)：实际打开的学术出版项目页面，支持作者沙斐仪卒于204 AH／820 CE、作品的法源学主题、阿拉伯语作为启示语言、文本解释、证据协调和推理等内容，并说明现代双语文本依据两种重要校勘本且保留异文。
- [纽约大学出版社：《法源理论书信》官方书页](https://nyupress.org/9780814769980/the-epistle-on-legal-theory/)：实际打开的出版社页面，支持该书作为现存最早的阿拉伯语法源学作品和伊斯兰法学基础性文献的学术定位，也列出作者、编辑译者、出版年份及主题范围。
- [澳大利亚国家图书馆书目：《伊斯兰法学：沙斐仪的〈书信〉》](https://catalogue.nla.gov.au/catalog/796457)：实际打开的国家图书馆书目页，核对马吉德·哈杜里译本的题名、作者、1961年约翰斯·霍普金斯出版社信息、376页及作者年代记载，说明不同现代译本和页码必须分版本核验。

### الموطأ · al-Muwaṭṭaʾ（`fiqh-muwatta`）
- [Sunnah.com：Muwatta Malik 官方阅读入口](https://sunnah.com/malik)：目录卡指定的官方阅读链接；实际打开页面确认其将 Muwatta Malik 列为独立圣训文献集合，并提供章节/检索入口。该页主要是阅读入口，不应替代批判性校订本。
- [KITAB Project：A Tale of 3 “Versions”](https://kitab-project.org/A-Tale-of-3-Versions/)：学术数字人文项目页面，实际比较叶海亚·本·叶海亚、艾布·穆斯阿卜与穆罕默德·沙伊巴尼的《الموطأ》传本，支持多传本、文本顺序差异、传承复杂性及179/796年代口径的信息。
- [Internet Archive：al-Muwatta : Mālik ibn Anas, -795](https://archive.org/details/almuwatta0000mlik)：实际打开的馆藏条目；其元数据记录题名、作者 Mālik ibn Anas、1982年出版、伊斯兰法和马立克派主题、页数及访问限制，支持书目核对，但不代表该受限现代版本可自由再分发。
- [OpenITI 官方文档：语料、版本与引用说明](https://openiti.org/documentation/)：实际打开的项目文档，说明OpenITI工作版本与可引用发行版的区别、数字文本质量差异和必须引用具体文件/版本的原则，为《الموطأ》传本比较和数字文本使用提供方法边界。

### 《المدونة الكبرى》· al-Mudawwana al-Kubrā（`fiqh-mudawwana`）
- [Shamela 官方检索页：《المدونة الكبرى》目录入口](https://shamela.ws/index.php/search?q=%D8%A7%D9%84%D9%85%D8%AF%D9%88%D9%86%D8%A9%20%D8%A7%D9%84%D9%83%D8%A8%D8%B1%D9%89)：核对目录提供的官方链接及当前检索入口；页面说明 Shamela 的书目、全文检索和只读文本项目，并提醒具体作者、版本标注须进入书页复核。
- [巴黎索邦大学出版社 OpenEdition：Ibn al-Qāsim 研究章](https://books.openedition.org/psorbonne/142623?lang=en)：学术机构开放章节，支持伊本·卡西姆作为马立克学说重要中介、其传述材料的多种保存方式，以及《المدونة》在伊本·卡西姆与萨赫农之间的归属和层累性存在争议。
- [Internet Archive：《Al Mudawwana al Kubra》五卷扫描条目](https://archive.org/details/179HijriAlMudawwanaAlKubraJild4ByFactofislamsms.wordpress.comOfShakil917698679976)：实际数字馆藏条目，显示五卷扫描、阿拉伯语 OCR、上传元数据和题名/作者标签；可用于确认可读版本与版本边界，但不能据上传标题反推古典成书年代。
- [الرابطة المحمدية للعلماء：المدونة لسحنون](https://www.arrabita.ma/%D8%A7%D9%84%D9%85%D8%AF%D9%88%D9%86%D8%A9-%D9%84%D8%B3%D8%AD%D9%86%D9%88%D9%86/)：摩洛哥穆罕默德学者联盟专题资料，详述《الأسدية》、阿萨德、伊本·卡西姆与萨赫农之间的传统编纂叙述、188/191 AH节点、整理编排和马立克学派对《المدونة》的接受；相关细节仍应与学术校勘研究交叉核验。

### مختصر القدوري · Mukhtaṣar al-Qudūrī（`fiqh-quduri`）
- [HathiTrust 书目：Matn al-Qudūrī fī fiqh madhhab al-Imām Abī Ḥanīfa](https://catalog.hathitrust.org/Record/102709712)：实际打开的馆藏书目页；支持题名变体、主作者古都里及972/973—1037年生卒信息，并显示1324 AH/1906或1907年、128页版本和 Harvard Full View 链接。
- [المكتبة الشاملة：كتاب مختصر القدوري](https://shamela.ws/book/124336)：实际打开的官方只读书页；支持作者全名、哈乃斐归属、卒年428 AH、1997年校订版元数据，并列出从 الطهارة 到 الفرائض 的56部“书”及其章节入口。
- [المكتبة الشاملة：作者页 القدوري](https://shamela.ws/author/2667)：实际打开的作者书目与简介页；支持其巴格达哈乃斐法学家身份、362—428 AH、在伊拉克哈乃斐学界的地位，并提醒《التجريد》是另一本讨论分歧的作品。
- [Internet Archive：Mukhtasar-Al-Quduri](https://archive.org/details/Mukhtasar-Al-Quduri)：实际打开的数字馆藏条目；提供阿拉伯语扫描、OCR、文本/PDF入口和条目元数据，标注作者古都里、362—428 AH/972—1037 CE；其OCR与上传版本需回看页图复核。

### بداية المجتهد ونهاية المقتصد · Bidāyat al-Mujtahid（`fiqh-bidaya`）
- [Shamela《بداية المجتهد ونهاية المقتصد》书目页](https://shamela.ws/book/21739)：实际打开的官方只读书目页；支持题名、作者为伊本·鲁世德、卒年595 AH、比较法学分类、马立克归属、所用版本与目录结构。
- [大英百科全书 Averroes 词条](https://www.britannica.com/biography/Averroes)：实际打开的学术参考页；支持1126–1198、科尔多瓦法学家族、传统伊斯兰学科训练、法官经历及阿尔摩哈德时代背景。
- [Brill《The Introduction To Ibn Rushd's Bidāyat Al-Mujtahid》](https://brill.com/view/journals/ils/1/2/article-p188_2.xml?language=en)：实际打开的《Islamic Law and Society》研究论文摘要页；支持本书处理逊尼法学学派之间的法律分歧，并追问支撑具体法学分支差异的法学原则；页面给出作者、1994年、页码188–205等书目信息。
- [多伦多大学图书馆《The Other Averroes: Revealed Law and the Craft of Juristic Disagreement》记录页](https://utoronto.scholaris.ca/items/f65890cf-a41a-41c4-aeea-cc4460ab6411)：实际打开的大学图书馆学位论文记录页；支持研究对象是伊本·鲁世德的法律著作、法律分析方法与asbāb al-khilāf；论文关于“在法律多样中寻求统一”的表述是研究者论点，不应改写成作者原话。

### المغني · al-Mughnī（`fiqh-mughni`）
- [Shamela：《المغني》书页（开罗版）](https://shamela.ws/book/8463)：实际打开的官方只读书页；支持题名、作者541–620 AH、以《مختصر الخرقي》为底本、10卷版本、法学与比较法学定位、目录结构及其关于证据、异说、共识和作者择强的说明。
- [Shamela：伊本·古达马作者页](https://shamela.ws/author/474)：实际打开的官方作者书目页；支持作者的汉百里归属、生平路线、卒年，以及《المغني》15卷图尔基—哈卢校订版和《الكافي》《المقنع》等作品信息。
- [University of Glasgow Enlighten Theses：Kitab al-jihad in al-Mughni by Ibn Qudamah](https://theses.gla.ac.uk/71197/)：实际打开的大学学术论文页面；摘要将《المغني》称为伊斯兰法的重要来源，并明确指出作者属于汉百里学派而书中呈现各法学学派观点。
- [Internet Archive：《المغني》— ابن قدامة — ت. التركي، الحلو](https://archive.org/details/almoghnismk)：实际打开的 Internet Archive 馆藏条目；支持图尔基、哈卢校订版本的书目元数据、15卷文件列表、阿拉伯语OCR及版本核验入口。

### الرسالة في أصول الفقه · al-Risāla fī Uṣūl al-Fiqh（`usul-risala`）
- [Internet Archive：《Imam Shafi's Risalah》条目](https://archive.org/details/imamshafirisalah)：实际打开的官方 BookReader 条目；支持目录所列题名、作者归属、阿拉伯语扫描／OCR、条目标识和逐页阅读入口。该条目元数据由上传者提供，不能替代校勘本。
- [NYU Press：《The Epistle on Legal Theory》](https://nyupress.org/9780814769980/the-epistle-on-legal-theory/)：出版社官方书目页；支持沙斐仪卒于204/820、作品作为最早存世阿拉伯语法源理论著作之一的定位、古兰经与圣训解释、法律认识论和推理等主题，并说明阿拉伯文本依据两种重要校勘本且保留异文。
- [剑桥大学出版社：Wael B. Hallaq《Was al-Shafiʿi the Master Architect of Islamic Jurisprudence?》](https://www.cambridge.org/core/journals/international-journal-of-middle-east-studies/article/abs/was-alshafii-the-master-architect-of-islamic-jurisprudence/71A7752678E37309173ABA27AB12710E)：实际打开的学术论文页面；支持对“沙斐仪是法源学唯一奠基者”的历史反思，以及“أصول الفقه”名称和《الرسالة》早期题名可能晚于作者时代的谨慎表述。
- [OpenITI 官方文档](https://openiti.org/documentation/)：实际打开的学术数字人文项目文档；支持版本元数据、具体文件引用、不同底本与文本质量差异、OCR 可能低于95%准确率等证据边界，因此说明数字文本不能替代原典核验。

### الورقات في أصول الفقه · al-Waraqāt（`usul-waraqat`）
- [المكتبة الشاملة：الورقات في أصول الفقه检索入口](https://shamela.ws/index.php/search?q=%D8%A7%D9%84%D9%88%D8%B1%D9%82%D8%A7%D8%AA%20%D9%81%D9%8A%20%D8%A3%D8%B5%D9%88%D9%84%20%D8%A7%D9%84%D9%81%D9%82%D9%87)：实际打开的官方检索页；核对了目录提供的 Shamela 链接、法源学分类及其只读/可检索书库性质。该页未呈现固定校勘版，因此不把它当作唯一版本。
- [Internet Archive：الورقات في أصول الفقه2](https://archive.org/details/2_20210218_20210218_1119)：实际打开的馆藏条目；支持题名、作者标为 الجويني、阿拉伯语扫描/OCR、PDF与全文下载入口等书目和版本事实。它是数字传本条目，不等于经过校勘的定本。
- [Internet Archive：该条目全文 OCR](https://archive.org/stream/2_20210218_20210218_1119/%D8%A7%D9%84%D9%88%D8%B1%D9%82%D8%A7%D8%AA%20%D9%81%D9%8A%20%D8%A3%D8%B5%D9%88%D9%84%20%D8%A7%D9%84%D9%81%D9%82%D9%87%202_djvu.txt)：实际打开并阅读了原文 OCR；核对了开头的 أصول الفقه 与 الحكم 定义、章节链条，以及 الأمر、العام والخاص、النسخ、الإجماع、الأخبار、القياس、الاجتهاد等术语。OCR 字形和页码需回看图像。
- [Encyclopaedia Iranica：Jovayni, Emām-al-Ḥaramayn](https://www.iranicaonline.org/articles/jovayni-emam-al-haramayn/)：实际打开的学术百科条目；支持朱韦尼 419–478 AH / 1028–1085 CE、生平、沙斐仪身份、阿什尔里传统背景，以及其法源学作品中《البرهان》与简短《Waraqāt》的关系。

### البرهان في أصول الفقه（al-Burhān）（`usul-burhan`）
- [Waqfeya《البرهان في أصول الفقه》书目与扫描入口（ عبد العظيم الديب 校订）](https://waqfeya.net/books/%D8%A7%D9%84%D8%A8%D8%B1%D9%87%D8%A7%D9%86-%D9%81%D9%8A-%D8%A3%D8%B5%D9%88%D9%84-%D8%A7%D9%84%D9%81%D9%82%D9%87-%D8%AA-%D8%A7%D9%84%D8%AF%D9%8A%D8%A8-f6921ab6ec314520a51a0d62eaa98591)：实际打开的官方馆藏书目页；支持题名、作者、校订者、1399年版本、两卷、1473页、第五世纪分类和目录中的 البيان、命令、禁止等章节。
- [Shamela《البرهان في أصول الفقه》书页](https://shamela.ws/book/7439)：实际打开的官方书页；支持作者全名与卒年478 AH、 صلاح بن محمد عويضة 校订、1418／1997年版本、两卷及“法源学”书目归类。
- [Shamela《البرهان》第一卷开篇](https://shamela.ws/book/7439/1)：实际打开的原文页；支持序言关于学科目的、定义、证据，以及法源学取材于教义学、阿拉伯语和法学的说明。
- [Shamela《البرهان》第二卷“类比之书”开篇](https://shamela.ws/book/7439/302)：实际打开的原文页；支持朱韦尼关于 القياس、无穷新事例、定义类比、呈现各派意见、辨明有效与错误反对意见并提出择定立场的论证次序。

### المستصفى من علم الأصول · al-Mustaṣfā（`usul-mustasfa`）
- [Waqfeya《المستصفى من علم الأصول》官方书目页](https://waqfeya.net/books/%D8%A7%D9%84%D9%85%D8%B3%D8%AA%D8%B5%D9%81%D9%89-%D9%85%D9%86-%D8%B9%D9%84%D9%85-%D8%A7%D9%84%D8%A3%D8%B5%D9%88%D9%84-%D8%AA-%D8%AD%D8%A7%D9%81%D8%B8-e1fd3e8ad67b469abe9fb22724b472f9)：实际打开的官方书目页，核对了目录所给当前题名及原站阅读入口；作者、卒年和现代版本细节与 Shamela 书页交叉核对。
- [Shamela《كتاب المستصفى》书页](https://shamela.ws/book/5459)：实际打开的官方书页列出作者 أبو حامد محمد بن محمد الغزالي الطوسي、卒年505 AH、编辑者 محمد عبد السلام عبد الشافي、出版社、1413 AH/1993 CE版次、383页，并将其置于法源学分类。
- [Internet Archive《Al Mustasfa Min Ilmul Usool》扫描条目](https://archive.org/details/in.ernet.dli.2015.432464)：实际打开的馆藏条目提供阿拉伯语扫描、页图和OCR入口，并列出出版者、1325出版元数据、440页等版本信息；条目作者字段同时带有注释者信息，不能直接当作无注释定本。
- [AJIS《Ghazali’s Juristic Treatment of the Shari‘ah Rules in al-Mustasfa》](https://www.ajis.org/index.php/ajiss/article/view/2851)：实际打开的学术期刊文章及摘要，将本书的法源学表述为从教法来源取得 ahkam，并明确分析 ahkam、adilla 与有资格推导者三个要素，为方法论和历史定位提供学术交叉核验。

### 《أصول السرخسي》·Uṣūl al-Sarakhsī（萨拉赫西法源学）（`usul-sarakhsi`）
- [Shamela：كتاب أصول السرخسي = تمهيد الفصول في الأصول - ت الأفغاني](https://shamela.ws/book/6301)：实际打开的Shamela书页；支持当前书名与题名异称、作者全名及483 AH卒年、阿富汗尼校订者、出版者、两卷和印刷本页码信息，并提供可逐页阅读的原典文本。
- [Internet Archive：《أصول السرخسي》馆藏条目](https://archive.org/details/20200830_20200830_1301)：实际打开的馆藏条目；支持题名、作者署名、阿拉伯语扫描/OCR、PDF与全文文件等馆藏元数据，可用来与Shamela版本交叉检查，但不能替代校勘本。
- [Oxford Reference：Al-Sarakhsi, Muhammad ibn Ahmad](https://www.oxfordreference.com/display/10.1093/oi/authority.20110803095405644)：实际打开的Oxford Reference传记条目；支持萨拉赫西约400–483 AH、约1009–1090 CE及出生于Sarakhs等基本年代与身份信息。
- [《أصول السرخسي》方法与结构二手导读](https://islam.wiki/books/usul-as-sarakhsi/2)：实际打开的二手导读；用于辅助定位法学家路径、类比、法学偏好与哈乃斐内部传承等学习主题，仅作研究线索，不替代原典、版本说明或学术校核。

### المحصول في علم أصول الفقه · al-Maḥṣūl（`usul-mahsul`）
- [Internet Archive：《المحصول في علم أصول الفقه》条目](https://archive.org/details/mhsol_elm_osoul)：实际打开的馆藏条目直接列出题名、作者全名、塔哈·贾比尔·费亚德·阿勒瓦尼校订、六卷及扫描/OCR文件，支持作者和版本入口核对；其 OCR 仅适合检索，不能单独作为校勘引文。
- [Shamela（المكتبة الشاملة）《المحصول》检索入口](https://shamela.ws/index.php/search?q=%D8%A7%D9%84%D9%85%D8%AD%D8%B5%D9%88%D9%84%20%D9%81%D9%8A%20%D8%B9%D9%84%D9%85%20%D8%A3%D8%B5%D9%88%D9%84%20%D8%A7%D9%84%D9%81%D9%82%D9%87)：这是随附目录指定的官方阅读链接；实际打开确认其为 Shamela 的书名、作者和法源学分类检索系统。结果页由动态界面加载，未据此臆造稳定卷页或版本细节。
- [斯坦福哲学百科：Fakhr al-Din al-Razi](https://plato.stanford.edu/entries/al-din-al-razi/)：学术机构资料支持拉齐的生卒（1149–1210 CE）、拉伊出身、阿什尔里神学与沙斐仪法学训练、求学旅行及后古典思想背景；这些资料用于历史定位，不替代《المحصول》原文。
- [埃及达尔伊夫塔：Islamic Legal Theory (Usul al-fiqh)](https://www.dar-alifta.org/en/article/details/110/islamic-legal-theory-usul-al-fiqh)：官方法学机构页面说明法源学围绕一般证据、推导方法和推导者资格展开，并转述《المحصول》中的法学定义，支持本导读的学习问题框架；不据此断定本书所有具体异说。

### 《الموافقات》· al-Muwāfaqāt（`usul-muwafaqat`）
- [Shamela《الموافقات》官方书页](https://shamela.ws/book/11435)：实际打开并核对到书名、作者全名、卒年790 AH、校订者、出版社、1417 AH/1997 CE首版信息、7卷及法源学分类；这是目录卡所指向的直接书页。
- [Shamela沙提比作者页](https://shamela.ws/author/68)：实际打开并核对作者的格拉纳达身份、马立克派学术归属、卒年790 AH及其作品列表；同时显示不同书目条目的版本差异。
- [Internet Archive《كتاب الموافقات》扫描条目](https://archive.org/details/Al_Mowafa9at)：实际打开的公开扫描条目，提供作者、2017年版校订信息、7卷条目标识及五部分编排说明；OCR和上传版本仅作导航，不能替代校勘。
- [国际伊斯兰思想研究院关于《الموافقات》的阅读导论](https://iiit.org/ar/%D9%82%D8%B1%D8%A7%D8%A1%D8%A9-%D9%88%D9%85%D8%AF%D8%A7%D8%B1%D8%B3%D8%A9-%D9%83%D8%AA%D8%A7%D8%A8-%D8%A7%D9%84%D9%85%D9%88%D8%A7%D9%81%D9%82%D8%A7%D8%AA-%D9%81%D9%8A-%D8%A3%D8%B5%D9%88%D9%84/)：实际打开的学术机构页面，说明全书的逻辑次序、13项前提、规范—目的—证据— الاجتهاد/التقليد 的关系，并概括其涉及的确定性/或然性、理性/传承等问题；作为二手导读使用，不冒充原典。


## 2026-09-27 大规模阿拉伯原文来源核验

本轮为“至少七八千部、每个系列数百部”的扩展目标核验六类来源。结论是：可以规模化接入**阿拉伯语书目元数据、版本信息、原文官方链接和明确许可/公版的按需正文**；不能因为网站可浏览或可下载，就整库复制、OCR 镜像或重新托管受保护正文。

### Shamela / المكتبة الشاملة

- 官方首页当前显示约 **700 万页、8,000 本书、3,000 位作者**：<https://shamela.ws/>。
- 官方提供只读 MCP：<https://shamela.ws/mcp>；支持页：<https://shamela.ws/page/support>；下载页提供官方客户端和数据库包：<https://shamela.ws/page/download>。
- 官方条款：<https://shamela.ws/page/terms>；robots：<https://shamela.ws/robots.txt>。
- 结论：阿拉伯原文和逐页阅读真实存在，但未发现整库开放许可。燃灯只保存书名、作者、版本、页数、书/页 ID、官方链接和权利状态；正文通过官方页面/MCP 按需检索，不建立整库镜像、不用于训练。

### OpenITI / KITAB

- 官方项目说明：<https://kitab-project.org/corpus/about>；使用方式：<https://kitab-project.org/corpus/use>；版本发布：<https://kitab-project.org/corpus/releases>。
- 官方 About 当前称 KITAB 超过 **10,200 个文本文件**，提供阿拉伯语机器可读文本和 YAML 元数据；稳定版本通过 Zenodo 发布，仓库/语料版本必须固定 commit、tag 或 DOI。
- OpenITI 文档：<http://openiti.org/documentation/>；项目页：<https://openiti.org/projects/OpenITI%20Corpus.html>。
- 许可证边界：OpenITI 文档声明语料使用 CC BY-NC-SA 4.0，但 KITAB 同时说明来源混合，包含 Shamela、Shia Online 和现代印刷版再现；不能把所有底层版本自动标成公版。燃灯优先导入 YAML/书目字段和官方版本链接，正文只对权利字段明确且可核验的条目按需读取。

### Waqfeya / المكتبة الوقفية

- 官方首页/分类：<https://waqfeya.net/>、<https://waqfeya.net/categories>；robots：<https://waqfeya.net/robots.txt>。
- 核验时首页显示约 **6,450 本**，以扫描 PDF/阅读入口为主；未发现公开稳定 API、整库导出协议或统一开放许可证。
- 官方保留权利并会响应出版社/作者下架请求：<https://waqfeya.net/books/%D8%A5%D9%8A%D8%B6%D8%A7%D8%AD-%D8%AD%D9%88%D9%84-%D8%B7%D9%84%D8%A8%D8%A7%D8%AA-%D8%A7%D9%84%D9%83%D8%AA%D8%A8-cd6ac9c862e54273a61133a6ea439d1f>。
- 结论：只采集逐书元数据和官方详情/PDF入口；不批量下载、OCR 或镜像扫描书。

### Internet Archive

- 官方元数据 API：<https://archive.org/services/docs/api/metadata.html>；机器人说明：<https://archive.org/developers/bots.html>；权利说明：<https://help.archive.org/help/rights/>。
- `collection:booksbylanguage_arabic` 的一次核验查询返回约 **569,047 个 item 匹配**，但这不是纯伊斯兰书籍数量，也不是稳定书目册数。
- 书目、语言、rights、licenseurl、文件格式可以逐条保存；rights 缺失时不能假定公版。正文仅对逐条明确 CC/开放许可或已核验公版的项目按需处理，默认保留官方 details URL。

### Maktabah Salafiyyah

- 官方 Books 分类：<https://maktabahsalafiyyah.org/category/books/>；WordPress API：<https://maktabahsalafiyyah.org/wp-json/>；版权政策：<https://maktabahsalafiyyah.org/rights-of-publication/>。
- 页面公开的主要是文章/书目和少量阿拉伯引文，未证明存在规模已知的完整阿拉伯原文库；官方版权政策不是整库开放许可。
- 结论：低频同步标题、作者、分类、摘要和官方链接；如需正文或 PDF，必须逐项获得授权或核验权利。

### Arabic Collections Online / ACO

- 官方项目：<https://aco.dlib.nyu.edu/>；About：<https://aco.dlib.nyu.edu/about>；元数据仓库：<https://github.com/NYULibraries/aco-karms>。
- 官方当前显示约 **17,698 volumes、10,474 subjects**，提供阿拉伯原书扫描和官方 PDF/在线阅读入口；MARCXML/CSV/handles 元数据可机器读取。
- ACO 项目方声明所选内容为公版，但仍需逐项核验；AUB 合作页面存在 CC BY-NC-ND 4.0 标识，因此不能把仓库元数据许可扩展到全部扫描正文。
- 结论：批量导入 MARC/CSV 书目与永久链接；正文以官方页面/PDF 外链为主，对明确公版条目才按需处理。

### 本轮产品决策

1. 目标规模按“书目索引”实现：首期导入 OpenITI/KITAB 机器可读元数据和 ACO MARC/CSV 元数据，合计目标 **8,000–10,000+ 条可追溯阿拉伯书目**，按学科分组。
2. 每条记录必须有原文题名、作者、学科、版本/来源、官方 URL、来源 ID、抓取时间、rights_status 和 text_mode；没有这些字段的记录不进入正式目录。
3. 受保护来源只显示“官方原文入口”，不复制正文；明确 CC BY-NC-SA 或公版的条目显示许可证，并在按需读取时保留署名、版本和来源。
4. 导入器使用低并发、缓存、指数退避、断点状态和明确 User-Agent；遇到 403/429、robots、下架或版权投诉立即停止相关来源。
5. “每个系列几百部”改为按来源实际可核验数量展示，不虚构配额；Waqfeya/Shamela/ACO 的规模数字会标注为来源页面快照而非永久保证。
