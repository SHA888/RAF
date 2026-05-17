"""
IBM Quantum backend for real hardware execution.

Requires:
    pip install qiskit-ibm-runtime

Setup:
    1. Create IBM Quantum account at https://quantum.ibm.com
    2. Get API token from account settings
    3. Set environment variable: export IBM_QUANTUM_TOKEN=your_token
       Or pass token directly to IBMQuantumBackend
"""

import os
import time
from typing import Any, List, Optional

from .base import BackendType, ExecutionResult, QuantumBackend


class IBMQuantumBackend(QuantumBackend):
    """
    IBM Quantum hardware backend using qiskit-ibm-runtime.

    Supports execution on real IBM Quantum processors.
    """

    def __init__(
        self,
        backend_name: str = "ibm_brisbane",
        token: Optional[str] = None,
        channel: str = "ibm_quantum",
        instance: str = "ibm-q/open/main",
    ):
        """
        Initialize IBM Quantum backend.

        Args:
            backend_name: Name of IBM backend (e.g., 'ibm_brisbane', 'ibm_kyoto')
            token: IBM Quantum API token (or set IBM_QUANTUM_TOKEN env var)
            channel: Service channel ('ibm_quantum' or 'ibm_cloud')
            instance: Instance for ibm_quantum channel
        """
        super().__init__(f"ibm_{backend_name}", BackendType.REAL_HARDWARE)

        self.backend_name = backend_name
        self.token = token or os.environ.get("IBM_QUANTUM_TOKEN")
        self.channel = channel
        self.instance = instance

        self._service: Any = None
        self._backend: Any = None

    def _initialize(self) -> None:
        """Lazy initialization of IBM Quantum service."""
        if self._service is not None:
            return

        try:
            from qiskit_ibm_runtime import QiskitRuntimeService
        except ImportError:
            raise ImportError(
                "qiskit-ibm-runtime required. Install with: pip install qiskit-ibm-runtime"
            )

        if not self.token:
            raise ValueError(
                "IBM Quantum token required. Set IBM_QUANTUM_TOKEN environment variable "
                "or pass token to constructor."
            )

        self._service = QiskitRuntimeService(
            channel=self.channel,
            token=self.token,
            instance=self.instance if self.channel == "ibm_quantum" else None,
        )
        self._backend = self._service.backend(self.backend_name)

    def execute(self, circuit: Any, shots: int = 1024, **kwargs: Any) -> ExecutionResult:
        """Execute circuit on IBM Quantum hardware."""
        self._initialize()

        from qiskit import transpile
        from qiskit_ibm_runtime import SamplerV2 as Sampler

        start_time = time.time()

        # Transpile for target backend
        transpiled = transpile(circuit, self._backend)

        # Run using Sampler primitive
        sampler = Sampler(self._backend)
        job = sampler.run([transpiled], shots=shots)
        result = job.result()

        execution_time_ms = (time.time() - start_time) * 1000

        # Extract counts from result
        pub_result = result[0]
        counts = pub_result.data.meas.get_counts()

        self._record_execution(shots, execution_time_ms)

        return ExecutionResult(
            counts=counts,
            shots=shots,
            backend_name=self.name,
            backend_type=self.backend_type,
            execution_time_ms=execution_time_ms,
            metadata={
                "job_id": job.job_id(),
                "backend": self.backend_name,
            },
        )

    def execute_batch(
        self, circuits: List[Any], shots: int = 1024, **kwargs: Any
    ) -> List[ExecutionResult]:
        """Execute multiple circuits in a batch."""
        self._initialize()

        from qiskit import transpile
        from qiskit_ibm_runtime import SamplerV2 as Sampler

        start_time = time.time()

        # Transpile all circuits
        transpiled = transpile(circuits, self._backend)

        # Run batch
        sampler = Sampler(self._backend)
        job = sampler.run(transpiled, shots=shots)
        result = job.result()

        total_time_ms = (time.time() - start_time) * 1000
        time_per_circuit = total_time_ms / len(circuits)

        results = []
        for i, pub_result in enumerate(result):
            counts = pub_result.data.meas.get_counts()

            results.append(
                ExecutionResult(
                    counts=counts,
                    shots=shots,
                    backend_name=self.name,
                    backend_type=self.backend_type,
                    execution_time_ms=time_per_circuit,
                    metadata={
                        "job_id": job.job_id(),
                        "circuit_index": i,
                    },
                )
            )
            self._record_execution(shots, time_per_circuit)

        return results

    @classmethod
    def list_backends(cls, token: Optional[str] = None) -> List[str]:
        """List available IBM Quantum backends."""
        try:
            from qiskit_ibm_runtime import QiskitRuntimeService
        except ImportError:
            return []

        token = token or os.environ.get("IBM_QUANTUM_TOKEN")
        if not token:
            return []

        try:
            service = QiskitRuntimeService(channel="ibm_quantum", token=token)
            return [b.name for b in service.backends()]
        except Exception:
            return []
