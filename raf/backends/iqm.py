"""
IQM Quantum backend for European quantum hardware access.

Requires:
    pip install iqm-client qiskit-iqm

Setup:
    1. IQM Resonance account at https://resonance.meetiqm.com
    2. Get API token from account settings
    3. Set environment variable: export IQM_TOKEN=your_token
       Or pass token directly to IQMBackend
"""

import os
import time
from typing import TYPE_CHECKING, Any

from .base import BackendType, ExecutionResult, QuantumBackend

# IQM server URLs
IQM_SERVERS = {
    "resonance": "https://cocos.resonance.meetiqm.com/garnet",
    "garnet": "https://cocos.resonance.meetiqm.com/garnet",
    "demo": "https://demo.qc.iqm.fi/cocos",
}


class IQMBackend(QuantumBackend):
    """
    IQM Quantum backend for European quantum hardware.

    Supports IQM Garnet and other IQM processors.
    """

    def __init__(
        self,
        server_url: str = "resonance",
        token: str | None = None,
    ):
        """
        Initialize IQM backend.

        Args:
            server_url: Server URL or name ('resonance', 'garnet', 'demo')
            token: IQM API token (or set IQM_TOKEN env var)
        """
        super().__init__(f"iqm_{server_url}", BackendType.REAL_HARDWARE)

        self.server_url = IQM_SERVERS.get(server_url, server_url)
        self.token = token or os.environ.get("IQM_TOKEN")

        self._backend = None

    def _initialize(self) -> None:
        """Lazy initialization of IQM backend."""
        if self._backend is not None:
            return

        if TYPE_CHECKING:
            from qiskit_iqm import IQMProvider
        else:
            try:
                from qiskit_iqm import IQMProvider
            except ImportError as err:
                raise ImportError(
                    "qiskit-iqm required. Install with: pip install qiskit-iqm"
                ) from err

        if not self.token:
            raise ValueError(
                "IQM token required. Set IQM_TOKEN environment variable "
                "or pass token to constructor."
            )

        provider = IQMProvider(self.server_url, token=self.token)
        self._backend = provider.get_backend()

    def execute(self, circuit: Any, shots: int = 1024, **_kwargs: Any) -> ExecutionResult:
        """Execute circuit on IQM hardware."""
        self._initialize()

        assert self._backend is not None

        from qiskit import transpile

        start_time = time.time()

        # Transpile for IQM backend
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
                "server": self.server_url,
            },
        )

    def execute_batch(
        self, circuits: list[Any], shots: int = 1024, **kwargs: Any
    ) -> list[ExecutionResult]:
        """Execute multiple circuits."""
        return [self.execute(circuit, shots=shots, **kwargs) for circuit in circuits]

    @classmethod
    def list_servers(cls) -> dict[str, str]:
        """List available IQM servers."""
        return IQM_SERVERS.copy()
