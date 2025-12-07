"""
Cross-loop validation experiments for the Reciprocal Acceleration Framework.

This module implements integrated experiments that demonstrate and quantify
how improvements in one acceleration loop benefit other loops.

Key experiments:
1. Integrated experiment: better calibration → better mitigation → larger circuits
2. Cross-loop coupling quantification from experimental data
3. Validation that improvements cascade across loops
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np

from raf.backends.noise_models import DeviceNoiseProfile


@dataclass
class LoopState:
    """State of a single loop at a point in time."""

    loop_name: str
    iteration: int
    timestamp: datetime
    primary_metric: float
    secondary_metrics: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "loop_name": self.loop_name,
            "iteration": self.iteration,
            "timestamp": self.timestamp.isoformat(),
            "primary_metric": self.primary_metric,
            "secondary_metrics": self.secondary_metrics,
            "metadata": self.metadata,
        }


@dataclass
class CrossLoopEffect:
    """Measured effect of one loop's improvement on another."""

    source_loop: str
    target_loop: str
    source_improvement: float  # Relative improvement in source
    target_improvement: float  # Resulting improvement in target
    coupling_strength: float  # Estimated coupling (target/source)
    lag_iterations: int  # Iterations before effect manifests
    confidence: float  # Statistical confidence
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_loop": self.source_loop,
            "target_loop": self.target_loop,
            "source_improvement": self.source_improvement,
            "target_improvement": self.target_improvement,
            "coupling_strength": self.coupling_strength,
            "lag_iterations": self.lag_iterations,
            "confidence": self.confidence,
            "description": self.description,
        }


@dataclass
class IntegratedExperimentResult:
    """Results from an integrated cross-loop experiment."""

    # Per-iteration data
    calibration_accuracy: List[float]
    gate_fidelity: List[float]
    mitigation_effectiveness: List[float]
    max_circuit_depth: List[int]
    error_rates: List[float]

    # Cross-loop effects
    calibration_to_mitigation: CrossLoopEffect
    mitigation_to_depth: CrossLoopEffect
    calibration_to_depth: CrossLoopEffect  # Second-order effect

    # Summary metrics
    total_iterations: int
    overall_improvement: float
    cascade_amplification: float  # How much cross-loop effects amplify gains

    def to_dict(self) -> Dict[str, Any]:
        return {
            "calibration_accuracy": self.calibration_accuracy,
            "gate_fidelity": self.gate_fidelity,
            "mitigation_effectiveness": self.mitigation_effectiveness,
            "max_circuit_depth": self.max_circuit_depth,
            "error_rates": self.error_rates,
            "calibration_to_mitigation": self.calibration_to_mitigation.to_dict(),
            "mitigation_to_depth": self.mitigation_to_depth.to_dict(),
            "calibration_to_depth": self.calibration_to_depth.to_dict(),
            "total_iterations": self.total_iterations,
            "overall_improvement": self.overall_improvement,
            "cascade_amplification": self.cascade_amplification,
        }


@dataclass
class CouplingMeasurement:
    """Single measurement of cross-loop coupling."""

    source_loop: str
    target_loop: str
    source_delta: float  # Change in source metric
    target_delta: float  # Resulting change in target metric
    iteration: int
    timestamp: datetime

    @property
    def instantaneous_coupling(self) -> float:
        """Compute instantaneous coupling strength."""
        if abs(self.source_delta) < 1e-10:
            return 0.0
        return self.target_delta / self.source_delta


