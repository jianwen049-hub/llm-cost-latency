# cost_lab

```bash
cd lab
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=src
python3 scripts/smoke_check.py
python3 -m cost_lab.cli demo
python3 -m cost_lab.cli table
```
