"""
Bottleneck validation experiments for the Reciprocal Acceleration Framework.

This module validates the bottleneck identification and impact prediction
by artificially introducing bottlenecks and measuring their effects.

Key experiments:
1. Artificially introduce bottlenecks (limit calibration data, bandwidth, etc.)
2. Measure impact on loop acceleration
3. Compare predicted vs. observed bottleneck effects
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from raf.core.metrics import BottleneckIndicator, BottleneckSeverity
from raf.utils import set_all_seeds


class BottleneckType(Enum):
    """Types of artificial bottlenecks that can be introduced."""

    LIMITED_CALIBRATION_DATA = "limited_calibration_data"
    HIGH_DRIFT_RATE = "high_drift_rate"
    LOW_CONTROL_BANDWIDTH = "low_control_bandwidth"
    HIGH_CHARACTERIZATION_OVERHEAD = "high_characterization_overhead"
    MODEL_COMPLEXITY = "model_complexity"
    MITIGATION_OVERHEAD = "mitigation_overhead"


@dataclass
class BottleneckScenario:
    """Configuration for an artificial bottleneck scenario."""

    bottleneck_type: BottleneckType
    severity: float  # 0-1, how severe the bottleneck is
    description: str
    parameters: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bottleneck_type": self.bottleneck_type.value,
            "severity": self.severity,
            "description": self.description,
            "parameters": self.parameters,
        }


@dataclass
class BottleneckEffect:
    """Measured effect of an artificial bottleneck."""

    scenario: BottleneckScenario
    baseline_acceleration: float
    bottlenecked_acceleration: float
    acceleration_drop: float  # Relative drop
    predicted_bottlenecks: List[Dict[str, Any]]
    observed_impact: Dict[str, float]
    prediction_accuracy: float  # How well prediction matched observation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario": self.scenario.to_dict(),
            "baseline_acceleration": self.baseline_acceleration,
            "bottlenecked_acceleration": self.bottlenecked_acceleration,
            "acceleration_drop": self.acceleration_drop,
            "predicted_bottlenecks": self.predicted_bottlenecks,
            "observed_impact": self.observed_impact,
            "prediction_accuracy": self.prediction_accuracy,
        }


@dataclass
class ValidationResult:
    """Results from bottleneck validation experiment."""

    total_scenarios: int
    effects: List[BottleneckEffect]
    avg_prediction_accuracy: float
    avg_acceleration_drop: float
    worst_bottleneck: Optional[BottleneckScenario]
    validation_passed: bool  # True if predictions align with observations

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_scenarios": self.total_scenarios,
            "effects": [e.to_dict() for e in self.effects],
            "avg_prediction_accuracy": self.avg_prediction_accuracy,
            "avg_acceleration_drop": self.avg_acceleration_drop,
            "worst_bottleneck": self.worst_bottleneck.to_dict() if self.worst_bottleneck else None,
            "validation_passed": self.validation_passed,
        }


class SimulatedLoop:
    """
    Simulated acceleration loop for bottleneck validation.

    This simulates a calibration-control style loop where we can
    inject artificial bottlenecks and measure their effects.
    """

    def __init__(
        self,
        name: str = "simulated_loop",
        random_seed: Optional[int] = None,
    ):
        self.name = name
        self.seed = random_seed
        self.rng = np.random.default_rng(random_seed)

        # Loop state
        self.state = {
            "noise_model_accuracy": 0.5,
            "gate_fidelity": 0.99,
            "max_circuit_depth": 100,
            "drift_rate": 1.0,
            "control_bandwidth": 1.0,
            "characterization_overhead": 1.0,
            "calibration_data_fraction": 1.0,  # 1.0 = full data
            "mitigation_overhead": 1.0,
        }

        # Bottleneck thresholds
        self.thresholds = {
            "drift_rate": 1.5,
            "control_bandwidth": 0.75,
            "characterization_overhead": 2.0,
            "calibration_data_fraction": 0.3,
            "mitigation_overhead": 5.0,
            "noise_model_accuracy": 0.6,
        }

        self.iteration = 0
        self.acceleration_history: List[float] = []

    def reset(self):
        """Reset loop to initial state."""
        self.state = {
            "noise_model_accuracy": 0.5,
            "gate_fidelity": 0.99,
            "max_circuit_depth": 100,
            "drift_rate": 1.0,
            "control_bandwidth": 1.0,
            "characterization_overhead": 1.0,
            "calibration_data_fraction": 1.0,
            "mitigation_overhead": 1.0,
        }
        self.iteration = 0
        self.acceleration_history = []

    def apply_bottleneck(self, scenario: BottleneckScenario):
        """Apply an artificial bottleneck to the loop."""
        bt = scenario.bottleneck_type
        severity = scenario.severity

        if bt == BottleneckType.LIMITED_CALIBRATION_DATA:
            # Reduce available calibration data
            self.state["calibration_data_fraction"] = 1.0 - severity * 0.9
        elif bt == BottleneckType.HIGH_DRIFT_RATE:
            # Increase drift rate
            self.state["drift_rate"] = 1.0 + severity * 4.0  # Up to 5x
        elif bt == BottleneckType.LOW_CONTROL_BANDWIDTH:
            # Reduce control bandwidth
            self.state["control_bandwidth"] = 1.0 - severity * 0.8
        elif bt == BottleneckType.HIGH_CHARACTERIZATION_OVERHEAD:
            # Increase characterization overhead
            self.state["characterization_overhead"] = 1.0 + severity * 9.0  # Up to 10x
        elif bt == BottleneckType.MODEL_COMPLEXITY:
            # Reduce model accuracy (simulating complex noise)
            self.state["noise_model_accuracy"] = max(0.1, 0.5 - severity * 0.4)
        elif bt == BottleneckType.MITIGATION_OVERHEAD:
            # Increase mitigation overhead
            self.state["mitigation_overhead"] = 1.0 + severity * 19.0  # Up to 20x

    def identify_bottlenecks(self) -> List[BottleneckIndicator]:
        """Identify current bottlenecks based on state."""
        bottlenecks = []

        # Check drift rate
        if self.state["drift_rate"] > self.thresholds["drift_rate"]:
            severity = (
                BottleneckSeverity.CRITICAL
                if self.state["drift_rate"] > 3.0
                else BottleneckSeverity.HIGH
            )
            bottlenecks.append(
                BottleneckIndicator(
                    name="fast_drift",
                    description="System parameters drift faster than characterization",
                    severity=severity,
                    loop_name=self.name,
                    constraint_type="hardware",
                    current_value=self.state["drift_rate"],
                    threshold=self.thresholds["drift_rate"],
                    addressability_score=0.4,
                )
            )

        # Check control bandwidth
        if self.state["control_bandwidth"] < self.thresholds["control_bandwidth"]:
            bottlenecks.append(
                BottleneckIndicator(
                    name="low_bandwidth",
                    description="Control bandwidth limits achievable precision",
                    severity=BottleneckSeverity.MEDIUM,
                    loop_name=self.name,
                    constraint_type="hardware",
                    current_value=self.state["control_bandwidth"],
                    threshold=self.thresholds["control_bandwidth"],
                    addressability_score=0.3,
                )
            )

        # Check characterization overhead
        if self.state["characterization_overhead"] > self.thresholds["characterization_overhead"]:
            bottlenecks.append(
                BottleneckIndicator(
                    name="high_characterization_cost",
                    description="Characterization takes too long",
                    severity=BottleneckSeverity.MEDIUM,
                    loop_name=self.name,
                    constraint_type="compute",
                    current_value=self.state["characterization_overhead"],
                    threshold=self.thresholds["characterization_overhead"],
                    addressability_score=0.7,
                )
            )

        # Check calibration data
        if self.state["calibration_data_fraction"] < self.thresholds["calibration_data_fraction"]:
            bottlenecks.append(
                BottleneckIndicator(
                    name="limited_calibration_data",
                    description="Insufficient calibration data for accurate models",
                    severity=BottleneckSeverity.HIGH,
                    loop_name=self.name,
                    constraint_type="data",
                    current_value=self.state["calibration_data_fraction"],
                    threshold=self.thresholds["calibration_data_fraction"],
                    addressability_score=0.8,
                )
            )

        # Check mitigation overhead
        if self.state["mitigation_overhead"] > self.thresholds["mitigation_overhead"]:
            bottlenecks.append(
                BottleneckIndicator(
                    name="high_mitigation_overhead",
                    description="Error mitigation overhead is too high",
                    severity=BottleneckSeverity.HIGH,
                    loop_name=self.name,
                    constraint_type="compute",
                    current_value=self.state["mitigation_overhead"],
                    threshold=self.thresholds["mitigation_overhead"],
                    addressability_score=0.6,
                )
            )

        # Check model accuracy (complexity bottleneck)
        if self.state["noise_model_accuracy"] < self.thresholds["noise_model_accuracy"]:
            bottlenecks.append(
                BottleneckIndicator(
                    name="model_complexity",
                    description="Noise too complex for current models",
                    severity=BottleneckSeverity.HIGH,
                    loop_name=self.name,
                    constraint_type="model",
                    current_value=self.state["noise_model_accuracy"],
                    threshold=self.thresholds["noise_model_accuracy"],
                    addressability_score=0.6,
                )
            )

        return bottlenecks

    def compute_acceleration(self) -> float:
        """
        Compute current acceleration rate.

        Acceleration is affected by:
        - Calibration data availability
        - Drift rate vs control bandwidth
        - Characterization overhead
        - Model accuracy
        """
        # Base improvement rate
        base_rate = 1.2

        # Data availability factor
        data_factor = self.state["calibration_data_fraction"] ** 0.5

        # Drift vs bandwidth factor
        drift_bandwidth_ratio = self.state["drift_rate"] / max(0.1, self.state["control_bandwidth"])
        drift_factor = 1.0 / (1.0 + 0.5 * max(0, drift_bandwidth_ratio - 1.0))

        # Overhead factor
        overhead_factor = 1.0 / (1.0 + 0.1 * (self.state["characterization_overhead"] - 1.0))

        # Model accuracy factor
        model_factor = self.state["noise_model_accuracy"]

        # Mitigation overhead factor
        mitigation_factor = 1.0 / (1.0 + 0.05 * (self.state["mitigation_overhead"] - 1.0))

        # Combined acceleration
        acceleration = (
            base_rate
            * data_factor
            * drift_factor
            * overhead_factor
            * model_factor
            * mitigation_factor
        )

        # Add small noise
        acceleration *= 1.0 + 0.05 * self.rng.standard_normal()

        return float(max(0.5, acceleration))

    def iterate(self, n_iterations: int = 5) -> float:
        """
        Run multiple iterations and return average acceleration.

        Args:
            n_iterations: Number of iterations to run

        Returns:
            Average acceleration over iterations
        """
        accelerations = []
        for _ in range(n_iterations):
            self.iteration += 1

            # Simulate improvement (with bottleneck effects)
            improvement_rate = 0.02 * self.state["calibration_data_fraction"]
            self.state["noise_model_accuracy"] = min(
                0.99,
                self.state["noise_model_accuracy"]
                + improvement_rate * (1.0 - self.state["noise_model_accuracy"]),
            )

            accel = self.compute_acceleration()
            accelerations.append(accel)
            self.acceleration_history.append(accel)

        return float(np.mean(accelerations))


class BottleneckValidationExperiment:
    """
    Validates bottleneck identification by introducing artificial bottlenecks
    and comparing predicted vs. observed effects.

    Example:
        >>> experiment = BottleneckValidationExperiment(random_seed=42)
        >>> result = experiment.run_full_validation()
        >>> print(f"Avg prediction accuracy: {result.avg_prediction_accuracy:.1%}")
        >>> print(f"Validation passed: {result.validation_passed}")
    """

    # Predefined bottleneck scenarios
    DEFAULT_SCENARIOS = [
        BottleneckScenario(
            bottleneck_type=BottleneckType.LIMITED_CALIBRATION_DATA,
            severity=0.8,
            description="Severely limited calibration data (20% available)",
            parameters={"data_fraction": 0.2},
        ),
        BottleneckScenario(
            bottleneck_type=BottleneckType.HIGH_DRIFT_RATE,
            severity=0.7,
            description="High parameter drift rate (3.8x normal)",
            parameters={"drift_rate": 3.8},
        ),
        BottleneckScenario(
            bottleneck_type=BottleneckType.LOW_CONTROL_BANDWIDTH,
            severity=0.6,
            description="Reduced control bandwidth (52% of normal)",
            parameters={"bandwidth": 0.52},
        ),
        BottleneckScenario(
            bottleneck_type=BottleneckType.HIGH_CHARACTERIZATION_OVERHEAD,
            severity=0.5,
            description="High characterization overhead (5.5x)",
            parameters={"overhead": 5.5},
        ),
        BottleneckScenario(
            bottleneck_type=BottleneckType.MODEL_COMPLEXITY,
            severity=0.6,
            description="Complex noise limiting model accuracy",
            parameters={"max_accuracy": 0.26},
        ),
        BottleneckScenario(
            bottleneck_type=BottleneckType.MITIGATION_OVERHEAD,
            severity=0.5,
            description="High error mitigation overhead (10.5x)",
            parameters={"overhead": 10.5},
        ),
    ]

    def __init__(
        self,
        scenarios: Optional[List[BottleneckScenario]] = None,
        random_seed: Optional[int] = None,
    ):
        """
        Initialize bottleneck validation experiment.

        Args:
            scenarios: Custom bottleneck scenarios (default: predefined set)
            random_seed: For reproducibility
        """
        self.seed = random_seed
        if random_seed is not None:
            set_all_seeds(random_seed)

        self.scenarios = scenarios or self.DEFAULT_SCENARIOS
        self.rng = np.random.default_rng(random_seed)
        self.loop = SimulatedLoop(random_seed=random_seed)
        self.results: List[BottleneckEffect] = []

    def run_baseline(self, n_iterations: int = 10) -> float:
        """Run baseline experiment without bottlenecks."""
        self.loop.reset()
        return self.loop.iterate(n_iterations)

    def run_with_bottleneck(
        self,
        scenario: BottleneckScenario,
        n_iterations: int = 10,
    ) -> Tuple[float, List[BottleneckIndicator]]:
        """
        Run experiment with artificial bottleneck.

        Args:
            scenario: Bottleneck to introduce
            n_iterations: Number of iterations

        Returns:
            Tuple of (acceleration, predicted_bottlenecks)
        """
        self.loop.reset()
        self.loop.apply_bottleneck(scenario)

        # Get predictions before running
        predicted = self.loop.identify_bottlenecks()

        # Run iterations
        acceleration = self.loop.iterate(n_iterations)

        return acceleration, predicted

    def measure_bottleneck_effect(
        self,
        scenario: BottleneckScenario,
        n_iterations: int = 10,
        n_trials: int = 3,
    ) -> BottleneckEffect:
        """
        Measure the effect of a bottleneck scenario.

        Args:
            scenario: Bottleneck to test
            n_iterations: Iterations per trial
            n_trials: Number of trials for averaging

        Returns:
            BottleneckEffect with measurements
        """
        # Run baseline trials
        baseline_accels = []
        for _ in range(n_trials):
            baseline_accels.append(self.run_baseline(n_iterations))
        baseline_acceleration = float(np.mean(baseline_accels))

        # Run bottlenecked trials
        bottleneck_accels = []
        all_predictions = []
        for _ in range(n_trials):
            accel, predictions = self.run_with_bottleneck(scenario, n_iterations)
            bottleneck_accels.append(accel)
            all_predictions.extend(predictions)
        bottlenecked_acceleration = float(np.mean(bottleneck_accels))

        # Compute acceleration drop
        if baseline_acceleration > 0:
            acceleration_drop = (
                baseline_acceleration - bottlenecked_acceleration
            ) / baseline_acceleration
        else:
            acceleration_drop = 0.0

        # Deduplicate predictions
        unique_predictions = {}
        for p in all_predictions:
            if p.name not in unique_predictions:
                unique_predictions[p.name] = p.to_dict()
        predicted_bottlenecks = list(unique_predictions.values())

        # Compute observed impact
        observed_impact = {
            "acceleration_drop": acceleration_drop,
            "baseline": baseline_acceleration,
            "bottlenecked": bottlenecked_acceleration,
        }

        # Compute prediction accuracy
        prediction_accuracy = self._compute_prediction_accuracy(
            scenario, predicted_bottlenecks, acceleration_drop
        )

        return BottleneckEffect(
            scenario=scenario,
            baseline_acceleration=baseline_acceleration,
            bottlenecked_acceleration=bottlenecked_acceleration,
            acceleration_drop=acceleration_drop,
            predicted_bottlenecks=predicted_bottlenecks,
            observed_impact=observed_impact,
            prediction_accuracy=prediction_accuracy,
        )

    def _compute_prediction_accuracy(
        self,
        scenario: BottleneckScenario,
        predictions: List[Dict[str, Any]],
        observed_drop: float,
    ) -> float:
        """
        Compute how well predictions matched observations.

        Accuracy is based on:
        1. Whether the correct bottleneck type was predicted
        2. Whether severity prediction aligns with observed impact
        """
        # Map scenario type to expected prediction names
        type_to_prediction = {
            BottleneckType.LIMITED_CALIBRATION_DATA: "limited_calibration_data",
            BottleneckType.HIGH_DRIFT_RATE: "fast_drift",
            BottleneckType.LOW_CONTROL_BANDWIDTH: "low_bandwidth",
            BottleneckType.HIGH_CHARACTERIZATION_OVERHEAD: "high_characterization_cost",
            BottleneckType.MODEL_COMPLEXITY: "model_complexity",
            BottleneckType.MITIGATION_OVERHEAD: "high_mitigation_overhead",
        }

        expected_name = type_to_prediction.get(scenario.bottleneck_type, "")

        # Check if correct bottleneck was predicted
        predicted_names = [p["name"] for p in predictions]
        type_match = 1.0 if expected_name in predicted_names else 0.0

        # Check severity alignment
        if predictions:
            # Get severity of the expected prediction
            expected_pred = next((p for p in predictions if p["name"] == expected_name), None)
            if expected_pred:
                # Map severity to expected drop
                severity_to_drop = {
                    "low": 0.1,
                    "medium": 0.2,
                    "high": 0.35,
                    "critical": 0.5,
                }
                expected_drop = severity_to_drop.get(expected_pred["severity"], 0.2)
                drop_error = abs(observed_drop - expected_drop)
                severity_match = max(0, 1.0 - drop_error * 2)
            else:
                severity_match = 0.0
        else:
            severity_match = 0.0 if observed_drop > 0.1 else 1.0

        # Combined accuracy
        return 0.6 * type_match + 0.4 * severity_match

    def run_single_scenario(
        self,
        scenario: BottleneckScenario,
        verbose: bool = True,
    ) -> BottleneckEffect:
        """
        Run validation for a single bottleneck scenario.

        Args:
            scenario: Bottleneck to test
            verbose: Print progress

        Returns:
            BottleneckEffect with results
        """
        if verbose:
            print(f"Testing: {scenario.description}")

        effect = self.measure_bottleneck_effect(scenario)
        self.results.append(effect)

        if verbose:
            print(f"  Baseline acceleration: {effect.baseline_acceleration:.3f}")
            print(f"  Bottlenecked acceleration: {effect.bottlenecked_acceleration:.3f}")
            print(f"  Acceleration drop: {effect.acceleration_drop:.1%}")
            print(f"  Predictions: {[p['name'] for p in effect.predicted_bottlenecks]}")
            print(f"  Prediction accuracy: {effect.prediction_accuracy:.1%}")
            print()

        return effect

    def run_full_validation(
        self,
        verbose: bool = True,
    ) -> ValidationResult:
        """
        Run validation across all bottleneck scenarios.

        Args:
            verbose: Print progress

        Returns:
            ValidationResult with aggregate metrics
        """
        if verbose:
            print("=" * 60)
            print("Bottleneck Validation Experiment")
            print("=" * 60)
            print(f"Testing {len(self.scenarios)} bottleneck scenarios...")
            print()

        self.results = []

        for scenario in self.scenarios:
            self.run_single_scenario(scenario, verbose=verbose)

        # Compute aggregate metrics
        if self.results:
            avg_accuracy = float(np.mean([e.prediction_accuracy for e in self.results]))
            avg_drop = float(np.mean([e.acceleration_drop for e in self.results]))

            # Find worst bottleneck
            worst_idx = np.argmax([e.acceleration_drop for e in self.results])
            worst_bottleneck = self.results[worst_idx].scenario
        else:
            avg_accuracy = 0.0
            avg_drop = 0.0
            worst_bottleneck = None

        # Validation passes if average accuracy > 60%
        validation_passed = avg_accuracy > 0.6

        result = ValidationResult(
            total_scenarios=len(self.scenarios),
            effects=self.results,
            avg_prediction_accuracy=avg_accuracy,
            avg_acceleration_drop=avg_drop,
            worst_bottleneck=worst_bottleneck,
            validation_passed=validation_passed,
        )

        if verbose:
            print("=" * 60)
            print("Validation Summary")
            print("=" * 60)
            print(f"Scenarios tested: {result.total_scenarios}")
            print(f"Average prediction accuracy: {result.avg_prediction_accuracy:.1%}")
            print(f"Average acceleration drop: {result.avg_acceleration_drop:.1%}")
            if result.worst_bottleneck:
                print(f"Worst bottleneck: {result.worst_bottleneck.description}")
            print(f"Validation passed: {result.validation_passed}")

        return result

    def compare_predicted_vs_observed(self) -> Dict[str, Any]:
        """
        Generate detailed comparison of predicted vs observed effects.

        Returns:
            Dictionary with comparison metrics
        """
        if not self.results:
            return {"error": "No results available. Run validation first."}

        comparisons = []
        for effect in self.results:
            # Expected bottleneck type
            expected_type = effect.scenario.bottleneck_type.value

            # Predicted types
            predicted_types = [p["name"] for p in effect.predicted_bottlenecks]

            # Was prediction correct?
            type_to_prediction = {
                "limited_calibration_data": "limited_calibration_data",
                "high_drift_rate": "fast_drift",
                "low_control_bandwidth": "low_bandwidth",
                "high_characterization_overhead": "high_characterization_cost",
                "model_complexity": "model_complexity",
                "mitigation_overhead": "high_mitigation_overhead",
            }
            expected_prediction = type_to_prediction.get(expected_type, "")
            correct_prediction = expected_prediction in predicted_types

            comparisons.append(
                {
                    "scenario": effect.scenario.description,
                    "expected_bottleneck": expected_type,
                    "predicted_bottlenecks": predicted_types,
                    "correct_prediction": correct_prediction,
                    "observed_drop": effect.acceleration_drop,
                    "prediction_accuracy": effect.prediction_accuracy,
                }
            )

        # Summary statistics
        correct_count = sum(1 for c in comparisons if c["correct_prediction"])
        total = len(comparisons)

        return {
            "comparisons": comparisons,
            "correct_predictions": correct_count,
            "total_scenarios": total,
            "prediction_rate": correct_count / total if total > 0 else 0.0,
            "interpretation": self._interpret_comparison(correct_count, total),
        }

    def _interpret_comparison(self, correct: int, total: int) -> str:
        """Generate interpretation of comparison results."""
        rate = correct / total if total > 0 else 0.0

        if rate >= 0.8:
            return (
                "Excellent: Bottleneck predictions closely match observations. "
                "The identification system is highly accurate."
            )
        elif rate >= 0.6:
            return (
                "Good: Most bottleneck predictions are correct. "
                "The system reliably identifies major constraints."
            )
        elif rate >= 0.4:
            return (
                "Moderate: Some predictions match observations. "
                "Consider refining bottleneck thresholds."
            )
        else:
            return (
                "Poor: Predictions often miss actual bottlenecks. "
                "Significant calibration of detection logic needed."
            )

    def summary(self) -> Dict[str, Any]:
        """Generate experiment summary."""
        comparison = self.compare_predicted_vs_observed()

        return {
            "scenarios_tested": len(self.scenarios),
            "results": [e.to_dict() for e in self.results],
            "comparison": comparison,
            "validation_passed": (
                self.results[-1].prediction_accuracy > 0.6 if self.results else False
            ),
        }
