import pytest

from tokenledger.pricing import cost_usd, family


def test_family():
    assert family("claude-opus-5-5") == "opus"
    assert family("claude-haiku-5-5") == "haiku"
    with pytest.raises(KeyError):
        family("gpt-9")


def test_plain_input_output():
    # 1M in at $5 + 100k out at $25/M
    assert cost_usd("claude-opus-5-5", {"input_tokens": 1_000_000, "output_tokens": 100_000}) == 7.5


def test_missing_fields_are_zero():
    assert cost_usd("claude-haiku-5-5", {}) == 0.0


def test_cache_read_is_tenth_of_input():
    assert cost_usd("claude-sonnet-5-5", {"cache_read_input_tokens": 1_000_000}) == 0.3


@pytest.mark.parametrize("ttl,expected", [("5m", 6.25), ("1h", 10.0)])
def test_cache_write_uses_default_ttl(ttl, expected):
    usage = {"cache_creation_input_tokens": 1_000_000}
    assert cost_usd("claude-opus-5-5", usage, default_ttl=ttl) == expected


def test_cache_creation_breakdown_wins_over_flat_count():
    usage = {
        "cache_creation_input_tokens": 3_000,
        "cache_creation": {"ephemeral_5m_input_tokens": 1_000, "ephemeral_1h_input_tokens": 2_000},
    }
    # 1000*5e-6*1.25 + 2000*5e-6*2, NOT 3000 at the default TTL
    assert cost_usd("claude-opus-5-5", usage, default_ttl="1h") == 0.02625


def test_rounds_to_six_decimals():
    assert cost_usd("claude-haiku-5-5", {"input_tokens": 1, "output_tokens": 1}) == 0.000006


def test_unknown_model_raises():
    with pytest.raises(KeyError):
        cost_usd("gpt-9", {"input_tokens": 1})
