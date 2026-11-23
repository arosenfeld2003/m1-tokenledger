"""Per-model prices (USD per million tokens) and cost calculation.

Prices are looked up by exact model ID (see PRICING.md). Cache reads have
their own per-model price; cache writes are a multiple of the input price:
  cache write, 5m TTL   1.25x
  cache write, 1h TTL   2x
"""

PRICES = {
    "claude-opus-5-5": {"input": 4.00, "output": 20.00, "cache_read": 0.20},
    "claude-opus-5": {"input": 5.00, "output": 25.00, "cache_read": 0.50},
    "claude-sonnet-5-5": {"input": 2.00, "output": 10.00, "cache_read": 0.20},
    "claude-haiku-5-5": {"input": 0.10, "output": 0.50, "cache_read": 0.01},
}

CACHE_WRITE = {"5m": 1.25, "1h": 2.0}

FAMILIES = ("opus", "sonnet", "haiku")


def family(model: str) -> str:
    """'claude-opus-5-5' -> 'opus'. Raises KeyError for unknown models."""
    for name in FAMILIES:
        if name in model:
            return name
    raise KeyError(model)


def cost_parts(model: str, usage: dict, default_ttl: str = "5m") -> dict[str, float]:
    """Unrounded dollar cost of one `usage` block, split into
    input / output / cache_read / cache_write.

    `cache_creation_input_tokens` is billed at `default_ttl` unless the usage
    has a `cache_creation` breakdown ({"ephemeral_5m_input_tokens": n,
    "ephemeral_1h_input_tokens": m}), which takes precedence.
    Missing counts are treated as 0. Raises KeyError for models not in PRICES.
    """
    p = PRICES[model]
    per = p["input"] / 1e6
    breakdown = usage.get("cache_creation")
    if breakdown:
        write = breakdown.get("ephemeral_5m_input_tokens", 0) * per * CACHE_WRITE["5m"]
        write += breakdown.get("ephemeral_1h_input_tokens", 0) * per * CACHE_WRITE["1h"]
    else:
        write = usage.get("cache_creation_input_tokens", 0) * per * CACHE_WRITE[default_ttl]
    return {
        "input": usage.get("input_tokens", 0) * per,
        "output": usage.get("output_tokens", 0) * p["output"] / 1e6,
        "cache_read": usage.get("cache_read_input_tokens", 0) * p["cache_read"] / 1e6,
        "cache_write": write,
    }


def cost_usd(model: str, usage: dict, default_ttl: str = "5m") -> float:
    """Dollar cost of one response's `usage` block, rounded to 6 decimals."""
    return round(sum(cost_parts(model, usage, default_ttl).values()), 6)
