"""Tests for configuration management utilities."""

import json
import tempfile
from pathlib import Path
from typing import Any

from raf.utils.config import LoopConfig, RAFConfig, get_default_config, load_config, save_config


class TestLoopConfig:
    """Tests for LoopConfig dataclass."""

    def test_loop_config_creation(self) -> None:
        """Test basic LoopConfig creation."""
        config = LoopConfig(name="test_loop")
        assert config.name == "test_loop"
        assert config.enabled is True
        assert config.initial_params == {}

    def test_loop_config_with_params(self) -> None:
        """Test LoopConfig with initial parameters."""
        params = {"param1": 0.5, "param2": 10}
        config = LoopConfig(name="test_loop", initial_params=params)
        assert config.initial_params == params

    def test_loop_config_disabled(self) -> None:
        """Test LoopConfig with disabled flag."""
        config = LoopConfig(name="test_loop", enabled=False)
        assert config.enabled is False


class TestRAFConfig:
    """Tests for RAFConfig dataclass."""

    def test_raf_config_creation(self) -> None:
        """Test basic RAFConfig creation."""
        config = RAFConfig()
        assert config.name == "RAF"
        assert config.loops == {}
        assert config.couplings == []
        assert isinstance(config.analysis_settings, dict)
        assert isinstance(config.visualization_settings, dict)

    def test_raf_config_custom_name(self) -> None:
        """Test RAFConfig with custom name."""
        config = RAFConfig(name="CustomRAF")
        assert config.name == "CustomRAF"

    def test_add_loop_config(self) -> None:
        """Test adding loop configuration."""
        config = RAFConfig()
        config.add_loop_config("test_loop", initial_params={"param1": 0.5})

        assert "test_loop" in config.loops
        assert config.loops["test_loop"].name == "test_loop"
        assert config.loops["test_loop"].initial_params == {"param1": 0.5}

    def test_get_loop_config(self) -> None:
        """Test retrieving loop configuration."""
        config = RAFConfig()
        config.add_loop_config("test_loop")

        loop_config = config.get_loop_config("test_loop")
        assert loop_config is not None
        assert loop_config.name == "test_loop"

    def test_get_nonexistent_loop_config(self) -> None:
        """Test retrieving nonexistent loop configuration."""
        config = RAFConfig()
        loop_config = config.get_loop_config("nonexistent")
        assert loop_config is None

    def test_to_dict(self) -> None:
        """Test converting RAFConfig to dictionary."""
        config = RAFConfig(name="TestRAF")
        config.add_loop_config("loop1", initial_params={"param": 1})
        config.couplings = [{"from": "loop1", "to": "loop2", "strength": 0.5}]

        config_dict = config.to_dict()
        assert config_dict["name"] == "TestRAF"
        assert "loop1" in config_dict["loops"]
        assert len(config_dict["couplings"]) == 1

    def test_from_dict(self) -> None:
        """Test creating RAFConfig from dictionary."""
        data = {
            "name": "TestRAF",
            "loops": {"loop1": {"name": "loop1", "enabled": True, "initial_params": {"param": 1}}},
            "couplings": [{"from": "loop1", "to": "loop2"}],
            "analysis_settings": {"threshold": 0.7},
            "visualization_settings": {"figsize": [12, 8]},
        }

        config = RAFConfig.from_dict(data)
        assert config.name == "TestRAF"
        assert "loop1" in config.loops
        assert config.loops["loop1"].initial_params == {"param": 1}
        assert len(config.couplings) == 1
        assert config.analysis_settings["threshold"] == 0.7

    def test_from_dict_with_defaults(self) -> None:
        """Test from_dict with minimal data uses defaults."""
        data: dict[str, Any] = {}
        config = RAFConfig.from_dict(data)
        assert config.name == "RAF"
        assert config.loops == {}
        assert config.couplings == []

    def test_round_trip_conversion(self) -> None:
        """Test converting to/from dict preserves data."""
        original = RAFConfig(name="TestRAF")
        original.add_loop_config("loop1", initial_params={"x": 0.5})
        original.couplings = [{"strength": 0.3}]

        config_dict = original.to_dict()
        restored = RAFConfig.from_dict(config_dict)

        assert restored.name == original.name
        assert restored.loops.keys() == original.loops.keys()
        assert restored.couplings == original.couplings


class TestConfigPersistence:
    """Tests for loading and saving configuration."""

    def test_save_and_load_config(self) -> None:
        """Test saving and loading configuration file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"

            # Create and save config
            config = RAFConfig(name="TestRAF")
            config.add_loop_config("loop1", initial_params={"param": 0.5})
            save_config(config, str(config_path))

            assert config_path.exists()

            # Load and verify
            loaded = load_config(str(config_path))
            assert loaded.name == "TestRAF"
            assert "loop1" in loaded.loops
            assert loaded.loops["loop1"].initial_params == {"param": 0.5}

    def test_save_config_creates_directories(self) -> None:
        """Test that save_config creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "subdir" / "nested" / "config.json"

            config = RAFConfig()
            save_config(config, str(config_path))

            assert config_path.exists()
            assert config_path.parent.exists()

    def test_load_config_file_format(self) -> None:
        """Test that saved config file has correct JSON format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"

            config = RAFConfig(name="TestRAF")
            config.add_loop_config("loop1")
            save_config(config, str(config_path))

            # Verify JSON format
            with open(config_path) as f:
                data = json.load(f)

            assert isinstance(data, dict)
            assert data["name"] == "TestRAF"
            assert "loop1" in data["loops"]


class TestDefaultConfig:
    """Tests for default configuration."""

    def test_default_config_creation(self) -> None:
        """Test that default config is created properly."""
        config = get_default_config()

        assert config.name == "RAF"
        assert len(config.loops) == 3
        assert "error_mitigation" in config.loops
        assert "ansatz_design" in config.loops
        assert "calibration_control" in config.loops

    def test_default_loop_params(self) -> None:
        """Test that default loops have expected parameters."""
        config = get_default_config()

        em_config = config.get_loop_config("error_mitigation")
        assert em_config is not None
        assert "initial_accuracy" in em_config.initial_params
        assert em_config.initial_params["initial_accuracy"] == 0.5
        assert em_config.initial_params["initial_scale"] == 10.0

    def test_default_analysis_settings(self) -> None:
        """Test default analysis settings."""
        config = get_default_config()

        assert "bottleneck_threshold" in config.analysis_settings
        assert config.analysis_settings["bottleneck_threshold"] == 0.5
        assert "acceleration_window" in config.analysis_settings
        assert "prediction_iterations" in config.analysis_settings

    def test_default_visualization_settings(self) -> None:
        """Test default visualization settings."""
        config = get_default_config()

        assert "figsize" in config.visualization_settings
        assert config.visualization_settings["figsize"] == [10, 6]
        assert "style" in config.visualization_settings
        assert "save_format" in config.visualization_settings
