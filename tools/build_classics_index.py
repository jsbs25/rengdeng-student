#!/usr/bin/env python3
"""Build a bounded Arabic classics/academic metadata index from existing pools.

This script never downloads book bodies and never invents authors or dates. It
only merges the project's existing title/id pools with the local Shamela index.
Classification is a title/category heuristic and is explicitly marked as such.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "data" / "library"
OUT = LIB / "classics_index.json"
AR = re.compile(r"[\u0600-\u06ff]")

RULES = [
    ("quran", "古兰经学与经注", ("القرآن", "قرآن", "التفسير", "تفسير", "علوم القرآن", "أسباب النزول")),
    ("hadith", "圣训学", ("الحديث", "حديث", "السنة", "سنن", "مسند", "رجال", "مصطلح الحديث", "شرح صحيح")),
    ("fiqh", "伊斯兰法学", ("الفقه", "فقه", "أحكام", "فتاوى", "الحلال", "الحرام", "القواعد الفقهية")),
    ("usul", "法源学", ("أصول الفقه", "أصول", "الاجتهاد", "القياس", "الإجماع")),
    ("language", "阿拉伯语言与修辞", ("النحو", "نحو", "الصرف", "صرف", "البلاغة", "بلاغة", "الأدب", "معجم", "اللغة", "العروض", "البيان")),
    ("history", "历史与传记", ("تاريخ", "السيرة", "سيرة", "تراجم", "الطبقات", "رحلة", "البلدان", "الأخبار")),
    ("aqida", "信仰与教义", ("العقيدة", "عقيدة", "التوحيد", "الكلام", "الملل والنحل")),
]

PATHS = [
    {"id": "language-to-literature", "title": "语言基础 → 修辞 → 文学阅读", "ar": "من اللغة إلى البلاغة والأدب", "summary": "先看词法与句法，再进入修辞和古典文本；每一步都能回到站内原文。", "collections": ["language", "literature"], "steps": ["词法与句法", "修辞与文体", "文学与诗歌"]},
    {"id": "quran-hadith-context", "title": "古兰经学 → 圣训学 → 语境比较", "ar": "علوم القرآن والحديث", "summary": "把原文、传承和解释层次分开，适合需要核对来源的经典阅读。", "collections": ["quran", "hadith", "language"], "steps": ["古兰经学与经注", "圣训学", "阿拉伯语言与修辞"]},
    {"id": "fiqh-evidence", "title": "法学入门 → 法源学 → 学派比较", "ar": "من الفقه إلى أصوله ومقارنته", "summary": "先读规则文本，再追踪证据和论证方法；AI 只做学习性比较，不替代法特瓦。", "collections": ["fiqh", "usul", "language"], "steps": ["伊斯兰法学", "法源学", "语言与论证"]},
    {"id": "history-and-biography", "title": "历史 → 传记 → 文本背景", "ar": "التاريخ والسير وسياق النص", "summary": "用历史与人物材料补足作品的时代坐标，再回到原文阅读。", "collections": ["history", "literature"], "steps": ["历史与传记", "文学与古典", "回到原文"]},
]


def load_items(name: str) -> list[dict]:
    obj = json.loads((LIB / name).read_text(encoding="utf-8"))
    rows = obj.get("items", []) if isinstance(obj, dict) else obj
    return [x for x in rows if isinstance(x, dict)]


def classify(title: str, shamela_cat: str, source_pool: str) -> tuple[str, str]:
    text = f"{title} {shamela_cat}".lower()
    for key, label, terms in RULES:
        if any(term.lower() in text for term in terms):
            return key, label
    if source_pool in ("grammar", "morph"):
        return "language", "阿拉伯语言与修辞"
    return "literature", "文学与古典"


def main() -> None:
    shamela = json.loads((LIB / "shamela_index.json").read_text(encoding="utf-8")).get("books", {})
    sources = [("lit_pool.json", "literature_pool"), ("grammar_books.json", "grammar"), ("morph_books.json", "morph")]
    by_id: dict[str, dict] = {}
    source_priority = {"literature_pool": 1, "grammar": 2, "morph": 3, "featured_shamela": 4}
    for filename, pool in sources:
        for raw in load_items(filename):
            title = str(raw.get("t") or "").strip()
            bid = str(raw.get("id") or "").strip()
            if not title or not bid or not AR.search(title):
                continue
            info = shamela.get(bid) or {}
            if not info:
                continue
            old = by_id.get(bid)
            if old and source_priority.get(old["source_pool"], 0) >= source_priority[pool]:
                continue
            collection, label = classify(title, str(info.get("cat") or ""), pool)
            by_id[bid] = {
                "id": bid, "title_ar": title, "title": title, "rt": "shamela",
                "collection": collection, "collection_label": label,
                "source_pool": pool, "source": "Shamela local index / existing project pool",
                "source_url": f"https://shamela.ws/book/{bid}", "read_entry": "openReadById",
                "readable": True,
                "classification_basis": "书名与本地目录类别关键词推断；不是作者自证、版本鉴定或教法裁决",
                "rights_notice": "只保存元数据与官方只读入口；正文按来源和权利边界按需读取。",
            }
    # Featured canonical entry: verified in the local Shamela index; body remains on-demand.
    featured = [("8220", "مختصر القدوري · Mukhtaṣar al-Qudūrī")]
    for bid, title in featured:
        info = shamela.get(bid) or {}
        if not info or bid in by_id:
            continue
        collection, label = classify(title, str(info.get("cat") or ""), "featured_shamela")
        by_id[bid] = {
            "id": bid, "title_ar": title, "title": title, "rt": "shamela",
            "collection": collection, "collection_label": label,
            "source_pool": "featured_shamela",
            "source": "Shamela local index / verified featured entry",
            "source_url": f"https://shamela.ws/book/{bid}", "read_entry": "openReadById",
            "readable": True,
            "classification_basis": "精选条目依据本地 Shamela 索引题名与类别；不代表作者自证、版本鉴定或教法裁决",
            "rights_notice": "只保存元数据与官方只读入口；正文按来源和权利边界按需读取。",
        }

    rows = sorted(by_id.values(), key=lambda x: (x["collection_label"], x["title_ar"]))
    counts = Counter(x["collection"] for x in rows)
    out = {
        "meta": {"title": "NOUR 阿拉伯语经典与学术扩展索引", "version": "20261004.2", "generated_from": [x[0] for x in sources] + ["shamela_index.json#featured:8220"], "source_index": "data/library/shamela_index.json", "notice": "这是由现有公开书目池合并而成的元数据发现索引，不代表完整收录、作者考订或版权结论；点开后仍需核对具体版本。", "total": len(rows), "counts": dict(sorted(counts.items()))},
        "reading_paths": PATHS,
        "items": rows,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUT), "total": len(rows), "counts": dict(counts)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
