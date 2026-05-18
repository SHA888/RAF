"""
Pytest configuration and fixtures for RAF tests.

Provides modern pytest 8.0+ fixtures with proper setup/teardown,
parametrization helpers, and backend availability detection.
"""

from __future__ import annotations

from collections.abc import Generator
from enum import Enum
from typing import Any

import pytest

from raf.core.framework import ReciprocalAccelerationFramework
from raf.core.loop import AccelerationLoop
from raf.loops import AnsatzDesignLoop, CalibrationControlLoop, ErrorMitigationLoop


class LoopType(Enum):
    """Enumeration of RAF loop types for parametrization."""

    ERROR_MITIGATION = "error_mitigation"
    ANSATZ_DESIGN = "ansatz_design"
    CALIBRATION_CONTROL = "calibration_control"


class BackendType(Enum):
    """Enumeration of available quantum backends."""

    IDEAL = "ideal"
    MANILA = "manila"
    HARMONY = "harmony"
    ARIA = "aria"


# ============================================================================
# Core Framework Fixtures
# ============================================================================


@pytest.fixture
def raf_framework() -> Generator[ReciprocalAccelerationFramework, None, None]:
    """
    Create a fresh RAF framework instance with proper setup/teardown.

    Provides a clean framework for each test with default couplings.
    Automatically cleans up after the test completes.

    Yields:
        ReciprocalAccelerationFramework: A fresh framework instance
    """
    framework = ReciprocalAccelerationFramework()
    yield framework
    # Cleanup: no explicit teardown needed, but could add cleanup logic here
    # if framework gains state that needs explicit cleanup


@pytest.fixture
def raf_framework_with_loops(
    raf_framework: ReciprocalAccelerationFramework,
) -> Generator[ReciprocalAccelerationFramework, None, None]:
    """
    Create a RAF framework with all three loops pre-added.

    Provides a fully configured framework ready for integration testing.

    Yields:
        ReciprocalAccelerationFramework: Framework with ErrorMitigation,
                                        AnsatzDesign, and CalibrationControl loops
    """
    framework = raf_framework
    framework.add_loop(ErrorMitigationLoop())
    framework.add_loop(AnsatzDesignLoop())
    framework.add_loop(CalibrationControlLoop())
    yield framework


# ============================================================================
# Loop Fixtures & Parametrization
# ============================================================================


@pytest.fixture(params=list(LoopType), ids=[lt.value for lt in LoopType])
def loop_type(request: pytest.FixtureRequest) -> LoopType:
    """
    Parametrize tests over all loop types.

    Provides one test run per loop type with descriptive IDs.
    Example: test_loop_creation[error_mitigation]

    Args:
        request: Pytest request object (automatic)

    Returns:
        LoopType: The current loop type for this test run
    """
    return request.param  # type: ignore[no-any-return]


@pytest.fixture
def loop_instance(
    loop_type: LoopType,
) -> AccelerationLoop:
    """
    Create a loop instance based on the current loop_type fixture.

    Depends on loop_type parametrization, so automatically creates
    different loop types across parametrized tests.

    Args:
        loop_type: The current loop type from parametrization

    Returns:
        AccelerationLoop: A fresh instance of the requested loop type
    """
    loop_map: dict[LoopType, type[Any]] = {
        LoopType.ERROR_MITIGATION: ErrorMitigationLoop,
        LoopType.ANSATZ_DESIGN: AnsatzDesignLoop,
        LoopType.CALIBRATION_CONTROL: CalibrationControlLoop,
    }
    loop_class: type[Any] = loop_map[loop_type]
    return loop_class()  # type: ignore[no-any-return]


# ============================================================================
# Backend Fixtures
# ============================================================================


def _get_available_backends() -> list[BackendType]:
    """
    Detect which backends are available in the current environment.

    Returns:
        list[BackendType]: List of available backends
    """
    available = []

    # Aer backend (required for ideal and Manila-like noise)
    try:
        import qiskit_aer  # noqa: F401

        available.extend([BackendType.IDEAL, BackendType.MANILA])
    except ImportError:
        pass

    # Additional profiles (require Aer)
    if BackendType.IDEAL in available:
        available.extend([BackendType.HARMONY, BackendType.ARIA])

    return available


@pytest.fixture
def available_backends() -> list[BackendType]:
    """
    Get list of available quantum backends in the test environment.

    Returns:
        list[BackendType]: Backends that are available and can be tested
    """
    return _get_available_backends()


_available_backends_cache = _get_available_backends()


@pytest.fixture(
    params=_available_backends_cache,
    ids=[bt.value for bt in _available_backends_cache],
)
def backend_type(request: pytest.FixtureRequest) -> BackendType:
    """
    Parametrize tests over available backends.

    Only includes backends that are actually available in the test environment.
    Automatically skips tests for unavailable backends.
    Example: test_backend_execution[ideal]

    Args:
        request: Pytest request object (automatic)

    Returns:
        BackendType: The current backend type for this test run
    """
    return request.param  # type: ignore[no-any-return]


@pytest.fixture
def backend_name(backend_type: BackendType) -> str:
    """
    Get the backend name string from the current backend_type fixture.

    Provides the string name that can be passed to create_backend().

    Args:
        backend_type: The current backend type from parametrization

    Returns:
        str: The backend name string (e.g., "ideal", "manila")
    """
    return backend_type.value


# ============================================================================
# Seeding & Reproducibility Fixtures
# ============================================================================


@pytest.fixture(scope="function")
def seeded_environment() -> Generator[int, None, None]:
    """
    Set up deterministic random number generation for reproducible tests.

    Yields:
        int: The seed value (42) used for all RNG
    """
    from raf.utils import set_all_seeds

    seed = 42
    set_all_seeds(seed)
    yield seed


# ============================================================================
# Parametrization Helpers
# ============================================================================


def pytest_configure(config: pytest.Config) -> None:
    """
    Register custom pytest markers.

    Args:
        config: Pytest configuration object
    """
    config.addinivalue_line(
        "markers",
        "integration: mark test as an integration test (requires backends)",
    )
    config.addinivalue_line(
        "markers",
        "backend_required: mark test as requiring quantum backend",
    )
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow (may take >1 second)",
    )


# ============================================================================
# Pytest Hooks
# ============================================================================


def pytest_collection_modifyitems(
    config: pytest.Config,  # noqa: ARG001
    items: list[pytest.Item],
) -> None:
    """
    Auto-mark tests based on naming conventions.

    Automatically applies markers to tests based on their module or
    function names, reducing boilerplate in test code.

    Args:
        config: Pytest configuration object (unused but required by hook)
        items: List of test items collected
    """
    for item in items:
        # Mark backend tests
        if "backend" in item.nodeid.lower() and item.get_closest_marker("backend_required") is None:
            item.add_marker(pytest.mark.backend_required)

        # Mark integration tests
        if "integration" in item.nodeid.lower() and item.get_closest_marker("integration") is None:
            item.add_marker(pytest.mark.integration)

        # Mark slow tests
        if (
            any(slow_test in item.nodeid for slow_test in ["full_validation", "multi_vendor"])
            and item.get_closest_marker("slow") is None
        ):
            item.add_marker(pytest.mark.slow)
