"""
Base classes for quantum backend abstraction.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class BackendType(Enum):
    """Type of quantum backend."""

    SIMULATOR = "simulator"
    NOISY_SIMULATOR = "noisy_simulator"
    REAL_HARDWARE = "real_hardware"


@dataclass
class ExecutionResult:
    """Result from quantum circuit execution."""

    # Raw measurement counts
    counts: dict[str, int]

    # Number of shots executed
    shots: int

    # Execution metadata
    backend_name: str
    backend_type: BackendType
    execution_time_ms: float

    # Optional: expectation values if computed
    expectation_values: dict[str, float] | None = None

    # Optional: raw statevector (for ideal simulation)
    statevector: Any | None = None

    # Optional: error information
    error_rate_estimate: float | None = None

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def probabilities(self) -> dict[str, float]:
        """Convert counts to probabilities."""
        total = sum(self.counts.values())
        return {k: v / total for k, v in self.counts.items()}

    def get_expectation(self, observable_name: str) -> float | None:
        """Get expectation value for a named observable."""
        if self.expectation_values:
            return self.expectation_values.get(observable_name)
        return None


class QuantumBackend(ABC):
    """
    Abstract base class for quantum backends.

    Provides unified interface for simulators and real hardware,
    enabling seamless switching between development and production.
    """

    def __init__(self, name: str, backend_type: BackendType):
        self.name = name
        self.backend_type = backend_type
        self._execution_count = 0
        self._total_shots = 0
        self._total_time_ms = 0.0

    @abstractmethod
    def execute(self, circuit: Any, shots: int = 1024, **kwargs: Any) -> ExecutionResult:
        """
        Execute a quantum circuit.

        Args:
            circuit: Quantum circuit to execute (Qiskit QuantumCircuit)
            shots: Number of measurement shots
            **kwargs: Backend-specific options

        Returns:
            ExecutionResult with counts and metadata
        """
        pass

    @abstractmethod
    def execute_batch(
        self, circuits: list[Any], shots: int = 1024, **kwargs: Any
    ) -> list[ExecutionResult]:
        """
        Execute multiple circuits in a batch.

        Args:
            circuits: List of quantum circuits
            shots: Number of shots per circuit
            **kwargs: Backend-specific options

        Returns:
            List of ExecutionResults
        """
        pass

    def compute_expectation(
        self, circuit: Any, observable: Any, shots: int = 1024, **kwargs: Any
    ) -> float:
        """
        Compute expectation value of an observable.

        Default implementation uses sampling; backends may override
        with more efficient methods.

        Args:
            circuit: Quantum circuit preparing the state
            observable: Observable to measure (Pauli string or operator)
            shots: Number of measurement shots

        Returns:
            Expectation value estimate
        """
        # Default: execute and compute from counts
        # Subclasses should override for efficiency
        result = self.execute(circuit, shots=shots, **kwargs)
        return self._expectation_from_counts(result.counts, observable)

    def _expectation_from_counts(self, counts: dict[str, int], _observable: Any) -> float:
        """
        Compute expectation value from measurement counts.

        For Z-basis observables (most common case).
        """
        total = sum(counts.values())
        expectation = 0.0

        for bitstring, count in counts.items():
            # Compute parity for Z-observable
            parity = 1
            for bit in bitstring:
                if bit == "1":
                    parity *= -1
            expectation += parity * count / total

        return expectation

    @property
    def statistics(self) -> dict[str, Any]:
        """Get execution statistics."""
        return {
            "name": self.name,
            "type": self.backend_type.value,
            "executions": self._execution_count,
            "total_shots": self._total_shots,
            "total_time_ms": self._total_time_ms,
            "avg_time_per_execution_ms": (
                self._total_time_ms / self._execution_count if self._execution_count > 0 else 0
            ),
        }

    def reset_statistics(self) -> None:
        """Reset execution statistics."""
        self._execution_count = 0
        self._total_shots = 0
        self._total_time_ms = 0.0

    def _record_execution(self, shots: int, time_ms: float) -> None:
        """Record execution for statistics."""
        self._execution_count += 1
        self._total_shots += shots
        self._total_time_ms += time_ms


@dataclass
class CircuitMetrics:
    """Metrics extracted from a quantum circuit."""

    num_qubits: int
    depth: int
    gate_counts: dict[str, int]
    two_qubit_gate_count: int
    parameter_count: int

    @property
    def total_gates(self) -> int:
        return sum(self.gate_counts.values())

    @classmethod
    def from_qiskit_circuit(cls, circuit: Any) -> "CircuitMetrics":
        """Extract metrics from a Qiskit QuantumCircuit."""
        gate_counts: dict[str, int] = {}
        two_qubit_count = 0

        for instruction in circuit.data:
            gate_name = instruction.operation.name
            gate_counts[gate_name] = gate_counts.get(gate_name, 0) + 1
            if len(instruction.qubits) >= 2:
                two_qubit_count += 1

        return cls(
            num_qubits=circuit.num_qubits,
            depth=circuit.depth(),
            gate_counts=gate_counts,
            two_qubit_gate_count=two_qubit_count,
            parameter_count=circuit.num_parameters,
        )
