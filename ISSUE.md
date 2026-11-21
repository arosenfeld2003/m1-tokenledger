# Use real per-model prices; add cost breakdowns

The ledger still uses family-level placeholder prices ("opus", "sonnet", "haiku") and a fixed 0.1x cache-read
multiplier. That's wrong for current models.

1. **Prices:** use the table in `PRICING.md`, looked up by exact model ID. A model that isn't in the table raises
   `KeyError`. Cache reads use each model's own cache-read price; cache writes stay 1.25x / 2x of input.
2. **`Ledger.breakdown()`:** return the session's dollars split into
   `{"input": ..., "output": ..., "cache_read": ..., "cache_write": ...}`, each rounded to 6 decimals.
3. **CLI `--by-model`:** after the total line, print `by model:` and then one line per model, sorted by model ID,
   formatted `"  {model:<18} ${cost:.6f}"`.
4. **Tests:** `tests/test_issue.py` has the acceptance tests. Update the existing tests to the new prices; don't
   delete tests to make the suite pass.
