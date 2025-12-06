"""
Calibration-Control Loop implementation.

This loop operates at the hardware/physics level:

ML Noise Models → Optimized Control → Lower Error Rates → Deeper Circuits → Richer Data → Refined Models

The loop accelerates through precision compounding. More accurate noise models
enable more aggressive control optimization, which reveals subtler noise mechanisms
that were previously masked by dominant error sources.
"""

from dataclasses import dataclass
from typing import Any, Dict, List

import numpy as np

from raf.core.loop import AccelerationLoop, LoopLevel, LoopState
from raf.core.metrics import (
    AccelerationMetric,
    BottleneckIndicator,
    BottleneckSeverity,
    ProgressMetric,
)


@dataclass
class CalibrationControlState:
    """
    State specific to the Calibration-Control Loop.

    Attributes:
        noise_model_accuracy: Accuracy of ML noise characterization (0-1)
        gate_fidelity: Current gate fidelity (0-1)
        coherence_time: T2 coherence time in microseconds
        max_circuit_depth: Maximum feasible circuit depth
        drift_rate: Rate of parameter drift (relative)
        control_bandwidth: Available control bandwidth (relative)
        characterization_overhead: Time/cost for characterization (relative)
    """

    noise_model_accuracy: float = 0.5
    gate_fidelity: float = 0.99
    coherence_time: float = 50.0  # microseconds
    max_circuit_depth: int = 100
    drift_rate: float = 1.0
    control_bandwidth: float = 1.0
    characterization_overhead: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "noise_model_accuracy": self.noise_model_accuracy,
            "gate_fidelity": self.gate_fidelity,
            "coherence_time": self.coherence_time,
            "max_circuit_depth": self.max_circuit_depth,
            "drift_rate": self.drift_rate,
            "control_bandwidth": self.control_bandwidth,
            "characterization_overhead": self.characterization_overhead,
        }


