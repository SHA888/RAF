"""
Metrics and measurements for the Reciprocal Acceleration Framework.

This module defines the core metric types used to quantify acceleration,
identify bottlenecks, and measure cross-loop coupling in QC-ML systems.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np


class MetricType(Enum):
    """Types of metrics tracked in the framework."""

    ACCELERATION = "acceleration"
    BOTTLENECK = "bottleneck"
    COUPLING = "coupling"
    PROGRESS = "progress"
    EFFICIENCY = "efficiency"


class BottleneckSeverity(Enum):
    """Severity levels for identified bottlenecks."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class LoopDirection(Enum):
    """Direction of information/capability flow."""

    QC_TO_ML = "qc_to_ml"  # Quantum Computing enhancing Machine Learning
    ML_TO_QC = "ml_to_qc"  # Machine Learning enhancing Quantum Computing
    BIDIRECTIONAL = "bidirectional"


@dataclass
class AccelerationMetric:
    """
    Measures the acceleration rate of a feedback loop.

    Acceleration occurs when each iteration increases the rate of progress
    in subsequent iterations—a positive feedback dynamic.

    Attributes:
        name: Identifier for this metric
        value: Current acceleration value (>1 indicates positive acceleration)
        baseline: Reference value for comparison
        timestamp: When this measurement was taken
        iteration: Which iteration of the loop this represents
        metadata: Additional context about the measurement
    """

    name: str
    value: float
    baseline: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    iteration: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def acceleration_ratio(self) -> float:
        """Ratio of current value to baseline (>1 = acceleration)."""
        if self.baseline == 0:
            return float("inf") if self.value > 0 else 0.0
        return self.value / self.baseline

    @property
    def is_accelerating(self) -> bool:
        """Whether the loop is exhibiting positive acceleration."""
        return self.acceleration_ratio > 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "value": self.value,
            "baseline": self.baseline,
            "acceleration_ratio": self.acceleration_ratio,
            "is_accelerating": self.is_accelerating,
            "timestamp": self.timestamp.isoformat(),
            "iteration": self.iteration,
            "metadata": self.metadata,
        }


@dataclass
class BottleneckIndicator:
    """
    Identifies rate-limiting factors that constrain loop acceleration.

    Bottlenecks are categorized by:
    - Type: What kind of constraint (data, compute, model, hardware)
    - Severity: How much it limits progress
    - Addressability: How feasible it is to resolve

    Attributes:
        name: Identifier for this bottleneck
        description: Human-readable description
        severity: How critical this bottleneck is
        loop_name: Which acceleration loop this affects
        constraint_type: Category of constraint
        current_value: Current measured value of the constraint
        threshold: Value at which this becomes a bottleneck
        addressability_score: 0-1 score of how addressable this is
        recommended_actions: Suggested interventions
    """

    name: str
    description: str
    severity: BottleneckSeverity
    loop_name: str
    constraint_type: str  # "data", "compute", "model", "hardware", "knowledge"
    current_value: float = 0.0
    threshold: float = 0.0
    addressability_score: float = 0.5
    recommended_actions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_active(self) -> bool:
        """Whether this bottleneck is currently limiting progress."""
        return self.current_value >= self.threshold

    @property
    def severity_score(self) -> float:
        """Numeric severity score (0-1)."""
        severity_map = {
            BottleneckSeverity.LOW: 0.25,
            BottleneckSeverity.MEDIUM: 0.5,
            BottleneckSeverity.HIGH: 0.75,
            BottleneckSeverity.CRITICAL: 1.0,
        }
        return severity_map[self.severity]

    @property
    def priority_score(self) -> float:
        """
        Combined score for prioritizing bottleneck resolution.
        Higher = more important to address.
        """
        # High severity + high addressability = high priority
        return self.severity_score * self.addressability_score

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "severity": self.severity.value,
            "loop_name": self.loop_name,
            "constraint_type": self.constraint_type,
            "current_value": self.current_value,
            "threshold": self.threshold,
            "is_active": self.is_active,
            "addressability_score": self.addressability_score,
            "priority_score": self.priority_score,
            "recommended_actions": self.recommended_actions,
            "metadata": self.metadata,
        }


