"""
RAF Quantum Backends Module.

Provides abstraction layer for quantum hardware and simulators,
enabling empirical validation of the Reciprocal Acceleration Framework.

Supported backends:
    - AerBackend: Qiskit Aer local simulator (always available)
    - IBMQuantumBackend: IBM Quantum hardware (requires qiskit-ibm-runtime)
    - BraketBackend: AWS Braket - IonQ, Rigetti, OQC, QuEra (requires amazon-braket-sdk)
    - AzureQuantumBackend: Azure Quantum - IonQ, Quantinuum, Rigetti (requires azure-quantum)
    - IQMBackend: IQM European hardware (requires qiskit-iqm)
"""

from typing import Any

from .aer import AerBackend, create_backend
from .base import BackendType, ExecutionResult, QuantumBackend
from .noise_models import (
    DeviceNoiseProfile,
    DriftConfig,
    DriftingNoiseModel,
    DriftType,
    NoiseModelBuilder,
)

__all__ = [
    "QuantumBackend",
    "BackendType",
    "ExecutionResult",
    "AerBackend",
    "create_backend",
    "NoiseModelBuilder",
    "DeviceNoiseProfile",
    "DriftingNoiseModel",
    "DriftConfig",
    "DriftType",
]

# Optional imports for real hardware vendors

# IBM Quantum
try:
    from .ibm import IBMQuantumBackend  # noqa: F401

    __all__.append("IBMQuantumBackend")
except ImportError:
    pass  # qiskit-ibm-runtime not installed

# AWS Braket (IonQ, Rigetti, OQC, QuEra)
try:
    from .braket import BRAKET_DEVICES, BraketBackend  # noqa: F401

    __all__.extend(["BraketBackend", "BRAKET_DEVICES"])
except ImportError:
    pass  # amazon-braket-sdk not installed

# Azure Quantum (IonQ, Quantinuum, Rigetti, PASQAL)
try:
    from .azure import AZURE_TARGETS, AzureQuantumBackend  # noqa: F401

    __all__.extend(["AzureQuantumBackend", "AZURE_TARGETS"])
except ImportError:
    pass  # azure-quantum not installed

# IQM (European)
try:
    from .iqm import IQM_SERVERS, IQMBackend  # noqa: F401

    __all__.extend(["IQMBackend", "IQM_SERVERS"])
except ImportError:
    pass  # qiskit-iqm not installed

# PennyLane (gradient-based optimization)
try:
    from .pennylane import (  # noqa: F401
        PENNYLANE_DEVICES,
        PennyLaneBackend,
        create_pennylane_backend,
    )

    __all__.extend(["PennyLaneBackend", "create_pennylane_backend", "PENNYLANE_DEVICES"])
except ImportError:
    pass  # pennylane not installed


def list_available_backends() -> dict[str, Any]:
    """
    List all available backends and their status.

    Returns:
        Dictionary with backend availability information
    """
    backends = {
        "aer": {"available": True, "description": "Qiskit Aer local simulator"},
        "ibm": {"available": False, "description": "IBM Quantum hardware"},
        "braket": {"available": False, "description": "AWS Braket (IonQ, Rigetti, OQC, QuEra)"},
        "azure": {"available": False, "description": "Azure Quantum (IonQ, Quantinuum, Rigetti)"},
        "iqm": {"available": False, "description": "IQM European hardware"},
        "pennylane": {
            "available": False,
            "description": "PennyLane (gradient-based optimization)",
        },
    }

    if "IBMQuantumBackend" in __all__:
        backends["ibm"]["available"] = True
    if "BraketBackend" in __all__:
        backends["braket"]["available"] = True
    if "AzureQuantumBackend" in __all__:
        backends["azure"]["available"] = True
    if "IQMBackend" in __all__:
        backends["iqm"]["available"] = True
    if "PennyLaneBackend" in __all__:
        backends["pennylane"]["available"] = True

    return backends
