"""
Azure Quantum backend for multi-vendor quantum hardware access.

Provides access to:
    - IonQ (trapped ion)
    - Quantinuum (trapped ion)
    - Rigetti (superconducting)
    - PASQAL (neutral atom)
    - Microsoft Resource Estimator

Requires:
    pip install azure-quantum qsharp

Setup:
    1. Azure account with Quantum workspace
    2. Set environment variables:
       - AZURE_QUANTUM_SUBSCRIPTION_ID
       - AZURE_QUANTUM_RESOURCE_GROUP
       - AZURE_QUANTUM_WORKSPACE_NAME
       - AZURE_QUANTUM_LOCATION
    3. Or use Azure CLI: az login
"""

import os
import time
from typing import Any

from .base import BackendType, ExecutionResult, QuantumBackend

# Provider targets for Azure Quantum
AZURE_TARGETS = {
    # IonQ
    "ionq.simulator": "ionq.simulator",
    "ionq.qpu": "ionq.qpu",
    "ionq.qpu.aria-1": "ionq.qpu.aria-1",
    # Quantinuum
    "quantinuum.sim.h1-1sc": "quantinuum.sim.h1-1sc",
    "quantinuum.sim.h1-1e": "quantinuum.sim.h1-1e",
    "quantinuum.qpu.h1-1": "quantinuum.qpu.h1-1",
    "quantinuum.qpu.h2-1": "quantinuum.qpu.h2-1",
    # Rigetti
    "rigetti.sim.qvm": "rigetti.sim.qvm",
    "rigetti.qpu.ankaa-2": "rigetti.qpu.ankaa-2",
    # PASQAL
    "pasqal.sim.emu-tn": "pasqal.sim.emu-tn",
    # Microsoft
    "microsoft.estimator": "microsoft.estimator",
}


class AzureQuantumBackend(QuantumBackend):
    """
    Azure Quantum backend for multi-vendor quantum hardware.

    Supports IonQ, Quantinuum, Rigetti, PASQAL, and Microsoft targets.
    """

    def __init__(
        self,
        target: str = "ionq.simulator",
        subscription_id: str | None = None,
        resource_group: str | None = None,
        workspace_name: str | None = None,
        location: str | None = None,
    ):
        """
        Initialize Azure Quantum backend.

        Args:
            target: Target name (e.g., 'ionq.simulator', 'quantinuum.qpu.h1-1')
            subscription_id: Azure subscription ID (or set AZURE_QUANTUM_SUBSCRIPTION_ID)
            resource_group: Resource group name (or set AZURE_QUANTUM_RESOURCE_GROUP)
            workspace_name: Workspace name (or set AZURE_QUANTUM_WORKSPACE_NAME)
            location: Azure region (or set AZURE_QUANTUM_LOCATION)
        """
        backend_type = (
            BackendType.SIMULATOR
            if "sim" in target or "simulator" in target
            else BackendType.REAL_HARDWARE
        )

        super().__init__(f"azure_{target.replace('.', '_')}", backend_type)

        self.target = AZURE_TARGETS.get(target, target)
        self.subscription_id = subscription_id or os.environ.get("AZURE_QUANTUM_SUBSCRIPTION_ID")
        self.resource_group = resource_group or os.environ.get("AZURE_QUANTUM_RESOURCE_GROUP")
        self.workspace_name = workspace_name or os.environ.get("AZURE_QUANTUM_WORKSPACE_NAME")
        self.location = location or os.environ.get("AZURE_QUANTUM_LOCATION", "eastus")

        self._workspace = None
        self._backend = None

    def _initialize(self) -> None:
        """Lazy initialization of Azure Quantum workspace."""
        if self._workspace is not None:
            return

        try:
            from azure.quantum import Workspace
            from azure.quantum.qiskit import AzureQuantumProvider
        except ImportError as err:
            raise ImportError(
                "azure-quantum required. Install with: pip install azure-quantum qsharp"
            ) from err

        if not all([self.subscription_id, self.resource_group, self.workspace_name]):
            raise ValueError(
                "Azure Quantum credentials required. Set environment variables: "
                "AZURE_QUANTUM_SUBSCRIPTION_ID, AZURE_QUANTUM_RESOURCE_GROUP, "
                "AZURE_QUANTUM_WORKSPACE_NAME"
            )

        self._workspace = Workspace(
            subscription_id=self.subscription_id,
            resource_group=self.resource_group,
            name=self.workspace_name,
            location=self.location,
        )

        # Get Qiskit backend
        provider = AzureQuantumProvider(workspace=self._workspace)
        self._backend = provider.get_backend(self.target)

    def execute(self, circuit: Any, shots: int = 1024, **_kwargs: Any) -> ExecutionResult:
        """Execute circuit on Azure Quantum target."""
        self._initialize()

        assert self._backend is not None

        from qiskit import transpile

        start_time = time.time()

        # Transpile for target
        transpiled = transpile(circuit, self._backend)

        # Run job
        job = self._backend.run(transpiled, shots=shots)
        result = job.result()

        execution_time_ms = (time.time() - start_time) * 1000

        counts = result.get_counts()

        self._record_execution(shots, execution_time_ms)

        return ExecutionResult(
            counts=counts,
            shots=shots,
            backend_name=self.name,
            backend_type=self.backend_type,
            execution_time_ms=execution_time_ms,
            metadata={
                "job_id": job.job_id(),
                "target": self.target,
            },
        )

    def execute_batch(
        self, circuits: list[Any], shots: int = 1024, **kwargs: Any
    ) -> list[ExecutionResult]:
        """Execute multiple circuits."""
        return [self.execute(circuit, shots=shots, **kwargs) for circuit in circuits]

    @classmethod
    def list_targets(cls) -> dict[str, str]:
        """List available Azure Quantum targets."""
        return AZURE_TARGETS.copy()

    def get_cost_estimate(self, circuit: Any, shots: int = 1024) -> dict[str, Any]:
        """Estimate cost for running a circuit."""
        self._initialize()

        assert self._backend is not None

        try:
            # Some Azure targets support cost estimation
            estimate = self._backend.estimate_cost(circuit, shots=shots)
            return {
                "estimated_cost": estimate,
                "currency": "USD",
            }
        except Exception:
            return {"error": "Cost estimation not available for this target"}
