#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cost_lab.accounting import estimate_tokens, UsageLedger
from cost_lab.cache import make_cache_key, InMemoryPromptCache
from cost_lab.compress import compress_messages
from cost_lab.router import route
from cost_lab.cli import cmd_demo, cmd_table


def main() -> int:
    assert estimate_tokens("hello world") >= 2
    assert estimate_tokens("退款时效说明") >= 4
    k1 = make_cache_key("sys", ["b", "a"], "请帮我退款一下")
    k2 = make_cache_key("sys", ["a", "b"], "退款")
    assert k1 == k2
    c = InMemoryPromptCache()
    c.set(k1, "x")
    assert c.get(k2) == "x"
    assert route("1+1等于几").tier == "cheap"
    assert route("请一步步分析为什么退款更慢").tier == "strong"
    msgs = [{"role": "system", "content": "必须守法"}] + [
        {"role": "user", "content": f"消息{i} 数字{i}"} for i in range(12)
    ]
    r = compress_messages(msgs, max_tokens=80, recent=3)
    assert r.tokens_after <= r.tokens_before
    led = UsageLedger()
    led.add("t", "cheap", 100, 10)
    assert led.total_cost() > 0
    assert cmd_table() == 0
    assert cmd_demo() == 0
    print("smoke_check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