class CrossLoopValidationExperiment:
    """
    Validates cross-loop acceleration through integrated experiments.

    This experiment demonstrates the core RAF hypothesis:
    improvements in one loop cascade to benefit other loops.

    The integrated experiment flow:
    1. Calibration Loop: Better noise characterization → higher gate fidelity
    2. Error Mitigation Loop: Better fidelity → more effective mitigation
    3. Circuit Scaling: Better mitigation → can run deeper circuits

    Example:
        >>> experiment = CrossLoopValidationExperiment(random_seed=42)
        >>> result = experiment.run_integrated_experiment(n_iterations=10)
        >>> print(f"Cascade amplification: {result.cascade_amplification:.2f}x")
        >>> print(f"Calibration→Mitigation coupling: {result.calibration_to_mitigation.coupling_strength:.2f}")
    """

    def __init__(
        self,
        noise_profile: Optional[DeviceNoiseProfile] = None,
        random_seed: Optional[int] = None,
    ):
        """
        Initialize cross-loop validation experiment.

        Args:
            noise_profile: Device noise profile (default: IBM Manila-like)
            random_seed: For reproducibility
        """
        self.noise_profile = noise_profile or DeviceNoiseProfile.ibm_manila_like()
        self.rng = np.random.default_rng(random_seed)

        # State tracking
        self.loop_states: Dict[str, List[LoopState]] = {
            "calibration": [],
            "mitigation": [],
            "circuit_scaling": [],
        }
        self.coupling_measurements: List[CouplingMeasurement] = []

        # Initialize loop parameters
        self._init_loop_parameters()

    def _init_loop_parameters(self):
        """Initialize parameters for each simulated loop."""
        # Calibration loop state
        self.calibration_state = {
            "noise_model_accuracy": 0.5,  # How well we characterize noise
            "gate_fidelity": 0.99,  # Current gate fidelity
            "drift_tracking_accuracy": 0.3,  # How well we track drift
        }

        # Error mitigation loop state
        self.mitigation_state = {
            "mitigation_effectiveness": 0.3,  # Error reduction factor
            "overhead_factor": 3.0,  # Computational overhead
            "training_data_quality": 0.5,  # Quality of training data
        }

        # Circuit scaling state
        self.circuit_state = {
            "max_reliable_depth": 20,  # Max depth with acceptable fidelity
            "effective_qubits": 3,  # Effective number of qubits
            "circuit_fidelity_threshold": 0.9,  # Minimum acceptable fidelity
        }

    def _simulate_calibration_improvement(
        self,
        iteration: int,
        base_improvement: float = 0.05,
    ) -> Dict[str, float]:
        """
        Simulate one iteration of calibration loop improvement.

        Returns updated calibration metrics.
        """
        # Diminishing returns as we approach perfect calibration
        room_for_improvement = 1.0 - self.calibration_state["noise_model_accuracy"]
        actual_improvement = base_improvement * room_for_improvement

        # Add some noise
        actual_improvement *= 1.0 + 0.2 * self.rng.standard_normal()
        actual_improvement = max(0, actual_improvement)

        # Update state
        self.calibration_state["noise_model_accuracy"] = min(
            0.99, self.calibration_state["noise_model_accuracy"] + actual_improvement
        )

        # Better noise models → better gate fidelity
        fidelity_improvement = actual_improvement * 0.3  # Coupling factor
        self.calibration_state["gate_fidelity"] = min(
            0.9999,
            self.calibration_state["gate_fidelity"]
            + fidelity_improvement * (0.9999 - self.calibration_state["gate_fidelity"]),
        )

        # Drift tracking improves with better models
        self.calibration_state["drift_tracking_accuracy"] = min(
            0.95,
            self.calibration_state["drift_tracking_accuracy"] + actual_improvement * 0.5,
        )

        return {
            "accuracy_improvement": actual_improvement,
            "fidelity_improvement": fidelity_improvement,
        }

    def _simulate_mitigation_improvement(
        self,
        iteration: int,
        calibration_quality: float,
    ) -> Dict[str, float]:
        """
        Simulate one iteration of error mitigation loop.

        Mitigation effectiveness depends on calibration quality.
        """
        # Base improvement from more training data
        base_improvement = 0.04

        # Calibration quality boosts mitigation effectiveness
        # This is the key cross-loop coupling!
        calibration_boost = calibration_quality * 0.5

        # Diminishing returns
        room_for_improvement = 1.0 - self.mitigation_state["mitigation_effectiveness"]
        actual_improvement = (base_improvement + calibration_boost) * room_for_improvement

        # Add noise
        actual_improvement *= 1.0 + 0.15 * self.rng.standard_normal()
        actual_improvement = max(0, actual_improvement)

        # Update state
        self.mitigation_state["mitigation_effectiveness"] = min(
            0.95, self.mitigation_state["mitigation_effectiveness"] + actual_improvement
        )

        # Better mitigation → can reduce overhead
        self.mitigation_state["overhead_factor"] = max(
            1.5, self.mitigation_state["overhead_factor"] - actual_improvement * 2
        )

        # Training data quality improves with better calibration
        self.mitigation_state["training_data_quality"] = min(
            0.95,
            0.5 * calibration_quality + 0.5 * self.mitigation_state["training_data_quality"],
        )

        return {
            "effectiveness_improvement": actual_improvement,
            "calibration_contribution": calibration_boost * room_for_improvement,
        }

    def _simulate_circuit_scaling(
        self,
        iteration: int,
        gate_fidelity: float,
        mitigation_effectiveness: float,
    ) -> Dict[str, float]:
        """
        Simulate circuit scaling based on fidelity and mitigation.

        Max circuit depth depends on both gate fidelity and mitigation.
        """
        # Compute effective error rate after mitigation
        base_error_rate = 1.0 - gate_fidelity
        mitigated_error_rate = base_error_rate * (1.0 - mitigation_effectiveness)

        # Max depth where circuit fidelity stays above threshold
        # Fidelity ≈ (1 - error_rate)^depth
        if mitigated_error_rate > 0:
            target_fidelity = self.circuit_state["circuit_fidelity_threshold"]
            max_depth = int(np.log(target_fidelity) / np.log(1 - mitigated_error_rate))
            max_depth = max(10, min(1000, max_depth))
        else:
            max_depth = 1000

        # Smooth update (don't jump instantly)
        old_depth = self.circuit_state["max_reliable_depth"]
        self.circuit_state["max_reliable_depth"] = int(0.7 * old_depth + 0.3 * max_depth)

        # Effective qubits also scale with fidelity
        self.circuit_state["effective_qubits"] = min(
            20, int(3 + 17 * gate_fidelity * mitigation_effectiveness)
        )

        return {
            "depth_improvement": self.circuit_state["max_reliable_depth"] - old_depth,
            "mitigated_error_rate": mitigated_error_rate,
        }

    def run_integrated_experiment(
        self,
        n_iterations: int = 10,
        verbose: bool = True,
    ) -> IntegratedExperimentResult:
        """
        Run the integrated cross-loop experiment.

        Demonstrates: better calibration → better mitigation → larger circuits

        Args:
            n_iterations: Number of iterations to run
            verbose: Print progress

        Returns:
            IntegratedExperimentResult with all metrics and coupling measurements
        """
        if verbose:
            print("=" * 60)
            print("Cross-Loop Validation: Integrated Experiment")
            print("=" * 60)
            print(f"Running {n_iterations} iterations...")
            print()

        # Reset state
        self._init_loop_parameters()
        self.loop_states = {k: [] for k in self.loop_states}
        self.coupling_measurements = []

        # Track metrics over iterations
        calibration_accuracy = []
        gate_fidelity = []
        mitigation_effectiveness = []
        max_circuit_depth = []
        error_rates = []

        for iteration in range(n_iterations):
            timestamp = datetime.now()

            # Store previous values for coupling measurement
            prev_calibration = self.calibration_state["noise_model_accuracy"]
            prev_mitigation = self.mitigation_state["mitigation_effectiveness"]
            prev_depth = self.circuit_state["max_reliable_depth"]

            # 1. Calibration loop iteration
            self._simulate_calibration_improvement(iteration)

            # 2. Mitigation loop iteration (depends on calibration)
            self._simulate_mitigation_improvement(
                iteration,
                calibration_quality=self.calibration_state["noise_model_accuracy"],
            )

            # 3. Circuit scaling (depends on both)
            scale_result = self._simulate_circuit_scaling(
                iteration,
                gate_fidelity=self.calibration_state["gate_fidelity"],
                mitigation_effectiveness=self.mitigation_state["mitigation_effectiveness"],
            )

            # Record metrics
            calibration_accuracy.append(self.calibration_state["noise_model_accuracy"])
            gate_fidelity.append(self.calibration_state["gate_fidelity"])
            mitigation_effectiveness.append(self.mitigation_state["mitigation_effectiveness"])
            max_circuit_depth.append(self.circuit_state["max_reliable_depth"])
            error_rates.append(scale_result["mitigated_error_rate"])

            # Record loop states
            self.loop_states["calibration"].append(
                LoopState(
                    loop_name="calibration",
                    iteration=iteration,
                    timestamp=timestamp,
                    primary_metric=self.calibration_state["noise_model_accuracy"],
                    secondary_metrics={
                        "gate_fidelity": self.calibration_state["gate_fidelity"],
                        "drift_tracking": self.calibration_state["drift_tracking_accuracy"],
                    },
                )
            )

            self.loop_states["mitigation"].append(
                LoopState(
                    loop_name="mitigation",
                    iteration=iteration,
                    timestamp=timestamp,
                    primary_metric=self.mitigation_state["mitigation_effectiveness"],
                    secondary_metrics={
                        "overhead": self.mitigation_state["overhead_factor"],
                        "data_quality": self.mitigation_state["training_data_quality"],
                    },
                )
            )

            self.loop_states["circuit_scaling"].append(
                LoopState(
                    loop_name="circuit_scaling",
                    iteration=iteration,
                    timestamp=timestamp,
                    primary_metric=float(self.circuit_state["max_reliable_depth"]),
                    secondary_metrics={
                        "effective_qubits": float(self.circuit_state["effective_qubits"]),
                        "error_rate": scale_result["mitigated_error_rate"],
                    },
                )
            )

            # Record coupling measurements
            cal_delta = self.calibration_state["noise_model_accuracy"] - prev_calibration
            mit_delta = self.mitigation_state["mitigation_effectiveness"] - prev_mitigation
            depth_delta = self.circuit_state["max_reliable_depth"] - prev_depth

            if abs(cal_delta) > 1e-6:
                self.coupling_measurements.append(
                    CouplingMeasurement(
                        source_loop="calibration",
                        target_loop="mitigation",
                        source_delta=cal_delta,
                        target_delta=mit_delta,
                        iteration=iteration,
                        timestamp=timestamp,
                    )
                )

            if abs(mit_delta) > 1e-6:
                self.coupling_measurements.append(
                    CouplingMeasurement(
                        source_loop="mitigation",
                        target_loop="circuit_scaling",
                        source_delta=mit_delta,
                        target_delta=float(depth_delta),
                        iteration=iteration,
                        timestamp=timestamp,
                    )
                )

            if verbose and (iteration + 1) % max(1, n_iterations // 5) == 0:
                print(f"Iteration {iteration + 1}/{n_iterations}:")
                print(f"  Calibration accuracy: {calibration_accuracy[-1]:.3f}")
                print(f"  Gate fidelity: {gate_fidelity[-1]:.5f}")
                print(f"  Mitigation effectiveness: {mitigation_effectiveness[-1]:.3f}")
                print(f"  Max circuit depth: {max_circuit_depth[-1]}")
                print(f"  Error rate: {error_rates[-1]:.5f}")
                print()

        # Compute cross-loop effects
        cal_to_mit = self._compute_coupling_effect(
            "calibration", "mitigation", calibration_accuracy, mitigation_effectiveness
        )
        mit_to_depth = self._compute_coupling_effect(
            "mitigation",
            "circuit_scaling",
            mitigation_effectiveness,
            [float(d) for d in max_circuit_depth],
        )
        cal_to_depth = self._compute_coupling_effect(
            "calibration",
            "circuit_scaling",
            calibration_accuracy,
            [float(d) for d in max_circuit_depth],
        )

        # Compute overall improvement
        initial_depth = max_circuit_depth[0] if max_circuit_depth else 20
        final_depth = max_circuit_depth[-1] if max_circuit_depth else 20
        overall_improvement = (final_depth - initial_depth) / max(1, initial_depth)

        # Compute cascade amplification
        # Compare actual improvement to what we'd get without cross-loop effects
        direct_improvement = (calibration_accuracy[-1] - calibration_accuracy[0]) * 0.3
        cascade_amplification = overall_improvement / max(0.01, direct_improvement)

        result = IntegratedExperimentResult(
            calibration_accuracy=calibration_accuracy,
            gate_fidelity=gate_fidelity,
            mitigation_effectiveness=mitigation_effectiveness,
            max_circuit_depth=max_circuit_depth,
            error_rates=error_rates,
            calibration_to_mitigation=cal_to_mit,
            mitigation_to_depth=mit_to_depth,
            calibration_to_depth=cal_to_depth,
            total_iterations=n_iterations,
            overall_improvement=overall_improvement,
            cascade_amplification=cascade_amplification,
        )

        if verbose:
            print("=" * 60)
            print("Results Summary")
            print("=" * 60)
            print(f"Overall depth improvement: {overall_improvement:.1%}")
            print(f"Cascade amplification: {cascade_amplification:.2f}x")
            print()
            print("Cross-loop coupling strengths:")
            print(f"  Calibration → Mitigation: {cal_to_mit.coupling_strength:.3f}")
            print(f"  Mitigation → Circuit Depth: {mit_to_depth.coupling_strength:.3f}")
            print(f"  Calibration → Circuit Depth: {cal_to_depth.coupling_strength:.3f}")

        return result

    def _compute_coupling_effect(
        self,
        source_loop: str,
        target_loop: str,
        source_values: List[float],
        target_values: List[float],
    ) -> CrossLoopEffect:
        """Compute coupling effect between two loops from time series data."""
        if len(source_values) < 2 or len(target_values) < 2:
            return CrossLoopEffect(
                source_loop=source_loop,
                target_loop=target_loop,
                source_improvement=0.0,
                target_improvement=0.0,
                coupling_strength=0.0,
                lag_iterations=0,
                confidence=0.0,
            )

        # Compute improvements
        source_improvement = (source_values[-1] - source_values[0]) / max(0.01, source_values[0])
        target_improvement = (target_values[-1] - target_values[0]) / max(0.01, target_values[0])

        # Compute correlation as proxy for coupling
        source_arr = np.array(source_values)
        target_arr = np.array(target_values)

        # Normalize
        source_norm = (source_arr - source_arr.mean()) / max(1e-6, source_arr.std())
        target_norm = (target_arr - target_arr.mean()) / max(1e-6, target_arr.std())

        # Cross-correlation to find lag
        correlation = np.correlate(source_norm, target_norm, mode="full")
        lag = np.argmax(correlation) - len(source_values) + 1

        # Coupling strength from correlation at optimal lag
        max_corr = np.max(correlation) / len(source_values)
        coupling_strength = min(1.0, max(0.0, max_corr))

        # Confidence based on sample size and correlation strength
        confidence = min(1.0, len(source_values) / 20) * coupling_strength

        return CrossLoopEffect(
            source_loop=source_loop,
            target_loop=target_loop,
            source_improvement=source_improvement,
            target_improvement=target_improvement,
            coupling_strength=coupling_strength,
            lag_iterations=max(0, lag),
            confidence=confidence,
            description=f"Improvements in {source_loop} lead to {target_improvement:.1%} "
            f"improvement in {target_loop}",
        )

    def quantify_coupling_from_data(
        self,
        source_loop: str,
        target_loop: str,
    ) -> Dict[str, Any]:
        """
        Quantify cross-loop coupling from collected experimental data.

        Args:
            source_loop: Name of source loop
            target_loop: Name of target loop

        Returns:
            Dictionary with coupling statistics
        """
        # Filter relevant measurements
        measurements = [
            m
            for m in self.coupling_measurements
            if m.source_loop == source_loop and m.target_loop == target_loop
        ]

        if not measurements:
            return {
                "source_loop": source_loop,
                "target_loop": target_loop,
                "n_measurements": 0,
                "mean_coupling": 0.0,
                "std_coupling": 0.0,
                "confidence": 0.0,
            }

        # Compute coupling statistics
        couplings = [m.instantaneous_coupling for m in measurements]
        couplings = [c for c in couplings if np.isfinite(c)]

        if not couplings:
            return {
                "source_loop": source_loop,
                "target_loop": target_loop,
                "n_measurements": len(measurements),
                "mean_coupling": 0.0,
                "std_coupling": 0.0,
                "confidence": 0.0,
            }

        mean_coupling = float(np.mean(couplings))
        std_coupling = float(np.std(couplings))

        # Confidence based on consistency and sample size
        cv = std_coupling / max(0.01, abs(mean_coupling))  # Coefficient of variation
        confidence = min(1.0, len(couplings) / 10) * max(0, 1 - cv)

        return {
            "source_loop": source_loop,
            "target_loop": target_loop,
            "n_measurements": len(measurements),
            "mean_coupling": mean_coupling,
            "std_coupling": std_coupling,
            "confidence": confidence,
            "measurements": [m.instantaneous_coupling for m in measurements[-10:]],
        }

    def validate_cross_loop_benefit(
        self,
        n_trials: int = 5,
        iterations_per_trial: int = 10,
    ) -> Dict[str, Any]:
        """
        Validate that improvements in one loop benefit others.

        Runs multiple trials comparing:
        1. Isolated improvement (only one loop improves)
        2. Coupled improvement (all loops improve together)

        Args:
            n_trials: Number of trials to run
            iterations_per_trial: Iterations per trial

        Returns:
            Validation results with statistical comparison
        """
        isolated_results = []
        coupled_results = []

        for trial in range(n_trials):
            # Run coupled experiment (normal)
            self._init_loop_parameters()
            coupled_result = self.run_integrated_experiment(
                n_iterations=iterations_per_trial,
                verbose=False,
            )
            coupled_results.append(coupled_result.overall_improvement)

            # Run isolated experiment (disable cross-loop effects)
            self._init_loop_parameters()
            isolated_improvement = self._run_isolated_experiment(iterations_per_trial)
            isolated_results.append(isolated_improvement)

        # Statistical comparison
        coupled_mean = float(np.mean(coupled_results))
        coupled_std = float(np.std(coupled_results))
        isolated_mean = float(np.mean(isolated_results))
        isolated_std = float(np.std(isolated_results))

        # Effect size (Cohen's d)
        pooled_std = np.sqrt((coupled_std**2 + isolated_std**2) / 2)
        effect_size = (coupled_mean - isolated_mean) / max(0.01, pooled_std)

        # Benefit ratio
        benefit_ratio = coupled_mean / max(0.01, isolated_mean)

        return {
            "n_trials": n_trials,
            "coupled_improvement": {
                "mean": coupled_mean,
                "std": coupled_std,
            },
            "isolated_improvement": {
                "mean": isolated_mean,
                "std": isolated_std,
            },
            "benefit_ratio": benefit_ratio,
            "effect_size": effect_size,
            "cross_loop_benefit_validated": benefit_ratio > 1.2 and effect_size > 0.5,
            "interpretation": self._interpret_validation(benefit_ratio, effect_size),
        }

    def _run_isolated_experiment(self, n_iterations: int) -> float:
        """Run experiment with cross-loop effects disabled."""
        initial_depth = self.circuit_state["max_reliable_depth"]

        for iteration in range(n_iterations):
            # Only calibration improves, no coupling to other loops
            room = 1.0 - self.calibration_state["noise_model_accuracy"]
            improvement = 0.05 * room * (1.0 + 0.2 * self.rng.standard_normal())
            self.calibration_state["noise_model_accuracy"] = min(
                0.99, self.calibration_state["noise_model_accuracy"] + max(0, improvement)
            )

            # Mitigation improves independently (no calibration boost)
            room = 1.0 - self.mitigation_state["mitigation_effectiveness"]
            improvement = 0.04 * room * (1.0 + 0.15 * self.rng.standard_normal())
            self.mitigation_state["mitigation_effectiveness"] = min(
                0.95, self.mitigation_state["mitigation_effectiveness"] + max(0, improvement)
            )

            # Circuit depth based only on base fidelity (no mitigation benefit)
            base_error = 1.0 - self.calibration_state["gate_fidelity"]
            if base_error > 0:
                max_depth = int(np.log(0.9) / np.log(1 - base_error))
                max_depth = max(10, min(1000, max_depth))
            else:
                max_depth = 1000

            self.circuit_state["max_reliable_depth"] = int(
                0.7 * self.circuit_state["max_reliable_depth"] + 0.3 * max_depth
            )

        final_depth = self.circuit_state["max_reliable_depth"]
        return (final_depth - initial_depth) / max(1, initial_depth)

    def _interpret_validation(self, benefit_ratio: float, effect_size: float) -> str:
        """Generate interpretation of validation results."""
        if benefit_ratio > 2.0 and effect_size > 1.0:
            return (
                "Strong validation: Cross-loop coupling provides substantial benefit. "
                "Improvements cascade effectively across loops."
            )
        elif benefit_ratio > 1.5 and effect_size > 0.5:
            return (
                "Moderate validation: Cross-loop coupling provides meaningful benefit. "
                "The RAF hypothesis is supported."
            )
        elif benefit_ratio > 1.2:
            return (
                "Weak validation: Some cross-loop benefit observed, but effect is modest. "
                "Further optimization of coupling mechanisms may be needed."
            )
        else:
            return (
                "Inconclusive: Cross-loop benefit not clearly demonstrated. "
                "Consider longer experiments or different coupling mechanisms."
            )

    def summary(self) -> Dict[str, Any]:
        """Generate experiment summary."""
        # Compute all coupling statistics
        coupling_stats = {}
        for source in ["calibration", "mitigation"]:
            for target in ["mitigation", "circuit_scaling"]:
                if source != target:
                    key = f"{source}_to_{target}"
                    coupling_stats[key] = self.quantify_coupling_from_data(source, target)

        return {
            "loop_states": {
                name: [s.to_dict() for s in states] for name, states in self.loop_states.items()
            },
            "coupling_statistics": coupling_stats,
            "n_coupling_measurements": len(self.coupling_measurements),
        }
