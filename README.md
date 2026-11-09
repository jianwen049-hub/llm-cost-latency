# llm-cost-latency — Token Accounting, Cache, Routing, Compression

> Open lab for **cost & latency engineering** on LLM calls: exact-ish token accounting, prompt cache keys, cheap/strong routing, and context compression demos — with a printable cost table.

**Author:** 马健文 / Evans Owen ([jianwen049-hub](https://github.com/jianwen049-hub))

| | |
|---|---|
| **Lab** | [`lab/`](./lab/) — accounting + cache + router + compress + cost table |
| **Blog** | [`docs/blog/`](./docs/blog/) |
| **Bio** | [`PROFILE.md`](./PROFILE.md) |

## Reading guide (EN)

```bash
cd lab
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=src
python3 scripts/smoke_check.py
python3 -m cost_lab.cli demo
python3 -m cost_lab.cli table
```

## License

MIT — see [`LICENSE`](./LICENSE).
