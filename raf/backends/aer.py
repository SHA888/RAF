"""
Qiskit Aer backend for noisy quantum simulation.
"""

import time
from typing import TYPE_CHECKING, Any, List, Optional

from .base import BackendType, ExecutionResult, QuantumBackend
from .noise_models import DeviceNoiseProfile, NoiseModelBuilder


class AerBackend(QuantumBackend):
    """
    Qiskit Aer simulator backend with optional noise modeling.

    Supports:
    - Ideal statevector simulation
    - Shot-based sampling (qasm_simulator)
    - Noisy simulation with device-calibrated noise models
    """

    def __init__(
        self,
        noise_profile: Optional[DeviceNoiseProfile] = None,
        use_gpu: bool = False,
    ):
        """
        Initialize Aer backend.

        Args:
            noise_profile: Optional noise profile for noisy simulation
            use_gpu: Whether to use GPU acceleration (requires qiskit-aer-gpu)
        """
        backend_type = BackendType.NOISY_SIMULATOR if noise_profile else BackendType.SIMULATOR

        name = "aer_simulator"
        if noise_profile:
            name = f"aer_noisy_{noise_profile.name}"

        super().__init__(name, backend_type)

        self.noise_profile = noise_profile
        self.use_gpu = use_gpu
        self._noise_model = None
        self._backend = None

        self._initialize_backend()

    def _initialize_backend(self) -> None:
        """Initialize the Qiskit Aer backend."""
        try:
            from qiskit_aer import AerSimulator
        except ImportError:
            raise ImportError("qiskit-aer is required. Install with: pip install qiskit-aer")

        # Build noise model if profile provided
        if self.noise_profile:
            builder = NoiseModelBuilder(self.noise_profile)
            self._noise_model = builder.build()
            self._backend = AerSimulator(noise_model=self._noise_model)
        else:
            self._backend = AerSimulator()

        # GPU configuration
        if self.use_gpu:
            self._backend.set_options(device="GPU")

    def execute(self, circuit: Any, shots: int = 1024, **kwargs: Any) -> ExecutionResult:
        """
        Execute a quantum circuit on Aer simulator.

        Args:
            circuit: Qiskit QuantumCircuit
            shots: Number of measurement shots
            **kwargs: Additional options (seed, memory, etc.)

        Returns:
            ExecutionResult with counts and metadata
        """
        from qiskit import transpile

        start_time = time.time()

        # Transpile for the backend
        transpiled = transpile(circuit, self._backend)

        # Run the circuit
        assert self._backend is not None
        job = self._backend.run(transpiled, shots=shots, **kwargs)
        result = job.result()

        execution_time_ms = (time.time() - start_time) * 1000

        # Extract counts
        counts = result.get_counts()

        # Record statistics
        self._record_execution(shots, execution_time_ms)

        # Estimate error rate if noisy
        error_rate = None
        if self.noise_profile:
            from .base import CircuitMetrics
            from .noise_models import estimate_circuit_fidelity

            metrics = CircuitMetrics.from_qiskit_circuit(circuit)
            fidelity = estimate_circuit_fidelity(
                metrics.depth, metrics.two_qubit_gate_count, self.noise_profile
            )
            error_rate = 1 - fidelity

        return ExecutionResult(
            counts=counts,
            shots=shots,
            backend_name=self.name,
            backend_type=self.backend_type,
            execution_time_ms=execution_time_ms,
            error_rate_estimate=error_rate,
            metadata={
                "transpiled_depth": transpiled.depth(),
                "noise_model": self.noise_profile.name if self.noise_profile else None,
            },
        )

    def execute_batch(
        self, circuits: List[Any], shots: int = 1024, **kwargs: Any
    ) -> List[ExecutionResult]:
        """
        Execute multiple circuits in a batch.

        Args:
            circuits: List of Qiskit QuantumCircuits
            shots: Number of shots per circuit
            **kwargs: Additional options

        Returns:
            List of ExecutionResults
        """
        from qiskit import transpile

        start_time = time.time()

        # Transpile all circuits
        transpiled = transpile(circuits, self._backend)

        # Run batch
        assert self._backend is not None
        job = self._backend.run(transpiled, shots=shots, **kwargs)
        result = job.result()

        total_time_ms = (time.time() - start_time) * 1000
        time_per_circuit = total_time_ms / len(circuits)

        # Extract results
        results = []
        for i, circuit in enumerate(circuits):
            counts = result.get_counts(i)

            error_rate = None
            if self.noise_profile:
                from .base import CircuitMetrics
                from .noise_models import estimate_circuit_fidelity

                metrics = CircuitMetrics.from_qiskit_circuit(circuit)
                fidelity = estimate_circuit_fidelity(
                    metrics.depth, metrics.two_qubit_gate_count, self.noise_profile
                )
                error_rate = 1 - fidelity

            results.append(
                ExecutionResult(
                    counts=counts,
                    shots=shots,
                    backend_name=self.name,
                    backend_type=self.backend_type,
                    execution_time_ms=time_per_circuit,
                    error_rate_estimate=error_rate,
                    metadata={"circuit_index": i},
                )
            )

            self._record_execution(shots, time_per_circuit)

        return results

    def run_statevector(self, circuit: Any) -> Any:
        """
        Run circuit and return final statevector.

        Only works for ideal (noiseless) simulation.

        Args:
            circuit: Qiskit QuantumCircuit (without measurements)

        Returns:
            Statevector object
        """
        if self.noise_profile:
            raise ValueError(
                "Statevector simulation not available with noise model. "
                "Use shots-based simulation instead."
            )

        from qiskit import transpile
        from qiskit_aer import AerSimulator

        sv_backend = AerSimulator(method="statevector")

        # Remove measurements for statevector
        circuit_copy = circuit.copy()
        circuit_copy.remove_final_measurements()
        circuit_copy.save_statevector()

        transpiled = transpile(circuit_copy, sv_backend)
        job = sv_backend.run(transpiled)
        result = job.result()

        return result.get_statevector()

    def compute_expectation(
        self, circuit: Any, observable: Any, shots: int = 1024, **kwargs: Any
    ) -> float:
        """
        Compute expectation value of an observable.

        Args:
            circuit: Qiskit QuantumCircuit
            observable: SparsePauliOp or Pauli string
            shots: Number of shots

        Returns:
            Expectation value
        """
        try:
            from qiskit.primitives import Estimator
            from qiskit.quantum_info import SparsePauliOp
        except ImportError:
            # Fall back to sampling-based estimation
            return super().compute_expectation(circuit, observable, shots, **kwargs)

        # Convert string to SparsePauliOp if needed
        if isinstance(observable, str):
            observable = SparsePauliOp.from_list([(observable, 1.0)])

        # Use Estimator primitive
        if self._noise_model:
            from qiskit_aer.primitives import Estimator as AerEstimator

            estimator = AerEstimator(backend_options={"noise_model": self._noise_model})
        else:
            estimator = Estimator()

        job = estimator.run(circuit, observable, shots=shots)
        result = job.result()

        return float(result.values[0])

    def set_noise_profile(self, profile: DeviceNoiseProfile) -> None:
        """
        Update the noise profile and rebuild noise model.

        Args:
            profile: New noise profile
        """
        self.noise_profile = profile
        self.name = f"aer_noisy_{profile.name}"
        self.backend_type = BackendType.NOISY_SIMULATOR
        self._initialize_backend()

    def clear_noise(self) -> None:
        """Remove noise model for ideal simulation."""
        self.noise_profile = None
        self._noise_model = None
        self.name = "aer_simulator"
        self.backend_type = BackendType.SIMULATOR
        self._initialize_backend()


def create_backend(profile_name: str = "ideal", **kwargs) -> AerBackend:
    """
    Factory function to create Aer backend with common profiles.

    Args:
        profile_name: One of 'ideal', 'manila', 'kolkata', 'ionq', 'sycamore'
        **kwargs: Additional backend options

    Returns:
        Configured AerBackend
    """
    profiles = {
        "ideal": None,
        "manila": DeviceNoiseProfile.ibm_manila_like(),
        "kolkata": DeviceNoiseProfile.ibm_kolkata_like(),
        "ionq": DeviceNoiseProfile.ionq_harmony_like(),
        "sycamore": DeviceNoiseProfile.google_sycamore_like(),
    }

    if profile_name not in profiles:
        raise ValueError(f"Unknown profile: {profile_name}. " f"Available: {list(profiles.keys())}")

    return AerBackend(noise_profile=profiles[profile_name], **kwargs)
