from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from cost_lab.accounting import estimate_tokens

_KEEP = re.compile(r"(\d+|必须|一定|不要|禁止|[A-Z]{2,}|\$)")


@dataclass
class CompressResult:
    messages: list[dict[str, str]]
    tokens_before: int
    tokens_after: int


def _msg_tokens(messages: list[dict[str, str]]) -> int:
    return sum(estimate_tokens(m.get("content", "")) + 4 for m in messages)


def _extractive_summary(texts: list[str]) -> str:
    kept: list[str] = []
    for t in texts:
        for sent in re.split(r"[。！？.!?\n]", t):
            s = sent.strip()
            if s and _KEEP.search(s):
                kept.append(s)
    if not kept:
        kept = [texts[0][:80]] if texts else []
    return "；".join(kept[:6])


def compress_messages(
    messages: list[dict[str, str]],
    *,
    max_tokens: int = 300,
    recent: int = 4,
) -> CompressResult:
    before = _msg_tokens(messages)
    if before <= max_tokens or len(messages) <= recent + 1:
        return CompressResult(messages=list(messages), tokens_before=before, tokens_after=before)

    pins = [m for m in messages if m.get("role") == "system"]
    non_system = [m for m in messages if m.get("role") != "system"]
    head = non_system[:-recent] if len(non_system) > recent else []
    tail = non_system[-recent:]
    summary = _extractive_summary([m["content"] for m in head]) if head else ""
    middle = [{"role": "system", "content": f"[summary] {summary}"}] if summary else []
    out = pins + middle + tail
    # If still too large, shrink tail contents
    while _msg_tokens(out) > max_tokens and len(out) > len(pins) + 1:
        out.pop(len(pins))  # drop oldest non-pin
    after = _msg_tokens(out)
    return CompressResult(messages=out, tokens_before=before, tokens_after=after)
