"""
Reciprocal Acceleration Framework (RAF)

A systematic framework for understanding and accelerating co-evolutionary
dynamics between Quantum Computing (QC) and Machine Learning (ML).

The framework identifies three primary acceleration loops:
1. Error Mitigation Loop - Operating at the output/application level
2. Ansatz Design Loop - Operating at the algorithm/circuit level
3. Calibration-Control Loop - Operating at the hardware/physics level
"""

from raf.core.framework import ReciprocalAccelerationFramework
from raf.core.loop import AccelerationLoop, LoopState, LoopMetrics
from raf.core.metrics import (
    AccelerationMetric,
    BottleneckIndicator,
    CrossLoopCoupling,
)

__version__ = "0.1.0"
__author__ = "RAF Contributors"

__all__ = [
    # Core framework
    "ReciprocalAccelerationFramework",
    # Loop components
    "AccelerationLoop",
    "LoopState",
    "LoopMetrics",
    # Metrics
    "AccelerationMetric",
    "BottleneckIndicator",
    "CrossLoopCoupling",
]
