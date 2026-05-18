"""
Configuration management for the Reciprocal Acceleration Framework.

This module provides configuration classes for RAF components, including
experiment-specific configurations like CrossLoopValidationConfig which
documents assumed coupling parameters for reference implementation studies.
"""

import json
import tomllib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class LoopConfig:
    """Configuration for an acceleration loop."""

    name: str
    enabled: bool = True
    initial_params: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class CrossLoopValidationConfig:
    """
    Configuration for cross-loop validation experiments.

    This dataclass exposes assumed coupling parameters that drive the
    integrated cross-loop experiment in raf.experiments.cross_loop_validation.
    These are NOT measured parameters but rather assumptions drawn from prior
    literature (Maes 2025, Shukla 2025) for structural sensitivity studies.

    Coupling strengths in [0, 1] represent the relative influence of one loop's
    improvements on another. Results illustrate cascade dynamics for the assumed
    parameter set rather than measured coupling strengths.
    """

    # Calibration loop assumptions
    calibration_base_improvement: float = 0.05
    calibration_to_gate_fidelity_coupling: float = 0.3
    calibration_to_drift_tracking_coupling: float = 0.5
    calibration_noise_factor: float = 0.2

    # Error mitigation loop assumptions
    mitigation_base_improvement: float = 0.04
    calibration_to_mitigation_coupling: float = 0.5
    mitigation_to_overhead_coupling: float = 2.0
    mitigation_noise_factor: float = 0.15

    # Circuit scaling assumptions
    depth_momentum_factor: float = 0.7
    depth_target_factor: float = 0.3
    training_data_weight_calibration: float = 0.5
    training_data_weight_history: float = 0.5

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CrossLoopValidationConfig":
        """Create from dictionary."""
        # Filter to only known fields
        fields_set = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in fields_set}
        return cls(**filtered)


@dataclass(slots=True)
class CouplingAssumptionsConfig:
    """
    Coupling strength assumptions for cross-loop interactions.

    These coupling strengths represent ASSUMED values drawn from prior literature
    (Maes 2025, Shukla 2025) that describe how improvements in one acceleration loop
    affect other loops. They are NOT measured empirical values but rather theoretical
    assumptions used for sensitivity studies and structural analysis.

    Coupling strengths are in [0, 1] where:
    - 0.0 = no interaction
    - 1.0 = complete coupling (full propagation of improvement)

    Strengths are directional: calibration_to_error_mitigation is different from
    error_mitigation_to_calibration.
    """

    # Calibration → Error Mitigation
    # Lower base error rates reduce mitigation requirements
    calibration_to_error_mitigation: float = 0.8

    # Calibration → Ansatz Design
    # Lower error rates enable larger feasible circuit depths
    calibration_to_ansatz_design: float = 0.7

    # Ansatz Design → Error Mitigation
    # Better ansätze can be more noise-resilient
    ansatz_design_to_error_mitigation: float = 0.6

    # Ansatz Design → Calibration
    # Optimized circuits can probe specific noise mechanisms
    ansatz_design_to_calibration: float = 0.5

    # Error Mitigation → Ansatz Design
    # Better mitigation enables evaluation of deeper circuits
    error_mitigation_to_ansatz_design: float = 0.6

    # Error Mitigation → Calibration
    # Mitigation insights inform noise characterization
    error_mitigation_to_calibration: float = 0.4

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CouplingAssumptionsConfig":
        """Create from dictionary, filtering to known fields."""
        fields_set = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in fields_set}
        return cls(**filtered)


