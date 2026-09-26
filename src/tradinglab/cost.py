"""Estimate data volume, request count, and optional model-token cost."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import math

from .config import load_config


MINUTES_PER_YEAR = 365.25 * 24 * 60
INTERVAL_MINUTES = {"1m": 1, "15m": 15, "1h": 60, "1d": 1_440}


@dataclass(frozen=True)
class CostEstimate:
    symbols: int
    history_years: int
    one_minute_bars: int
    all_interval_bars: int
    market_data_requests_from_1m: int
    market_data_requests_separate: int
    approximate_binary_gib: float
    model_decisions: int
    model_input_tokens: int
    model_output_tokens: int
    model_cost_usd: float


def estimate_cost(
    *,
    symbols: int,
    history_years: int,
    intervals: tuple[str, ...],
    page_size: int = 1_000,
    bytes_per_bar: int = 64,
    input_tokens_per_decision: int = 0,
    output_tokens_per_decision: int = 0,
    input_usd_per_million: float = 0,
    output_usd_per_million: float = 0,
) -> CostEstimate:
    """Return transparent upper-bound estimates for a historical run.

    Model decisions assume one uncached call per symbol and bar across every
    interval. This is deliberately conservative; deterministic agents cost no
    model tokens, and screening can call a model much less frequently.
    """
    if symbols <= 0 or history_years <= 0 or page_size <= 0 or bytes_per_bar <= 0:
        raise ValueError("counts and sizes must be positive")
    if any(value < 0 for value in (
        input_tokens_per_decision,
        output_tokens_per_decision,
        input_usd_per_million,
        output_usd_per_million,
    )):
        raise ValueError("token amounts and prices cannot be negative")

    bars_per_symbol = {
        interval: math.ceil(MINUTES_PER_YEAR * history_years / INTERVAL_MINUTES[interval])
        for interval in intervals
    }
    one_minute_bars_per_symbol = math.ceil(MINUTES_PER_YEAR * history_years)
    one_minute_bars = one_minute_bars_per_symbol * symbols
    all_interval_bars = sum(bars_per_symbol.values()) * symbols
    requests_from_1m = math.ceil(one_minute_bars_per_symbol / page_size) * symbols
    requests_separate = sum(
        math.ceil(bars / page_size) for bars in bars_per_symbol.values()
    ) * symbols
    input_tokens = all_interval_bars * input_tokens_per_decision
    output_tokens = all_interval_bars * output_tokens_per_decision
    model_cost = (
        input_tokens * input_usd_per_million
        + output_tokens * output_usd_per_million
    ) / 1_000_000
    return CostEstimate(
        symbols=symbols,
        history_years=history_years,
        one_minute_bars=one_minute_bars,
        all_interval_bars=all_interval_bars,
        market_data_requests_from_1m=requests_from_1m,
        market_data_requests_separate=requests_separate,
        approximate_binary_gib=round(one_minute_bars * bytes_per_bar / 1024**3, 2),
        model_decisions=all_interval_bars,
        model_input_tokens=input_tokens,
        model_output_tokens=output_tokens,
        model_cost_usd=round(model_cost, 2),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate trading-agent research cost")
    parser.add_argument("--config", default="configs/experiment.toml")
    parser.add_argument("--symbols", type=int, default=100)
    parser.add_argument("--page-size", type=int, default=1_000)
    parser.add_argument("--input-tokens", type=int, default=0)
    parser.add_argument("--output-tokens", type=int, default=0)
    parser.add_argument("--input-usd-per-million", type=float, default=0)
    parser.add_argument("--output-usd-per-million", type=float, default=0)
    args = parser.parse_args()

    config = load_config(args.config)
    estimate = estimate_cost(
        symbols=args.symbols,
        history_years=config.data.history_years,
        intervals=config.data.intervals,
        page_size=args.page_size,
        input_tokens_per_decision=args.input_tokens,
        output_tokens_per_decision=args.output_tokens,
        input_usd_per_million=args.input_usd_per_million,
        output_usd_per_million=args.output_usd_per_million,
    )
    print(json.dumps(asdict(estimate), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
