"""Per-model prices (USD per million tokens) and cost calculation.

Cache pricing is a multiple of the model's base input price:
  cache read            0.1x
  cache write, 5m TTL   1.25x
  cache write, 1h TTL   2x
"""

PRICES = {
    "opus": {"input": 5.00, "output": 25.00},
    "sonnet": {"input": 3.00, "output": 15.00},
    "haiku": {"input": 1.00, "output": 5.00},
}

CACHE_READ = 0.1
CACHE_WRITE = {"5m": 1.25, "1h": 2.0}


def family(model: str) -> str:
    """'claude-opus-5-5' -> 'opus'. Raises KeyError for unknown models."""
    for name in PRICES:
        if name in model:
            return name
    raise KeyError(model)

