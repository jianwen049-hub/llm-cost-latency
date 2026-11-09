from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelPrice:
    name: str
    in_per_1k: float
    out_per_1k: float


PRICEBOOK = {
    "cheap": ModelPrice("cheap", 0.0001, 0.0002),
    "strong": ModelPrice("strong", 0.0010, 0.0020),
}


def cost_usd(tier: str, tokens_in: int, tokens_out: int) -> float:
    p = PRICEBOOK[tier]
    return (tokens_in / 1000.0) * p.in_per_1k + (tokens_out / 1000.0) * p.out_per_1k


def printable_rows(typical_in: int = 2000, typical_out: int = 500) -> list[dict]:
    rows = []
    for tier, p in PRICEBOOK.items():
        rows.append(
            {
                "tier": tier,
                "in_per_1k": p.in_per_1k,
                "out_per_1k": p.out_per_1k,
                f"cost_per_{typical_in}in_{typical_out}out": round(
                    cost_usd(tier, typical_in, typical_out), 6
                ),
            }
        )
    return rows