class CalibrationControlLoop(AccelerationLoop):
    """
    Calibration-Control Loop - Operating at the hardware/physics level.

    This loop captures the feedback cycle where:
    1. ML-based noise characterization models system behavior
    2. Models enable optimized pulse-level control
    3. Optimized control reduces error rates
    4. Lower error rates enable deeper circuits
    5. Deeper circuits generate richer characterization data
    6. Improved characterization refines models

    Bottlenecks:
    - Model complexity (quantum noise is high-dimensional and non-Markovian)
    - Drift timescales (parameters change faster than characterization)
    - Control bandwidth (hardware limits on pulse generation)

    Example:
        >>> loop = CalibrationControlLoop()
        >>> loop.set_noise_model_accuracy(0.7)
        >>> loop.set_gate_fidelity(0.995)
        >>> state = loop.iterate()
        >>> print(state.acceleration_rate)
    """

    # Loop stage definitions
    STAGES = [
        "ml_noise_models",  # ML-based noise characterization
        "optimized_control",  # Pulse-level control optimization
        "lower_error_rates",  # Reduced gate errors
        "deeper_circuits",  # Larger feasible circuit depths
        "richer_data",  # More characterization data
        "refined_models",  # Improved noise models
    ]

    # Bottleneck type definitions
    BOTTLENECK_TYPES = [
        "model_complexity",  # Non-Markovian noise complexity
        "drift_timescales",  # Parameter drift rate
        "control_bandwidth",  # Hardware control limitations
        "characterization_cost",  # Cost of noise characterization
    ]

    # Hardware modality options
    HARDWARE_MODALITIES = [
        "superconducting",  # Google, IBM, Rigetti
        "trapped_ion",  # IonQ, Quantinuum
        "neutral_atom",  # Pasqal, QuEra
        "photonic",  # Xanadu, PsiQuantum
    ]

    def __init__(
        self,
        name: str = "calibration_control",
        initial_model_accuracy: float = 0.5,
        initial_gate_fidelity: float = 0.99,
        hardware_modality: str = "superconducting",
    ):
        """
        Initialize the Calibration-Control Loop.

        Args:
            name: Identifier for this loop instance
            initial_model_accuracy: Starting noise model accuracy (0-1)
            initial_gate_fidelity: Starting gate fidelity (0-1)
            hardware_modality: Type of quantum hardware
        """
        super().__init__(
            name=name,
            level=LoopLevel.HARDWARE,
            description="ML-based calibration and control feedback loop at the hardware level",
        )

        self.cc_state = CalibrationControlState(
            noise_model_accuracy=initial_model_accuracy,
            gate_fidelity=initial_gate_fidelity,
        )
        self.hardware_modality = hardware_modality

        # Set modality-specific defaults
        self._set_modality_defaults()

        # Initialize progress metrics
        self.metrics.progress["noise_model_accuracy"] = ProgressMetric(
            domain="noise_model_accuracy",
            current_value=initial_model_accuracy,
            target_value=0.95,
            direction="higher",
        )
        self.metrics.progress["gate_fidelity"] = ProgressMetric(
            domain="gate_fidelity",
            current_value=initial_gate_fidelity,
            target_value=0.9999,
            direction="higher",
        )
        self.metrics.progress["max_circuit_depth"] = ProgressMetric(
            domain="max_circuit_depth",
            current_value=100,
            target_value=10000,
            unit="gates",
            direction="higher",
        )

    def _set_modality_defaults(self):
        """Set hardware modality-specific default parameters."""
        modality_params = {
            "superconducting": {
                "coherence_time": 50.0,  # ~50 μs T2
                "drift_rate": 2.0,  # Faster drift
                "control_bandwidth": 1.5,  # Good bandwidth
            },
            "trapped_ion": {
                "coherence_time": 1000.0,  # ~1 ms T2
                "drift_rate": 0.5,  # Slower drift
                "control_bandwidth": 0.8,  # Limited bandwidth
            },
            "neutral_atom": {
                "coherence_time": 500.0,  # ~500 μs T2
                "drift_rate": 1.0,  # Moderate drift
                "control_bandwidth": 1.0,  # Moderate bandwidth
            },
            "photonic": {
                "coherence_time": 10000.0,  # Very long (room temp)
                "drift_rate": 0.3,  # Slow drift
                "control_bandwidth": 2.0,  # High bandwidth
            },
        }

        params = modality_params.get(self.hardware_modality, modality_params["superconducting"])
        self.cc_state.coherence_time = params["coherence_time"]
        self.cc_state.drift_rate = params["drift_rate"]
        self.cc_state.control_bandwidth = params["control_bandwidth"]

    @property
    def stages(self) -> List[str]:
        return self.STAGES

    @property
    def bottleneck_types(self) -> List[str]:
        return self.BOTTLENECK_TYPES

    def set_noise_model_accuracy(self, accuracy: float):
        """Set the current noise model accuracy."""
        self.cc_state.noise_model_accuracy = np.clip(accuracy, 0.0, 1.0)
        self.metrics.progress["noise_model_accuracy"].record(accuracy)

    def set_gate_fidelity(self, fidelity: float):
        """Set the current gate fidelity."""
        self.cc_state.gate_fidelity = np.clip(fidelity, 0.9, 0.9999)
        self.metrics.progress["gate_fidelity"].record(fidelity)

    def set_coherence_time(self, time_us: float):
        """Set the coherence time in microseconds."""
        self.cc_state.coherence_time = max(1.0, time_us)

    def set_max_circuit_depth(self, depth: int):
        """Set the maximum feasible circuit depth."""
        self.cc_state.max_circuit_depth = max(10, depth)
        self.metrics.progress["max_circuit_depth"].record(float(depth))

    def set_drift_rate(self, rate: float):
        """Set the parameter drift rate."""
        self.cc_state.drift_rate = max(0.1, rate)

    def set_control_bandwidth(self, bandwidth: float):
        """Set the control bandwidth."""
        self.cc_state.control_bandwidth = max(0.1, bandwidth)

    def compute_acceleration(self) -> AccelerationMetric:
        """
        Compute the current acceleration rate.

        Acceleration is computed based on:
        - Improvement in noise model accuracy
        - Improvement in gate fidelity
        - Growth in maximum circuit depth
        - Reduction in characterization overhead
        """
        # Get historical values
        model_history = self.metrics.progress["noise_model_accuracy"].history
        fidelity_history = self.metrics.progress["gate_fidelity"].history
        depth_history = self.metrics.progress["max_circuit_depth"].history

        # Compute acceleration components
        model_factor = 1.0
        if len(model_history) >= 2:
            prev = model_history[-2][1]
            curr = self.cc_state.noise_model_accuracy
            if prev > 0:
                model_factor = curr / prev

        # For fidelity, use log scale since we're approaching 1
        fidelity_factor = 1.0
        if len(fidelity_history) >= 2:
            prev_infidelity = 1.0 - fidelity_history[-2][1]
            curr_infidelity = 1.0 - self.cc_state.gate_fidelity
            if prev_infidelity > 0 and curr_infidelity > 0:
                # Improvement = reduction in infidelity
                fidelity_factor = prev_infidelity / curr_infidelity

        depth_factor = 1.0
        if len(depth_history) >= 2:
            prev = depth_history[-2][1]
            curr = float(self.cc_state.max_circuit_depth)
            if prev > 0:
                depth_factor = curr / prev

        # Precision compounding effect
        precision_factor = self.cc_state.noise_model_accuracy * self.cc_state.gate_fidelity

        # Control efficiency
        control_factor = self.cc_state.control_bandwidth / self.cc_state.drift_rate

        # Combined acceleration
        acceleration = (
            model_factor
            * (fidelity_factor**0.5)  # Fidelity improvements are harder
            * depth_factor
            * (1 + precision_factor)
            * min(2.0, control_factor)
        ) ** 0.2

        return AccelerationMetric(
            name=f"{self.name}_acceleration",
            value=acceleration,
            baseline=1.0,
            iteration=self.state.iteration,
            metadata={
                "model_factor": model_factor,
                "fidelity_factor": fidelity_factor,
                "depth_factor": depth_factor,
                "precision_factor": precision_factor,
                "control_factor": control_factor,
                "hardware_modality": self.hardware_modality,
            },
        )

    def identify_bottlenecks(self) -> List[BottleneckIndicator]:
        """
        Identify current bottlenecks in the loop.

        Checks for:
        1. Model complexity limitations
        2. Fast drift timescales
        3. Control bandwidth limitations
        4. High characterization cost
        """
        bottlenecks = []

        # Bottleneck 1: Model complexity
        # If model accuracy is low despite good data, complexity is the issue
        if self.cc_state.noise_model_accuracy < 0.6 and self.cc_state.max_circuit_depth > 200:
            bottlenecks.append(
                BottleneckIndicator(
                    name="model_complexity",
                    description="Quantum noise is too complex for current ML models to capture",
                    severity=BottleneckSeverity.HIGH,
                    loop_name=self.name,
                    constraint_type="model",
                    current_value=self.cc_state.noise_model_accuracy,
                    threshold=0.6,
                    addressability_score=0.6,
                    recommended_actions=[
                        "Use physics-informed neural networks for noise modeling",
                        "Implement hierarchical models separating Markovian and non-Markovian components",
                        "Apply tensor network methods for high-dimensional noise",
                        "Focus on dominant error sources first",
                    ],
                )
            )

        # Bottleneck 2: Drift timescales
        if self.cc_state.drift_rate > 1.5:
            severity = (
                BottleneckSeverity.CRITICAL
                if self.cc_state.drift_rate > 3.0
                else BottleneckSeverity.HIGH
            )
            bottlenecks.append(
                BottleneckIndicator(
                    name="fast_drift",
                    description="System parameters drift faster than characterization can track",
                    severity=severity,
                    loop_name=self.name,
                    constraint_type="hardware",
                    current_value=self.cc_state.drift_rate,
                    threshold=1.5,
                    addressability_score=0.4,
                    recommended_actions=[
                        "Implement continuous online calibration",
                        "Use predictive models to anticipate drift",
                        "Improve environmental isolation",
                        "Develop drift-robust control strategies",
                    ],
                )
            )

        # Bottleneck 3: Control bandwidth
        bandwidth_needed = (
            self.cc_state.noise_model_accuracy * 1.5
        )  # Better models need more bandwidth
        if self.cc_state.control_bandwidth < bandwidth_needed:
            bottlenecks.append(
                BottleneckIndicator(
                    name="control_bandwidth",
                    description="Hardware control bandwidth limits achievable precision",
                    severity=BottleneckSeverity.MEDIUM,
                    loop_name=self.name,
                    constraint_type="hardware",
                    current_value=self.cc_state.control_bandwidth,
                    threshold=bandwidth_needed,
                    addressability_score=0.3,
                    recommended_actions=[
                        "Upgrade control electronics",
                        "Use optimal control theory to maximize bandwidth utilization",
                        "Implement pulse shaping within bandwidth constraints",
                        "Focus on control strategies robust to bandwidth limits",
                    ],
                )
            )

        # Bottleneck 4: Characterization overhead
        if self.cc_state.characterization_overhead > 2.0:
            bottlenecks.append(
                BottleneckIndicator(
                    name="characterization_overhead",
                    description="Noise characterization takes too long, limiting iteration speed",
                    severity=BottleneckSeverity.MEDIUM,
                    loop_name=self.name,
                    constraint_type="compute",
                    current_value=self.cc_state.characterization_overhead,
                    threshold=2.0,
                    addressability_score=0.7,
                    recommended_actions=[
                        "Use compressed sensing for efficient tomography",
                        "Implement ML-based characterization from reduced measurements",
                        "Develop shadow tomography techniques",
                        "Focus on characterizing most relevant noise parameters",
                    ],
                )
            )

        # Bottleneck 5: Fidelity plateau
        fidelity_trend = self.metrics.progress["gate_fidelity"].trend
        if (
            self.cc_state.gate_fidelity > 0.995
            and fidelity_trend is not None
            and fidelity_trend < 0.0001
        ):
            bottlenecks.append(
                BottleneckIndicator(
                    name="fidelity_plateau",
                    description="Gate fidelity improvement has plateaued near current limits",
                    severity=BottleneckSeverity.LOW,
                    loop_name=self.name,
                    constraint_type="knowledge",
                    current_value=self.cc_state.gate_fidelity,
                    threshold=0.995,
                    addressability_score=0.4,
                    recommended_actions=[
                        "Investigate secondary error sources (leakage, crosstalk)",
                        "Consider hardware upgrades for next fidelity tier",
                        "Shift focus to error correction rather than further mitigation",
                        "Optimize for specific application requirements",
                    ],
                )
            )

        return bottlenecks

    def get_recommendations(self) -> List[str]:
        """Generate recommendations for accelerating this loop."""
        recommendations = []

        # Based on current state
        if self.cc_state.noise_model_accuracy < 0.7:
            recommendations.append("Priority: Improve noise characterization models")

        if self.cc_state.gate_fidelity < 0.995:
            recommendations.append("Focus on pulse optimization to improve gate fidelity")

        if self.cc_state.max_circuit_depth < 500:
            recommendations.append("Work on extending coherence to enable deeper circuits")

        if self.cc_state.drift_rate > 1.5:
            recommendations.append("Implement continuous calibration to track parameter drift")

        # Modality-specific recommendations
        if self.hardware_modality == "superconducting":
            recommendations.append("Consider AlphaQubit-style neural decoders for error correction")
        elif self.hardware_modality == "trapped_ion":
            recommendations.append("Leverage long coherence for deep circuit characterization")
        elif self.hardware_modality == "neutral_atom":
            recommendations.append("Exploit flexible geometry for noise-resilient configurations")

        # Based on loop dynamics
        if self.state.status.value == "accelerating":
            recommendations.append("Loop is accelerating; push for next fidelity milestone")
        elif self.state.status.value == "bottlenecked":
            recommendations.append("Address drift or bandwidth constraints before scaling")

        return recommendations

    def simulate_iteration(
        self,
        model_improvement: float = 0.03,
        fidelity_improvement: float = 0.001,
        depth_growth: float = 1.1,
    ) -> LoopState:
        """
        Simulate one iteration with specified improvement rates.

        Args:
            model_improvement: Additive improvement in model accuracy
            fidelity_improvement: Additive improvement in gate fidelity
            depth_growth: Multiplicative growth in max circuit depth

        Returns:
            Updated loop state
        """
        # Apply improvements (with diminishing returns)
        model_room = 1.0 - self.cc_state.noise_model_accuracy
        new_model = self.cc_state.noise_model_accuracy + model_improvement * model_room

        # Fidelity improvements get harder as we approach 1
        fidelity_room = 0.9999 - self.cc_state.gate_fidelity
        new_fidelity = self.cc_state.gate_fidelity + fidelity_improvement * (fidelity_room / 0.01)

        new_depth = int(self.cc_state.max_circuit_depth * depth_growth)

        # Update state
        self.set_noise_model_accuracy(new_model)
        self.set_gate_fidelity(new_fidelity)
        self.set_max_circuit_depth(new_depth)

        # Characterization overhead decreases with better models
        new_overhead = self.cc_state.characterization_overhead * (1.0 - 0.05 * new_model)
        self.cc_state.characterization_overhead = max(0.5, new_overhead)

        # Run iteration
        return self.iterate()

    def compute_effective_quantum_volume(self) -> float:
        """
        Compute effective quantum volume based on current state.

        This is a simplified metric combining fidelity and depth.
        """
        # Effective depth accounting for errors
        error_rate = 1.0 - self.cc_state.gate_fidelity
        effective_depth = self.cc_state.max_circuit_depth * np.exp(
            -error_rate * self.cc_state.max_circuit_depth
        )

        # Quantum volume ~ 2^(effective_depth)^(1/3) for reasonable approximation
        return 2 ** (effective_depth ** (1 / 3))

    def summary(self) -> Dict[str, Any]:
        """Generate a summary including calibration-control-specific state."""
        base_summary = super().summary()
        base_summary["cc_state"] = self.cc_state.to_dict()
        base_summary["hardware_modality"] = self.hardware_modality
        base_summary["effective_quantum_volume"] = self.compute_effective_quantum_volume()
        return base_summary
