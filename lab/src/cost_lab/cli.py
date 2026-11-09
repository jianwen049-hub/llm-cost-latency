from __future__ import annotations

import argparse
import json

from cost_lab.accounting import UsageLedger, estimate_tokens
from cost_lab.cache import InMemoryPromptCache, make_cache_key
from cost_lab.compress import compress_messages
from cost_lab.pricing import printable_rows
from cost_lab.router import route


def cmd_table() -> int:
    rows = printable_rows()
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


def cmd_demo() -> int:
    system = "你是售后助手。必须给出可核对的政策依据。"
    history = [
        {"role": "system", "content": system},
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "您好，请问需要什么帮助"},
        {"role": "user", "content": "我想了解退款"},
        {"role": "assistant", "content": "退款一般 3 到 7 个工作日"},
        {"role": "user", "content": "积分可以折现吗"},
        {"role": "assistant", "content": "积分不可折现，可兑换券"},
        {"role": "user", "content": "请比较一下退货和退款的区别，一步步说明，为什么时效不同"},
    ]
    compressed = compress_messages(history, max_tokens=180, recent=3)
    decision = route(history[-1]["content"])
    cache = InMemoryPromptCache()
    key = make_cache_key(system, ["d1", "d2"], history[-1]["content"])
    key2 = make_cache_key(system, ["d2", "d1"], "麻烦" + history[-1]["content"] + "谢谢")
    assert key == key2
    cache.set(key, {"answer": "cached-demo"})
    hit = cache.get(key2)

    ledger = UsageLedger()
    # pretend call on compressed prompt
    tin = compressed.tokens_after
    tout = 60
    ledger.add("chat", decision.tier, tin, tout, cache="hit" if hit else "miss", route=decision.tier)
    # also show uncompressed cost
    ledger.add("chat_uncompressed_baseline", decision.tier, compressed.tokens_before, tout)

    print(json.dumps(
        {
            "route": decision.__dict__,
            "cache_hits": cache.hits,
            "compress": {
                "tokens_before": compressed.tokens_before,
                "tokens_after": compressed.tokens_after,
            },
            "ledger": ledger.summary(),
            "price_table": printable_rows(),
        },
        ensure_ascii=False,
        indent=2,
    ))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="cost_lab")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("demo")
    sub.add_parser("table")
    args = p.parse_args(argv)
    if args.cmd == "demo":
        return cmd_demo()
    if args.cmd == "table":
        return cmd_table()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
