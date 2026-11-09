from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from cost_lab.pricing import cost_usd

_CJK = re.compile(r"[\u4e00-\u9fff]")


def estimate_tokens(text: str) -> int:
    """Heuristic token estimate for CN/EN mixed text (offline, no tiktoken)."""
    if not text:
        return 0
    cjk = len(_CJK.findall(text))
    rest = _CJK.sub(" ", text)
    words = [w for w in re.split(r"\s+", rest.strip()) if w]
    # CJK ~1 token/char; latin words ~1.3 tokens
    return max(1, cjk + int(round(len(words) * 1.3)))


@dataclass
class Usage:
    feature: str
    model_tier: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class UsageLedger:
    items: list[Usage] = field(default_factory=list)

    def add(self, feature: str, model_tier: str, tokens_in: int, tokens_out: int, **meta: Any) -> Usage:
        u = Usage(
            feature=feature,
            model_tier=model_tier,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_usd=cost_usd(model_tier, tokens_in, tokens_out),
            meta=meta,
        )
        self.items.append(u)
        return u

    def total_cost(self) -> float:
        return round(sum(i.cost_usd for i in self.items), 6)

    def summary(self) -> dict[str, Any]:
        return {
            "n": len(self.items),
            "tokens_in": sum(i.tokens_in for i in self.items),
            "tokens_out": sum(i.tokens_out for i in self.items),
            "cost_usd": self.total_cost(),
            "by_feature": _by_feature(self.items),
        }


def _by_feature(items: list[Usage]) -> dict[str, float]:
    out: dict[str, float] = {}
    for i in items:
        out[i.feature] = round(out.get(i.feature, 0.0) + i.cost_usd, 6)
    return out
