"""
Ansatz Design Loop implementation.

This loop operates at the algorithm/circuit level:

QAS → Improved Circuits → Better QML Results → Training Signal → Neural Surrogates → Efficient QAS

The loop accelerates through learned inductive biases. As QAS systems accumulate
experience across problem instances, they develop "intuition" for effective circuit
motifs, reducing the search space for new problems.
"""

from dataclasses import dataclass
from typing import Any

import numpy as np

from raf.core.loop import AccelerationLoop, LoopLevel, LoopState
from raf.core.metrics import (
    AccelerationMetric,
    BottleneckIndicator,
    BottleneckSeverity,
    ProgressMetric,
)


@dataclass
class AnsatzDesignState:
    """
    State specific to the Ansatz Design Loop.

    Attributes:
        circuit_quality: Quality of discovered circuits (0-1)
        search_efficiency: Efficiency of architecture search (evaluations per discovery)
        surrogate_accuracy: Accuracy of neural surrogate models (0-1)
        problem_coverage: Number of problem types with good ansätze
        evaluation_cost: Cost per circuit evaluation (relative)
        hardware_platforms: Number of hardware platforms supported
    """

    circuit_quality: float = 0.5
    search_efficiency: float = 0.1  # Higher is better
    surrogate_accuracy: float = 0.3
    problem_coverage: int = 5
    evaluation_cost: float = 1.0
    hardware_platforms: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "circuit_quality": self.circuit_quality,
            "search_efficiency": self.search_efficiency,
            "surrogate_accuracy": self.surrogate_accuracy,
            "problem_coverage": self.problem_coverage,
            "evaluation_cost": self.evaluation_cost,
            "hardware_platforms": self.hardware_platforms,
        }


