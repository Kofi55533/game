from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from tradinglab.cost import estimate_cost


class CostEstimateTest(unittest.TestCase):
    def test_resampling_one_minute_data_uses_fewer_requests(self) -> None:
        estimate = estimate_cost(
            symbols=100,
            history_years=4,
            intervals=("1m", "15m", "1h", "1d"),
        )
        self.assertEqual(estimate.symbols, 100)
        self.assertGreater(estimate.one_minute_bars, 200_000_000)
        self.assertLess(
            estimate.market_data_requests_from_1m,
            estimate.market_data_requests_separate,
        )

    def test_model_cost_is_zero_without_model_calls(self) -> None:
        estimate = estimate_cost(
            symbols=10,
            history_years=2,
            intervals=("1h",),
        )
        self.assertEqual(estimate.model_cost_usd, 0)
        self.assertEqual(estimate.model_input_tokens, 0)

    def test_model_cost_uses_caller_supplied_prices(self) -> None:
        estimate = estimate_cost(
            symbols=1,
            history_years=2,
            intervals=("1d",),
            input_tokens_per_decision=1_000,
            output_tokens_per_decision=100,
            input_usd_per_million=2,
            output_usd_per_million=8,
        )
        expected = (
            estimate.model_input_tokens * 2 + estimate.model_output_tokens * 8
        ) / 1_000_000
        self.assertEqual(estimate.model_cost_usd, round(expected, 2))


if __name__ == "__main__":
    unittest.main()
