"""
Ansatz Design Loop - Empirical Validation Experiment.

This module implements experiments to validate the Ansatz Design acceleration loop:
    QAS → Improved Circuits → Better QML Results → Training Signal →
    Neural Surrogates → Efficient QAS

Key components:
    - Neural surrogate for circuit performance prediction
    - Evolutionary QAS algorithm
    - Hardware heterogeneity study
"""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

from ..backends import create_backend
from .metrics_collector import ExperimentalMetricsCollector


@dataclass
class CircuitCandidate:
    """Represents a candidate ansatz circuit."""

    # Circuit structure parameters
    num_qubits: int
    depth: int
    gate_sequence: List[str]  # e.g., ['ry', 'cx', 'rz', 'cx']
    entanglement: str  # 'linear', 'full', 'circular'

    # Performance metrics (filled after evaluation)
    performance: Optional[float] = None
    fidelity: Optional[float] = None
    evaluation_time_ms: Optional[float] = None

    # Metadata
    generation: int = 0
    parent_id: Optional[int] = None
    circuit_id: int = field(default_factory=lambda: np.random.randint(0, 1000000))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "circuit_id": self.circuit_id,
            "num_qubits": self.num_qubits,
            "depth": self.depth,
            "gate_sequence": self.gate_sequence,
            "entanglement": self.entanglement,
            "performance": self.performance,
            "fidelity": self.fidelity,
            "evaluation_time_ms": self.evaluation_time_ms,
            "generation": self.generation,
        }


class NeuralSurrogate:
    """
    Simple MLP surrogate for circuit performance prediction.

    Predicts circuit performance without running on quantum hardware,
    enabling faster architecture search.
    """

    def __init__(self, hidden_sizes: List[int] = None):
        """
        Initialize neural surrogate.

        Args:
            hidden_sizes: Hidden layer sizes for MLP
        """
        self.hidden_sizes = hidden_sizes or [64, 32]
        self.model = None
        self.scaler_X = None
        self.scaler_y = None
        self.is_trained = False
        self.training_history: List[Dict] = []

    def _encode_circuit(self, candidate: CircuitCandidate) -> np.ndarray:
        """Encode circuit candidate as feature vector."""
        # Simple encoding: structural features
        gate_counts = {
            "rx": 0,
            "ry": 0,
            "rz": 0,
            "cx": 0,
            "cz": 0,
            "h": 0,
        }
        for gate in candidate.gate_sequence:
            if gate in gate_counts:
                gate_counts[gate] += 1

        entanglement_map = {"linear": 0, "circular": 1, "full": 2}

        features = [
            candidate.num_qubits,
            candidate.depth,
            len(candidate.gate_sequence),
            gate_counts["rx"],
            gate_counts["ry"],
            gate_counts["rz"],
            gate_counts["cx"],
            gate_counts["cz"],
            gate_counts["h"],
            entanglement_map.get(candidate.entanglement, 0),
            candidate.num_qubits * candidate.depth,  # Circuit volume
        ]

        return np.array(features, dtype=np.float32)

    def train(
        self,
        candidates: List[CircuitCandidate],
        epochs: int = 100,
        learning_rate: float = 0.01,
    ) -> Dict[str, Any]:
        """
        Train surrogate on evaluated circuits.

        Args:
            candidates: List of evaluated circuit candidates
            epochs: Training epochs
            learning_rate: Learning rate

        Returns:
            Training metrics
        """
        # Filter candidates with performance data
        evaluated = [c for c in candidates if c.performance is not None]

        if len(evaluated) < 10:
            return {"error": "Need at least 10 evaluated circuits"}

        # Prepare data
        X = np.array([self._encode_circuit(c) for c in evaluated])
        y = np.array([c.performance for c in evaluated])

        # Simple normalization
        self.scaler_X = (X.mean(axis=0), X.std(axis=0) + 1e-8)
        self.scaler_y = (y.mean(), y.std() + 1e-8)

        X_norm = (X - self.scaler_X[0]) / self.scaler_X[1]
        y_norm = (y - self.scaler_y[0]) / self.scaler_y[1]

        # Simple MLP with numpy (no external dependencies)
        np.random.seed(42)

        # Initialize weights
        layers = [X.shape[1]] + self.hidden_sizes + [1]
        self.weights = []
        self.biases = []

        for i in range(len(layers) - 1):
            w = np.random.randn(layers[i], layers[i + 1]) * 0.1
            b = np.zeros(layers[i + 1])
            self.weights.append(w)
            self.biases.append(b)

        # Training loop (simple gradient descent)
        losses = []
        for epoch in range(epochs):
            # Forward pass
            activations = [X_norm]
            for i, (w, b) in enumerate(zip(self.weights, self.biases)):
                z = activations[-1] @ w + b
                if i < len(self.weights) - 1:
                    a = np.maximum(0, z)  # ReLU
                else:
                    a = z  # Linear output
                activations.append(a)

            # Loss
            pred = activations[-1].flatten()
            loss = np.mean((pred - y_norm) ** 2)
            losses.append(loss)

            # Backward pass (simplified)
            n_samples = len(y_norm)
            delta = (pred - y_norm).reshape(-1, 1)  # (n_samples, 1)

            for i in range(len(self.weights) - 1, -1, -1):
                # Gradient for weights and biases
                dw = activations[i].T @ delta / n_samples
                db = delta.mean(axis=0)

                # Update
                self.weights[i] -= learning_rate * dw
                self.biases[i] -= learning_rate * db.flatten()

                # Backpropagate delta
                if i > 0:
                    delta = delta @ self.weights[i].T
                    # ReLU derivative
                    delta = delta * (activations[i] > 0).astype(float)

        self.is_trained = True

        # Compute final accuracy
        final_pred = self.predict_batch(evaluated)
        mae = np.mean(np.abs(final_pred - y))
        r2 = 1 - np.sum((y - final_pred) ** 2) / np.sum((y - y.mean()) ** 2)

        metrics = {
            "epochs": epochs,
            "final_loss": losses[-1],
            "mae": mae,
            "r2": r2,
            "training_samples": len(evaluated),
        }

        self.training_history.append(metrics)
        return metrics

    def predict(self, candidate: CircuitCandidate) -> float:
        """Predict performance for a circuit candidate."""
        if not self.is_trained:
            raise ValueError("Surrogate not trained")

        x = self._encode_circuit(candidate)
        x_norm = (x - self.scaler_X[0]) / self.scaler_X[1]

        # Forward pass
        a = x_norm
        for i, (w, b) in enumerate(zip(self.weights, self.biases)):
            z = a @ w + b
            if i < len(self.weights) - 1:
                a = np.maximum(0, z)
            else:
                a = z

        # Denormalize
        pred = a * self.scaler_y[1] + self.scaler_y[0]
        return float(pred)

    def predict_batch(self, candidates: List[CircuitCandidate]) -> np.ndarray:
        """Predict performance for multiple candidates."""
        return np.array([self.predict(c) for c in candidates])


