import subprocess
import sys
from pathlib import Path

import pytest

from tokenledger.capture import load_calls

FIXTURE = Path(__file__).parent / "fixtures" / "capture.jsonl"
pytestmark = pytest.mark.skipif(not FIXTURE.exists(), reason="real capture not present (gitignored)")


def test_load_calls_finds_every_messages_call():
    calls = load_calls(FIXTURE)
    assert len(calls) == 11
    assert calls[0]["model"] == "claude-haiku-4-5-20251001"
    assert [c["model"] for c in calls].count("claude-opus-5-5") == 9
    assert all(isinstance(c["usage"]["output_tokens"], int) for c in calls)


def test_cli_prices_a_real_capture():
    out = subprocess.run(
        [sys.executable, "-m", "tokenledger.cli", "--capture", str(FIXTURE), "--by-model"],
        capture_output=True, text=True, cwd=Path(__file__).parent.parent,
    )
    assert out.returncode == 0, out.stderr
    lines = out.stdout.splitlines()
    assert len(lines) == 10 + 4  # 10 priced calls, total, "by model:", 2 models
    assert lines[-4:] == [
        "total                $0.415398",
        "by model:",
        "  claude-haiku-5-5   $0.000128",
        "  claude-opus-5-5    $0.415270",
    ]
    assert "claude-haiku-4-5-20251001" in out.stderr
    assert len(out.stderr.strip().splitlines()) == 1
