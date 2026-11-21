import pytest

from tokenledger.cli import summarize
from tokenledger.ledger import Ledger
from tokenledger.pricing import cost_usd

M = 1_000_000


def test_opus_5_5_list_price():
    assert cost_usd("claude-opus-5-5", {"input_tokens": M, "output_tokens": M}) == 24.0


def test_opus_5_is_not_opus_5_5():
    assert cost_usd("claude-opus-5", {"input_tokens": M}) == 5.0


@pytest.mark.parametrize("model,expected", [("claude-opus-5-5", 0.2), ("claude-sonnet-5-5", 0.2), ("claude-haiku-5-5", 0.01)])
def test_cache_read_is_per_model(model, expected):
    assert cost_usd(model, {"cache_read_input_tokens": M}) == expected


@pytest.mark.parametrize("model", ["claude-opus-4-8", "claude-sonnet-5", "opus"])
def test_models_not_in_table_raise(model):
    with pytest.raises(KeyError):
        cost_usd(model, {"input_tokens": 1})


def test_breakdown():
    led = Ledger(default_ttl="1h")
    led.record("claude-opus-5-5", {"input_tokens": 1_000, "output_tokens": 2_000, "cache_creation_input_tokens": 10_000})
    led.record("claude-haiku-5-5", {"cache_read_input_tokens": 100_000, "output_tokens": 1_000})
    assert led.breakdown() == {"input": 0.004, "output": 0.0405, "cache_read": 0.001, "cache_write": 0.08}
    assert led.total == 0.1255


def test_cli_by_model():
    lines = [
        '{"model": "claude-sonnet-5-5", "usage": {"input_tokens": 1000}}',
        '{"model": "claude-opus-5-5", "usage": {"output_tokens": 1000}}',
        '{"model": "claude-sonnet-5-5", "usage": {"output_tokens": 1000}}',
    ]
    assert summarize(lines, by_model=True).splitlines() == [
        "claude-sonnet-5-5    $0.002000",
        "claude-opus-5-5      $0.020000",
        "claude-sonnet-5-5    $0.010000",
        "total                $0.032000",
        "by model:",
        "  claude-opus-5-5    $0.020000",
        "  claude-sonnet-5-5  $0.012000",
    ]
