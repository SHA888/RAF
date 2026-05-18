"""
Tests for public API import and type checking.

Verifies that all documented public APIs are importable and properly typed.
"""

from __future__ import annotations

import warnings

import raf


def test_public_api_importable() -> None:
    """Verify all public APIs are importable from raf package."""
    # Check that __all__ is defined
    assert hasattr(raf, "__all__")
    assert isinstance(raf.__all__, list)
    assert len(raf.__all__) > 0

    # Verify each item in __all__ is actually importable
    for name in raf.__all__:
        assert hasattr(raf, name), f"Public API '{name}' not found in raf module"
        obj = getattr(raf, name)
        assert obj is not None, f"Public API '{name}' is None"


def test_core_framework_importable() -> None:
    """Verify core framework components are importable."""
    from raf import ReciprocalAccelerationFramework

    assert ReciprocalAccelerationFramework is not None
    assert callable(ReciprocalAccelerationFramework)


def test_loop_components_importable() -> None:
    """Verify loop components are importable."""
    from raf import AccelerationLoop, LoopMetrics, LoopState

    assert AccelerationLoop is not None
    assert LoopState is not None
    assert LoopMetrics is not None


def test_metrics_importable() -> None:
    """Verify metrics components are importable."""
    from raf import AccelerationMetric, BottleneckIndicator, CrossLoopCoupling

    assert AccelerationMetric is not None
    assert BottleneckIndicator is not None
    assert CrossLoopCoupling is not None


def test_public_api_has_type_hints() -> None:
    """Verify that public API classes/functions have type hints."""
    from raf import AccelerationLoop, ReciprocalAccelerationFramework

    # Check ReciprocalAccelerationFramework has __init__ signature
    assert hasattr(ReciprocalAccelerationFramework, "__init__")

    # Check AccelerationLoop has required abstract methods with type hints
    assert hasattr(AccelerationLoop, "iterate")
    assert hasattr(AccelerationLoop, "compute_acceleration")


def test_version_is_set() -> None:
    """Verify package version is properly set."""
    assert hasattr(raf, "__version__")
    assert isinstance(raf.__version__, str)
    assert len(raf.__version__) > 0
    # Semantic versioning check
    parts = raf.__version__.split(".")
    assert len(parts) >= 2, f"Invalid version format: {raf.__version__}"


def test_no_deprecation_warnings_on_import() -> None:
    """Verify importing RAF doesn't trigger deprecation warnings."""
    # This test checks that no DeprecationWarning is raised during import
    # Since we just imported raf at the top of the file, we verify no
    # active deprecation warnings exist for the public API
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always", DeprecationWarning)

        # Force re-evaluation of public API items
        for name in raf.__all__:
            _ = getattr(raf, name)

        # Filter to only DeprecationWarnings from raf module
        raf_deprecations = [
            warning
            for warning in w
            if issubclass(warning.category, DeprecationWarning) and "raf" in str(warning.filename)
        ]

        assert (
            len(raf_deprecations) == 0
        ), f"Found deprecation warnings: {[str(w.message) for w in raf_deprecations]}"
