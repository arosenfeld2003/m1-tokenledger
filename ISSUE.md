# Price a real tracer capture

Our mitmproxy tracer writes one JSON object per HTTP flow an agent made:
`seq, t_start, t_end, method, host, path, req_headers, req_body, status, resp_headers, resp_body`, with the request
and response bodies parsed as JSON when they are JSON. We want the ledger to price a whole agent session from one of
these captures.

1. **`tokenledger/capture.py`:** `load_calls(path) -> list[dict]` returns `{"model": ..., "usage": ...}` for every
   Messages API call in the capture, in capture order.
2. **CLI:** `python -m tokenledger.cli --capture FILE` summarizes a capture exactly like a calls file (and works with
   `--ttl` and `--by-model`).
3. **Models not in `PRICING.md`** must not crash the summary: leave them out of the rows and totals, and print one
   warning line to stderr naming them.
4. **Tests:** `tests/test_capture.py` runs against a real capture at `tests/fixtures/capture.jsonl` (gitignored:
   captures contain account details). Keep the whole suite passing.
