"""Common type aliases and advanced typing patterns for RAF.

This module centralises frequently‑used type aliases to keep the codebase tidy and
makes it easier to update them in a single place.
"""

from __future__ import annotations

from typing import TypedDict

from .core.metrics import AccelerationMetric, BottleneckIndicator

# Simple alias for the mapping of loop names to their metrics.
type LoopMetrics = dict[str, AccelerationMetric]

# Mapping of loop names to a list of bottleneck indicators.
type BottleneckMap = dict[str, list[BottleneckIndicator]]


# Example TypedDict for configuration structures – can be extended as needed.
class ConfigDict(TypedDict, total=False):
    """Base TypedDict for configuration dictionaries.

    Specific configuration sections can inherit from this to gain type‑checking
    for known keys while still allowing extra keys when ``total=False``.
    """

    # Example placeholder keys – real keys should be added by the consuming
    # modules (e.g., ``raf.utils.config``) as they become concrete.
    example_key: str
