from pathlib import Path
import contextlib
import io
import os
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from tradinglab.secrets import inspect_environment, main


class SecretStatusTest(unittest.TestCase):
    def test_empty_environment_is_not_ready(self) -> None:
        status = inspect_environment({})
        self.assertFalse(status.model_ready)
        self.assertFalse(status.bybit_private_ready)

    def test_model_requires_only_key(self) -> None:
        status = inspect_environment(
            {
                "MODEL_API_KEY": "not-a-real-key",
            }
        )
        self.assertTrue(status.model_ready)
        self.assertFalse(status.bybit_private_ready)

    def test_values_are_not_exposed_by_status(self) -> None:
        secret = "must-never-be-returned"
        status = inspect_environment({"MODEL_API_KEY": secret})
        self.assertNotIn(secret, repr(status))

    def test_require_model_exits_when_key_is_missing(self) -> None:
        previous_argv = sys.argv
        previous_value = os.environ.pop("MODEL_API_KEY", None)
        sys.argv = ["trading-check-secrets", "--require-model"]
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
                io.StringIO()
            ):
                with self.assertRaises(SystemExit) as raised:
                    main()
            self.assertEqual(raised.exception.code, 1)
        finally:
            sys.argv = previous_argv
            if previous_value is not None:
                os.environ["MODEL_API_KEY"] = previous_value


if __name__ == "__main__":
    unittest.main()
