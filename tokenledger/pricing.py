"""Per-model prices (USD per million tokens, see PRICING.md) and cost calculation.

Cache writes are a multiple of the model's input price: 1.25x (5m TTL), 2x (1h TTL).
Cache reads have their own per-model price.
"""

PRICES = {
    "claude-opus-5-5": {"input": 4.00, "output": 20.00, "cache_read": 0.20},
    "claude-opus-5": {"input": 5.00, "output": 25.00, "cache_read": 0.50},
    "claude-sonnet-5-5": {"input": 2.00, "output": 10.00, "cache_read": 0.20},
    "claude-haiku-5-5": {"input": 0.10, "output": 0.50, "cache_read": 0.01},
}

CACHE_WRITE = {"5m": 1.25, "1h": 2.0}


def cost_parts(model: str, usage: dict, default_ttl: str = "5m") -> dict[str, float]:
    """Unrounded dollars per category. Raises KeyError for models not in PRICES."""
    p = PRICES[model]
    per = p["input"] / 1e6
    breakdown = usage.get("cache_creation")
    if breakdown:
        write = (breakdown.get("ephemeral_5m_input_tokens", 0) * CACHE_WRITE["5m"]
                 + breakdown.get("ephemeral_1h_input_tokens", 0) * CACHE_WRITE["1h"]) * per
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
