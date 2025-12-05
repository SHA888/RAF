"""
Acceleration loop implementations for the Reciprocal Acceleration Framework.

This module provides concrete implementations of the three primary
acceleration loops identified in the RAF:

1. ErrorMitigationLoop - Operating at the output/application level
2. AnsatzDesignLoop - Operating at the algorithm/circuit level
3. CalibrationControlLoop - Operating at the hardware/physics level
"""

from raf.loops.error_mitigation import ErrorMitigationLoop
from raf.loops.ansatz_design import AnsatzDesignLoop
from raf.loops.calibration_control import CalibrationControlLoop

__all__ = [
    "ErrorMitigationLoop",
    "AnsatzDesignLoop",
    "CalibrationControlLoop",
]