class EvolutionaryQAS:
    """
    Simple evolutionary Quantum Architecture Search.

    Uses mutation and selection to find optimal ansatz structures.
    """

    def __init__(
        self,
        num_qubits: int = 4,
        population_size: int = 20,
        mutation_rate: float = 0.3,
        elite_fraction: float = 0.2,
    ):
        self.num_qubits = num_qubits
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.elite_fraction = elite_fraction

        self.gate_options = ["rx", "ry", "rz", "cx", "h"]
        self.entanglement_options = ["linear", "circular", "full"]

    def initialize_population(self) -> List[CircuitCandidate]:
        """Create initial random population."""
        population = []

        for _ in range(self.population_size):
            depth = np.random.randint(2, 8)
            gate_sequence = [np.random.choice(self.gate_options) for _ in range(depth * 2)]
            entanglement = np.random.choice(self.entanglement_options)

            candidate = CircuitCandidate(
                num_qubits=self.num_qubits,
                depth=depth,
                gate_sequence=gate_sequence,
                entanglement=entanglement,
                generation=0,
            )
            population.append(candidate)

        return population

    def mutate(self, candidate: CircuitCandidate, generation: int) -> CircuitCandidate:
        """Create mutated offspring from parent."""
        new_sequence = candidate.gate_sequence.copy()
        new_depth = candidate.depth
        new_entanglement = candidate.entanglement

        # Mutate gate sequence
        if np.random.random() < self.mutation_rate:
            if len(new_sequence) > 0:
                idx = np.random.randint(len(new_sequence))
                new_sequence[idx] = np.random.choice(self.gate_options)

        # Mutate depth (add/remove layer)
        if np.random.random() < self.mutation_rate * 0.5:
            if np.random.random() < 0.5 and new_depth > 2:
                new_depth -= 1
                new_sequence = new_sequence[:-2] if len(new_sequence) > 2 else new_sequence
            else:
                new_depth += 1
                new_sequence.extend([np.random.choice(self.gate_options) for _ in range(2)])

        # Mutate entanglement
        if np.random.random() < self.mutation_rate * 0.3:
            new_entanglement = np.random.choice(self.entanglement_options)

        return CircuitCandidate(
            num_qubits=self.num_qubits,
            depth=new_depth,
            gate_sequence=new_sequence,
            entanglement=new_entanglement,
            generation=generation,
            parent_id=candidate.circuit_id,
        )

    def select(self, population: List[CircuitCandidate]) -> List[CircuitCandidate]:
        """Select top performers for next generation."""
        # Sort by performance (higher is better)
        evaluated = [c for c in population if c.performance is not None]
        evaluated.sort(key=lambda c: c.performance or 0, reverse=True)

        # Keep elite
        n_elite = max(1, int(len(evaluated) * self.elite_fraction))
        return evaluated[:n_elite]


