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


def cost_usd(model: str, usage: dict, default_ttl: str = "5m") -> float:
    """Dollar cost of one response's `usage` block, rounded to 6 decimals.

    `cache_creation_input_tokens` is billed at `default_ttl` unless the usage
    has a `cache_creation` breakdown ({"ephemeral_5m_input_tokens": n,
    "ephemeral_1h_input_tokens": m}), which takes precedence.
    Missing counts are treated as 0.
    """
    p = PRICES[family(model)]
    per = p["input"] / 1e6
    total = usage.get("input_tokens", 0) * per
    total += usage.get("output_tokens", 0) * p["output"] / 1e6
    total += usage.get("cache_read_input_tokens", 0) * per * CACHE_READ
    breakdown = usage.get("cache_creation")
    if breakdown:
        total += breakdown.get("ephemeral_5m_input_tokens", 0) * per * CACHE_WRITE["5m"]
        total += breakdown.get("ephemeral_1h_input_tokens", 0) * per * CACHE_WRITE["1h"]
    else:
        total += usage.get("cache_creation_input_tokens", 0) * per * CACHE_WRITE[default_ttl]
    return round(total, 6)
