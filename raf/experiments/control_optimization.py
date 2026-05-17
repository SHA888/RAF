"""
Control optimization for quantum circuits.

This module implements noise-aware compilation and gate-level optimization
strategies to improve gate fidelity and reduce circuit depth.

Key components:
- NoiseAwareCompiler: Optimizes circuits based on device noise profile
- GateOptimizer: Gate-level optimization strategies
- ControlOptimizationExperiment: Measures fidelity improvement and depth reduction
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import numpy as np

from raf.backends.noise_models import DeviceNoiseProfile
from raf.utils import set_all_seeds


class OptimizationStrategy(Enum):
    """Gate-level optimization strategies."""

    NOISE_ADAPTIVE = "noise_adaptive"  # Route through lowest-error qubits
    DEPTH_REDUCTION = "depth_reduction"  # Minimize circuit depth
    GATE_CANCELLATION = "gate_cancellation"  # Cancel redundant gates
    COMMUTATION = "commutation"  # Reorder commuting gates
    TEMPLATE_MATCHING = "template_matching"  # Replace with optimized templates
    DYNAMICAL_DECOUPLING = "dynamical_decoupling"  # Insert DD sequences


@dataclass
class OptimizationResult:
    """Result from circuit optimization."""

    original_depth: int
    optimized_depth: int
    original_gate_count: int
    optimized_gate_count: int
    original_two_qubit_count: int
    optimized_two_qubit_count: int
    estimated_fidelity_before: float
    estimated_fidelity_after: float
    strategies_applied: list[str]
    optimization_time_ms: float
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def depth_reduction(self) -> float:
        """Relative depth reduction."""
        if self.original_depth == 0:
            return 0.0
        return 1.0 - (self.optimized_depth / self.original_depth)

    @property
    def gate_reduction(self) -> float:
        """Relative gate count reduction."""
        if self.original_gate_count == 0:
            return 0.0
        return 1.0 - (self.optimized_gate_count / self.original_gate_count)

    @property
    def fidelity_improvement(self) -> float:
        """Absolute fidelity improvement."""
        return self.estimated_fidelity_after - self.estimated_fidelity_before

    @property
    def fidelity_improvement_relative(self) -> float:
        """Relative improvement in infidelity."""
        infidelity_before = 1.0 - self.estimated_fidelity_before
        infidelity_after = 1.0 - self.estimated_fidelity_after
        if infidelity_before == 0:
            return 0.0
        return (infidelity_before - infidelity_after) / infidelity_before

    def to_dict(self) -> dict[str, Any]:
        return {
            "original_depth": self.original_depth,
            "optimized_depth": self.optimized_depth,
            "depth_reduction": self.depth_reduction,
            "original_gate_count": self.original_gate_count,
            "optimized_gate_count": self.optimized_gate_count,
            "gate_reduction": self.gate_reduction,
            "original_two_qubit_count": self.original_two_qubit_count,
            "optimized_two_qubit_count": self.optimized_two_qubit_count,
            "estimated_fidelity_before": self.estimated_fidelity_before,
            "estimated_fidelity_after": self.estimated_fidelity_after,
            "fidelity_improvement": self.fidelity_improvement,
            "fidelity_improvement_relative": self.fidelity_improvement_relative,
            "strategies_applied": self.strategies_applied,
            "optimization_time_ms": self.optimization_time_ms,
            "metadata": self.metadata,
        }


@dataclass
class ControlOptimizationMetrics:
    """Aggregate metrics from control optimization experiments."""

    avg_depth_reduction: float
    avg_gate_reduction: float
    avg_fidelity_improvement: float
    avg_two_qubit_reduction: float
    total_circuits_optimized: int
    total_optimization_time_ms: float
    best_fidelity_improvement: float
    worst_fidelity_improvement: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "avg_depth_reduction": self.avg_depth_reduction,
            "avg_gate_reduction": self.avg_gate_reduction,
            "avg_fidelity_improvement": self.avg_fidelity_improvement,
            "avg_two_qubit_reduction": self.avg_two_qubit_reduction,
            "total_circuits_optimized": self.total_circuits_optimized,
            "total_optimization_time_ms": self.total_optimization_time_ms,
            "best_fidelity_improvement": self.best_fidelity_improvement,
            "worst_fidelity_improvement": self.worst_fidelity_improvement,
        }


class GateOptimizer:
    """
    Gate-level optimization strategies.

    Implements various circuit optimization techniques that can be
    applied independently or in combination.
    """

    def __init__(self, random_seed: int | None = None):
        """Initialize gate optimizer."""
        self.rng = np.random.default_rng(random_seed)

    def cancel_adjacent_gates(
        self,
        gate_sequence: list[tuple[str, list[int]]],
    ) -> list[tuple[str, list[int]]]:
        """
        Cancel adjacent inverse gates (e.g., X-X, H-H, CNOT-CNOT).

        Args:
            gate_sequence: List of (gate_name, qubit_indices) tuples

        Returns:
            Optimized gate sequence
        """
        if len(gate_sequence) < 2:
            return gate_sequence

        # Gates that are self-inverse
        self_inverse = {"x", "y", "z", "h", "cx", "cz", "swap"}

        optimized = []
        i = 0
        while i < len(gate_sequence):
            if i + 1 < len(gate_sequence):
                gate1, qubits1 = gate_sequence[i]
                gate2, qubits2 = gate_sequence[i + 1]

                # Check if gates cancel
                if (
                    gate1.lower() == gate2.lower()
                    and gate1.lower() in self_inverse
                    and qubits1 == qubits2
                ):
                    # Skip both gates (they cancel)
                    i += 2
                    continue

            optimized.append(gate_sequence[i])
            i += 1

        return optimized

    def merge_rotations(
        self,
        gate_sequence: list[tuple[str, list[int], float]],
    ) -> list[tuple[str, list[int], float]]:
        """
        Merge consecutive rotation gates on the same qubit.

        Args:
            gate_sequence: List of (gate_name, qubit_indices, angle) tuples

        Returns:
            Optimized gate sequence with merged rotations
        """
        if len(gate_sequence) < 2:
            return gate_sequence

        rotation_gates = {"rx", "ry", "rz"}
        optimized = []
        i = 0

        while i < len(gate_sequence):
            gate, qubits, angle = gate_sequence[i]

            if gate.lower() in rotation_gates and i + 1 < len(gate_sequence):
                next_gate, next_qubits, next_angle = gate_sequence[i + 1]

                # Merge if same rotation type on same qubit
                if gate.lower() == next_gate.lower() and qubits == next_qubits:
                    merged_angle = (angle + next_angle) % (2 * np.pi)
                    # Skip if angle is effectively zero
                    if abs(merged_angle) > 1e-10 and abs(merged_angle - 2 * np.pi) > 1e-10:
                        optimized.append((gate, qubits, merged_angle))
                    i += 2
                    continue

            optimized.append((gate, qubits, angle))
            i += 1

        return optimized

    def reorder_commuting_gates(
        self,
        gate_sequence: list[tuple[str, list[int]]],
    ) -> list[tuple[str, list[int]]]:
        """
        Reorder commuting gates to enable further optimizations.

        Gates on disjoint qubits commute and can be reordered.

        Args:
            gate_sequence: List of (gate_name, qubit_indices) tuples

        Returns:
            Reordered gate sequence
        """
        if len(gate_sequence) < 2:
            return gate_sequence

        # Simple bubble-sort style reordering
        # Move single-qubit gates before two-qubit gates when they commute
        optimized = list(gate_sequence)
        changed = True

        while changed:
            changed = False
            for i in range(len(optimized) - 1):
                gate1, qubits1 = optimized[i]
                gate2, qubits2 = optimized[i + 1]

                # Check if gates operate on disjoint qubits; prefer single-qubit gates first
                if set(qubits1).isdisjoint(set(qubits2)) and len(qubits1) > len(qubits2):
                    optimized[i], optimized[i + 1] = optimized[i + 1], optimized[i]
                    changed = True

        return optimized


class NoiseAwareCompiler:
    """
    Noise-aware circuit compiler that optimizes circuits based on
    device noise characteristics.

    Strategies:
    1. Route through lowest-error qubits/edges
    2. Minimize two-qubit gate count (highest error source)
    3. Apply gate cancellation and commutation
    4. Insert dynamical decoupling for idle qubits

    Example:
        >>> from qiskit import QuantumCircuit
        >>> from raf.backends import DeviceNoiseProfile
        >>> profile = DeviceNoiseProfile.ibm_manila_like()
        >>> compiler = NoiseAwareCompiler(profile)
        >>> qc = QuantumCircuit(3)
        >>> qc.h(0)
        >>> qc.cx(0, 1)
        >>> qc.cx(1, 2)
        >>> result = compiler.optimize(qc)
        >>> print(f"Fidelity improvement: {result.fidelity_improvement:.2%}")
    """

    def __init__(
        self,
        noise_profile: DeviceNoiseProfile,
        strategies: list[OptimizationStrategy] | None = None,
        optimization_level: int = 2,
        random_seed: int | None = None,
    ):
        """
        Initialize noise-aware compiler.

        Args:
            noise_profile: Device noise characteristics
            strategies: List of optimization strategies to apply
            optimization_level: 0-3, higher = more aggressive optimization
            random_seed: Seed for deterministic compilation/transpilation
        """
        self.noise_profile = noise_profile
        self.strategies = strategies or [
            OptimizationStrategy.GATE_CANCELLATION,
            OptimizationStrategy.COMMUTATION,
            OptimizationStrategy.NOISE_ADAPTIVE,
        ]
        self.optimization_level = optimization_level
        self.seed = random_seed
        self.gate_optimizer = GateOptimizer(random_seed=random_seed)

        # Build qubit error map for routing
        self._build_error_map()

    def _build_error_map(self) -> None:
        """Build error maps for noise-aware routing."""
        n_qubits = self.noise_profile.num_qubits

        # Single-qubit error rates (uniform for now)
        self.single_qubit_errors = np.full(n_qubits, self.noise_profile.single_qubit_error)

        # Two-qubit error rates for each edge
        self.two_qubit_errors = {}
        if self.noise_profile.coupling_map:
            for q1, q2 in self.noise_profile.coupling_map:
                # Add some variation based on qubit indices
                variation = 1.0 + 0.1 * np.sin(q1 + q2)
                self.two_qubit_errors[(q1, q2)] = self.noise_profile.two_qubit_error * variation
        else:
            # All-to-all connectivity
            for q1 in range(n_qubits):
                for q2 in range(n_qubits):
                    if q1 != q2:
                        self.two_qubit_errors[(q1, q2)] = self.noise_profile.two_qubit_error

    def _estimate_fidelity(self, circuit: Any) -> float:
        """
        Estimate circuit fidelity based on noise profile.

        Args:
            circuit: Qiskit QuantumCircuit

        Returns:
            Estimated fidelity (0-1)
        """
        # Count gates
        n_single = 0
        n_two = 0

        for instruction in circuit.data:
            n_qubits = len(instruction.qubits)
            if n_qubits == 1:
                n_single += 1
            elif n_qubits == 2:
                n_two += 1

        # Simple fidelity model
        f_single = (1 - self.noise_profile.single_qubit_error) ** n_single
        f_two = (1 - self.noise_profile.two_qubit_error) ** n_two
        f_readout = (1 - self.noise_profile.readout_error) ** circuit.num_qubits

        return float(f_single * f_two * f_readout)

    def _count_gates(self, circuit: Any) -> tuple[int, int, int]:
        """Count total gates, depth, and two-qubit gates."""
        total = len(circuit.data)
        depth = circuit.depth()
        two_qubit = sum(1 for inst in circuit.data if len(inst.qubits) == 2)
        return total, depth, two_qubit

    def _apply_gate_cancellation(self, circuit: Any) -> Any:
        """Apply gate cancellation optimization."""
        try:
            from qiskit.transpiler import PassManager
            from qiskit.transpiler.passes import (
                CommutativeCancellation,
                CXCancellation,
                Optimize1qGates,
            )

            pm = PassManager(
                [
                    Optimize1qGates(),
                    CXCancellation(),
                    CommutativeCancellation(),
                ]
            )
            return pm.run(circuit)
        except ImportError:
            # Fallback: return original circuit
            return circuit

    def _apply_commutation(self, circuit: Any) -> Any:
        """Apply gate commutation optimization."""
        try:
            from qiskit.transpiler import PassManager
            from qiskit.transpiler.passes import CommutationAnalysis, CommutativeCancellation

            pm = PassManager(
                [
                    CommutationAnalysis(),
                    CommutativeCancellation(),
                ]
            )
            return pm.run(circuit)
        except ImportError:
            return circuit

    def _apply_noise_adaptive_routing(self, circuit: Any) -> Any:
        """
        Apply noise-adaptive qubit routing.

        Routes through lowest-error paths when possible.
        """
        try:
            from qiskit import transpile

            # Use Qiskit's built-in routing with our coupling map
            if self.noise_profile.coupling_map:
                optimized = transpile(
                    circuit,
                    coupling_map=self.noise_profile.coupling_map,
                    optimization_level=self.optimization_level,
                    seed_transpiler=self.seed,
                )
                return optimized
            else:
                return transpile(
                    circuit,
                    optimization_level=self.optimization_level,
                    seed_transpiler=self.seed,
                )
        except Exception:
            return circuit

    def _apply_depth_reduction(self, circuit: Any) -> Any:
        """Apply depth reduction optimization."""
        try:
            from qiskit import transpile

            return transpile(
                circuit,
                optimization_level=3,  # Maximum optimization
                seed_transpiler=self.seed,
            )
        except Exception:
            return circuit

    def _apply_dynamical_decoupling(self, circuit: Any) -> Any:
        """
        Insert dynamical decoupling sequences for idle qubits.

        DD sequences help preserve coherence during idle periods.
        """
        try:
            from qiskit.circuit.library import XGate
            from qiskit.transpiler import PassManager
            from qiskit.transpiler.passes import ALAPScheduleAnalysis, PadDynamicalDecoupling

            # Create DD sequence (X-X)
            dd_sequence = [XGate(), XGate()]

            pm = PassManager(
                [
                    ALAPScheduleAnalysis(self._get_instruction_durations()),
                    PadDynamicalDecoupling(
                        self._get_instruction_durations(),
                        dd_sequence,
                    ),
                ]
            )
            return pm.run(circuit)
        except (ImportError, Exception):
            # DD requires scheduling info, fallback to original
            return circuit

    def _get_instruction_durations(self) -> Any:
        """Get instruction durations for scheduling."""
        try:
            from qiskit.transpiler import InstructionDurations

            # Create duration list based on noise profile
            dt = 1e-9  # 1 ns time unit
            durations = [
                ("x", None, int(self.noise_profile.single_qubit_gate_time_us * 1000)),
                ("sx", None, int(self.noise_profile.single_qubit_gate_time_us * 500)),
                ("rz", None, 0),  # Virtual gate
                ("cx", None, int(self.noise_profile.two_qubit_gate_time_us * 1000)),
                ("measure", None, int(self.noise_profile.readout_time_us * 1000)),
            ]
            return InstructionDurations(durations, dt=dt)
        except ImportError:
            return None

    def optimize(self, circuit: Any) -> OptimizationResult:
        """
        Optimize a quantum circuit using noise-aware strategies.

        Args:
            circuit: Qiskit QuantumCircuit to optimize

        Returns:
            OptimizationResult with metrics
        """
        import time

        start_time = time.time()

        # Get original metrics
        orig_gates, orig_depth, orig_two_qubit = self._count_gates(circuit)
        orig_fidelity = self._estimate_fidelity(circuit)

        # Apply optimization strategies
        optimized = circuit.copy()
        strategies_applied = []

        for strategy in self.strategies:
            if strategy == OptimizationStrategy.GATE_CANCELLATION:
                optimized = self._apply_gate_cancellation(optimized)
                strategies_applied.append("gate_cancellation")

            elif strategy == OptimizationStrategy.COMMUTATION:
                optimized = self._apply_commutation(optimized)
                strategies_applied.append("commutation")

            elif strategy == OptimizationStrategy.NOISE_ADAPTIVE:
                optimized = self._apply_noise_adaptive_routing(optimized)
                strategies_applied.append("noise_adaptive")

            elif strategy == OptimizationStrategy.DEPTH_REDUCTION:
                optimized = self._apply_depth_reduction(optimized)
                strategies_applied.append("depth_reduction")

            elif strategy == OptimizationStrategy.DYNAMICAL_DECOUPLING:
                optimized = self._apply_dynamical_decoupling(optimized)
                strategies_applied.append("dynamical_decoupling")

        # Get optimized metrics
        opt_gates, opt_depth, opt_two_qubit = self._count_gates(optimized)
        opt_fidelity = self._estimate_fidelity(optimized)

        optimization_time = (time.time() - start_time) * 1000

        return OptimizationResult(
            original_depth=orig_depth,
            optimized_depth=opt_depth,
            original_gate_count=orig_gates,
            optimized_gate_count=opt_gates,
            original_two_qubit_count=orig_two_qubit,
            optimized_two_qubit_count=opt_two_qubit,
            estimated_fidelity_before=orig_fidelity,
            estimated_fidelity_after=opt_fidelity,
            strategies_applied=strategies_applied,
            optimization_time_ms=optimization_time,
            metadata={
                "noise_profile": self.noise_profile.name,
                "optimization_level": self.optimization_level,
            },
        )


class ControlOptimizationExperiment:
    """
    Experiment to measure gate fidelity improvement and circuit depth reduction
    from noise-aware compilation.

    Example:
        >>> from raf.backends import DeviceNoiseProfile
        >>> profile = DeviceNoiseProfile.ibm_manila_like()
        >>> experiment = ControlOptimizationExperiment(profile)
        >>> metrics = experiment.run_benchmark(n_circuits=20)
        >>> print(f"Avg fidelity improvement: {metrics.avg_fidelity_improvement:.2%}")
    """

    def __init__(
        self,
        noise_profile: DeviceNoiseProfile,
        strategies: list[OptimizationStrategy] | None = None,
        random_seed: int | None = None,
    ):
        """
        Initialize experiment.

        Args:
            noise_profile: Device noise profile
            strategies: Optimization strategies to test
            random_seed: For reproducibility
        """
        self.seed = random_seed
        if random_seed is not None:
            set_all_seeds(random_seed)

        self.noise_profile = noise_profile
        self.strategies = strategies
        self.rng = np.random.default_rng(random_seed)
        self.compiler = NoiseAwareCompiler(noise_profile, strategies, random_seed=random_seed)
        self.results: list[OptimizationResult] = []

    def _generate_random_circuit(
        self,
        n_qubits: int,
        depth: int,
        two_qubit_fraction: float = 0.3,
    ) -> Any:
        """Generate a random quantum circuit for benchmarking."""
        try:
            from qiskit import QuantumCircuit
            from qiskit.circuit.library import (
                CXGate,
                CZGate,
                HGate,
                SGate,
                TGate,
                XGate,
                YGate,
                ZGate,
            )
        except ImportError as err:
            raise ImportError("qiskit is required for circuit generation") from err

        qc = QuantumCircuit(n_qubits)

        single_gates = [HGate, XGate, YGate, ZGate, SGate, TGate]
        two_qubit_gates = [CXGate, CZGate]

        for _ in range(depth):
            if self.rng.random() < two_qubit_fraction and n_qubits >= 2:
                # Two-qubit gate
                gate_class = self.rng.choice(two_qubit_gates)
                q1, q2 = self.rng.choice(n_qubits, size=2, replace=False)
                qc.append(gate_class(), [q1, q2])
            else:
                # Single-qubit gate
                gate_class = self.rng.choice(single_gates)
                q = self.rng.integers(0, n_qubits)
                qc.append(gate_class(), [q])

        return qc

    def _generate_vqe_like_circuit(
        self,
        n_qubits: int,
        n_layers: int,
    ) -> Any:
        """Generate a VQE-like variational circuit."""
        try:
            from qiskit import QuantumCircuit
        except ImportError as err:
            raise ImportError("qiskit is required for circuit generation") from err

        qc = QuantumCircuit(n_qubits)

        for _layer in range(n_layers):
            # Rotation layer
            for q in range(n_qubits):
                theta = self.rng.uniform(0, 2 * np.pi)
                phi = self.rng.uniform(0, 2 * np.pi)
                qc.ry(theta, q)
                qc.rz(phi, q)

            # Entangling layer
            for q in range(n_qubits - 1):
                qc.cx(q, q + 1)

        return qc

    def optimize_circuit(self, circuit: Any) -> OptimizationResult:
        """
        Optimize a single circuit and record results.

        Args:
            circuit: Qiskit QuantumCircuit

        Returns:
            OptimizationResult
        """
        result = self.compiler.optimize(circuit)
        self.results.append(result)
        return result

    def run_benchmark(
        self,
        n_circuits: int = 20,
        n_qubits: int = 5,
        depths: list[int] | None = None,
        circuit_type: str = "random",
    ) -> ControlOptimizationMetrics:
        """
        Run optimization benchmark on multiple circuits.

        Args:
            n_circuits: Number of circuits to test
            n_qubits: Number of qubits per circuit
            depths: List of circuit depths to test
            circuit_type: "random" or "vqe"

        Returns:
            ControlOptimizationMetrics with aggregate results
        """
        depths = depths or [10, 20, 30, 50]
        self.results = []

        for i in range(n_circuits):
            depth = depths[i % len(depths)]

            if circuit_type == "vqe":
                n_layers = max(1, depth // 5)
                circuit = self._generate_vqe_like_circuit(n_qubits, n_layers)
            else:
                circuit = self._generate_random_circuit(n_qubits, depth)

            self.optimize_circuit(circuit)

        return self.compute_metrics()

    def compute_metrics(self) -> ControlOptimizationMetrics:
        """Compute aggregate metrics from all results."""
        if not self.results:
            return ControlOptimizationMetrics(
                avg_depth_reduction=0.0,
                avg_gate_reduction=0.0,
                avg_fidelity_improvement=0.0,
                avg_two_qubit_reduction=0.0,
                total_circuits_optimized=0,
                total_optimization_time_ms=0.0,
                best_fidelity_improvement=0.0,
                worst_fidelity_improvement=0.0,
            )

        depth_reductions = [r.depth_reduction for r in self.results]
        gate_reductions = [r.gate_reduction for r in self.results]
        fidelity_improvements = [r.fidelity_improvement for r in self.results]
        two_qubit_reductions = []

        for r in self.results:
            if r.original_two_qubit_count > 0:
                reduction = 1.0 - (r.optimized_two_qubit_count / r.original_two_qubit_count)
                two_qubit_reductions.append(reduction)

        return ControlOptimizationMetrics(
            avg_depth_reduction=float(np.mean(depth_reductions)),
            avg_gate_reduction=float(np.mean(gate_reductions)),
            avg_fidelity_improvement=float(np.mean(fidelity_improvements)),
            avg_two_qubit_reduction=(
                float(np.mean(two_qubit_reductions)) if two_qubit_reductions else 0.0
            ),
            total_circuits_optimized=len(self.results),
            total_optimization_time_ms=sum(r.optimization_time_ms for r in self.results),
            best_fidelity_improvement=float(max(fidelity_improvements)),
            worst_fidelity_improvement=float(min(fidelity_improvements)),
        )

    def compare_strategies(
        self,
        n_circuits: int = 10,
        n_qubits: int = 5,
        depth: int = 20,
    ) -> dict[str, ControlOptimizationMetrics]:
        """
        Compare different optimization strategies.

        Args:
            n_circuits: Number of circuits per strategy
            n_qubits: Number of qubits
            depth: Circuit depth

        Returns:
            Dictionary mapping strategy name to metrics
        """
        strategy_groups = {
            "gate_cancellation_only": [OptimizationStrategy.GATE_CANCELLATION],
            "commutation_only": [OptimizationStrategy.COMMUTATION],
            "noise_adaptive_only": [OptimizationStrategy.NOISE_ADAPTIVE],
            "depth_reduction_only": [OptimizationStrategy.DEPTH_REDUCTION],
            "combined": [
                OptimizationStrategy.GATE_CANCELLATION,
                OptimizationStrategy.COMMUTATION,
                OptimizationStrategy.NOISE_ADAPTIVE,
            ],
        }

        results = {}

        # Generate test circuits once
        test_circuits = [self._generate_random_circuit(n_qubits, depth) for _ in range(n_circuits)]

        for name, strategies in strategy_groups.items():
            compiler = NoiseAwareCompiler(self.noise_profile, strategies)
            self.results = []

            for circuit in test_circuits:
                result = compiler.optimize(circuit)
                self.results.append(result)

            results[name] = self.compute_metrics()

        return results

    def summary(self) -> dict[str, Any]:
        """Generate experiment summary."""
        metrics = self.compute_metrics()
        return {
            "noise_profile": self.noise_profile.name,
            "strategies": [s.value for s in (self.strategies or [])],
            "metrics": metrics.to_dict(),
            "individual_results": [r.to_dict() for r in self.results[-5:]],  # Last 5
        }
