#!/usr/bin/env python3
"""Bounded live regression for Hanafi/Shafi'i comparison of الاستحسان."""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import server  # noqa: E402

PROMPT = (
    "请做一个详细但谨慎的横向比较：哈乃斐学派与沙斐仪学派如何理解法源学概念"
    " الاستحسان（istihsan）。请分成：定义、与 القياس 的关系、证据基础、学派内部的"
    "常见表述、沙斐仪对无约束择优的批评、两派差异与相似点、应回到哪些原典核验。"
    "必须区分原典明确表述、后世学派归纳、现代研究和模型归纳；具体卷页、圣训编号、"
    "经文编号若未核验就明确写‘待核验’。不要把两派观点绝对化，不要给现实个案法特瓦，"
    "不要只重复问题。请用中文为主，保留关键阿拉伯术语。"
)

def main() -> int:
    messages = [
        {"role": "system", "content": server._AI_GUARD + server.SYSTEM},
        {"role": "user", "content": PROMPT},
    ]
    started = time.perf_counter()
    answer = server.call_deepseek(messages, fast=True)
    elapsed = round((time.perf_counter() - started) * 1000)
    usage = dict(server.LAST_USAGE or {})
    text = str(answer or "").strip()
    checks = {
        "hanafi": any(x in text for x in ("哈乃斐", "الحنفية", "Hanafi")),
        "shafii": any(x in text for x in ("沙斐仪", "الشافعية", "Shafi")),
        "definition_and_qiyas": "استحسان" in text and ("类比" in text or "قياس" in text),
        "evidence_basis": any(x in text for x in ("证据", "原典", "النص", "核验")),
        "historical_caveat": any(x in text for x in ("待核验", "不能绝对化", "学习性", "内部差异", "不等于")),
        "not_echo_only": len(text) >= 500 and text.replace(" ", "") != PROMPT.replace(" ", ""),
    }
    result = {
        "ok": bool(text) and all(checks.values()),
        "elapsed_ms": elapsed,
        "requested_max_tokens": server._chat_token_budget(messages, fast=True),
        "usage": {k: usage.get(k) for k in ("prompt_tokens", "completion_tokens", "total_tokens", "prompt_cache_hit_tokens", "prompt_cache_miss_tokens") if k in usage},
        "answer_chars": len(text),
        "checks": checks,
        "answer_excerpt": text[:5000],
        "note": "一次受控现场样本；不代表长期 SLA、原典校勘结果或现实法特瓦。",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
