from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RouteDecision:
    tier: str  # cheap | strong
    reasons: list[str]


_STRONG_HINTS = ("为什么", "比较", "一步步", "分析", "对比", "derive", "why", "compare", "step by step")


def route(prompt: str) -> RouteDecision:
    reasons: list[str] = []
    tier = "cheap"
    if len(prompt) > 400:
        tier = "strong"
        reasons.append("long_prompt")
    for h in _STRONG_HINTS:
        if h in prompt.lower() or h in prompt:
            tier = "strong"
            reasons.append(f"hint:{h}")
            break
    if not reasons:
        reasons.append("default_cheap")
    return RouteDecision(tier=tier, reasons=reasons)
