from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from tradinglab.config import load_config
from tradinglab.matrix import build_matrix


CONFIG = Path(__file__).parents[1] / "configs" / "experiment.toml"


class ExperimentMatrixTest(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config(CONFIG)

    def test_screening_covers_all_requested_intervals_and_actions(self) -> None:
        experiments = build_matrix(self.config, "screening")
        self.assertEqual({item.interval for item in experiments}, {"1m", "15m", "1h", "1d"})
        self.assertEqual(
            {item.action_space for item in experiments},
            {"buy_sell_hold", "target_position", "portfolio_weights"},
        )
        self.assertEqual(len(experiments), 36)
        self.assertTrue(all(item.leverage == 1 for item in experiments))

    def test_risk_stage_includes_aggressive_leverage(self) -> None:
        experiments = build_matrix(self.config, "risk")
        perpetual = [item for item in experiments if item.market == "linear_perpetual"]
        self.assertEqual({item.leverage for item in perpetual}, {1, 2, 3, 5})
        self.assertEqual(len(experiments), 108)

    def test_spot_never_uses_short_or_leverage(self) -> None:
        experiments = build_matrix(self.config, "risk")
        spot = [item for item in experiments if item.market == "spot"]
        self.assertTrue(spot)
        self.assertTrue(all(item.direction == "long_only" for item in spot))
        self.assertTrue(all(item.leverage == 1 for item in spot))

    def test_rejects_leverage_above_gross_exposure(self) -> None:
        text = CONFIG.read_text().replace("max_gross_exposure = 5.0", "max_gross_exposure = 2.0")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.toml"
            path.write_text(text)
            with self.assertRaisesRegex(ValueError, "leverage cannot exceed"):
                load_config(path)


if __name__ == "__main__":
    unittest.main()
