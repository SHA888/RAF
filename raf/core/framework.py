"""
Main Reciprocal Acceleration Framework class.

This module provides the central orchestration for analyzing co-evolutionary
dynamics between Quantum Computing and Machine Learning systems.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from raf.core.loop import AccelerationLoop, LoopState
from raf.core.metrics import CrossLoopCoupling, MetricsAggregator


@dataclass
class FrameworkAnalysis:
    """
    Results of a framework analysis.

    Attributes:
        timestamp: When the analysis was performed
        overall_acceleration: Aggregate acceleration across all loops
        loop_states: Current state of each loop
        bottlenecks: All identified bottlenecks, prioritized
        cross_loop_effects: Coupling effects between loops
        recommendations: Prioritized recommendations
        high_leverage_investments: Investments that affect multiple loops
    """

    timestamp: datetime = field(default_factory=datetime.now)
    overall_acceleration: float = 1.0
    loop_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    bottlenecks: List[Dict[str, Any]] = field(default_factory=list)
    cross_loop_effects: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    high_leverage_investments: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "overall_acceleration": self.overall_acceleration,
            "loop_states": self.loop_states,
            "bottlenecks": self.bottlenecks,
            "cross_loop_effects": self.cross_loop_effects,
            "recommendations": self.recommendations,
            "high_leverage_investments": self.high_leverage_investments,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


class ReciprocalAccelerationFramework:
    """
    Main framework for analyzing QC-ML co-evolutionary dynamics.

    The Reciprocal Acceleration Framework identifies and analyzes feedback
    loops between Quantum Computing and Machine Learning, providing:

    1. Loop dynamics analysis - How each acceleration loop is performing
    2. Bottleneck identification - What's limiting progress
    3. Cross-loop coupling - How loops affect each other
    4. Research prioritization - Where to invest for maximum impact

    Example:
        >>> from raf import ReciprocalAccelerationFramework
        >>> from raf.loops import ErrorMitigationLoop, AnsatzDesignLoop
        >>>
        >>> raf = ReciprocalAccelerationFramework()
        >>> raf.add_loop(ErrorMitigationLoop())
        >>> raf.add_loop(AnsatzDesignLoop())
        >>>
        >>> analysis = raf.analyze()
        >>> print(analysis.recommendations)
    """

    # Default cross-loop couplings based on RAF paper analysis
    DEFAULT_COUPLINGS = [
        {
            "source": "calibration_control",
            "target": "error_mitigation",
            "strength": 0.8,
            "type": "direct",
            "description": "Lower base error rates reduce mitigation requirements",
        },
        {
            "source": "calibration_control",
            "target": "ansatz_design",
            "strength": 0.7,
            "type": "enabling",
            "description": "Lower error rates enable larger feasible circuit depths",
        },
        {
            "source": "ansatz_design",
            "target": "error_mitigation",
            "strength": 0.6,
            "type": "indirect",
            "description": "Better ansätze can be more noise-resilient",
        },
        {
            "source": "ansatz_design",
            "target": "calibration_control",
            "strength": 0.5,
            "type": "indirect",
            "description": "Optimized circuits can probe specific noise mechanisms",
        },
        {
            "source": "error_mitigation",
            "target": "ansatz_design",
            "strength": 0.6,
            "type": "enabling",
            "description": "Better mitigation enables evaluation of deeper circuits",
        },
        {
            "source": "error_mitigation",
            "target": "calibration_control",
            "strength": 0.4,
            "type": "indirect",
            "description": "Mitigation insights inform noise characterization",
        },
    ]

    # High-leverage investments identified in RAF paper
    HIGH_LEVERAGE_INVESTMENTS = [
        {
            "name": "Surrogate Model Development",
            "description": "Neural surrogates that predict quantum circuit performance without execution",
            "affected_loops": ["error_mitigation", "ansatz_design", "calibration_control"],
            "impact_score": 0.9,
            "current_maturity": 0.3,
            "rationale": "Accelerates all three loops by reducing evaluation costs",
        },
        {
            "name": "Standardized Benchmarks",
            "description": "Benchmark suites analogous to ImageNet for quantum-ML",
            "affected_loops": ["error_mitigation", "ansatz_design"],
            "impact_score": 0.7,
            "current_maturity": 0.2,
            "rationale": "Enables systematic progress tracking and knowledge transfer",
        },
        {
            "name": "Cross-Platform Abstractions",
            "description": "Hardware abstraction layers enabling knowledge transfer across platforms",
            "affected_loops": ["ansatz_design", "calibration_control"],
            "impact_score": 0.8,
            "current_maturity": 0.4,
            "rationale": "Reduces redundant effort from hardware heterogeneity",
        },
        {
            "name": "Foundation Models for Quantum",
            "description": "Large pre-trained models capturing quantum circuit behavior",
            "affected_loops": ["error_mitigation", "ansatz_design", "calibration_control"],
            "impact_score": 0.85,
            "current_maturity": 0.1,
            "rationale": "Enables few-shot adaptation to new tasks",
        },
    ]

    def __init__(self, name: str = "RAF"):
        """
        Initialize the Reciprocal Acceleration Framework.

        Args:
            name: Identifier for this framework instance
        """
        self.name = name
        self.loops: Dict[str, AccelerationLoop] = {}
        self.metrics = MetricsAggregator()
        self.couplings: List[CrossLoopCoupling] = []
        self.analysis_history: List[FrameworkAnalysis] = []

        # Initialize default couplings
        self._init_default_couplings()

    def _init_default_couplings(self):
        """Initialize default cross-loop couplings."""
        for coupling_def in self.DEFAULT_COUPLINGS:
            coupling = CrossLoopCoupling(
                source_loop=coupling_def["source"],
                target_loop=coupling_def["target"],
                coupling_strength=coupling_def["strength"],
                coupling_type=coupling_def["type"],
                description=coupling_def["description"],
            )
            self.couplings.append(coupling)
            self.metrics.add_coupling(coupling)

    def add_loop(self, loop: AccelerationLoop) -> "ReciprocalAccelerationFramework":
        """
        Add an acceleration loop to the framework.

        Args:
            loop: The acceleration loop to add

        Returns:
            Self for method chaining
        """
        self.loops[loop.name] = loop
        return self

    def remove_loop(self, name: str) -> Optional[AccelerationLoop]:
        """
        Remove an acceleration loop from the framework.

        Args:
            name: Name of the loop to remove

        Returns:
            The removed loop, or None if not found
        """
        return self.loops.pop(name, None)

    def get_loop(self, name: str) -> Optional[AccelerationLoop]:
        """
        Get a loop by name.

        Args:
            name: Name of the loop

        Returns:
            The loop, or None if not found
        """
        return self.loops.get(name)

    def add_coupling(self, coupling: CrossLoopCoupling):
        """
        Add a custom cross-loop coupling.

        Args:
            coupling: The coupling to add
        """
        self.couplings.append(coupling)
        self.metrics.add_coupling(coupling)

    def iterate_all(self) -> Dict[str, LoopState]:
        """
        Execute one iteration of all loops.

        Returns:
            Dictionary mapping loop names to their updated states
        """
        states = {}
        for name, loop in self.loops.items():
            states[name] = loop.iterate()
        return states

    def analyze(self) -> FrameworkAnalysis:
        """
        Perform comprehensive analysis of the framework state.

        This analyzes all loops, identifies bottlenecks, computes
        cross-loop effects, and generates prioritized recommendations.

        Returns:
            FrameworkAnalysis with complete analysis results
        """
        analysis = FrameworkAnalysis()

        # Collect loop states
        for name, loop in self.loops.items():
            analysis.loop_states[name] = loop.summary()

        # Compute overall acceleration
        if self.loops:
            accelerations = [loop.state.acceleration_rate for loop in self.loops.values()]
            analysis.overall_acceleration = sum(accelerations) / len(accelerations)

        # Collect and prioritize bottlenecks
        all_bottlenecks = []
        for loop in self.loops.values():
            bottlenecks = loop.identify_bottlenecks()
            for b in bottlenecks:
                all_bottlenecks.append(b.to_dict())

        # Sort by priority score
        analysis.bottlenecks = sorted(
            all_bottlenecks, key=lambda b: b.get("priority_score", 0), reverse=True
        )

        # Analyze cross-loop effects
        analysis.cross_loop_effects = self._analyze_cross_loop_effects()

        # Generate recommendations
        analysis.recommendations = self._generate_recommendations(analysis)

        # Identify high-leverage investments
        analysis.high_leverage_investments = self._identify_high_leverage_investments()

        # Store in history
        self.analysis_history.append(analysis)

        return analysis

    def _analyze_cross_loop_effects(self) -> List[Dict[str, Any]]:
        """Analyze how loops are affecting each other."""
        effects = []

        for coupling in self.couplings:
            source_loop = self.loops.get(coupling.source_loop)
            target_loop = self.loops.get(coupling.target_loop)

            if source_loop and target_loop:
                # Estimate effect based on source acceleration and coupling strength
                source_accel = source_loop.state.acceleration_rate
                estimated_effect = (source_accel - 1.0) * coupling.coupling_strength

                effects.append(
                    {
                        "source": coupling.source_loop,
                        "target": coupling.target_loop,
                        "coupling_strength": coupling.coupling_strength,
                        "source_acceleration": source_accel,
                        "estimated_effect": estimated_effect,
                        "description": coupling.description,
                    }
                )

        return sorted(effects, key=lambda e: abs(e["estimated_effect"]), reverse=True)

    def _generate_recommendations(self, analysis: FrameworkAnalysis) -> List[str]:
        """Generate prioritized recommendations based on analysis."""
        recommendations = []

        # Recommendations from bottlenecks
        for bottleneck in analysis.bottlenecks[:3]:  # Top 3 bottlenecks
            if bottleneck.get("is_active"):
                for action in bottleneck.get("recommended_actions", []):
                    recommendations.append(f"[{bottleneck['loop_name']}] {action}")

        # Recommendations from loop states
        for name, state in analysis.loop_states.items():
            loop_status = state.get("state", {}).get("status", "")
            if loop_status == "bottlenecked":
                recommendations.append(
                    f"[{name}] Address critical bottlenecks to restore acceleration"
                )
            elif loop_status == "saturating":
                recommendations.append(
                    f"[{name}] Consider paradigm shift or new approaches as returns diminish"
                )

        # Recommendations from cross-loop analysis
        strong_couplings = [e for e in analysis.cross_loop_effects if e["coupling_strength"] > 0.7]
        if strong_couplings:
            top_coupling = strong_couplings[0]
            recommendations.append(
                f"Leverage strong coupling: improvements in {top_coupling['source']} "
                f"will significantly benefit {top_coupling['target']}"
            )

        # Add high-leverage investment recommendations
        for investment in self.HIGH_LEVERAGE_INVESTMENTS[:2]:
            if investment["current_maturity"] < 0.5:
                recommendations.append(
                    f"[High-Leverage] Invest in {investment['name']}: {investment['rationale']}"
                )

        return recommendations

    def _identify_high_leverage_investments(self) -> List[Dict[str, Any]]:
        """Identify investments that would accelerate multiple loops."""
        investments = []

        for inv in self.HIGH_LEVERAGE_INVESTMENTS:
            # Check which affected loops are actually in the framework
            active_affected = [loop for loop in inv["affected_loops"] if loop in self.loops]

            if active_affected:
                # Compute adjusted impact based on active loops
                coverage = len(active_affected) / len(inv["affected_loops"])
                adjusted_impact = float(inv["impact_score"]) * coverage

                investments.append(
                    {
                        "name": inv["name"],
                        "description": inv["description"],
                        "affected_loops": active_affected,
                        "impact_score": adjusted_impact,
                        "current_maturity": float(inv["current_maturity"]),
                        "opportunity_score": adjusted_impact * (1 - float(inv["current_maturity"])),
                        "rationale": inv["rationale"],
                    }
                )

        return sorted(investments, key=lambda i: i["opportunity_score"], reverse=True)

    def get_loop_coupling_matrix(self) -> Dict[str, Dict[str, float]]:
        """
        Get the coupling matrix between all loops.

        Returns:
            Nested dictionary with coupling strengths
        """
        loop_names = list(self.loops.keys())
        matrix = {name: {n: 0.0 for n in loop_names} for name in loop_names}

        for coupling in self.couplings:
            if coupling.source_loop in matrix and coupling.target_loop in matrix:
                matrix[coupling.source_loop][coupling.target_loop] = coupling.coupling_strength

        return matrix

    def predict_acceleration(self, iterations: int = 10) -> List[Dict[str, float]]:
        """
        Predict future acceleration based on current dynamics.

        This is a simplified model that accounts for:
        - Current acceleration rates
        - Cross-loop coupling effects
        - Bottleneck constraints

        Args:
            iterations: Number of iterations to predict

        Returns:
            List of predicted acceleration values per loop per iteration
        """
        predictions = []

        # Get current state
        current_accels = {name: loop.state.acceleration_rate for name, loop in self.loops.items()}

        coupling_matrix = self.get_loop_coupling_matrix()

        for i in range(iterations):
            new_accels = {}

            for name in self.loops:
                # Base: current acceleration with some decay
                base = current_accels[name] * 0.95

                # Add cross-loop effects
                cross_effect = 0.0
                for source, targets in coupling_matrix.items():
                    if name in targets and source in current_accels:
                        effect = (current_accels[source] - 1.0) * targets[name] * 0.1
                        cross_effect += effect

                new_accels[name] = max(0.5, min(2.0, base + cross_effect))

            predictions.append(new_accels)
            current_accels = new_accels

        return predictions

    def summary(self) -> Dict[str, Any]:
        """Generate a summary of the framework state."""
        return {
            "name": self.name,
            "loops": list(self.loops.keys()),
            "num_couplings": len(self.couplings),
            "overall_metrics": self.metrics.summary(),
            "analysis_count": len(self.analysis_history),
        }

    def __repr__(self) -> str:
        loop_names = list(self.loops.keys())
        return f"ReciprocalAccelerationFramework(loops={loop_names})"
