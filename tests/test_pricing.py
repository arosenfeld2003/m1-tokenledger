import pytest

from tokenledger.pricing import cost_usd


def test_plain_input_output():
    # 1M in at $4 + 100k out at $20/M
    assert cost_usd("claude-opus-5-5", {"input_tokens": 1_000_000, "output_tokens": 100_000}) == 6.0


def test_missing_fields_are_zero():
    assert cost_usd("claude-haiku-5-5", {}) == 0.0


def test_cache_read_uses_model_price():
    assert cost_usd("claude-sonnet-5-5", {"cache_read_input_tokens": 1_000_000}) == 0.2


@pytest.mark.parametrize("ttl,expected", [("5m", 5.0), ("1h", 8.0)])
def test_cache_write_uses_default_ttl(ttl, expected):
    usage = {"cache_creation_input_tokens": 1_000_000}
    assert cost_usd("claude-opus-5-5", usage, default_ttl=ttl) == expected


def test_cache_creation_breakdown_wins_over_flat_count():
    usage = {
        "cache_creation_input_tokens": 3_000,
        "cache_creation": {"ephemeral_5m_input_tokens": 1_000, "ephemeral_1h_input_tokens": 2_000},
    }
    # 1000*4e-6*1.25 + 2000*4e-6*2, NOT 3000 at the default TTL
    assert cost_usd("claude-opus-5-5", usage, default_ttl="1h") == 0.021


def test_rounds_to_six_decimals():
    assert cost_usd("claude-haiku-5-5", {"input_tokens": 1, "output_tokens": 1}) == 0.000001


def test_unknown_model_raises():
    with pytest.raises(KeyError):
        cost_usd("gpt-9", {"input_tokens": 1})
