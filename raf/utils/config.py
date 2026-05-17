"""
Configuration management for the Reciprocal Acceleration Framework.
"""

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class LoopConfig:
    """Configuration for an acceleration loop."""

    name: str
    enabled: bool = True
    initial_params: dict[str, Any] = field(default_factory=dict)


@dataclass
class RAFConfig:
    """
    Configuration for the Reciprocal Acceleration Framework.

    Attributes:
        name: Framework instance name
        loops: Configuration for each loop
        couplings: Custom coupling definitions
        analysis_settings: Settings for analysis tools
        visualization_settings: Settings for visualization
    """

    name: str = "RAF"
    loops: dict[str, LoopConfig] = field(default_factory=dict)
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

        return cls(
            name=data.get("name", "RAF"),
            loops=loops,
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
