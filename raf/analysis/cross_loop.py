"""
Cross-loop interaction analysis for the Reciprocal Acceleration Framework.

This module analyzes how improvements in one loop affect other loops,
identifying leverage points and synergistic opportunities.
"""

from dataclasses import dataclass
from typing import Any, Dict, List

import numpy as np


@dataclass
class InteractionEffect:
    """
    Represents the effect of one loop's progress on another.

    Attributes:
        source_loop: Loop providing the improvement
        target_loop: Loop receiving the effect
        effect_magnitude: Estimated magnitude of effect
        effect_type: Type of effect (enabling, amplifying, etc.)
        confidence: Confidence in the estimate
        description: Human-readable description
    """

    source_loop: str
    target_loop: str
    effect_magnitude: float
    effect_type: str
    confidence: float
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_loop": self.source_loop,
            "target_loop": self.target_loop,
            "effect_magnitude": self.effect_magnitude,
            "effect_type": self.effect_type,
            "confidence": self.confidence,
            "description": self.description,
        }


class CrossLoopAnalyzer:
    """
    Analyzes interactions between acceleration loops.

    This analyzer:
    1. Computes coupling matrices
    2. Identifies leverage points
    3. Predicts cascade effects
    4. Recommends investment allocation

    Example:
        >>> from raf import ReciprocalAccelerationFramework
        >>> from raf.analysis import CrossLoopAnalyzer
        >>>
        >>> raf = ReciprocalAccelerationFramework()
        >>> # ... add loops ...
        >>>
        >>> analyzer = CrossLoopAnalyzer()
        >>> results = analyzer.analyze(raf)
        >>> print(results["leverage_points"])
    """

    def __init__(self):
        """Initialize the cross-loop analyzer."""
        self.analysis_history: List[Dict[str, Any]] = []

    def analyze(self, framework) -> Dict[str, Any]:
        """
        Perform comprehensive cross-loop analysis.

        Args:
            framework: ReciprocalAccelerationFramework instance

        Returns:
            Dictionary with analysis results
        """
        # Build coupling matrix
        coupling_matrix = self._build_coupling_matrix(framework)

        # Compute current effects
        current_effects = self._compute_current_effects(framework)

        # Identify leverage points
        leverage_points = self._identify_leverage_points(coupling_matrix, framework)

        # Predict cascade effects
        cascade_predictions = self._predict_cascades(coupling_matrix, framework)

        # Compute optimal investment allocation
        allocation = self._compute_optimal_allocation(coupling_matrix, framework)

        results = {
            "coupling_matrix": coupling_matrix,
            "current_effects": [e.to_dict() for e in current_effects],
            "leverage_points": leverage_points,
            "cascade_predictions": cascade_predictions,
            "optimal_allocation": allocation,
            "total_coupling_strength": self._total_coupling(coupling_matrix),
            "network_density": self._network_density(coupling_matrix),
        }

        self.analysis_history.append(results)
        return results

    def _build_coupling_matrix(self, framework) -> Dict[str, Dict[str, float]]:
        """Build the coupling matrix from framework couplings."""
        loop_names = list(framework.loops.keys())
        matrix = {name: {n: 0.0 for n in loop_names} for name in loop_names}

        for coupling in framework.couplings:
            if coupling.source_loop in matrix and coupling.target_loop in matrix:
                matrix[coupling.source_loop][coupling.target_loop] = coupling.coupling_strength

        return matrix

    def _compute_current_effects(self, framework) -> List[InteractionEffect]:
        """Compute current interaction effects based on loop states."""
        effects = []

        for coupling in framework.couplings:
            source_loop = framework.loops.get(coupling.source_loop)
            target_loop = framework.loops.get(coupling.target_loop)

            if source_loop and target_loop:
                # Effect = (source acceleration - 1) × coupling strength
                source_accel = source_loop.state.acceleration_rate
                effect_mag = (source_accel - 1.0) * coupling.coupling_strength

                # Confidence based on iteration count
                confidence = min(1.0, source_loop.state.iteration / 10)

                effects.append(
                    InteractionEffect(
                        source_loop=coupling.source_loop,
                        target_loop=coupling.target_loop,
                        effect_magnitude=effect_mag,
                        effect_type=coupling.coupling_type,
                        confidence=confidence,
                        description=coupling.description,
                    )
                )

        return sorted(effects, key=lambda e: abs(e.effect_magnitude), reverse=True)

    def _identify_leverage_points(
        self, coupling_matrix: Dict[str, Dict[str, float]], framework
    ) -> List[Dict[str, Any]]:
        """Identify high-leverage intervention points."""
        leverage_points = []

        for loop_name in coupling_matrix:
            # Compute outgoing influence (how much this loop affects others)
            outgoing = sum(coupling_matrix[loop_name].values())

            # Compute incoming influence (how much others affect this loop)
            incoming = sum(coupling_matrix[other][loop_name] for other in coupling_matrix)

            # Leverage = outgoing influence × (1 + addressability)
            loop = framework.loops.get(loop_name)
            if loop:
                bottlenecks = loop.identify_bottlenecks()
                avg_addressability = (
                    np.mean([b.addressability_score for b in bottlenecks]) if bottlenecks else 0.5
                )
                leverage = outgoing * (1 + avg_addressability)

                leverage_points.append(
                    {
                        "loop": loop_name,
                        "outgoing_influence": outgoing,
                        "incoming_influence": incoming,
                        "leverage_score": leverage,
                        "addressability": avg_addressability,
                        "recommendation": self._get_leverage_recommendation(
                            loop_name, outgoing, incoming
                        ),
                    }
                )

        return sorted(leverage_points, key=lambda p: p["leverage_score"], reverse=True)

    def _get_leverage_recommendation(self, loop_name: str, outgoing: float, incoming: float) -> str:
        """Generate recommendation based on leverage analysis."""
        if outgoing > incoming * 1.5:
            return f"High-leverage: Improvements in {loop_name} will cascade to other loops"
        elif incoming > outgoing * 1.5:
            return f"Dependent: {loop_name} benefits from improvements in other loops"
        else:
            return f"Balanced: {loop_name} both influences and is influenced by other loops"

    def _predict_cascades(
        self, coupling_matrix: Dict[str, Dict[str, float]], framework
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Predict cascade effects from improvements in each loop."""
        predictions = {}

        for source_loop in coupling_matrix:
            cascade = []

            # First-order effects
            for target_loop, strength in coupling_matrix[source_loop].items():
                if strength > 0:
                    cascade.append(
                        {
                            "target": target_loop,
                            "order": 1,
                            "strength": strength,
                            "cumulative": strength,
                        }
                    )

            # Second-order effects
            for first_target, first_strength in coupling_matrix[source_loop].items():
                if first_strength > 0:
                    for second_target, second_strength in coupling_matrix[first_target].items():
                        if second_strength > 0 and second_target != source_loop:
                            cumulative = first_strength * second_strength
                            if cumulative > 0.1:  # Threshold for significance
                                cascade.append(
                                    {
                                        "target": second_target,
                                        "order": 2,
                                        "strength": second_strength,
                                        "cumulative": cumulative,
                                        "via": first_target,
                                    }
                                )

            predictions[source_loop] = sorted(cascade, key=lambda c: c["cumulative"], reverse=True)

        return predictions

    def _compute_optimal_allocation(
        self, coupling_matrix: Dict[str, Dict[str, float]], framework
    ) -> Dict[str, float]:
        """Compute optimal resource allocation across loops."""
        allocations = {}

        # Compute total impact potential for each loop
        impact_scores = {}
        for loop_name in coupling_matrix:
            # Direct impact (outgoing influence)
            direct = sum(coupling_matrix[loop_name].values())

            # Cascade impact (second-order effects)
            cascade = 0.0
            for target, strength in coupling_matrix[loop_name].items():
                cascade += strength * sum(coupling_matrix[target].values())

            # Current state factor (prioritize loops that are accelerating)
            loop = framework.loops.get(loop_name)
            state_factor = 1.0
            if loop:
                if loop.state.acceleration_rate > 1.0:
                    state_factor = 1.2  # Boost accelerating loops
                elif loop.state.status.value == "bottlenecked":
                    state_factor = 0.8  # Reduce bottlenecked loops

            impact_scores[loop_name] = (direct + 0.5 * cascade) * state_factor

        # Normalize to get allocation percentages
        total_impact = sum(impact_scores.values())
        if total_impact > 0:
            for loop_name, impact in impact_scores.items():
                allocations[loop_name] = impact / total_impact
        else:
            # Equal allocation if no coupling data
            n_loops = len(coupling_matrix)
            for loop_name in coupling_matrix:
                allocations[loop_name] = 1.0 / n_loops if n_loops > 0 else 0.0

        return allocations

    def _total_coupling(self, coupling_matrix: Dict[str, Dict[str, float]]) -> float:
        """Compute total coupling strength in the system."""
        total = 0.0
        for source in coupling_matrix:
            for target, strength in coupling_matrix[source].items():
                total += strength
        return total

    def _network_density(self, coupling_matrix: Dict[str, Dict[str, float]]) -> float:
        """Compute network density (fraction of possible connections that exist)."""
        n = len(coupling_matrix)
        if n <= 1:
            return 0.0

        max_connections = n * (n - 1)  # Directed graph
        actual_connections = sum(
            1
            for source in coupling_matrix
            for target, strength in coupling_matrix[source].items()
            if strength > 0
        )

        return actual_connections / max_connections

    def simulate_intervention(
        self, framework, target_loop: str, improvement: float = 0.2
    ) -> Dict[str, float]:
        """
        Simulate the effect of an intervention on one loop.

        Args:
            framework: RAF instance
            target_loop: Loop to improve
            improvement: Magnitude of improvement

        Returns:
            Predicted effects on all loops
        """
        coupling_matrix = self._build_coupling_matrix(framework)
        effects = {loop: 0.0 for loop in coupling_matrix}
        effects[target_loop] = improvement

        # Propagate through coupling matrix
        for _ in range(3):  # 3 iterations for cascade
            new_effects = effects.copy()
            for source, targets in coupling_matrix.items():
                for target, strength in targets.items():
                    if effects[source] > 0:
                        new_effects[target] += effects[source] * strength * 0.5
            effects = new_effects

        return effects