class AnsatzDesignLoop(AccelerationLoop):
    """
    Ansatz Design Loop - Operating at the algorithm/circuit level.

    This loop captures the feedback cycle where:
    1. ML-based architecture search (QAS) discovers improved circuit structures
    2. Improved circuits achieve better results on quantum learning tasks
    3. Quantum learning results provide training signal for neural surrogates
    4. Neural surrogates enable more efficient architecture search
    5. Search discovers next-generation circuits

    Bottlenecks:
    - Evaluation cost (quantum circuit execution is slow/expensive)
    - Surrogate accuracy (imperfect predictions limit search efficiency)
    - Hardware heterogeneity (circuits optimal for one platform may fail on others)

    Example:
        >>> loop = AnsatzDesignLoop()
        >>> loop.set_surrogate_accuracy(0.7)
        >>> loop.set_circuit_quality(0.6)
        >>> state = loop.iterate()
        >>> print(state.acceleration_rate)
    """

    # Loop stage definitions
    STAGES = [
        "qas",  # Quantum Architecture Search
        "improved_circuits",  # Better circuit structures
        "qml_results",  # Quantum ML task results
        "training_signal",  # Signal for surrogate training
        "neural_surrogates",  # Improved surrogate models
    ]

    # Bottleneck type definitions
    BOTTLENECK_TYPES = [
        "evaluation_cost",  # Cost of quantum circuit evaluation
        "surrogate_accuracy",  # Accuracy of performance predictors
        "hardware_heterogeneity",  # Cross-platform generalization
        "search_space",  # Size of architecture search space
    ]

    # Search strategy options
    SEARCH_STRATEGIES = [
        "evolutionary",  # Evolutionary algorithms
        "reinforcement_learning",  # RL-based search
        "gradient_based",  # Differentiable architecture search
        "monte_carlo_tree",  # MCTS-based search
        "bayesian",  # Bayesian optimization
    ]

    def __init__(
        self,
        name: str = "ansatz_design",
        initial_quality: float = 0.5,
        initial_surrogate_accuracy: float = 0.3,
        search_strategy: str = "evolutionary",
    ):
        """
        Initialize the Ansatz Design Loop.

        Args:
            name: Identifier for this loop instance
            initial_quality: Starting circuit quality (0-1)
            initial_surrogate_accuracy: Starting surrogate accuracy (0-1)
            search_strategy: QAS strategy to use
        """
        super().__init__(
            name=name,
            level=LoopLevel.ALGORITHM,
            description="Quantum architecture search feedback loop at the algorithm level",
        )

        self.ad_state = AnsatzDesignState(
            circuit_quality=initial_quality,
            surrogate_accuracy=initial_surrogate_accuracy,
        )
        self.search_strategy = search_strategy

        # Initialize progress metrics
        self.metrics.progress["circuit_quality"] = ProgressMetric(
            domain="circuit_quality",
            current_value=initial_quality,
            target_value=0.95,
            direction="higher",
        )
        self.metrics.progress["surrogate_accuracy"] = ProgressMetric(
            domain="surrogate_accuracy",
            current_value=initial_surrogate_accuracy,
            target_value=0.9,
            direction="higher",
        )
        self.metrics.progress["search_efficiency"] = ProgressMetric(
            domain="search_efficiency",
            current_value=0.1,
            target_value=0.8,
            direction="higher",
        )

    @property
    def stages(self) -> list[str]:
        return self.STAGES

    @property
    def bottleneck_types(self) -> list[str]:
        return self.BOTTLENECK_TYPES

    def set_circuit_quality(self, quality: float) -> None:
        """Set the current circuit quality."""
        self.ad_state.circuit_quality = np.clip(quality, 0.0, 1.0)
        self.metrics.progress["circuit_quality"].record(quality)

    def set_search_efficiency(self, efficiency: float) -> None:
        """Set the current search efficiency."""
        self.ad_state.search_efficiency = np.clip(efficiency, 0.0, 1.0)
        self.metrics.progress["search_efficiency"].record(efficiency)

    def set_surrogate_accuracy(self, accuracy: float) -> None:
        """Set the current surrogate model accuracy."""
        self.ad_state.surrogate_accuracy = np.clip(accuracy, 0.0, 1.0)
        self.metrics.progress["surrogate_accuracy"].record(accuracy)

    def set_problem_coverage(self, coverage: int) -> None:
        """Set the number of problem types with good ansätze."""
        self.ad_state.problem_coverage = max(1, coverage)

    def set_evaluation_cost(self, cost: float) -> None:
        """Set the current evaluation cost."""
        self.ad_state.evaluation_cost = max(0.1, cost)

    def set_hardware_platforms(self, platforms: int) -> None:
        """Set the number of supported hardware platforms."""
        self.ad_state.hardware_platforms = max(1, platforms)

    def compute_acceleration(self) -> AccelerationMetric:
        """
        Compute the current acceleration rate.

        Acceleration is computed based on:
        - Improvement in circuit quality
        - Growth in search efficiency
        - Improvement in surrogate accuracy
        - Expansion of problem coverage
        """
        # Get historical values
        quality_history = self.metrics.progress["circuit_quality"].history
        efficiency_history = self.metrics.progress["search_efficiency"].history
        surrogate_history = self.metrics.progress["surrogate_accuracy"].history

        # Compute acceleration components
        quality_factor = 1.0
        if len(quality_history) >= 2:
            prev = quality_history[-2][1]
            curr = self.ad_state.circuit_quality
            if prev > 0:
                quality_factor = curr / prev

        efficiency_factor = 1.0
        if len(efficiency_history) >= 2:
            prev = efficiency_history[-2][1]
            curr = self.ad_state.search_efficiency
            if prev > 0:
                efficiency_factor = curr / prev

        surrogate_factor = 1.0
        if len(surrogate_history) >= 2:
            prev = surrogate_history[-2][1]
            curr = self.ad_state.surrogate_accuracy
            if prev > 0:
                surrogate_factor = curr / prev

        # Learned inductive bias effect: more problems → better priors
        coverage_factor = np.log1p(self.ad_state.problem_coverage) / 3.0

        # Cost efficiency
        cost_factor = 1.0 / self.ad_state.evaluation_cost

        # Combined acceleration
        acceleration = (
            quality_factor
            * efficiency_factor
            * surrogate_factor
            * (1 + coverage_factor)
            * cost_factor
        ) ** 0.2

        return AccelerationMetric(
            name=f"{self.name}_acceleration",
            value=acceleration,
            baseline=1.0,
            iteration=self.state.iteration,
            metadata={
                "quality_factor": quality_factor,
                "efficiency_factor": efficiency_factor,
                "surrogate_factor": surrogate_factor,
                "coverage_factor": coverage_factor,
                "cost_factor": cost_factor,
                "search_strategy": self.search_strategy,
            },
        )

    def identify_bottlenecks(self) -> list[BottleneckIndicator]:
        """
        Identify current bottlenecks in the loop.

        Checks for:
        1. High evaluation cost
        2. Low surrogate accuracy
        3. Hardware heterogeneity issues
        4. Large search space
        """
        bottlenecks = []

        # Bottleneck 1: Evaluation cost
        if self.ad_state.evaluation_cost > 2.0:
            severity = (
                BottleneckSeverity.CRITICAL
                if self.ad_state.evaluation_cost > 10.0
                else (
                    BottleneckSeverity.HIGH
                    if self.ad_state.evaluation_cost > 5.0
                    else BottleneckSeverity.MEDIUM
                )
            )
            bottlenecks.append(
                BottleneckIndicator(
                    name="high_evaluation_cost",
                    description="Each architecture evaluation requires expensive quantum circuit execution",
                    severity=severity,
                    loop_name=self.name,
                    constraint_type="compute",
                    current_value=self.ad_state.evaluation_cost,
                    threshold=2.0,
                    addressability_score=0.7,
                    recommended_actions=[
                        "Develop more accurate neural surrogate models",
                        "Use multi-fidelity optimization (cheap approximations first)",
                        "Implement early stopping for unpromising architectures",
                        "Leverage classical simulation for initial screening",
                    ],
                )
            )

        # Bottleneck 2: Surrogate accuracy
        if self.ad_state.surrogate_accuracy < 0.6:
            severity = (
                BottleneckSeverity.HIGH
                if self.ad_state.surrogate_accuracy < 0.4
                else BottleneckSeverity.MEDIUM
            )
            bottlenecks.append(
                BottleneckIndicator(
                    name="low_surrogate_accuracy",
                    description="Neural surrogates cannot accurately predict circuit performance",
                    severity=severity,
                    loop_name=self.name,
                    constraint_type="model",
                    current_value=self.ad_state.surrogate_accuracy,
                    threshold=0.6,
                    addressability_score=0.8,
                    recommended_actions=[
                        "Collect more diverse training data for surrogates",
                        "Use graph neural networks to capture circuit structure",
                        "Implement uncertainty-aware surrogates (Bayesian approaches)",
                        "Transfer learning from related problem domains",
                    ],
                )
            )

        # Bottleneck 3: Hardware heterogeneity
        if self.ad_state.hardware_platforms == 1 and self.ad_state.circuit_quality > 0.7:
            bottlenecks.append(
                BottleneckIndicator(
                    name="hardware_heterogeneity",
                    description="Circuits optimized for one platform may not transfer to others",
                    severity=BottleneckSeverity.MEDIUM,
                    loop_name=self.name,
                    constraint_type="hardware",
                    current_value=1.0 / self.ad_state.hardware_platforms,
                    threshold=0.5,
                    addressability_score=0.5,
                    recommended_actions=[
                        "Develop hardware-agnostic circuit representations",
                        "Train on multiple hardware backends simultaneously",
                        "Create abstraction layers for cross-platform optimization",
                        "Focus on hardware-native gate sets",
                    ],
                )
            )

        # Bottleneck 4: Search efficiency
        if self.ad_state.search_efficiency < 0.2:
            bottlenecks.append(
                BottleneckIndicator(
                    name="low_search_efficiency",
                    description="Architecture search requires too many evaluations per discovery",
                    severity=BottleneckSeverity.MEDIUM,
                    loop_name=self.name,
                    constraint_type="compute",
                    current_value=self.ad_state.search_efficiency,
                    threshold=0.2,
                    addressability_score=0.7,
                    recommended_actions=[
                        "Use curriculum learning to start with simpler circuits",
                        "Implement weight sharing across candidate architectures",
                        "Apply MCTS or other sample-efficient search methods",
                        "Leverage prior knowledge about effective circuit motifs",
                    ],
                )
            )

        return bottlenecks

    def get_recommendations(self) -> list[str]:
        """Generate recommendations for accelerating this loop."""
        recommendations = []

        # Based on current state
        if self.ad_state.surrogate_accuracy < 0.6:
            recommendations.append(
                "Priority: Improve neural surrogate models to reduce evaluation costs"
            )

        if self.ad_state.circuit_quality < 0.7:
            recommendations.append("Expand search to discover higher-quality circuit architectures")

        if self.ad_state.problem_coverage < 10:
            recommendations.append("Apply QAS to more problem types to build transferable priors")

        if self.ad_state.hardware_platforms == 1:
            recommendations.append(
                "Extend to multiple hardware platforms for broader applicability"
            )

        # Strategy-specific recommendations
        if self.search_strategy == "evolutionary":
            recommendations.append(
                "Consider hybrid approach: evolutionary search with surrogate-guided selection"
            )
        elif self.search_strategy == "reinforcement_learning":
            recommendations.append("Implement curriculum learning for progressive complexity")

        # Based on loop dynamics
        if self.state.status.value == "accelerating":
            recommendations.append("Loop is accelerating; consider expanding problem coverage")
        elif self.state.status.value == "bottlenecked":
            recommendations.append("Focus on surrogate model improvement to unblock the loop")

        return recommendations

    def simulate_iteration(
        self,
        quality_improvement: float = 0.03,
        efficiency_improvement: float = 0.05,
        surrogate_improvement: float = 0.04,
    ) -> LoopState:
        """
        Simulate one iteration with specified improvement rates.

        Args:
            quality_improvement: Additive improvement in circuit quality
            efficiency_improvement: Additive improvement in search efficiency
            surrogate_improvement: Additive improvement in surrogate accuracy

        Returns:
            Updated loop state
        """
        # Apply improvements (with diminishing returns near limits)
        quality_room = 1.0 - self.ad_state.circuit_quality
        new_quality = self.ad_state.circuit_quality + quality_improvement * quality_room

        efficiency_room = 1.0 - self.ad_state.search_efficiency
        new_efficiency = self.ad_state.search_efficiency + efficiency_improvement * efficiency_room

        surrogate_room = 1.0 - self.ad_state.surrogate_accuracy
        new_surrogate = self.ad_state.surrogate_accuracy + surrogate_improvement * surrogate_room

        # Update state
        self.set_circuit_quality(new_quality)
        self.set_search_efficiency(new_efficiency)
        self.set_surrogate_accuracy(new_surrogate)

        # Evaluation cost decreases with better surrogates
        new_cost = self.ad_state.evaluation_cost * (1.0 - 0.1 * new_surrogate)
        self.set_evaluation_cost(max(0.5, new_cost))

        # Run iteration
        return self.iterate()

    def summary(self) -> dict[str, Any]:
        """Generate a summary including ansatz design-specific state."""
        base_summary = super().summary()
        base_summary["ad_state"] = self.ad_state.to_dict()
        base_summary["search_strategy"] = self.search_strategy
        return base_summary