class AnsatzDesignExperiment:
    """
    Empirical validation experiment for the Ansatz Design acceleration loop.

    Demonstrates:
    1. Neural surrogate training and accuracy
    2. Surrogate-guided vs random search comparison
    3. Acceleration metrics from architecture search
    """

    def __init__(
        self,
        noise_profile_name: str = "manila",
        num_qubits: int = 4,
    ):
        """
        Initialize experiment.

        Args:
            noise_profile_name: Noise profile for simulation
            num_qubits: Number of qubits for circuits
        """
        self.backend = create_backend(noise_profile_name)
        self.num_qubits = num_qubits
        self.noise_profile_name = noise_profile_name

        self.surrogate = NeuralSurrogate()
        self.qas = EvolutionaryQAS(num_qubits=num_qubits)
        self.collector = ExperimentalMetricsCollector("ansatz_design")

        self.all_candidates: List[CircuitCandidate] = []
        self.search_history: List[Dict] = []

    def _build_circuit(self, candidate: CircuitCandidate) -> Any:
        """Build Qiskit circuit from candidate specification."""
        try:
            from qiskit import QuantumCircuit
            from qiskit.circuit import Parameter
        except ImportError:
            raise ImportError("qiskit required")

        qc = QuantumCircuit(candidate.num_qubits)

        # Add parameterized layers
        param_idx = 0
        for layer in range(candidate.depth):
            # Single-qubit gates
            for q in range(candidate.num_qubits):
                gate_idx = (layer * 2) % len(candidate.gate_sequence)
                gate = candidate.gate_sequence[gate_idx]

                if gate in ["rx", "ry", "rz"]:
                    param = Parameter(f"θ_{param_idx}")
                    param_idx += 1
                    if gate == "rx":
                        qc.rx(param, q)
                    elif gate == "ry":
                        qc.ry(param, q)
                    else:
                        qc.rz(param, q)
                elif gate == "h":
                    qc.h(q)

            # Entanglement
            if candidate.entanglement == "linear":
                for q in range(candidate.num_qubits - 1):
                    qc.cx(q, q + 1)
            elif candidate.entanglement == "circular":
                for q in range(candidate.num_qubits):
                    qc.cx(q, (q + 1) % candidate.num_qubits)
            elif candidate.entanglement == "full":
                for q1 in range(candidate.num_qubits):
                    for q2 in range(q1 + 1, candidate.num_qubits):
                        qc.cx(q1, q2)

        qc.measure_all()
        return qc

    def evaluate_candidate(
        self,
        candidate: CircuitCandidate,
        shots: int = 512,
    ) -> CircuitCandidate:
        """
        Evaluate circuit candidate on noisy simulator.

        Performance metric: probability of measuring target state.
        """
        start_time = time.time()

        try:
            circuit = self._build_circuit(candidate)

            # Bind random parameters
            params = {p: np.random.uniform(0, 2 * np.pi) for p in circuit.parameters}
            bound_circuit = circuit.assign_parameters(params)

            # Execute
            result = self.backend.execute(bound_circuit, shots=shots)

            # Performance: entropy-based metric (lower entropy = better)
            probs = list(result.probabilities.values())
            entropy = -sum(p * np.log2(p + 1e-10) for p in probs if p > 0)
            max_entropy = np.log2(len(probs))

            # Normalize: 1 = perfect (zero entropy), 0 = maximum entropy
            performance = 1 - (entropy / max_entropy) if max_entropy > 0 else 0

            candidate.performance = performance
            candidate.fidelity = max(probs) if probs else 0
            candidate.evaluation_time_ms = (time.time() - start_time) * 1000

        except Exception:
            candidate.performance = 0
            candidate.fidelity = 0
            candidate.evaluation_time_ms = (time.time() - start_time) * 1000

        return candidate

    def run_random_search(
        self,
        num_evaluations: int = 50,
        shots: int = 512,
    ) -> Dict[str, Any]:
        """
        Run random architecture search (baseline).

        Args:
            num_evaluations: Number of circuits to evaluate
            shots: Shots per evaluation

        Returns:
            Search results
        """
        print(f"Running random search ({num_evaluations} evaluations)...")

        candidates = []
        best_performance = 0
        best_candidate = None

        for i in range(num_evaluations):
            # Generate random candidate
            depth = np.random.randint(2, 8)
            gate_sequence = [np.random.choice(self.qas.gate_options) for _ in range(depth * 2)]
            entanglement = np.random.choice(self.qas.entanglement_options)

            candidate = CircuitCandidate(
                num_qubits=self.num_qubits,
                depth=depth,
                gate_sequence=gate_sequence,
                entanglement=entanglement,
            )

            # Evaluate
            candidate = self.evaluate_candidate(candidate, shots=shots)
            candidates.append(candidate)

            if candidate.performance > best_performance:
                best_performance = candidate.performance
                best_candidate = candidate

            if (i + 1) % 10 == 0:
                print(f"  Evaluated {i + 1}/{num_evaluations}, best: {best_performance:.3f}")

        return {
            "method": "random",
            "num_evaluations": num_evaluations,
            "best_performance": best_performance,
            "best_candidate": best_candidate.to_dict() if best_candidate else None,
            "candidates": candidates,
        }

    def run_surrogate_guided_search(
        self,
        num_evaluations: int = 50,
        initial_samples: int = 20,
        shots: int = 512,
    ) -> Dict[str, Any]:
        """
        Run surrogate-guided architecture search.

        Args:
            num_evaluations: Total evaluation budget
            initial_samples: Initial random samples for surrogate training
            shots: Shots per evaluation

        Returns:
            Search results
        """
        print(f"Running surrogate-guided search ({num_evaluations} evaluations)...")

        candidates = []
        best_performance = 0
        best_candidate = None

        # Phase 1: Initial random sampling
        print(f"  Phase 1: Initial sampling ({initial_samples} circuits)...")
        for i in range(initial_samples):
            depth = np.random.randint(2, 8)
            gate_sequence = [np.random.choice(self.qas.gate_options) for _ in range(depth * 2)]
            entanglement = np.random.choice(self.qas.entanglement_options)

            candidate = CircuitCandidate(
                num_qubits=self.num_qubits,
                depth=depth,
                gate_sequence=gate_sequence,
                entanglement=entanglement,
            )

            candidate = self.evaluate_candidate(candidate, shots=shots)
            candidates.append(candidate)

            if candidate.performance > best_performance:
                best_performance = candidate.performance
                best_candidate = candidate

        # Train surrogate
        print("  Training surrogate model...")
        train_metrics = self.surrogate.train(candidates, epochs=200)
        print(f"    Surrogate R²: {train_metrics.get('r2', 0):.3f}")

        # Phase 2: Surrogate-guided search
        remaining = num_evaluations - initial_samples
        print(f"  Phase 2: Surrogate-guided search ({remaining} evaluations)...")

        for i in range(remaining):
            # Generate candidates and predict with surrogate
            batch_size = 50
            test_candidates = []

            for _ in range(batch_size):
                depth = np.random.randint(2, 8)
                gate_sequence = [np.random.choice(self.qas.gate_options) for _ in range(depth * 2)]
                entanglement = np.random.choice(self.qas.entanglement_options)

                test_candidates.append(
                    CircuitCandidate(
                        num_qubits=self.num_qubits,
                        depth=depth,
                        gate_sequence=gate_sequence,
                        entanglement=entanglement,
                    )
                )

            # Predict and select best
            predictions = self.surrogate.predict_batch(test_candidates)
            best_idx = np.argmax(predictions)
            selected = test_candidates[best_idx]

            # Evaluate selected candidate
            selected = self.evaluate_candidate(selected, shots=shots)
            candidates.append(selected)

            if selected.performance > best_performance:
                best_performance = selected.performance
                best_candidate = selected

            # Periodically retrain surrogate
            if (i + 1) % 10 == 0:
                self.surrogate.train(candidates, epochs=100)
                print(
                    f"    Evaluated {initial_samples + i + 1}/{num_evaluations}, "
                    f"best: {best_performance:.3f}"
                )

        return {
            "method": "surrogate_guided",
            "num_evaluations": num_evaluations,
            "initial_samples": initial_samples,
            "best_performance": best_performance,
            "best_candidate": best_candidate.to_dict() if best_candidate else None,
            "surrogate_r2": train_metrics.get("r2", 0),
            "candidates": candidates,
        }

    def run_comparison_study(
        self,
        num_evaluations: int = 50,
        shots: int = 512,
    ) -> Dict[str, Any]:
        """
        Compare random vs surrogate-guided search.

        Args:
            num_evaluations: Evaluation budget for each method
            shots: Shots per evaluation

        Returns:
            Comparison results with acceleration metrics
        """
        print("=" * 60)
        print("Ansatz Design Loop - Comparison Study")
        print("=" * 60)
        print()

        # Run random search
        random_results = self.run_random_search(num_evaluations, shots)
        print()

        # Run surrogate-guided search
        surrogate_results = self.run_surrogate_guided_search(num_evaluations, shots=shots)
        print()

        # Compute acceleration metrics
        random_best = random_results["best_performance"]
        surrogate_best = surrogate_results["best_performance"]

        # Find evaluations to reach 90% of best
        def evals_to_threshold(candidates, threshold):
            for i, c in enumerate(candidates):
                if c.performance >= threshold:
                    return i + 1
            return len(candidates)

        threshold = 0.9 * max(random_best, surrogate_best)
        random_evals = evals_to_threshold(random_results["candidates"], threshold)
        surrogate_evals = evals_to_threshold(surrogate_results["candidates"], threshold)

        acceleration = random_evals / surrogate_evals if surrogate_evals > 0 else 1.0

        # Record metrics
        self.collector.record_run(
            iteration=0,
            circuit_depth=4,
            num_qubits=self.num_qubits,
            num_two_qubit_gates=self.num_qubits - 1,
            ideal_value=1.0,
            noisy_value=random_best,
            mitigated_value=surrogate_best,
            mitigation_overhead=surrogate_results["initial_samples"] / num_evaluations,
            random_evals_to_threshold=random_evals,
            surrogate_evals_to_threshold=surrogate_evals,
        )

        results = {
            "random_search": {
                "best_performance": random_best,
                "evaluations": num_evaluations,
            },
            "surrogate_guided": {
                "best_performance": surrogate_best,
                "evaluations": num_evaluations,
                "surrogate_r2": surrogate_results["surrogate_r2"],
            },
            "comparison": {
                "performance_improvement": (
                    (surrogate_best - random_best) / random_best if random_best > 0 else 0
                ),
                "evaluations_to_threshold": {
                    "random": random_evals,
                    "surrogate": surrogate_evals,
                },
                "acceleration": acceleration,
            },
            "summary": self._generate_summary(random_results, surrogate_results, acceleration),
        }

        self.search_history.append(results)
        self.all_candidates.extend(random_results["candidates"])
        self.all_candidates.extend(surrogate_results["candidates"])

        print(results["summary"])

        return results

    def _generate_summary(
        self,
        random_results: Dict,
        surrogate_results: Dict,
        acceleration: float,
    ) -> str:
        """Generate human-readable summary."""
        lines = [
            "",
            "=" * 60,
            "ANSATZ DESIGN LOOP - RESULTS SUMMARY",
            "=" * 60,
            "",
            "Random Search:",
            f"  Best Performance: {random_results['best_performance']:.4f}",
            f"  Evaluations: {random_results['num_evaluations']}",
            "",
            "Surrogate-Guided Search:",
            f"  Best Performance: {surrogate_results['best_performance']:.4f}",
            f"  Surrogate R²: {surrogate_results['surrogate_r2']:.3f}",
            f"  Evaluations: {surrogate_results['num_evaluations']}",
            "",
            f"Acceleration: {acceleration:.2f}x",
            f"Surrogate improves search efficiency by {(acceleration - 1) * 100:.0f}%",
            "",
            "=" * 60,
        ]
        return "\n".join(lines)

    def plot_results(self, save_path: Optional[str] = None):
        """Plot comparison results."""
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("matplotlib required for plotting")
            return

        if not self.search_history:
            print("No results to plot. Run comparison study first.")
            return

        results = self.search_history[-1]

        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        # 1. Performance comparison
        ax = axes[0]
        methods = ["Random", "Surrogate-Guided"]
        performances = [
            results["random_search"]["best_performance"],
            results["surrogate_guided"]["best_performance"],
        ]
        colors = ["red", "blue"]
        ax.bar(methods, performances, color=colors, alpha=0.7)
        ax.set_ylabel("Best Performance Found")
        ax.set_title("Search Performance Comparison")
        ax.set_ylim(0, 1)

        # 2. Convergence curves
        ax = axes[1]
        # Get candidates from all_candidates (first half random, second half surrogate)
        n = len(self.all_candidates) // 2
        random_candidates = self.all_candidates[:n]
        surrogate_candidates = self.all_candidates[n:]

        # Compute running best
        def running_best(candidates):
            best = 0
            curve = []
            for c in candidates:
                if c.performance and c.performance > best:
                    best = c.performance
                curve.append(best)
            return curve

        random_curve = running_best(random_candidates)
        surrogate_curve = running_best(surrogate_candidates)

        ax.plot(random_curve, label="Random", color="red", alpha=0.7)
        ax.plot(surrogate_curve, label="Surrogate-Guided", color="blue", alpha=0.7)
        ax.set_xlabel("Evaluations")
        ax.set_ylabel("Best Performance")
        ax.set_title("Convergence Comparison")
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 3. Acceleration summary
        ax = axes[2]
        ax.axis("off")

        summary_text = [
            "═" * 35,
            "ACCELERATION SUMMARY",
            "═" * 35,
            "",
            f"Acceleration: {results['comparison']['acceleration']:.2f}x",
            "",
            "Evaluations to 90% threshold:",
            f"  Random: {results['comparison']['evaluations_to_threshold']['random']}",
            f"  Surrogate: {results['comparison']['evaluations_to_threshold']['surrogate']}",
            "",
            f"Surrogate R²: {results['surrogate_guided']['surrogate_r2']:.3f}",
            "",
            "═" * 35,
        ]

        ax.text(
            0.5,
            0.5,
            "\n".join(summary_text),
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=11,
            family="monospace",
            bbox=dict(boxstyle="round", facecolor="lightgray", alpha=0.8),
        )

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
            print(f"Figure saved to {save_path}")
        else:
            plt.show()

    def save_results(self, filepath: str):
        """Save experiment results."""
        import json

        data = {
            "experiment": "ansatz_design",
            "noise_profile": self.noise_profile_name,
            "num_qubits": self.num_qubits,
            "search_history": self.search_history,
            "total_candidates": len(self.all_candidates),
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)

        print(f"Results saved to {filepath}")


