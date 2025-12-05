"""
RAF Quantum Backends Module.

Provides abstraction layer for quantum hardware and simulators,
enabling empirical validation of the Reciprocal Acceleration Framework.
"""

from .base import QuantumBackend, BackendType, ExecutionResult
from .aer import AerBackend, create_backend
from .noise_models import NoiseModelBuilder, DeviceNoiseProfile

__all__ = [
    "QuantumBackend",
    "BackendType",
    "ExecutionResult",
    "AerBackend",
    "create_backend",
    "NoiseModelBuilder",
    "DeviceNoiseProfile",
]

# Optional imports for real hardware
try:
    from .ibm import IBMQuantumBackend
    __all__.append("IBMQuantumBackend")
except ImportError:
    pass  # qiskit-ibm-runtime not installed
