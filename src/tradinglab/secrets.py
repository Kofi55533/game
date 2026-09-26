"""Validate secret environment variables without reading or printing their values."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
import sys


MODEL_KEY_VARIABLE = "MODEL_API_KEY"
BYBIT_KEY_VARIABLE = "BYBIT_API_KEY"
BYBIT_SECRET_VARIABLE = "BYBIT_API_SECRET"


@dataclass(frozen=True)
class SecretStatus:
    model_api_key: bool
    bybit_api_key: bool
    bybit_api_secret: bool

    @property
    def model_ready(self) -> bool:
        return self.model_api_key

    @property
    def bybit_private_ready(self) -> bool:
        return self.bybit_api_key and self.bybit_api_secret


def inspect_environment(environment: dict[str, str] | None = None) -> SecretStatus:
    """Report presence only; secret values are never returned or logged."""
    values = os.environ if environment is None else environment

    def is_set(name: str) -> bool:
        return bool(values.get(name, "").strip())

    return SecretStatus(
        model_api_key=is_set(MODEL_KEY_VARIABLE),
        bybit_api_key=is_set(BYBIT_KEY_VARIABLE),
        bybit_api_secret=is_set(BYBIT_SECRET_VARIABLE),
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check trading-agent secret presence without displaying values"
    )
    parser.add_argument(
        "--require-model",
        action="store_true",
        help="exit with an error when MODEL_API_KEY is missing",
    )
    args = parser.parse_args()
    status = inspect_environment()
    print(
        json.dumps(
            {
                "model_api_key": status.model_api_key,
                "model_ready": status.model_ready,
                "bybit_api_key": status.bybit_api_key,
                "bybit_api_secret": status.bybit_api_secret,
                "bybit_private_ready": status.bybit_private_ready,
            },
            indent=2,
            sort_keys=True,
        )
    )
    if args.require_model and not status.model_ready:
        print("MODEL_API_KEY is not configured", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