@dataclass(slots=True)
class RAFConfig:
    """
    Configuration for the Reciprocal Acceleration Framework.

    Attributes:
        name: Framework instance name
        loops: Configuration for each loop
        coupling_assumptions: Assumed coupling strengths between loops
        couplings: Custom coupling definitions
        analysis_settings: Settings for analysis tools
        visualization_settings: Settings for visualization
    """

    name: str = "RAF"
    loops: dict[str, LoopConfig] = field(default_factory=dict)
    coupling_assumptions: CouplingAssumptionsConfig = field(
        default_factory=CouplingAssumptionsConfig
    )
    couplings: list[dict[str, Any]] = field(default_factory=list)
    analysis_settings: dict[str, Any] = field(
        default_factory=lambda: {
            "bottleneck_threshold": 0.5,
            "acceleration_window": 5,
            "prediction_iterations": 10,
        }
    )
    visualization_settings: dict[str, Any] = field(
        default_factory=lambda: {
            "figsize": [10, 6],
            "style": "default",
            "save_format": "png",
        }
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "loops": {name: asdict(config) for name, config in self.loops.items()},
            "coupling_assumptions": asdict(self.coupling_assumptions),
            "couplings": self.couplings,
            "analysis_settings": self.analysis_settings,
            "visualization_settings": self.visualization_settings,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RAFConfig":
        """Create from dictionary."""
        loops = {}
        for name, config in data.get("loops", {}).items():
            loops[name] = LoopConfig(**config)

        coupling_assumptions_data = data.get("coupling_assumptions", {})
        coupling_assumptions = CouplingAssumptionsConfig.from_dict(coupling_assumptions_data)

        return cls(
            name=data.get("name", "RAF"),
            loops=loops,
            coupling_assumptions=coupling_assumptions,
            couplings=data.get("couplings", []),
            analysis_settings=data.get("analysis_settings", {}),
            visualization_settings=data.get("visualization_settings", {}),
        )

    def add_loop_config(self, name: str, **kwargs: Any) -> None:
        """Add or update loop configuration."""
        self.loops[name] = LoopConfig(name=name, **kwargs)

    def get_loop_config(self, name: str) -> LoopConfig | None:
        """Get configuration for a specific loop."""
        return self.loops.get(name)


def load_config(path: str) -> RAFConfig:
    """
    Load configuration from a JSON file.

    Args:
        path: Path to configuration file

    Returns:
        RAFConfig instance
    """
    with open(path) as f:
        data = json.load(f)
    return RAFConfig.from_dict(data)


def load_cross_loop_config(path: str | None = None) -> CrossLoopValidationConfig:
    """
    Load cross-loop validation configuration from TOML file.

    Args:
        path: Path to TOML config file. If None, loads from default location.

    Returns:
        CrossLoopValidationConfig instance
    """
    if path is None:
        # Try default location relative to package
        default_path = (
            Path(__file__).parent.parent.parent / "configs" / "cross_loop_validation.toml"
        )
        if default_path.exists():
            path = str(default_path)
        else:
            return CrossLoopValidationConfig()

    with open(path, "rb") as f:
        data = tomllib.load(f)

    # Flatten nested sections into single-level dict with underscore separators
    flattened: dict[str, Any] = {}
    for section, section_data in data.items():
        if isinstance(section_data, dict):
            for key, value in section_data.items():
                flattened[f"{section}_{key}"] = value
        else:
            flattened[section] = section_data

    return CrossLoopValidationConfig.from_dict(flattened)


def save_config(config: RAFConfig, path: str) -> None:
    """
    Save configuration to a JSON file.

    Args:
        config: RAFConfig instance
        path: Path to save to
    """
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(config.to_dict(), f, indent=2)


def get_default_config() -> RAFConfig:
    """Get default configuration."""
    config = RAFConfig()

    # Default loop configurations
    config.add_loop_config(
        "error_mitigation",
        initial_params={
            "initial_accuracy": 0.5,
            "initial_scale": 10.0,
        },
    )
    config.add_loop_config(
        "ansatz_design",
        initial_params={
            "initial_quality": 0.5,
            "initial_surrogate_accuracy": 0.3,
            "search_strategy": "evolutionary",
        },
    )
    config.add_loop_config(
        "calibration_control",
        initial_params={
            "initial_model_accuracy": 0.5,
            "initial_gate_fidelity": 0.99,
            "hardware_modality": "superconducting",
        },
    )

    return config