class HardwareHeterogeneityStudy:
    """
    Study how ansatz performance transfers across different hardware noise profiles.

    Validates the bottleneck: hardware heterogeneity limits transfer of
    optimized circuits between devices.
    """

    def __init__(
        self,
        noise_profiles: List[str] = None,
        num_qubits: int = 4,
    ):
        """
        Initialize heterogeneity study.

        Args:
            noise_profiles: List of noise profile names to compare
            num_qubits: Number of qubits for circuits
        """
        self.noise_profiles = noise_profiles or ["manila", "kolkata", "ionq"]
        self.num_qubits = num_qubits
        self.results: Dict[str, Any] = {}
        self.transfer_matrix: Optional[np.ndarray] = None

    def run_study(
        self,
        num_evaluations: int = 30,
        shots: int = 512,
    ) -> Dict[str, Any]:
        """
        Run QAS on multiple noise profiles and measure transfer degradation.

        Args:
            num_evaluations: Evaluations per profile
            shots: Shots per circuit evaluation

        Returns:
            Study results with transfer analysis
        """
        print("=" * 60)
        print("Hardware Heterogeneity Study")
        print("=" * 60)
        print(f"Noise profiles: {self.noise_profiles}")
        print(f"Qubits: {self.num_qubits}")
        print()

        # Run QAS on each profile
        profile_results = {}
        best_circuits = {}

        for profile in self.noise_profiles:
            print(f"\n--- Running QAS on {profile} ---")
            experiment = AnsatzDesignExperiment(
                noise_profile_name=profile,
                num_qubits=self.num_qubits,
            )

            # Run surrogate-guided search
            results = experiment.run_surrogate_guided_search(
                num_evaluations=num_evaluations,
                initial_samples=min(20, num_evaluations // 2),
                shots=shots,
            )

            profile_results[profile] = {
                "best_performance": results["best_performance"],
                "best_candidate": results["best_candidate"],
                "surrogate_r2": results["surrogate_r2"],
            }

            # Store best circuit for transfer testing
            best_circuits[profile] = results["candidates"][
                np.argmax([c.performance or 0 for c in results["candidates"]])
            ]

        # Test transfer: evaluate each best circuit on all profiles
        print("\n--- Testing Circuit Transfer ---")
        transfer_matrix = np.zeros((len(self.noise_profiles), len(self.noise_profiles)))

        for i, source_profile in enumerate(self.noise_profiles):
            source_circuit = best_circuits[source_profile]
            print(f"\nCircuit optimized on {source_profile}:")

            for j, target_profile in enumerate(self.noise_profiles):
                # Create experiment with target profile
                target_exp = AnsatzDesignExperiment(
                    noise_profile_name=target_profile,
                    num_qubits=self.num_qubits,
                )

                # Evaluate source circuit on target
                evaluated = target_exp.evaluate_candidate(source_circuit, shots=shots)
                transfer_matrix[i, j] = evaluated.performance or 0

                degradation = ""
                if i != j:
                    orig_perf = (
                        transfer_matrix[i, i]
                        if i == j
                        else profile_results[source_profile]["best_performance"]
                    )
                    if orig_perf > 0:
                        deg_pct = (1 - evaluated.performance / orig_perf) * 100
                        degradation = (
                            f" ({deg_pct:+.1f}% degradation)"
                            if deg_pct > 0
                            else f" ({-deg_pct:.1f}% improvement)"
                        )

                print(f"  → {target_profile}: {evaluated.performance:.4f}{degradation}")

        self.transfer_matrix = transfer_matrix

        # Compute transfer metrics
        transfer_metrics = self._compute_transfer_metrics(transfer_matrix)

        self.results = {
            "profile_results": profile_results,
            "transfer_matrix": transfer_matrix.tolist(),
            "transfer_metrics": transfer_metrics,
            "noise_profiles": self.noise_profiles,
            "summary": self._generate_summary(profile_results, transfer_metrics),
        }

        print(self.results["summary"])

        return self.results

    def _compute_transfer_metrics(self, transfer_matrix: np.ndarray) -> Dict[str, Any]:
        """Compute metrics quantifying transfer degradation."""
        n = len(self.noise_profiles)

        # Diagonal = native performance
        native_performance = np.diag(transfer_matrix)

        # Off-diagonal = transfer performance
        transfer_performances = []
        degradations = []

        for i in range(n):
            for j in range(n):
                if i != j:
                    transfer_performances.append(transfer_matrix[i, j])
                    if native_performance[i] > 0:
                        deg = 1 - transfer_matrix[i, j] / native_performance[i]
                        degradations.append(deg)

        avg_native = np.mean(native_performance)
        avg_transfer = np.mean(transfer_performances) if transfer_performances else 0
        avg_degradation = np.mean(degradations) if degradations else 0

        # Transferability score: how well circuits transfer (1 = perfect, 0 = complete failure)
        transferability = avg_transfer / avg_native if avg_native > 0 else 0

        return {
            "avg_native_performance": float(avg_native),
            "avg_transfer_performance": float(avg_transfer),
            "avg_degradation": float(avg_degradation),
            "transferability_score": float(transferability),
            "heterogeneity_impact": float(1 - transferability),
            "native_performances": native_performance.tolist(),
        }

    def _generate_summary(
        self,
        profile_results: Dict,
        transfer_metrics: Dict,
    ) -> str:
        """Generate human-readable summary."""
        lines = [
            "",
            "=" * 60,
            "HARDWARE HETEROGENEITY STUDY - RESULTS",
            "=" * 60,
            "",
            "Native Performance (optimized on same device):",
        ]

        for profile, results in profile_results.items():
            lines.append(f"  {profile}: {results['best_performance']:.4f}")

        lines.extend(
            [
                "",
                "Transfer Metrics:",
                f"  Avg Native Performance: {transfer_metrics['avg_native_performance']:.4f}",
                f"  Avg Transfer Performance: {transfer_metrics['avg_transfer_performance']:.4f}",
                f"  Avg Degradation: {transfer_metrics['avg_degradation']:.1%}",
                "",
                f"  Transferability Score: {transfer_metrics['transferability_score']:.2f}",
                f"  Heterogeneity Impact: {transfer_metrics['heterogeneity_impact']:.1%}",
                "",
                "Bottleneck Validated: "
                + (
                    "YES - Hardware heterogeneity significantly limits transfer"
                    if transfer_metrics["avg_degradation"] > 0.1
                    else (
                        "PARTIAL - Some degradation observed"
                        if transfer_metrics["avg_degradation"] > 0.05
                        else "NO - Circuits transfer well across devices"
                    )
                ),
                "",
                "=" * 60,
            ]
        )

        return "\n".join(lines)

    def plot_results(self, save_path: Optional[str] = None):
        """Plot heterogeneity study results."""
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("matplotlib required for plotting")
            return

        if self.transfer_matrix is None:
            print("No results to plot. Run study first.")
            return

        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        # 1. Transfer matrix heatmap
        ax = axes[0]
        im = ax.imshow(self.transfer_matrix, cmap="RdYlGn", vmin=0, vmax=1)
        ax.set_xticks(range(len(self.noise_profiles)))
        ax.set_yticks(range(len(self.noise_profiles)))
        ax.set_xticklabels(self.noise_profiles, rotation=45, ha="right")
        ax.set_yticklabels(self.noise_profiles)
        ax.set_xlabel("Target Device")
        ax.set_ylabel("Source Device (optimized on)")
        ax.set_title("Circuit Transfer Matrix")

        # Add values
        for i in range(len(self.noise_profiles)):
            for j in range(len(self.noise_profiles)):
                val = self.transfer_matrix[i, j]
                color = "white" if val < 0.5 else "black"
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=color)

        plt.colorbar(im, ax=ax, label="Performance")

        # 2. Native vs Transfer performance
        ax = axes[1]
        x = np.arange(len(self.noise_profiles))
        width = 0.35

        native = np.diag(self.transfer_matrix)
        transfer_avg = []
        for i in range(len(self.noise_profiles)):
            others = [self.transfer_matrix[i, j] for j in range(len(self.noise_profiles)) if i != j]
            transfer_avg.append(np.mean(others) if others else 0)

        ax.bar(x - width / 2, native, width, label="Native", color="green", alpha=0.7)
        ax.bar(
            x + width / 2, transfer_avg, width, label="Transfer (avg)", color="orange", alpha=0.7
        )
        ax.set_xticks(x)
        ax.set_xticklabels(self.noise_profiles)
        ax.set_ylabel("Performance")
        ax.set_title("Native vs Transfer Performance")
        ax.legend()
        ax.set_ylim(0, 1)

        # 3. Summary
        ax = axes[2]
        ax.axis("off")

        metrics = self.results.get("transfer_metrics", {})
        summary_text = [
            "═" * 35,
            "HETEROGENEITY SUMMARY",
            "═" * 35,
            "",
            f"Transferability: {metrics.get('transferability_score', 0):.2f}",
            f"Heterogeneity Impact: {metrics.get('heterogeneity_impact', 0):.1%}",
            "",
            f"Avg Degradation: {metrics.get('avg_degradation', 0):.1%}",
            "",
            "Bottleneck: "
            + ("VALIDATED ✓" if metrics.get("avg_degradation", 0) > 0.1 else "PARTIAL"),
            "",
            "═" * 35,
        ]

        ax.text(
            0.5,
            0.5,
            "\n".join(summary_text),
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=11,
            family="monospace",
            bbox=dict(boxstyle="round", facecolor="lightgray", alpha=0.8),
        )

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
            print(f"Figure saved to {save_path}")
        else:
            plt.show()

    def save_results(self, filepath: str):
        """Save study results."""
        import json

        with open(filepath, "w") as f:
            json.dump(self.results, f, indent=2, default=str)

        print(f"Results saved to {filepath}")


def run_demo():
    """Run demonstration of Ansatz Design experiment."""
    print("=" * 60)
    print("Ansatz Design Loop - Empirical Validation Demo")
    print("=" * 60)
    print()

    experiment = AnsatzDesignExperiment(noise_profile_name="manila", num_qubits=4)

    results = experiment.run_comparison_study(num_evaluations=30, shots=512)

    return experiment, results


if __name__ == "__main__":
    run_demo()
