"""
Bottleneck analysis for the Reciprocal Acceleration Framework.

This module provides tools for identifying, analyzing, and prioritizing
bottlenecks across acceleration loops.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List

import numpy as np

from raf.core.metrics import BottleneckIndicator


@dataclass
class BottleneckCluster:
    """
    A cluster of related bottlenecks.

    Attributes:
        name: Cluster identifier
        bottlenecks: List of bottlenecks in this cluster
        common_type: Shared constraint type
        affected_loops: Loops affected by this cluster
        aggregate_severity: Combined severity score
        recommended_intervention: Unified intervention strategy
    """

    name: str
    bottlenecks: List[BottleneckIndicator]
    common_type: str
    affected_loops: List[str]
    aggregate_severity: float
    recommended_intervention: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "bottleneck_count": len(self.bottlenecks),
            "common_type": self.common_type,
            "affected_loops": self.affected_loops,
            "aggregate_severity": self.aggregate_severity,
            "recommended_intervention": self.recommended_intervention,
        }


class BottleneckAnalyzer:
    """
    Analyzes bottlenecks across the RAF to identify patterns and priorities.

    This analyzer:
    1. Clusters related bottlenecks
    2. Identifies systemic vs. local issues
    3. Computes intervention priorities
    4. Generates actionable recommendations

    Example:
        >>> from raf import ReciprocalAccelerationFramework
        >>> from raf.analysis import BottleneckAnalyzer
        >>>
        >>> raf = ReciprocalAccelerationFramework()
        >>> # ... add loops ...
        >>>
        >>> analyzer = BottleneckAnalyzer()
        >>> results = analyzer.analyze(raf)
        >>> print(results["priority_ranking"])
    """

    # Bottleneck type categories for clustering
    TYPE_CATEGORIES = {
        "resource": ["compute", "data", "hardware"],
        "knowledge": ["model", "knowledge"],
        "systemic": ["generalization", "heterogeneity"],
    }

    def __init__(self):
        """Initialize the bottleneck analyzer."""
        self.analysis_history: List[Dict[str, Any]] = []

    def analyze(self, framework) -> Dict[str, Any]:
        """
        Perform comprehensive bottleneck analysis.

        Args:
            framework: ReciprocalAccelerationFramework instance

        Returns:
            Dictionary with analysis results
        """
        # Collect all bottlenecks
        all_bottlenecks = self._collect_bottlenecks(framework)

        # Cluster bottlenecks
        clusters = self._cluster_bottlenecks(all_bottlenecks)

        # Compute priorities
        priority_ranking = self._compute_priorities(all_bottlenecks)

        # Identify systemic issues
        systemic_issues = self._identify_systemic_issues(all_bottlenecks, framework)

        # Generate recommendations
        recommendations = self._generate_recommendations(clusters, systemic_issues)

        results = {
            "total_bottlenecks": len(all_bottlenecks),
            "active_bottlenecks": len([b for b in all_bottlenecks if b.is_active]),
            "clusters": [c.to_dict() for c in clusters],
            "priority_ranking": priority_ranking,
            "systemic_issues": systemic_issues,
            "recommendations": recommendations,
            "by_loop": self._group_by_loop(all_bottlenecks),
            "by_type": self._group_by_type(all_bottlenecks),
        }

        self.analysis_history.append(results)
        return results

    def _collect_bottlenecks(self, framework) -> List[BottleneckIndicator]:
        """Collect all bottlenecks from framework loops."""
        bottlenecks = []
        for loop in framework.loops.values():
            loop_bottlenecks = loop.identify_bottlenecks()
            bottlenecks.extend(loop_bottlenecks)
        return bottlenecks

    def _cluster_bottlenecks(
        self, bottlenecks: List[BottleneckIndicator]
    ) -> List[BottleneckCluster]:
        """Cluster related bottlenecks."""
        clusters = []

        # Group by constraint type
        type_groups = defaultdict(list)
        for b in bottlenecks:
            type_groups[b.constraint_type].append(b)

        for constraint_type, group in type_groups.items():
            if len(group) >= 1:
                affected_loops = list(set(b.loop_name for b in group))
                aggregate_severity = np.mean([b.severity_score for b in group])

                # Determine category
                category = "other"
                for cat, types in self.TYPE_CATEGORIES.items():
                    if constraint_type in types:
                        category = cat
                        break

                cluster = BottleneckCluster(
                    name=f"{category}_{constraint_type}",
                    bottlenecks=group,
                    common_type=constraint_type,
                    affected_loops=affected_loops,
                    aggregate_severity=aggregate_severity,
                    recommended_intervention=self._get_intervention(constraint_type),
                )
                clusters.append(cluster)

        return sorted(clusters, key=lambda c: c.aggregate_severity, reverse=True)

    def _get_intervention(self, constraint_type: str) -> str:
        """Get recommended intervention for a constraint type."""
        interventions = {
            "compute": "Invest in surrogate models and efficient evaluation methods",
            "data": "Develop efficient data generation and transfer learning",
            "hardware": "Hardware upgrades or alternative platforms",
            "model": "Improve ML architectures and training procedures",
            "knowledge": "Fundamental research and paradigm exploration",
            "generalization": "Cross-domain training and abstraction layers",
            "heterogeneity": "Platform-agnostic methods and standardization",
        }
        return interventions.get(constraint_type, "Further investigation needed")

    def _compute_priorities(self, bottlenecks: List[BottleneckIndicator]) -> List[Dict[str, Any]]:
        """Compute priority ranking for bottlenecks."""
        priorities = []

        for b in bottlenecks:
            if b.is_active:
                # Priority = severity × addressability × (1 + cross-loop impact)
                cross_loop_factor = 1.0  # Could be enhanced with coupling analysis
                priority = b.severity_score * b.addressability_score * (1 + cross_loop_factor)

                priorities.append(
                    {
                        "name": b.name,
                        "loop": b.loop_name,
                        "priority_score": priority,
                        "severity": b.severity.value,
                        "addressability": b.addressability_score,
                        "recommended_actions": b.recommended_actions[:2],  # Top 2 actions
                    }
                )

        return sorted(priorities, key=lambda p: p["priority_score"], reverse=True)

    def _identify_systemic_issues(
        self, bottlenecks: List[BottleneckIndicator], framework
    ) -> List[Dict[str, Any]]:
        """Identify issues that affect multiple loops."""
        systemic = []

        # Check for bottlenecks appearing in multiple loops
        type_loop_map = defaultdict(set)
        for b in bottlenecks:
            if b.is_active:
                type_loop_map[b.constraint_type].add(b.loop_name)

        for constraint_type, loops in type_loop_map.items():
            if len(loops) >= 2:
                systemic.append(
                    {
                        "type": constraint_type,
                        "affected_loops": list(loops),
                        "is_systemic": True,
                        "description": f"{constraint_type} constraints affect {len(loops)} loops",
                        "leverage": "high" if len(loops) == len(framework.loops) else "medium",
                    }
                )

        return systemic

    def _generate_recommendations(
        self, clusters: List[BottleneckCluster], systemic_issues: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate prioritized recommendations."""
        recommendations = []

        # Address systemic issues first
        for issue in systemic_issues:
            if issue["leverage"] == "high":
                recommendations.append(
                    f"[HIGH LEVERAGE] Address {issue['type']} constraints - "
                    f"affects all loops: {', '.join(issue['affected_loops'])}"
                )

        # Then cluster-based recommendations
        for cluster in clusters[:3]:  # Top 3 clusters
            if cluster.aggregate_severity > 0.5:
                recommendations.append(
                    f"[{cluster.common_type.upper()}] {cluster.recommended_intervention} "
                    f"(affects: {', '.join(cluster.affected_loops)})"
                )

        return recommendations

    def _group_by_loop(self, bottlenecks: List[BottleneckIndicator]) -> Dict[str, List[Dict]]:
        """Group bottlenecks by loop."""
        grouped = defaultdict(list)
        for b in bottlenecks:
            grouped[b.loop_name].append(
                {
                    "name": b.name,
                    "severity": b.severity.value,
                    "is_active": b.is_active,
                    "priority_score": b.priority_score,
                }
            )
        return dict(grouped)

    def _group_by_type(self, bottlenecks: List[BottleneckIndicator]) -> Dict[str, int]:
        """Count bottlenecks by type."""
        counts = defaultdict(int)
        for b in bottlenecks:
            counts[b.constraint_type] += 1
        return dict(counts)

    def compare_analyses(self, idx1: int = -2, idx2: int = -1) -> Dict[str, Any]:
        """
        Compare two analyses to track progress.

        Args:
            idx1: Index of first analysis (default: second-to-last)
            idx2: Index of second analysis (default: last)

        Returns:
            Comparison results
        """
        if len(self.analysis_history) < 2:
            return {"error": "Need at least 2 analyses to compare"}

        a1 = self.analysis_history[idx1]
        a2 = self.analysis_history[idx2]

        return {
            "bottleneck_change": a2["active_bottlenecks"] - a1["active_bottlenecks"],
            "resolved": a1["active_bottlenecks"] - a2["active_bottlenecks"],
            "new": a2["active_bottlenecks"] - a1["active_bottlenecks"],
            "systemic_change": len(a2["systemic_issues"]) - len(a1["systemic_issues"]),
        }
