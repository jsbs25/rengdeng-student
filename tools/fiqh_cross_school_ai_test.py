#!/usr/bin/env python3
"""One bounded live regression for the complex الاستحسان answer path.
It calls the configured DeepSeek provider directly (not /api/chat/message), so
it does not mutate user quota, sessions, or site data. It never prints secrets.
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import server  # noqa: E402

PROMPT = (
    "请用中文解释法源学概念 الاستحسان（istihsan）。要求一次性完整回答："
    "给出术语定义与它和 القياس 的关系；区分哈乃斐、马立克、沙斐仪、汉百里四种传统"
    "在学习性比较中的常见视角；把原典明确表述、学派传承、现代研究和模型归纳分开；"
    "说明证据应回到哪些类型的原典，并把未核验的经文、圣训编号、页码标为待核验。"
    "不要给现实个案法特瓦，不要只重复问题。"
)

def main() -> int:
    messages = [
        {"role": "system", "content": server._AI_GUARD + server.SYSTEM},
        {"role": "user", "content": PROMPT},
    ]
    expected_budget = server._chat_token_budget(messages, fast=True)
    started = time.perf_counter()
    answer = server.call_deepseek(messages, fast=True)
    elapsed = round((time.perf_counter() - started) * 1000)
    usage = dict(server.LAST_USAGE or {})
    text = str(answer or "").strip()
    lower = text.lower()
    required_groups = {
        "definition_or_relation": ("استحسان" in text and ("类比" in text or "قياس" in text)),
        "school_comparison": any(x in text for x in ("哈乃斐", "马立克", "沙斐仪", "汉百里", "الحنفية", "المالكية", "الشافعية", "الحنابلة")),
        "evidence_boundary": any(x in text for x in ("核验", "原典", "证据", "待核验", "التحقق")),
        "not_echo_only": len(text) >= 360 and text.replace(" ", "") != PROMPT.replace(" ", ""),
    }
    result = {
        "ok": bool(text) and all(required_groups.values()),
        "elapsed_ms": elapsed,
        "requested_max_tokens": expected_budget,
        "usage": {k: usage.get(k) for k in ("prompt_tokens", "completion_tokens", "total_tokens", "prompt_cache_hit_tokens", "prompt_cache_miss_tokens") if k in usage},
        "answer_chars": len(text),
        "checks": required_groups,
        "answer_excerpt": text[:3200],
        "note": "一次受控现场样本，不代表长期 SLA、教法正确性或所有主题质量。",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
