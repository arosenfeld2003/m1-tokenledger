"""Summarize a JSONL file of {"model": ..., "usage": {...}} records, or a tracer capture.

  python -m tokenledger.cli calls.jsonl [--ttl 1h] [--by-model]
  python -m tokenledger.cli --capture capture.jsonl [--ttl 1h] [--by-model]

Calls to models not in PRICING.md are left out, with one warning line on stderr.
"""

import argparse
import json
import sys

from tokenledger.capture import load_calls
from tokenledger.ledger import Ledger
from tokenledger.pricing import PRICES, cost_usd


def summarize_calls(calls, ttl: str = "5m", by_model: bool = False) -> str:
    ledger = Ledger(default_ttl=ttl)
    rows = []
    unpriced = []
    for rec in calls:
        if rec["model"] not in PRICES:
            if rec["model"] not in unpriced:
                unpriced.append(rec["model"])
            continue
        ledger.record(rec["model"], rec["usage"])
        rows.append(f"{rec['model']:<20} ${cost_usd(rec['model'], rec['usage'], ttl):.6f}")
    if unpriced:
        print(f"warning: skipped calls to models not in PRICING.md: {', '.join(map(str, unpriced))}",
              file=sys.stderr)
    rows.append(f"{'total':<20} ${ledger.total:.6f}")
    if by_model:
        rows.append("by model:")
        rows += [f"  {m:<18} ${c:.6f}" for m, c in sorted(ledger.by_model().items())]
    return "\n".join(rows)


def summarize(lines, ttl: str = "5m", by_model: bool = False) -> str:
    return summarize_calls((json.loads(line) for line in lines if line.strip()), ttl, by_model)


def main():
    ap = argparse.ArgumentParser()
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("path", nargs="?")
    src.add_argument("--capture", metavar="FILE")
    ap.add_argument("--ttl", default="5m", choices=["5m", "1h"])
    ap.add_argument("--by-model", action="store_true")
    args = ap.parse_args()
    if args.capture:
        print(summarize_calls(load_calls(args.capture), args.ttl, args.by_model))
    else:
        with open(args.path) as f:
            print(summarize(f, args.ttl, args.by_model))


if __name__ == "__main__":
    main()
