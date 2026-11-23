from dataclasses import dataclass, field

from tokenledger.pricing import cost_parts, cost_usd


@dataclass
class Ledger:
    """Running total of model calls in one agent session."""

    default_ttl: str = "5m"
    entries: list[tuple[str, dict, float]] = field(default_factory=list)

    def record(self, model: str, usage: dict) -> float:
        c = cost_usd(model, usage, self.default_ttl)
        self.entries.append((model, usage, c))
        return c

    @property
    def total(self) -> float:
        return round(sum(c for _, _, c in self.entries), 6)

    def by_model(self) -> dict[str, float]:
        out: dict[str, float] = {}
        for model, _, c in self.entries:
            out[model] = round(out.get(model, 0) + c, 6)
        return out

    def breakdown(self) -> dict[str, float]:
        out = dict.fromkeys(("input", "output", "cache_read", "cache_write"), 0.0)
        for model, usage, _ in self.entries:
            for k, v in cost_parts(model, usage, self.default_ttl).items():
                out[k] += v
        return {k: round(v, 6) for k, v in out.items()}
