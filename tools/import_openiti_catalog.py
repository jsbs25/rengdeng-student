#!/usr/bin/env python3
"""Import OpenITI/KITAB Arabic metadata into the Nour catalog.

This importer downloads only the official release TSV metadata. It does not
fetch, mirror, OCR, or redistribute any book body text.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_RELEASE = "v2025.1.9"
DEFAULT_URL = f"https://raw.githubusercontent.com/OpenITI/RELEASE/{DEFAULT_RELEASE}/metadata/OpenITI_metadata_2025-1-9.tsv"

DISCIPLINES = [
    ("法源学", "أصول الفقه", re.compile(r"أصول|usul|uṣūl", re.I)),
    ("古兰经学与经注", "علوم القرآن والتفسير", re.compile(r"قرآن|quran|tafsir|تفسير|علوم القرآن", re.I)),
    ("圣训学", "علوم الحديث", re.compile(r"حديث|hadith|ḥadīth", re.I)),
    ("伊斯兰法学", "الفقه", re.compile(r"فقه|fiqh|figh|furū|furu", re.I)),
    ("阿拉伯语言与修辞", "اللغة والبلاغة", re.compile(r"بلاغ|balag|نحو|لغ|لغة|adab|أدب|شعر|دواوين", re.I)),
    ("信仰与教义", "العقيدة والكلام", re.compile(r"عقيدة|عقائد|aqida|kalam|كلام", re.I)),
    ("历史与传记", "التاريخ والسير", re.compile(r"تاريخ|سيرة|طبقات|تراجم|history|biograph", re.I)),
]


def download(url: str, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "NourStudent/1.0 metadata-only; https://xn--dqry4os3s3gb.com/",
            "Accept": "text/tab-separated-values,text/plain;q=0.9,*/*;q=0.5",
        },
    )
    with urllib.request.urlopen(request, timeout=90) as response, out.open("wb") as handle:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)


def clean(value: str | None) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def classify(row: dict[str, str]) -> list[tuple[str, str]]:
    haystack = " ".join(clean(row.get(k)) for k in ("tags", "title_ar", "book", "author_ar"))
    found = [(cn, ar) for cn, ar, pattern in DISCIPLINES if pattern.search(haystack)]
    return found or [("其他阿拉伯文献", "مصنفات عربية أخرى")]


def choose_primary(rows: list[dict[str, str]]) -> dict[str, str]:
    def score(row: dict[str, str]) -> tuple[int, int, int, str]:
        return (
            1 if clean(row.get("status")) == "pri" else 0,
            1 if clean(row.get("uncorrected_OCR")).lower() not in {"true", "1"} else 0,
            int(row.get("char_length") or 0),
            clean(row.get("version_uri")),
        )

    return max(rows, key=score)


def official_urls(row: dict[str, str], release: str) -> tuple[str, str]:
    path = clean(row.get("local_path"))
    blob = f"https://github.com/OpenITI/RELEASE/blob/{release}/{path}"
    raw = f"https://raw.githubusercontent.com/OpenITI/RELEASE/{release}/{path}"
    return blob, raw


def make_book(book_key: str, rows: list[dict[str, str]], release: str) -> dict:
    primary = choose_primary(rows)
    title = clean(primary.get("title_ar")) or clean(primary.get("book")) or book_key
    author = clean(primary.get("author_ar")) or clean(primary.get("author_from_uri")) or "未标明"
    disciplines = classify(primary)
    blob_url, raw_url = official_urls(primary, release)
    stable_id = "openiti-" + hashlib.sha1(book_key.encode("utf-8")).hexdigest()[:16]
    versions = sorted({clean(r.get("version_uri")) for r in rows if clean(r.get("version_uri"))})
    tags = clean(primary.get("tags"))
    return {
        "id": stable_id,
        "t": title,
        "a": author,
        "y": clean(primary.get("date")) or "古典/现代版本见来源",
        "c": disciplines[0][0],
        "c_ar": disciplines[0][1],
        "discipline": "openiti",
        "disciplines": [cn for cn, _ in disciplines],
        "u": blob_url,
        "text_url": raw_url,
        "source": f"OpenITI/KITAB · {release} 固定版本",
        "access": "官方机器可读阿拉伯原文入口；本站不镜像正文",
        "rights": "OpenITI 语料标注 CC BY-NC-SA 4.0；底层版本与来源权利仍需逐条核验",
        "license": "CC BY-NC-SA 4.0（语料层，按来源与版本核验）",
        "text_mode": "arabic_original_link",
        "level": "研究",
        "intro": "来自 OpenITI/KITAB 固定 release 的阿拉伯语书目。书卡提供官方版本原文链接、作者、标签和版本数量；重要引文请回到原文和扫描版本核对。",
        "ai_profile": "只根据本条公开书目、版本、标签和用户当前打开的官方原文页做学习辅助；不得虚构作者观点、页码、圣训编号或学派结论。先区分原文、版本、后世解释和模型归纳；法学内容可选择综合对比、哈乃斐、马立克、沙斐仪或汉百里视角，但不能代替法特瓦。",
        "openiti": {
            "book": book_key,
            "primary_version_uri": clean(primary.get("version_uri")),
            "primary_id": clean(primary.get("id")),
            "version_count": len(versions),
            "versions": versions[:12],
            "tags": tags[:1800],
            "ed_info": clean(primary.get("ed_info")),
            "status": clean(primary.get("status")),
            "uncorrected_ocr": clean(primary.get("uncorrected_OCR")),
            "release": release,
            "metadata_source": f"https://github.com/OpenITI/RELEASE/tree/{release}/metadata",
        },
    }


def import_catalog(catalog_path: Path, tsv_path: Path, release: str, source_url: str) -> dict:
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    existing = list(data.get("books") or [])
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    rows = 0
    for row in csv.DictReader(tsv_path.open(encoding="utf-8-sig", newline=""), delimiter="\t"):
        rows += 1
        if clean(row.get("language")) != "ara":
            continue
        book_key = clean(row.get("book"))
        if book_key:
            groups[book_key].append(row)
    imported = [make_book(key, rs, release) for key, rs in sorted(groups.items())]
    existing_ids = {str(b.get("id")) for b in existing}
    merged = existing + [b for b in imported if b["id"] not in existing_ids]

    meta = dict(data.get("meta") or {})
    meta["catalog_mode"] = "作品级书目 + 版本入口；正文按官方链接/权利按需读取"
    meta["openiti_release"] = release
    meta["openiti_metadata_url"] = source_url
    meta["openiti_metadata_fetched_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    meta["openiti_rows_scanned"] = rows
    meta["openiti_arabic_works"] = len(imported)
    meta["openiti_notice"] = "OpenITI/KITAB 元数据与版本入口已导入；不代表所有底层版本均为公版，正文权利按条目核验。"
    meta["disciplines"] = list(meta.get("disciplines") or [])
    known = {str(x.get("name")) for x in meta["disciplines"] if isinstance(x, dict)}
    series_counts = defaultdict(int)
    for book in imported:
        for label in book.get("disciplines", []):
            series_counts[label] += 1
            if label not in known:
                ar = next((ar for cn, ar, _ in DISCIPLINES if cn == label), "مصنفات عربية أخرى")
                meta["disciplines"].append({"id": "openiti-" + hashlib.sha1(label.encode()).hexdigest()[:8], "name": label, "ar": ar, "icon": "📚", "desc": "OpenITI/KITAB 阿拉伯语作品索引；按版本和来源进入原文。", "level": "研究"})
                known.add(label)
    meta["openiti_series_counts"] = dict(sorted(series_counts.items()))
    meta["total"] = len(merged)
    data["schema_version"] = max(int(data.get("schema_version") or 1), 3)
    data["meta"] = meta
    data["books"] = merged
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", default="data/islamic_catalog.json")
    parser.add_argument("--metadata", default="data/cache/source_catalog/OpenITI_metadata_2025-1-9.tsv")
    parser.add_argument("--release", default=DEFAULT_RELEASE)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--refresh", action="store_true", help="download the official metadata TSV")
    args = parser.parse_args()
    catalog = Path(args.catalog)
    metadata = Path(args.metadata)
    if args.refresh or not metadata.exists():
        print(f"Downloading metadata only: {args.url}", file=sys.stderr)
        download(args.url, metadata)
    result = import_catalog(catalog, metadata, args.release, args.url)
    catalog.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "catalog": str(catalog),
        "total_books": len(result.get("books") or []),
        "openiti_works": result.get("meta", {}).get("openiti_arabic_works"),
        "series_counts": result.get("meta", {}).get("openiti_series_counts"),
        "metadata_only": True,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
