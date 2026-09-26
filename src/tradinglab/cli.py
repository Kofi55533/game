"""Command-line interface for inspecting the planned experiment matrix."""

from __future__ import annotations

import argparse
import json

from .config import load_config
from .matrix import build_matrix


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate trading experiment plans")
    parser.add_argument("--config", default="configs/experiment.toml")
    parser.add_argument("--stage", choices=("screening", "risk"), default="screening")
    parser.add_argument("--count", action="store_true", help="print only the plan size")
    args = parser.parse_args()

    experiments = build_matrix(load_config(args.config), args.stage)
    if args.count:
        print(len(experiments))
        return
    for experiment in experiments:
        print(json.dumps(experiment.as_dict(), sort_keys=True))


if __name__ == "__main__":
    main()
