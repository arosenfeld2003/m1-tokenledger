# Model prices

USD per million tokens. Cache writes are a multiple of the model's input price: 1.25x for the 5-minute TTL,
2x for the 1-hour TTL. Cache reads have their own per-model price (it is not a fixed fraction of input).

| model ID | input | output | cache read |
|---|---|---|---|
| `claude-opus-5-5` | 4.00 | 20.00 | 0.20 |
| `claude-opus-5` | 5.00 | 25.00 | 0.50 |
| `claude-sonnet-5-5` | 2.00 | 10.00 | 0.20 |
| `claude-haiku-5-5` | 0.10 | 0.50 | 0.01 |

Exercise fixture. Input/output and the Opus 5.5 / Sonnet 5.5 cache-read prices match Anthropic's list prices as of
2026-10; the Opus 5 and Haiku 5.5 cache-read prices are assumed (0.1x input).
