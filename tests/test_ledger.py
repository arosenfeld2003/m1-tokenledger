from tokenledger.cli import summarize
from tokenledger.ledger import Ledger

OPUS = "claude-opus-5-5"
HAIKU = "claude-haiku-5-5"


def test_ledger_totals_and_by_model():
    led = Ledger(default_ttl="1h")
    led.record(OPUS, {"input_tokens": 2_000, "cache_creation_input_tokens": 10_000, "output_tokens": 500})
    led.record(OPUS, {"input_tokens": 50, "cache_read_input_tokens": 10_000, "output_tokens": 300})
    led.record(HAIKU, {"input_tokens": 4_000, "output_tokens": 200})
    assert led.by_model() == {OPUS: 0.1062, HAIKU: 0.0005}
    assert led.total == 0.1067


def test_cli_summary():
    lines = [
        '{"model": "claude-opus-5-5", "usage": {"input_tokens": 1000, "output_tokens": 1000}}\n',
        "\n",
        '{"model": "claude-haiku-5-5", "usage": {"cache_read_input_tokens": 1000000}}\n',
    ]
    assert summarize(lines).splitlines() == [
        "claude-opus-5-5      $0.024000",
        "claude-haiku-5-5     $0.010000",
        "total                $0.034000",
    ]
