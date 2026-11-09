from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Any

_POLITE = re.compile(r"(请|谢谢|麻烦|帮我|一下)+")


def normalize_query(q: str) -> str:
    q = q.strip().lower()
    q = _POLITE.sub("", q)
    q = re.sub(r"\s+", " ", q)
    return q.strip()


def make_cache_key(system: str, retrieved_ids: list[str], query: str) -> str:
    basis = "|".join(
        [
            system.strip(),
            ",".join(sorted(retrieved_ids)),
            normalize_query(query),
        ]
    )
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()


@dataclass
class InMemoryPromptCache:
    store: dict[str, Any]

    def __init__(self) -> None:
        self.store = {}
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Any | None:
        if key in self.store:
            self.hits += 1
            return self.store[key]
        self.misses += 1
        return None

    def set(self, key: str, value: Any) -> None:
        self.store[key] = value
