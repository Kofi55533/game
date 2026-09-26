"""Build bounded, staged experiment matrices instead of one giant grid search."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import product

from .config import ExperimentConfig


@dataclass(frozen=True)
class Experiment:
    id: str
    stage: str
    venue: str
    market: str
    interval: str
    action_space: str
    direction: str
    leverage: float
    history_years: int
    universe: str

    def as_dict(self) -> dict[str, str | float | int]:
        return asdict(self)


def build_matrix(config: ExperimentConfig, stage: str = "screening") -> list[Experiment]:
    """Create screening or risk experiments with invalid spot cases removed.

    Screening compares every requested interval, market and action model at 1x.
    The risk stage adds requested leverage levels. Spot remains long-only at 1x.
    """
    if stage not in {"screening", "risk"}:
        raise ValueError("stage must be 'screening' or 'risk'")

    experiments: list[Experiment] = []
    dimensions = product(
        config.data.markets,
        config.data.intervals,
        config.agent.action_spaces,
        config.agent.directions,
    )
    for market, interval, action_space, direction in dimensions:
        if market == "spot" and direction == "long_short":
            continue
        leverages = (1.0,) if stage == "screening" else config.risk.leverages
        if market == "spot":
            leverages = (1.0,)
        for leverage in leverages:
            experiment_id = "-".join(
                (
                    stage,
                    market,
                    interval,
                    action_space,
                    direction,
                    f"{leverage:g}x",
                )
            )
            experiments.append(
                Experiment(
                    id=experiment_id,
                    stage=stage,
                    venue=config.data.venue,
                    market=market,
                    interval=interval,
                    action_space=action_space,
                    direction=direction,
                    leverage=leverage,
                    history_years=config.data.history_years,
                    universe=config.universe.mode,
                )
            )
    return experiments
