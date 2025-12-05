"""
Core components of the Reciprocal Acceleration Framework.
"""

from raf.core.framework import ReciprocalAccelerationFramework
from raf.core.loop import AccelerationLoop, LoopState, LoopMetrics
from raf.core.metrics import (
    AccelerationMetric,
    BottleneckIndicator,
    CrossLoopCoupling,
)

__all__ = [
    "ReciprocalAccelerationFramework",
    "AccelerationLoop",
    "LoopState",
    "LoopMetrics",
    "AccelerationMetric",
    "BottleneckIndicator",
    "CrossLoopCoupling",
]
