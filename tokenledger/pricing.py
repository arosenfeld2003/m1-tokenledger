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
    """Cost in USD of one call's `usage` block, rounded to 6 decimals.

    Missing fields count as zero. If `usage["cache_creation"]` has a per-TTL
    breakdown it is used; otherwise `cache_creation_input_tokens` is billed
    at `default_ttl`. Raises KeyError for unknown models.
    """
    p = PRICES[family(model)]
    inp = p["input"] / 1_000_000
    out = p["output"] / 1_000_000

    breakdown = usage.get("cache_creation")
    if breakdown:
        writes = {
            "5m": breakdown.get("ephemeral_5m_input_tokens", 0),
            "1h": breakdown.get("ephemeral_1h_input_tokens", 0),
        }
    else:
        writes = {default_ttl: usage.get("cache_creation_input_tokens", 0)}

    cost = (
        usage.get("input_tokens", 0) * inp
        + usage.get("output_tokens", 0) * out
        + usage.get("cache_read_input_tokens", 0) * inp * CACHE_READ
        + sum(n * inp * CACHE_WRITE[ttl] for ttl, n in writes.items())
    )
    return round(cost, 6)
