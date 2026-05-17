"""
Experimental metrics collection for RAF validation.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ExperimentRun:
    """Single experimental run data."""

    timestamp: datetime
    iteration: int

    # Circuit properties
    circuit_depth: int
    num_qubits: int
    num_two_qubit_gates: int

    # Results
    ideal_value: float
    noisy_value: float
    mitigated_value: float | None = None

    # Errors
    noisy_error: float = 0.0
    mitigated_error: float | None = None

    # Overhead
    mitigation_overhead: float = 1.0  # Multiplier on shots/time

    # Metadata
    backend_name: str = ""
    noise_profile: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.noisy_error = abs(self.noisy_value - self.ideal_value)
        if self.mitigated_value is not None:
            self.mitigated_error = abs(self.mitigated_value - self.ideal_value)

    @property
    def error_reduction(self) -> float | None:
        """Fraction of error reduced by mitigation."""
        if self.mitigated_error is None or self.noisy_error == 0:
            return None
        return 1 - (self.mitigated_error / self.noisy_error)

    @property
    def mitigation_efficiency(self) -> float | None:
        """Error reduction per unit overhead."""
        if self.error_reduction is None:
            return None
        return self.error_reduction / self.mitigation_overhead

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "iteration": self.iteration,
            "circuit_depth": self.circuit_depth,
            "num_qubits": self.num_qubits,
            "num_two_qubit_gates": self.num_two_qubit_gates,
            "ideal_value": self.ideal_value,
            "noisy_value": self.noisy_value,
            "mitigated_value": self.mitigated_value,
            "noisy_error": self.noisy_error,
            "mitigated_error": self.mitigated_error,
            "error_reduction": self.error_reduction,
            "mitigation_overhead": self.mitigation_overhead,
            "mitigation_efficiency": self.mitigation_efficiency,
            "backend_name": self.backend_name,
            "noise_profile": self.noise_profile,
            "metadata": self.metadata,
        }


class ExperimentalMetricsCollector:
    """
    Collects and analyzes experimental metrics for RAF validation.

    Tracks acceleration dynamics across iterations and computes
    RAF-specific metrics from real/simulated data.
    """

    def __init__(self, experiment_name: str):
        self.experiment_name = experiment_name
        self.runs: list[ExperimentRun] = []
        self.start_time = datetime.now()

    def record_run(
        self,
        iteration: int,
        circuit_depth: int,
        num_qubits: int,
        num_two_qubit_gates: int,
        ideal_value: float,
        noisy_value: float,
        mitigated_value: float | None = None,
        mitigation_overhead: float = 1.0,
        backend_name: str = "",
        noise_profile: str = "",
        **metadata: Any,
    ) -> None:
        """Record a single experimental run."""
        run = ExperimentRun(
            timestamp=datetime.now(),
            iteration=iteration,
            circuit_depth=circuit_depth,
            num_qubits=num_qubits,
            num_two_qubit_gates=num_two_qubit_gates,
            ideal_value=ideal_value,
            noisy_value=noisy_value,
            mitigated_value=mitigated_value,
            mitigation_overhead=mitigation_overhead,
            backend_name=backend_name,
            noise_profile=noise_profile,
            metadata=metadata,
        )
        self.runs.append(run)

    def compute_acceleration_metrics(self) -> dict[str, Any]:
        """
        Compute RAF acceleration metrics from collected data.

        Returns:
            Dictionary with acceleration analysis
        """
        if len(self.runs) < 2:
            return {"error": "Need at least 2 runs for acceleration analysis"}

        # Group by iteration
        iterations = sorted({r.iteration for r in self.runs})

        # Compute per-iteration averages
        iteration_stats = []
        for it in iterations:
            it_runs = [r for r in self.runs if r.iteration == it]

            avg_noisy_error = sum(r.noisy_error for r in it_runs) / len(it_runs)

            mitigated_runs = [r for r in it_runs if r.mitigated_error is not None]
            avg_mitigated_error = (
                sum((float(r.mitigated_error) for r in mitigated_runs), 0.0) / len(mitigated_runs)  # type: ignore[arg-type]
                if mitigated_runs
                else None
            )

            avg_reduction = (
                sum(r.error_reduction for r in mitigated_runs if r.error_reduction)
                / len([r for r in mitigated_runs if r.error_reduction])
                if mitigated_runs
                else None
            )

            iteration_stats.append(
                {
                    "iteration": it,
                    "num_runs": len(it_runs),
                    "avg_noisy_error": avg_noisy_error,
                    "avg_mitigated_error": avg_mitigated_error,
                    "avg_error_reduction": avg_reduction,
                }
            )

        # Compute acceleration (improvement rate over iterations)
        if len(iteration_stats) >= 2:
            reductions = [
                s["avg_error_reduction"]
                for s in iteration_stats
                if s["avg_error_reduction"] is not None
            ]

            if len(reductions) >= 2:
                # Acceleration = ratio of improvement rates
                early_reduction = sum(reductions[: len(reductions) // 2]) / (len(reductions) // 2)
                late_reduction = sum(reductions[len(reductions) // 2 :]) / (
                    len(reductions) - len(reductions) // 2
                )

                acceleration = late_reduction / early_reduction if early_reduction > 0 else 1.0
            else:
                acceleration = 1.0
        else:
            acceleration = 1.0

        return {
            "experiment_name": self.experiment_name,
            "total_runs": len(self.runs),
            "iterations": len(iterations),
            "iteration_stats": iteration_stats,
            "overall_acceleration": acceleration,
            "is_accelerating": acceleration > 1.0,
            "final_error_reduction": (
                iteration_stats[-1]["avg_error_reduction"] if iteration_stats else None
            ),
        }

    def compute_bottleneck_indicators(self) -> dict[str, Any]:
        """
        Identify bottlenecks from experimental data.

        Returns:
            Dictionary with bottleneck analysis
        """
        if not self.runs:
            return {"error": "No runs recorded"}

        bottlenecks = []

        # Check for diminishing returns
        metrics = self.compute_acceleration_metrics()
        if "iteration_stats" in metrics:
            stats = metrics["iteration_stats"]
            if len(stats) >= 3:
                reductions = [s["avg_error_reduction"] for s in stats if s["avg_error_reduction"]]
                if len(reductions) >= 3:
                    # Check if improvement is slowing
                    early_improvement = reductions[1] - reductions[0] if len(reductions) > 1 else 0
                    late_improvement = reductions[-1] - reductions[-2] if len(reductions) > 1 else 0

                    if late_improvement < early_improvement * 0.5:
                        bottlenecks.append(
                            {
                                "name": "diminishing_returns",
                                "severity": "medium",
                                "description": "Error reduction improvement is slowing",
                                "early_improvement": early_improvement,
                                "late_improvement": late_improvement,
                            }
                        )

        # Check for overhead scaling
        overheads = [r.mitigation_overhead for r in self.runs]
        if max(overheads) > 10:
            bottlenecks.append(
                {
                    "name": "high_overhead",
                    "severity": "high",
                    "description": "Mitigation overhead exceeds 10x",
                    "max_overhead": max(overheads),
                }
            )

        # Check for depth limitation
        depths = [float(r.circuit_depth) for r in self.runs]
        errors = [r.noisy_error for r in self.runs]

        # Simple correlation check
        if len(depths) > 5:
            depth_error_corr = self._correlation(depths, errors)
            if depth_error_corr > 0.8:
                bottlenecks.append(
                    {
                        "name": "depth_limited",
                        "severity": "high",
                        "description": "Strong correlation between depth and error",
                        "correlation": depth_error_corr,
                    }
                )

        return {
            "bottlenecks": bottlenecks,
            "num_bottlenecks": len(bottlenecks),
            "high_severity_count": len([b for b in bottlenecks if b["severity"] == "high"]),
        }

    def _correlation(self, x: list[float], y: list[float]) -> float:
        """Compute Pearson correlation coefficient."""
        n = len(x)
        if n < 2:
            return 0.0

        mean_x = sum(x) / n
        mean_y = sum(y) / n

        numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y, strict=False))

        var_x = sum((xi - mean_x) ** 2 for xi in x)
        var_y = sum((yi - mean_y) ** 2 for yi in y)

        denominator = (var_x * var_y) ** 0.5

        if denominator == 0:
            return 0.0

        return float(numerator / denominator)

    def to_dataframe(self) -> Any:
        """Convert runs to pandas DataFrame."""
        try:
            import pandas as pd

            return pd.DataFrame([r.to_dict() for r in self.runs])
        except ImportError as err:
            raise ImportError("pandas is required for DataFrame export") from err

    def save(self, filepath: str) -> None:
        """Save collected data to JSON file."""
        data = {
            "experiment_name": self.experiment_name,
            "start_time": self.start_time.isoformat(),
            "runs": [r.to_dict() for r in self.runs],
            "acceleration_metrics": self.compute_acceleration_metrics(),
            "bottleneck_indicators": self.compute_bottleneck_indicators(),
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, filepath: str) -> "ExperimentalMetricsCollector":
        """Load from JSON file."""
        with open(filepath) as f:
            data = json.load(f)

        collector = cls(data["experiment_name"])
        collector.start_time = datetime.fromisoformat(data["start_time"])

        for run_data in data["runs"]:
            run_data["timestamp"] = datetime.fromisoformat(run_data["timestamp"])
            # Remove computed fields
            for key in [
                "noisy_error",
                "mitigated_error",
                "error_reduction",
                "mitigation_efficiency",
            ]:
                run_data.pop(key, None)
            collector.runs.append(ExperimentRun(**run_data))

        return collector

    def summary(self) -> str:
        """Generate text summary of experiment."""
        metrics = self.compute_acceleration_metrics()
        bottlenecks = self.compute_bottleneck_indicators()

        lines = [
            f"=== {self.experiment_name} ===",
            f"Total runs: {len(self.runs)}",
            f"Iterations: {metrics.get('iterations', 0)}",
            "",
            f"Acceleration: {metrics.get('overall_acceleration', 1.0):.3f}",
            f"Is accelerating: {metrics.get('is_accelerating', False)}",
            (
                f"Final error reduction: {metrics.get('final_error_reduction', 0):.1%}"
                if metrics.get("final_error_reduction")
                else ""
            ),
            "",
            f"Bottlenecks identified: {bottlenecks.get('num_bottlenecks', 0)}",
        ]

        lines += [
            f"  - {b['name']} ({b['severity']}): {b['description']}"
            for b in bottlenecks.get("bottlenecks", [])
        ]

        return "\n".join(lines)