@dataclass
class CrossLoopCoupling:
    """
    Measures the coupling strength between two acceleration loops.

    Cross-loop coupling indicates how improvements in one loop
    affect the dynamics of another loop.

    Attributes:
        source_loop: The loop providing the improvement
        target_loop: The loop receiving the benefit
        coupling_strength: 0-1 measure of coupling (1 = strong coupling)
        coupling_type: Nature of the coupling relationship
        lag_iterations: How many iterations before effect manifests
        description: Human-readable description of the coupling
    """

    source_loop: str
    target_loop: str
    coupling_strength: float  # 0-1
    coupling_type: str  # "direct", "indirect", "enabling", "amplifying"
    lag_iterations: int = 0
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate coupling strength is in valid range."""
        if not 0 <= self.coupling_strength <= 1:
            raise ValueError(f"coupling_strength must be in [0, 1], got {self.coupling_strength}")

    @property
    def is_strong(self) -> bool:
        """Whether this represents strong coupling (>0.5)."""
        return self.coupling_strength > 0.5

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "source_loop": self.source_loop,
            "target_loop": self.target_loop,
            "coupling_strength": self.coupling_strength,
            "coupling_type": self.coupling_type,
            "lag_iterations": self.lag_iterations,
            "is_strong": self.is_strong,
            "description": self.description,
            "metadata": self.metadata,
        }


@dataclass
class ProgressMetric:
    """
    Tracks progress within a specific domain or capability.

    Attributes:
        domain: Area being measured (e.g., "error_rate", "circuit_depth")
        current_value: Current measured value
        target_value: Goal value
        unit: Unit of measurement
        direction: Whether lower or higher is better
        history: Historical values for trend analysis
    """

    domain: str
    current_value: float
    target_value: float
    unit: str = ""
    direction: str = "lower"  # "lower" or "higher" is better
    history: List[tuple[datetime, float]] = field(default_factory=list)

    @property
    def progress_ratio(self) -> float:
        """Progress toward target (0-1, can exceed 1 if target met)."""
        if self.direction == "lower":
            if self.target_value == 0:
                return 1.0 if self.current_value == 0 else 0.0
            # For "lower is better", progress = how much we've reduced
            return 1.0 - (self.current_value / self.target_value)
        else:
            if self.target_value == 0:
                return float("inf") if self.current_value > 0 else 0.0
            return self.current_value / self.target_value

    @property
    def trend(self) -> Optional[float]:
        """Calculate trend from history (positive = improving)."""
        if len(self.history) < 2:
            return None
        values = [v for _, v in self.history[-10:]]  # Last 10 points
        if len(values) < 2:
            return None
        # Simple linear trend
        x = np.arange(len(values))
        slope = float(np.polyfit(x, values, 1)[0])
        # Adjust sign based on direction
        return -slope if self.direction == "lower" else slope

    def record(self, value: float, timestamp: Optional[datetime] = None) -> None:
        """Record a new measurement."""
        if timestamp is None:
            timestamp = datetime.now()
        self.history.append((timestamp, value))
        self.current_value = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "domain": self.domain,
            "current_value": self.current_value,
            "target_value": self.target_value,
            "unit": self.unit,
            "direction": self.direction,
            "progress_ratio": self.progress_ratio,
            "trend": self.trend,
            "history_length": len(self.history),
        }


class MetricsAggregator:
    """
    Aggregates and analyzes metrics across the framework.
    """

    def __init__(self) -> None:
        self.acceleration_metrics: Dict[str, List[AccelerationMetric]] = {}
        self.bottlenecks: Dict[str, List[BottleneckIndicator]] = {}
        self.couplings: List[CrossLoopCoupling] = []
        self.progress_metrics: Dict[str, ProgressMetric] = {}

    def add_acceleration_metric(self, metric: AccelerationMetric) -> None:
        """Add an acceleration metric."""
        if metric.name not in self.acceleration_metrics:
            self.acceleration_metrics[metric.name] = []
        self.acceleration_metrics[metric.name].append(metric)

    def add_bottleneck(self, bottleneck: BottleneckIndicator) -> None:
        """Add a bottleneck indicator."""
        if bottleneck.loop_name not in self.bottlenecks:
            self.bottlenecks[bottleneck.loop_name] = []
        self.bottlenecks[bottleneck.loop_name].append(bottleneck)

    def add_coupling(self, coupling: CrossLoopCoupling) -> None:
        """Add a cross-loop coupling."""
        self.couplings.append(coupling)

    def add_progress_metric(self, metric: ProgressMetric) -> None:
        """Add a progress metric."""
        self.progress_metrics[metric.domain] = metric

    def get_active_bottlenecks(self) -> List[BottleneckIndicator]:
        """Get all currently active bottlenecks, sorted by priority."""
        active = []
        for loop_bottlenecks in self.bottlenecks.values():
            active.extend([b for b in loop_bottlenecks if b.is_active])
        return sorted(active, key=lambda b: b.priority_score, reverse=True)

    def get_strong_couplings(self) -> List[CrossLoopCoupling]:
        """Get all strong cross-loop couplings."""
        return [c for c in self.couplings if c.is_strong]

    def compute_overall_acceleration(self) -> float:
        """Compute weighted average acceleration across all loops."""
        if not self.acceleration_metrics:
            return 1.0

        total_acceleration = 0.0
        count = 0
        for metrics in self.acceleration_metrics.values():
            if metrics:
                latest = metrics[-1]
                total_acceleration += latest.acceleration_ratio
                count += 1

        return total_acceleration / count if count > 0 else 1.0

    def summary(self) -> Dict[str, Any]:
        """Generate summary of all metrics."""
        return {
            "overall_acceleration": self.compute_overall_acceleration(),
            "active_bottlenecks": len(self.get_active_bottlenecks()),
            "strong_couplings": len(self.get_strong_couplings()),
            "loops_tracked": list(self.bottlenecks.keys()),
            "progress_domains": list(self.progress_metrics.keys()),
        }
