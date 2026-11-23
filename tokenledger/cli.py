"""Summarize a JSONL file of {"model": ..., "usage": {...}} records.

  python -m tokenledger.cli calls.jsonl [--ttl 1h]
"""

import argparse
import json

from tokenledger.ledger import Ledger
from tokenledger.pricing import cost_usd


def summarize(lines, ttl: str = "5m", by_model: bool = False) -> str:
    ledger = Ledger(default_ttl=ttl)
    rows = []
    for line in lines:
        if not line.strip():
            continue
        rec = json.loads(line)
        ledger.record(rec["model"], rec["usage"])
        rows.append(f"{rec['model']:<20} ${cost_usd(rec['model'], rec['usage'], ttl):.6f}")
    rows.append(f"{'total':<20} ${ledger.total:.6f}")
    if by_model:
        rows.append("by model:")
        rows += [f"  {m:<18} ${c:.6f}" for m, c in sorted(ledger.by_model().items())]
    return "\n".join(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--ttl", default="5m", choices=["5m", "1h"])
    ap.add_argument("--by-model", action="store_true")
    args = ap.parse_args()
    with open(args.path) as f:
        print(summarize(f, args.ttl, args.by_model))


if __name__ == "__main__":
    main()
