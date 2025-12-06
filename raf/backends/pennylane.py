"""
PennyLane backend for gradient-based quantum optimization.

PennyLane provides automatic differentiation for quantum circuits,
making it ideal for variational quantum algorithms (VQA).

Supported devices:
    - default.qubit: Fast CPU simulator with analytic gradients
    - lightning.qubit: High-performance C++ simulator
    - lightning.gpu: GPU-accelerated simulator
    - qiskit.aer: Qiskit Aer through PennyLane-Qiskit plugin
    - braket.aws.qubit: AWS Braket through PennyLane-Braket plugin

Requires:
    pip install pennylane

Optional plugins:
    pip install pennylane-qiskit    # For Qiskit integration
    pip install pennylane-lightning  # For lightning.qubit
    pip install amazon-braket-pennylane-plugin  # For AWS Braket
"""

import time
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from .base import BackendType, ExecutionResult, QuantumBackend

# Device configurations
PENNYLANE_DEVICES = {
    # Built-in simulators
    "default.qubit": {
        "description": "Default PennyLane qubit simulator",
        "supports_gradients": True,
        "supports_shots": True,
        "max_qubits": 26,
    },
    "default.mixed": {
        "description": "Mixed state simulator (density matrix)",
        "supports_gradients": True,
        "supports_shots": True,
        "max_qubits": 14,
    },
    # Lightning simulators (requires pennylane-lightning)
    "lightning.qubit": {
        "description": "High-performance C++ simulator",
        "supports_gradients": True,
        "supports_shots": True,
        "max_qubits": 30,
    },
    "lightning.gpu": {
        "description": "GPU-accelerated simulator (CUDA)",
        "supports_gradients": True,
        "supports_shots": True,
        "max_qubits": 32,
    },
    # Qiskit integration (requires pennylane-qiskit)
    "qiskit.aer": {
        "description": "Qiskit Aer simulator via PennyLane",
        "supports_gradients": False,
        "supports_shots": True,
        "max_qubits": 30,
    },
    "qiskit.ibmq": {
        "description": "IBM Quantum hardware via PennyLane",
        "supports_gradients": False,
        "supports_shots": True,
        "max_qubits": 127,
    },
    # AWS Braket (requires amazon-braket-pennylane-plugin)
    "braket.aws.qubit": {
        "description": "AWS Braket devices via PennyLane",
        "supports_gradients": False,
        "supports_shots": True,
        "max_qubits": 34,
    },
    "braket.local.qubit": {
        "description": "Local Braket simulator via PennyLane",
        "supports_gradients": True,
        "supports_shots": True,
        "max_qubits": 26,
    },
}


