"""Trading-agent research utilities."""

from .config import ExperimentConfig, load_config
from .matrix import Experiment, build_matrix

__all__ = ["Experiment", "ExperimentConfig", "build_matrix", "load_config"]
