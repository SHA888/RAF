"""
Reproducibility helpers for RAF experiments.

Provides utilities to set seeds across common RNGs and to persist run
configuration for replayability.
"""

import json
import random
from pathlib import Path
from typing import Any, Dict

import numpy as np


def set_all_seeds(seed: int, *, deterministic_torch: bool = False) -> Dict[str, Any]:
    """
    Set seeds across Python, NumPy, (optional) PyTorch, and Qiskit defaults.

    Args:
        seed: Seed value to apply.
        deterministic_torch: If True and torch is available, enable deterministic
            algorithms where supported.

    Returns:
        Dict of seed parameters usable for Qiskit transpile/run calls.
    """
    random.seed(seed)
    np.random.seed(seed)

    # Optional torch seeding
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        if deterministic_torch:
            torch.use_deterministic_algorithms(True, warn_only=True)
    except ImportError:
        pass

    # Qiskit seed parameters (consumer must apply)
    qiskit_kwargs = {"seed_simulator": seed, "seed_transpiler": seed}
    return qiskit_kwargs


def persist_run_config(config: Dict[str, Any], path: str, *, mkdir: bool = True) -> str:
    """
    Persist a run configuration (including seed + params) for replayability.

    Args:
        config: Serializable configuration dictionary.
        path: Destination file path (JSON).
        mkdir: If True, create parent directories as needed.

    Returns:
        The path written.
    """
    target = Path(path)
    if mkdir:
        target.parent.mkdir(parents=True, exist_ok=True)

    with target.open("w") as f:
        json.dump(config, f, indent=2)

    return str(target)
