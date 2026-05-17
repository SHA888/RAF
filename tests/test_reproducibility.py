"""Tests for reproducibility utilities."""

import json
import random
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from raf.utils.reproducibility import persist_run_config, set_all_seeds


class TestSetAllSeeds:
    """Tests for set_all_seeds function."""

    def test_set_all_seeds_returns_qiskit_kwargs(self) -> None:
        """Test that set_all_seeds returns Qiskit seed parameters."""
        qiskit_kwargs = set_all_seeds(42)

        assert isinstance(qiskit_kwargs, dict)
        assert "seed_simulator" in qiskit_kwargs
        assert "seed_transpiler" in qiskit_kwargs
        assert qiskit_kwargs["seed_simulator"] == 42
        assert qiskit_kwargs["seed_transpiler"] == 42

    def test_set_all_seeds_reproducibility_random(self) -> None:
        """Test that setting the same seed produces same random values."""
        set_all_seeds(42)
        val1 = random.random()

        set_all_seeds(42)
        val2 = random.random()

        assert val1 == val2

    def test_set_all_seeds_reproducibility_numpy(self) -> None:
        """Test that setting the same seed produces same numpy values."""
        set_all_seeds(42)
        arr1 = np.random.randn(5)

        set_all_seeds(42)
        arr2 = np.random.randn(5)

        np.testing.assert_array_equal(arr1, arr2)

    def test_set_all_seeds_different_seeds(self) -> None:
        """Test that different seeds produce different values."""
        set_all_seeds(42)
        val1 = random.random()

        set_all_seeds(43)
        val2 = random.random()

        assert val1 != val2

    def test_set_all_seeds_with_deterministic_torch_false(self) -> None:
        """Test set_all_seeds with deterministic_torch=False."""
        qiskit_kwargs = set_all_seeds(42, deterministic_torch=False)
        assert qiskit_kwargs["seed_simulator"] == 42

    def test_set_all_seeds_with_deterministic_torch_true(self) -> None:
        """Test set_all_seeds with deterministic_torch=True."""
        qiskit_kwargs = set_all_seeds(42, deterministic_torch=True)
        assert qiskit_kwargs["seed_simulator"] == 42

    def test_set_all_seeds_zero_seed(self) -> None:
        """Test that zero is a valid seed value."""
        qiskit_kwargs = set_all_seeds(0)
        assert qiskit_kwargs["seed_simulator"] == 0

    def test_set_all_seeds_large_seed(self) -> None:
        """Test that large seed values work."""
        qiskit_kwargs = set_all_seeds(2**31 - 1)
        assert qiskit_kwargs["seed_simulator"] == 2**31 - 1

    def test_set_all_seeds_with_torch_available(self) -> None:
        """Test set_all_seeds when torch is available."""
        from unittest.mock import MagicMock, patch

        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        with patch.dict("sys.modules", {"torch": mock_torch}):
            qiskit_kwargs = set_all_seeds(42, deterministic_torch=False)
            assert qiskit_kwargs["seed_simulator"] == 42
            mock_torch.manual_seed.assert_called_once_with(42)

    def test_set_all_seeds_with_torch_cuda_available(self) -> None:
        """Test set_all_seeds when torch with CUDA is available."""
        from unittest.mock import MagicMock, patch

        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True
        with patch.dict("sys.modules", {"torch": mock_torch}):
            qiskit_kwargs = set_all_seeds(99, deterministic_torch=False)
            assert qiskit_kwargs["seed_simulator"] == 99
            mock_torch.manual_seed.assert_called_once_with(99)
            mock_torch.cuda.manual_seed_all.assert_called_once_with(99)

    def test_set_all_seeds_with_torch_deterministic(self) -> None:
        """Test set_all_seeds with deterministic_torch=True."""
        from unittest.mock import MagicMock, patch

        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        with patch.dict("sys.modules", {"torch": mock_torch}):
            qiskit_kwargs = set_all_seeds(42, deterministic_torch=True)
            assert qiskit_kwargs["seed_simulator"] == 42
            mock_torch.use_deterministic_algorithms.assert_called_once_with(True, warn_only=True)


class TestPersistRunConfig:
    """Tests for persist_run_config function."""

    def test_persist_run_config_basic(self) -> None:
        """Test basic config persistence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "run_config.json"
            config = {"seed": 42, "learning_rate": 0.001, "num_iterations": 100}

            result = persist_run_config(config, str(config_path))

            assert Path(result).exists()
            with open(result) as f:
                saved_config = json.load(f)
            assert saved_config == config

    def test_persist_run_config_creates_directories(self) -> None:
        """Test that persist_run_config creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "nested" / "deep" / "config.json"
            config = {"seed": 42}

            persist_run_config(config, str(config_path), mkdir=True)

            assert config_path.exists()

    def test_persist_run_config_no_mkdir(self) -> None:
        """Test persist_run_config with mkdir=False on existing directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config = {"seed": 42}

            persist_run_config(config, str(config_path), mkdir=False)

            assert config_path.exists()

    def test_persist_run_config_no_mkdir_fails_missing_directory(self) -> None:
        """Test persist_run_config with mkdir=False on missing directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "missing" / "config.json"
            config = {"seed": 42}

            with pytest.raises(FileNotFoundError):
                persist_run_config(config, str(config_path), mkdir=False)

    def test_persist_run_config_complex_structure(self) -> None:
        """Test persisting complex nested config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config: dict[str, Any] = {
                "seed": 42,
                "hyperparameters": {"lr": 0.001, "momentum": 0.9},
                "loops": ["error_mitigation", "ansatz_design"],
                "nested": {"deep": {"structure": [1, 2, 3]}},
            }

            persist_run_config(config, str(config_path))

            with open(config_path) as f:
                saved_config = json.load(f)
            assert saved_config == config

    def test_persist_run_config_returns_path(self) -> None:
        """Test that persist_run_config returns the path as string."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config = {"seed": 42}

            result = persist_run_config(config, str(config_path))

            assert isinstance(result, str)
            assert result == str(config_path)

    def test_persist_run_config_json_format(self) -> None:
        """Test that saved config is valid JSON with proper formatting."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config = {"seed": 42, "param": "value"}

            persist_run_config(config, str(config_path))

            with open(config_path) as f:
                content = f.read()

            # Should be valid JSON with indentation
            assert json.loads(content) == config
            assert "  " in content  # Should have indentation