class PennyLaneBackend(QuantumBackend):
    """
    PennyLane backend for gradient-based quantum computing.

    Key features:
    - Automatic differentiation of quantum circuits
    - Support for multiple simulator and hardware backends
    - Native VQA optimization support
    - Hybrid quantum-classical workflows
    """

    def __init__(
        self,
        device_name: str = "default.qubit",
        wires: int = 4,
        shots: Optional[int] = None,
        **device_kwargs,
    ):
        """
        Initialize PennyLane backend.

        Args:
            device_name: PennyLane device name (e.g., 'default.qubit', 'lightning.qubit')
            wires: Number of qubits
            shots: Number of shots (None for analytic mode)
            **device_kwargs: Additional device-specific arguments
        """
        backend_type = BackendType.SIMULATOR
        if "ibmq" in device_name or "braket.aws" in device_name:
            backend_type = BackendType.REAL_HARDWARE

        super().__init__(f"pennylane_{device_name}", backend_type)

        self.device_name = device_name
        self.wires = wires
        self.shots = shots
        self.device_kwargs = device_kwargs

        self._device = None
        self._initialize_device()

    def _initialize_device(self):
        """Initialize the PennyLane device."""
        try:
            import pennylane as qml
        except ImportError:
            raise ImportError("pennylane required. Install with: pip install pennylane")

        # Create device
        self._device = qml.device(
            self.device_name,
            wires=self.wires,
            shots=self.shots,
            **self.device_kwargs,
        )

    def execute(
        self,
        circuit: Any,
        shots: int = 1024,
        **kwargs,
    ) -> ExecutionResult:
        """
        Execute a quantum circuit.

        Args:
            circuit: PennyLane QNode or Qiskit QuantumCircuit
            shots: Number of measurement shots
            **kwargs: Additional execution options

        Returns:
            ExecutionResult with counts and metadata
        """
        import pennylane as qml

        start_time = time.time()

        # Handle different circuit types
        if hasattr(circuit, "data"):  # Qiskit circuit
            circuit = self._qiskit_to_pennylane(circuit)

        # Update shots if different from device default
        if shots != self.shots:
            self._device = qml.device(
                self.device_name,
                wires=self.wires,
                shots=shots,
                **self.device_kwargs,
            )

        # Execute circuit
        if callable(circuit):
            # QNode
            result = circuit()
        else:
            raise ValueError("Circuit must be a PennyLane QNode or Qiskit QuantumCircuit")

        execution_time_ms = (time.time() - start_time) * 1000

        # Convert result to counts format
        counts = self._result_to_counts(result, shots)

        self._record_execution(shots, execution_time_ms)

        return ExecutionResult(
            counts=counts,
            shots=shots,
            backend_name=self.name,
            backend_type=self.backend_type,
            execution_time_ms=execution_time_ms,
            metadata={
                "device": self.device_name,
                "wires": self.wires,
            },
        )

    def execute_batch(
        self,
        circuits: List[Any],
        shots: int = 1024,
        **kwargs,
    ) -> List[ExecutionResult]:
        """Execute multiple circuits."""
        return [self.execute(circuit, shots=shots, **kwargs) for circuit in circuits]

    def _qiskit_to_pennylane(self, qiskit_circuit: Any) -> Callable:
        """Convert Qiskit circuit to PennyLane QNode."""
        try:
            import pennylane as qml
        except ImportError:
            raise ImportError("pennylane required")

        try:
            import qiskit  # noqa: F401
        except ImportError:
            raise ImportError("qiskit required for circuit conversion")

        # Extract gate operations from Qiskit circuit
        ops = []
        for instruction in qiskit_circuit.data:
            gate_name = instruction.operation.name
            qubits = [q._index for q in instruction.qubits]
            params = instruction.operation.params

            ops.append((gate_name, qubits, params))

        @qml.qnode(self._device)
        def circuit():
            for gate_name, qubits, params in ops:
                if gate_name == "h":
                    qml.Hadamard(wires=qubits[0])
                elif gate_name == "x":
                    qml.PauliX(wires=qubits[0])
                elif gate_name == "y":
                    qml.PauliY(wires=qubits[0])
                elif gate_name == "z":
                    qml.PauliZ(wires=qubits[0])
                elif gate_name == "s":
                    qml.S(wires=qubits[0])
                elif gate_name == "t":
                    qml.T(wires=qubits[0])
                elif gate_name == "cx":
                    qml.CNOT(wires=qubits)
                elif gate_name == "cz":
                    qml.CZ(wires=qubits)
                elif gate_name == "swap":
                    qml.SWAP(wires=qubits)
                elif gate_name == "rx":
                    qml.RX(params[0], wires=qubits[0])
                elif gate_name == "ry":
                    qml.RY(params[0], wires=qubits[0])
                elif gate_name == "rz":
                    qml.RZ(params[0], wires=qubits[0])
                elif gate_name == "u3" or gate_name == "u":
                    qml.U3(params[0], params[1], params[2], wires=qubits[0])
                elif gate_name == "measure":
                    pass  # Measurements handled separately

            return qml.probs(wires=range(self.wires))

        return circuit

    def _result_to_counts(self, result: Any, shots: int) -> Dict[str, int]:
        """Convert PennyLane result to counts dictionary."""
        if isinstance(result, np.ndarray):
            # Probability distribution
            probs = result
            num_qubits = int(np.log2(len(probs)))

            counts = {}
            for i, prob in enumerate(probs):
                if prob > 0:
                    bitstring = format(i, f"0{num_qubits}b")
                    counts[bitstring] = int(prob * shots)

            # Ensure total counts equals shots
            total = sum(counts.values())
            if total < shots and counts:
                # Add remaining to most probable
                max_key = max(counts, key=counts.get)
                counts[max_key] += shots - total

            return counts
        else:
            # Sample results
            return dict(result)

    def create_qnode(
        self,
        circuit_fn: Callable,
        diff_method: str = "best",
        **qnode_kwargs,
    ) -> Callable:
        """
        Create a PennyLane QNode from a circuit function.

        Args:
            circuit_fn: Function defining the quantum circuit
            diff_method: Differentiation method ('best', 'parameter-shift', 'adjoint', etc.)
            **qnode_kwargs: Additional QNode arguments

        Returns:
            QNode ready for execution and differentiation
        """
        import pennylane as qml

        return qml.QNode(
            circuit_fn,
            self._device,
            diff_method=diff_method,
            **qnode_kwargs,
        )

    def compute_expectation(
        self,
        circuit_fn: Callable,
        observable: Any,
        params: Optional[np.ndarray] = None,
        **kwargs,
    ) -> float:
        """
        Compute expectation value of an observable.

        Args:
            circuit_fn: Function defining the quantum circuit
            observable: PennyLane observable (e.g., qml.PauliZ(0))
            params: Circuit parameters
            **kwargs: Additional options

        Returns:
            Expectation value
        """
        import pennylane as qml

        @qml.qnode(self._device)
        def expectation_circuit(*args):
            circuit_fn(*args)
            return qml.expval(observable)

        if params is not None:
            return float(expectation_circuit(params))
        else:
            return float(expectation_circuit())

    def compute_gradient(
        self,
        circuit_fn: Callable,
        observable: Any,
        params: np.ndarray,
        diff_method: str = "best",
    ) -> np.ndarray:
        """
        Compute gradient of expectation value with respect to parameters.

        Args:
            circuit_fn: Function defining the quantum circuit
            observable: PennyLane observable
            params: Circuit parameters
            diff_method: Differentiation method

        Returns:
            Gradient array
        """
        import pennylane as qml

        @qml.qnode(self._device, diff_method=diff_method)
        def cost(*args):
            circuit_fn(*args)
            return qml.expval(observable)

        grad_fn = qml.grad(cost)
        return np.array(grad_fn(params))

    def optimize_vqe(
        self,
        circuit_fn: Callable,
        hamiltonian: Any,
        initial_params: np.ndarray,
        optimizer: str = "adam",
        max_iterations: int = 100,
        step_size: float = 0.1,
        convergence_threshold: float = 1e-6,
        callback: Optional[Callable] = None,
    ) -> Tuple[np.ndarray, float, List[float]]:
        """
        Run VQE optimization.

        Args:
            circuit_fn: Ansatz circuit function
            hamiltonian: Hamiltonian as PennyLane observable
            initial_params: Initial parameter values
            optimizer: Optimizer name ('adam', 'sgd', 'qng')
            max_iterations: Maximum optimization iterations
            step_size: Learning rate
            convergence_threshold: Convergence criterion
            callback: Optional callback function(iteration, params, energy)

        Returns:
            Tuple of (optimal_params, final_energy, energy_history)
        """
        import pennylane as qml

        # Create cost function
        @qml.qnode(self._device, diff_method="best")
        def cost_fn(params):
            circuit_fn(params)
            return qml.expval(hamiltonian)

        # Select optimizer
        optimizers = {
            "adam": qml.AdamOptimizer(stepsize=step_size),
            "sgd": qml.GradientDescentOptimizer(stepsize=step_size),
            "qng": qml.QNGOptimizer(stepsize=step_size),
            "nesterov": qml.NesterovMomentumOptimizer(stepsize=step_size),
            "rms": qml.RMSPropOptimizer(stepsize=step_size),
        }

        if optimizer not in optimizers:
            raise ValueError(
                f"Unknown optimizer: {optimizer}. Available: {list(optimizers.keys())}"
            )

        opt = optimizers[optimizer]

        # Optimization loop
        params = initial_params.copy()
        energy_history = []
        prev_energy = float("inf")

        for i in range(max_iterations):
            params, energy = opt.step_and_cost(cost_fn, params)
            energy = float(energy)
            energy_history.append(energy)

            if callback:
                callback(i, params, energy)

            # Check convergence
            if abs(energy - prev_energy) < convergence_threshold:
                break

            prev_energy = energy

        return params, energy_history[-1], energy_history

    @property
    def device(self):
        """Get the underlying PennyLane device."""
        return self._device

    @classmethod
    def list_devices(cls) -> Dict[str, Dict[str, Any]]:
        """List available PennyLane devices."""
        return PENNYLANE_DEVICES.copy()

    @classmethod
    def check_device_available(cls, device_name: str) -> bool:
        """Check if a device is available."""
        try:
            import pennylane as qml

            qml.device(device_name, wires=1)
            return True
        except Exception:
            return False


def create_pennylane_backend(
    device_name: str = "default.qubit",
    wires: int = 4,
    shots: Optional[int] = None,
    **kwargs,
) -> PennyLaneBackend:
    """
    Factory function to create PennyLane backend.

    Args:
        device_name: Device name
        wires: Number of qubits
        shots: Number of shots (None for analytic)
        **kwargs: Device-specific options

    Returns:
        Configured PennyLaneBackend
    """
    return PennyLaneBackend(
        device_name=device_name,
        wires=wires,
        shots=shots,
        **kwargs,
    )
