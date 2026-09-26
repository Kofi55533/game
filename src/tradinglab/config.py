"""Load and validate experiment configuration without external dependencies."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


SUPPORTED_INTERVALS = frozenset({"1m", "15m", "1h", "1d"})
SUPPORTED_MARKETS = frozenset({"spot", "linear_perpetual"})
SUPPORTED_ACTION_SPACES = frozenset(
    {"buy_sell_hold", "target_position", "portfolio_weights"}
)
SUPPORTED_DIRECTIONS = frozenset({"long_only", "long_short"})


@dataclass(frozen=True)
class DataConfig:
    venue: str
    history_years: int
    intervals: tuple[str, ...]
    markets: tuple[str, ...]


@dataclass(frozen=True)
class UniverseConfig:
    mode: str
    quote_assets: tuple[str, ...]
    minimum_history_days: int
    minimum_daily_quote_volume: float
    exclude_stablecoin_bases: bool


@dataclass(frozen=True)
class AgentConfig:
    action_spaces: tuple[str, ...]
    directions: tuple[str, ...]


@dataclass(frozen=True)
class RiskConfig:
    profile: str
    leverages: tuple[float, ...]
    max_portfolio_drawdown: float
    max_position_weight: float
    max_gross_exposure: float


@dataclass(frozen=True)
class EvaluationConfig:
    walk_forward_folds: int
    seeds: tuple[int, ...]
    fee_multiplier: float
    slippage_multipliers: tuple[float, ...]


@dataclass(frozen=True)
class ExperimentConfig:
    data: DataConfig
    universe: UniverseConfig
    agent: AgentConfig
    risk: RiskConfig
    evaluation: EvaluationConfig


def _tuple(section: dict, key: str) -> tuple:
    value = section.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"{key} must be a non-empty list")
    return tuple(value)


def load_config(path: str | Path) -> ExperimentConfig:
    """Read a TOML config and reject unsafe or unsupported combinations."""
    with Path(path).open("rb") as config_file:
        raw = tomllib.load(config_file)

    data = DataConfig(
        venue=str(raw["data"]["venue"]),
        history_years=int(raw["data"]["history_years"]),
        intervals=_tuple(raw["data"], "intervals"),
        markets=_tuple(raw["data"], "markets"),
    )
    universe = UniverseConfig(
        mode=str(raw["universe"]["mode"]),
        quote_assets=_tuple(raw["universe"], "quote_assets"),
        minimum_history_days=int(raw["universe"]["minimum_history_days"]),
        minimum_daily_quote_volume=float(
            raw["universe"]["minimum_daily_quote_volume"]
        ),
        exclude_stablecoin_bases=bool(raw["universe"]["exclude_stablecoin_bases"]),
    )
    agent = AgentConfig(
        action_spaces=_tuple(raw["agent"], "action_spaces"),
        directions=_tuple(raw["agent"], "directions"),
    )
    risk = RiskConfig(
        profile=str(raw["risk"]["profile"]),
        leverages=tuple(float(value) for value in _tuple(raw["risk"], "leverages")),
        max_portfolio_drawdown=float(raw["risk"]["max_portfolio_drawdown"]),
        max_position_weight=float(raw["risk"]["max_position_weight"]),
        max_gross_exposure=float(raw["risk"]["max_gross_exposure"]),
    )
    evaluation = EvaluationConfig(
        walk_forward_folds=int(raw["evaluation"]["walk_forward_folds"]),
        seeds=tuple(int(value) for value in _tuple(raw["evaluation"], "seeds")),
        fee_multiplier=float(raw["evaluation"]["fee_multiplier"]),
        slippage_multipliers=tuple(
            float(value) for value in _tuple(raw["evaluation"], "slippage_multipliers")
        ),
    )
    config = ExperimentConfig(data, universe, agent, risk, evaluation)
    _validate(config)
    return config


def _validate(config: ExperimentConfig) -> None:
    if not 2 <= config.data.history_years <= 4:
        raise ValueError("history_years must be between 2 and 4")
    if set(config.data.intervals) - SUPPORTED_INTERVALS:
        raise ValueError("unsupported interval")
    if set(config.data.markets) - SUPPORTED_MARKETS:
        raise ValueError("unsupported market")
    if set(config.agent.action_spaces) - SUPPORTED_ACTION_SPACES:
        raise ValueError("unsupported action space")
    if set(config.agent.directions) - SUPPORTED_DIRECTIONS:
        raise ValueError("unsupported direction")
    if config.universe.mode != "point_in_time_all_eligible":
        raise ValueError("universe must be point-in-time to prevent survivorship bias")
    if not 0 < config.risk.max_portfolio_drawdown < 1:
        raise ValueError("max_portfolio_drawdown must be between zero and one")
    if not 0 < config.risk.max_position_weight <= 1:
        raise ValueError("max_position_weight must be between zero and one")
    if max(config.risk.leverages) > config.risk.max_gross_exposure:
        raise ValueError("leverage cannot exceed max_gross_exposure")
    if config.evaluation.walk_forward_folds < 3:
        raise ValueError("at least three walk-forward folds are required")
