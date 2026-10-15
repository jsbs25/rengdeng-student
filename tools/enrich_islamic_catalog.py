#!/usr/bin/env python3
"""Enrich the Islamic catalogue with conservative topic and school facets.

Metadata-only: this script never downloads book bodies. School facets are
inferred from title/author/source metadata and are explicitly marked as such.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

TOPICS = [
    ("quran", "古兰经学与经注", "علوم القرآن والتفسير", re.compile(r"قرآن|quran|tafsir|تفسير|علوم القرآن|مصحف|آيات", re.I)),
    ("hadith", "圣训学", "علوم الحديث", re.compile(r"حديث|hadith|ḥadīth|سنة|سنن|مسند|موطأ|صحاح", re.I)),
    ("fiqh", "法学", "الفقه", re.compile(r"فقه|fiqh|figh|فروع|فتاوى|أحكام|حلال|حرام", re.I)),
    ("usul", "法源学", "أصول الفقه", re.compile(r"أصول الفقه|أصول|usul|uṣūl|قياس|اجتهاد|استصحاب", re.I)),
    ("aqida", "信仰与教义", "العقيدة والكلام", re.compile(r"عقيدة|عقائد|aqida|كلام|توحيد|الإيمان", re.I)),
    ("language", "阿拉伯语言", "اللغة العربية", re.compile(r"نحو|صرف|لغة|لغات|نقد|معجم|لسان|grammar|lingu|لغة العربية", re.I)),
    ("balagha", "修辞与文体", "البلاغة والأسلوب", re.compile(r"بلاغ|بيان|بديع|معاني|بلاغة|balag|فصاحة", re.I)),
    ("literature", "文学与诗歌", "الأدب والشعر", re.compile(r"أدب|شعر|ديوان|قصائد|رواية|رسائل|adab|poetry|literature", re.I)),
    ("history", "历史与文明", "التاريخ والحضارة", re.compile(r"تاريخ|تراجم|طبقات|حضارة|history|chron|تاريخ", re.I)),
    ("biography", "传记与人物", "السير والتراجم", re.compile(r"سيرة|ترجمة|تراجم|رجال|أعلام|biograph", re.I)),
    ("ethics", "伦理与灵修", "الأخلاق والتزكية", re.compile(r"أخلاق|تزكية|زهد|رقائق|آداب|suf|روحاني", re.I)),
    ("logic", "逻辑与哲学", "المنطق والفلسفة", re.compile(r"فلسفة|منطق|حكمة|فلاسفة|logic|philos", re.I)),
    ("science", "医学与自然科学", "الطب والعلوم", re.compile(r"طب|صيدلة|رياضيات|فلك|هندسة|علوم|medicine|science", re.I)),
    ("geography", "地理与旅行", "الجغرافيا والرحلات", re.compile(r"جغرافيا|رحلة|بلدان|أمصار|geograph|travel", re.I)),
]

SCHOOLS = [
    ("hanafi", "哈乃斐学派", "الحنفية", ("حنفي", "حنفية", "أبو حنيفة", "الكاساني", "السرخسي", "المرغيناني", "القدوري", "الزيلعي", "ابن عابدين", "ابن الهمام", "ملا خسرو", "النسفي", "Hanafi", "Abu Hanifa", "al-Kasani", "al-Sarakhsi", "al-Marghinani", "al-Quduri")),
    ("maliki", "马立克学派", "المالكية", ("مالكي", "مالكية", "مالك بن أنس", "سحنون", "ابن رشد", "القرافي", "خليل", "الدردير", "النفراوي", "العدوي", "Maliki", "Malik ibn Anas", "Sahnun", "Ibn Rushd", "al-Qarafi")),
    ("shafii", "沙斐仪学派", "الشافعية", ("شافعي", "شافعية", "الشافعي", "النووي", "الرافعي", "الغزالي", "الجويني", "الماوردي", "ابن حجر الهيتمي", "الرملي", "Shafii", "Shafi'i", "al-Nawawi", "al-Ghazali", "al-Juwayni")),
    ("hanbali", "汉百里学派", "الحنابلة", ("حنبلي", "حنابلة", "أحمد بن حنبل", "ابن قدامة", "ابن تيمية", "ابن القيم", "البهوتي", "المرداوي", "الرحيباني", "Hanbali", "Ahmad ibn Hanbal", "Ibn Qudama", "Ibn Taymiyya", "Ibn al-Qayyim")),
    ("zahiri", "扎希里学派", "الظاهرية", ("ظاهري", "ابن حزم", "الظاهرية", "Zahiri", "Ibn Hazm")),
    ("jafari", "贾法里学派", "الجعفرية", ("جعفري", "إمامي", "الشيعة", "الصدر", "الخميني", "Ja'fari", "Jafari", "Imami")),
    ("zaydi", "宰德派", "الزيدية", ("زيدي", "زيدية", "Zaydi", "Zaydiyya")),
    ("ibadi", "伊巴德派", "الإباضية", ("إباضي", "إباضية", "Ibadi", "Ibadhi")),
]


def haystack(book: dict) -> str:
    values = [book.get(k) for k in ("t", "a", "c", "c_ar", "discipline", "source", "intro")]
    oi = book.get("openiti")
    if isinstance(oi, dict):
        values.extend([oi.get("book"), oi.get("tags"), oi.get("ed_info")])
    return " ".join(str(v or "") for v in values)


def add_topic_tags(book: dict) -> list[str]:
    text = haystack(book)
    tags = []
    existing = " ".join(str(x) for x in (book.get("disciplines") or []))
    for tag_id, name, _ar, pattern in TOPICS:
        if pattern.search(text) or pattern.search(existing):
            tags.append(tag_id)
    # Preserve the catalogue's existing primary discipline even when its
    # Arabic title is sparse, and make source/format facets explicit.
    discipline = str(book.get("c") or "").strip()
    if discipline and not tags:
        tags.append("other")
    if str(book.get("text_mode") or "") == "arabic_original_link":
        tags.append("arabic-original")
    if isinstance(book.get("openiti"), dict):
        tags.append("openiti")
        if int(book.get("openiti", {}).get("version_count") or 0) > 1:
            tags.append("multi-version")
    return list(dict.fromkeys(tags or ["other"]))


def school_tags(book: dict) -> tuple[list[str], dict[str, list[str]]]:
    text = haystack(book)
    legal_context = bool(re.search(r"فقه|أصول|فتوى|أحكام|fiqh|usul|madhhab|مذهب", text, re.I))
    out, evidence = [], {}
    for school_id, _name, _ar, terms in SCHOOLS:
        hits = [term for term in terms if term and term.lower() in text.lower()]
        if hits and (legal_context or school_id in {"jafari", "zaydi", "ibadi"}):
            out.append(school_id)
            evidence[school_id] = hits[:5]
    return list(dict.fromkeys(out)), evidence


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", default="data/islamic_catalog.json")
    ap.add_argument("--index", default="data/islamic_catalog_index.json")
    args = ap.parse_args()
    path = Path(args.catalog)
    data = json.loads(path.read_text(encoding="utf-8"))
    tag_labels = {"other": {"id": "other", "name": "其他阿拉伯文献", "ar": "مصنفات عربية أخرى"}, "arabic-original": {"id": "arabic-original", "name": "阿拉伯原文", "ar": "النص العربي"}, "openiti": {"id": "openiti", "name": "OpenITI/KITAB", "ar": "OpenITI/KITAB"}, "multi-version": {"id": "multi-version", "name": "多版本作品", "ar": "متعدد النسخ"}}
    for tag_id, name, ar, _pattern in TOPICS:
        tag_labels[tag_id] = {"id": tag_id, "name": name, "ar": ar}
    school_labels = {sid: {"id": sid, "name": name, "ar": ar} for sid, name, ar, _terms in SCHOOLS}
    tag_counts, school_counts = Counter(), Counter()
    tag_books, school_books = defaultdict(list), defaultdict(list)
    for book in data.get("books") or []:
        tags = add_topic_tags(book)
        schools, evidence = school_tags(book)
        book["catalog_tags"] = tags
        book["catalog_tag_labels"] = [tag_labels[k]["name"] for k in tags if k in tag_labels]
        book["fiqh_schools"] = schools
        book["fiqh_school_labels"] = [school_labels[k]["name"] for k in schools if k in school_labels]
        book["fiqh_school_evidence"] = evidence
        book["fiqh_school_inference"] = "从书名、作者和公开元数据推断；不是作者自证或教法裁决" if schools else "未从公开元数据确认学派归属"
        for tag in tags:
            tag_counts[tag] += 1; tag_books[tag].append(book.get("id"))
        for school in schools:
            school_counts[school] += 1; school_books[school].append(book.get("id"))
    meta = dict(data.get("meta") or {})
    meta["catalog_tags_version"] = "2026-09-27.1"
    meta["catalog_tags_notice"] = "专题和法学派标签仅依据书名、作者、OpenITI 标签等公开元数据推断；请回到版本正文和可靠研究核验。"
    meta["tag_facets"] = [{**tag_labels[k], "count": tag_counts[k]} for k in sorted(tag_counts, key=lambda k: (-tag_counts[k], k))]
    meta["fiqh_school_facets"] = [{**school_labels[k], "count": school_counts[k]} for k in sorted(school_counts, key=lambda k: (-school_counts[k], k))]
    meta["fiqh_school_index_notice"] = "法学派索引优先标记公开元数据中出现的学派名称、代表作者或作品线索；多派比较作品可有多个标签。"
    data["schema_version"] = max(int(data.get("schema_version") or 1), 4)
    data["meta"] = meta
    data["books"] = data.get("books") or []
    index = {"schema_version": 1, "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(), "total_books": len(data["books"]), "tags": {k: {"count": tag_counts[k], "book_ids": tag_books[k]} for k in sorted(tag_books)}, "fiqh_schools": {k: {"count": school_counts[k], "book_ids": school_books[k]} for k in sorted(school_books)}}
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    Path(args.index).write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"total": len(data["books"]), "tag_facets": len(tag_counts), "school_facets": dict(school_counts), "index": args.index}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
