"""
Research prioritization for the Reciprocal Acceleration Framework.

This module provides tools for prioritizing research investments
based on loop dynamics, bottleneck analysis, and cross-loop effects.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import numpy as np


class InvestmentCategory(Enum):
    """Categories of research investment."""
    SURROGATE_MODELS = "surrogate_models"
    BENCHMARKS = "benchmarks"
    ABSTRACTIONS = "abstractions"
    FOUNDATION_MODELS = "foundation_models"
    ERROR_MITIGATION = "error_mitigation"
    ARCHITECTURE_SEARCH = "architecture_search"
    CALIBRATION = "calibration"
    HARDWARE = "hardware"


@dataclass
class InvestmentOpportunity:
    """
    Represents a research investment opportunity.
    
    Attributes:
        name: Investment identifier
        category: Investment category
        description: What the investment entails
        affected_loops: Which loops benefit
        impact_score: Expected impact (0-1)
        maturity: Current maturity level (0-1)
        effort: Estimated effort required (relative)
        timeline: Expected timeline to impact
        roi_score: Return on investment score
    """
    name: str
    category: InvestmentCategory
    description: str
    affected_loops: List[str]
    impact_score: float
    maturity: float
    effort: float
    timeline: str
    roi_score: float = 0.0
    
    def __post_init__(self):
        # Compute ROI: impact × (1 - maturity) / effort
        if self.effort > 0:
            self.roi_score = self.impact_score * (1 - self.maturity) / self.effort
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "affected_loops": self.affected_loops,
            "impact_score": self.impact_score,
            "maturity": self.maturity,
            "effort": self.effort,
            "timeline": self.timeline,
            "roi_score": self.roi_score,
        }


class ResearchPrioritizer:
    """
    Prioritizes research investments based on RAF analysis.
    
    This prioritizer:
    1. Evaluates investment opportunities
    2. Considers loop dynamics and bottlenecks
    3. Accounts for cross-loop effects
    4. Generates prioritized roadmaps
    
    Example:
        >>> from raf import ReciprocalAccelerationFramework
        >>> from raf.analysis import ResearchPrioritizer
        >>> 
        >>> raf = ReciprocalAccelerationFramework()
        >>> # ... add loops ...
        >>> 
        >>> prioritizer = ResearchPrioritizer()
        >>> roadmap = prioritizer.generate_roadmap(raf)
        >>> print(roadmap["priority_investments"])
    """
    
    # Default investment opportunities based on RAF paper
    DEFAULT_OPPORTUNITIES = [
        {
            "name": "Neural Surrogate Models",
            "category": InvestmentCategory.SURROGATE_MODELS,
            "description": "Neural networks predicting quantum circuit performance without execution",
            "affected_loops": ["error_mitigation", "ansatz_design", "calibration_control"],
            "impact_score": 0.9,
            "maturity": 0.3,
            "effort": 1.5,
            "timeline": "1-2 years",
        },
        {
            "name": "Quantum ML Benchmarks",
            "category": InvestmentCategory.BENCHMARKS,
            "description": "Standardized benchmark suites for quantum ML evaluation",
            "affected_loops": ["error_mitigation", "ansatz_design"],
            "impact_score": 0.7,
            "maturity": 0.2,
            "effort": 1.0,
            "timeline": "6-12 months",
        },
        {
            "name": "Cross-Platform Abstractions",
            "category": InvestmentCategory.ABSTRACTIONS,
            "description": "Hardware abstraction layers for cross-platform optimization",
            "affected_loops": ["ansatz_design", "calibration_control"],
            "impact_score": 0.8,
            "maturity": 0.4,
            "effort": 1.2,
            "timeline": "1-2 years",
        },
        {
            "name": "Quantum Foundation Models",
            "category": InvestmentCategory.FOUNDATION_MODELS,
            "description": "Large pre-trained models for quantum circuit behavior",
            "affected_loops": ["error_mitigation", "ansatz_design", "calibration_control"],
            "impact_score": 0.85,
            "maturity": 0.1,
            "effort": 2.0,
            "timeline": "2-3 years",
        },
        {
            "name": "Integrated ML-QEM",
            "category": InvestmentCategory.ERROR_MITIGATION,
            "description": "ML error mitigation integrated into quantum software stacks",
            "affected_loops": ["error_mitigation"],
            "impact_score": 0.75,
            "maturity": 0.4,
            "effort": 0.8,
            "timeline": "6-12 months",
        },
        {
            "name": "Automated QAS",
            "category": InvestmentCategory.ARCHITECTURE_SEARCH,
            "description": "Fully automated quantum architecture search systems",
            "affected_loops": ["ansatz_design"],
            "impact_score": 0.8,
            "maturity": 0.35,
            "effort": 1.3,
            "timeline": "1-2 years",
        },
        {
            "name": "Continuous Calibration",
            "category": InvestmentCategory.CALIBRATION,
            "description": "Always-on ML-based calibration tracking drift in real-time",
            "affected_loops": ["calibration_control"],
            "impact_score": 0.7,
            "maturity": 0.3,
            "effort": 1.0,
            "timeline": "1 year",
        },
        {
            "name": "Physics-Informed Noise Models",
            "category": InvestmentCategory.CALIBRATION,
            "description": "ML models incorporating physical noise structure",
            "affected_loops": ["calibration_control", "error_mitigation"],
            "impact_score": 0.75,
            "maturity": 0.25,
            "effort": 1.2,
            "timeline": "1-2 years",
        },
    ]
    
    def __init__(self):
        """Initialize the research prioritizer."""
        self.opportunities: List[InvestmentOpportunity] = []
        self._init_default_opportunities()
    
    def _init_default_opportunities(self):
        """Initialize default investment opportunities."""
        for opp_def in self.DEFAULT_OPPORTUNITIES:
            opp = InvestmentOpportunity(**opp_def)
            self.opportunities.append(opp)
    
    def add_opportunity(self, opportunity: InvestmentOpportunity):
        """Add a custom investment opportunity."""
        self.opportunities.append(opportunity)
    
    def generate_roadmap(self, framework) -> Dict[str, Any]:
        """
        Generate a prioritized research roadmap.
        
        Args:
            framework: ReciprocalAccelerationFramework instance
            
        Returns:
            Dictionary with roadmap details
        """
        # Adjust opportunities based on framework state
        adjusted_opportunities = self._adjust_for_framework(framework)
        
        # Rank by ROI
        ranked = sorted(adjusted_opportunities, key=lambda o: o.roi_score, reverse=True)
        
        # Group by timeline
        timeline_groups = self._group_by_timeline(ranked)
        
        # Generate phase recommendations
        phases = self._generate_phases(ranked, framework)
        
        # Compute expected acceleration
        expected_acceleration = self._compute_expected_acceleration(ranked[:3], framework)
        
        return {
            "priority_investments": [o.to_dict() for o in ranked[:5]],
            "all_opportunities": [o.to_dict() for o in ranked],
            "timeline_groups": timeline_groups,
            "phases": phases,
            "expected_acceleration": expected_acceleration,
            "total_opportunities": len(ranked),
            "high_roi_count": len([o for o in ranked if o.roi_score > 0.3]),
        }
    
    def _adjust_for_framework(self, framework) -> List[InvestmentOpportunity]:
        """Adjust opportunity scores based on framework state."""
        adjusted = []
        
        for opp in self.opportunities:
            # Check which affected loops are in the framework
            active_loops = [
                loop for loop in opp.affected_loops
                if loop in framework.loops
            ]
            
            if not active_loops:
                continue
            
            # Adjust impact based on loop states
            loop_factor = 1.0
            for loop_name in active_loops:
                loop = framework.loops[loop_name]
                
                # Boost if loop is bottlenecked (more need for improvement)
                if loop.state.status.value == "bottlenecked":
                    loop_factor *= 1.2
                # Reduce if loop is already accelerating well
                elif loop.state.acceleration_rate > 1.3:
                    loop_factor *= 0.9
            
            # Create adjusted opportunity
            adjusted_impact = opp.impact_score * loop_factor * (len(active_loops) / len(opp.affected_loops))
            
            adjusted_opp = InvestmentOpportunity(
                name=opp.name,
                category=opp.category,
                description=opp.description,
                affected_loops=active_loops,
                impact_score=adjusted_impact,
                maturity=opp.maturity,
                effort=opp.effort,
                timeline=opp.timeline,
            )
            adjusted.append(adjusted_opp)
        
        return adjusted
    
    def _group_by_timeline(self, opportunities: List[InvestmentOpportunity]) -> Dict[str, List[str]]:
        """Group opportunities by timeline."""
        groups = {
            "short_term": [],   # < 1 year
            "medium_term": [],  # 1-2 years
            "long_term": [],    # > 2 years
        }
        
        for opp in opportunities:
            if "month" in opp.timeline or "6" in opp.timeline:
                groups["short_term"].append(opp.name)
            elif "1-2" in opp.timeline or "1 year" in opp.timeline:
                groups["medium_term"].append(opp.name)
            else:
                groups["long_term"].append(opp.name)
        
        return groups
    
    def _generate_phases(
        self, 
        opportunities: List[InvestmentOpportunity],
        framework
    ) -> List[Dict[str, Any]]:
        """Generate phased implementation plan."""
        phases = []
        
        # Phase 1: Quick wins (high ROI, low effort)
        quick_wins = [o for o in opportunities if o.effort < 1.0 and o.roi_score > 0.3]
        if quick_wins:
            phases.append({
                "phase": 1,
                "name": "Quick Wins",
                "timeline": "0-6 months",
                "investments": [o.name for o in quick_wins[:3]],
                "expected_impact": "Immediate acceleration in targeted loops",
            })
        
        # Phase 2: Core infrastructure
        core = [o for o in opportunities if o.category in [
            InvestmentCategory.SURROGATE_MODELS,
            InvestmentCategory.BENCHMARKS,
        ]]
        if core:
            phases.append({
                "phase": 2,
                "name": "Core Infrastructure",
                "timeline": "6-18 months",
                "investments": [o.name for o in core[:3]],
                "expected_impact": "Accelerate all loops through shared infrastructure",
            })
        
        # Phase 3: Advanced capabilities
        advanced = [o for o in opportunities if o.category in [
            InvestmentCategory.FOUNDATION_MODELS,
            InvestmentCategory.ABSTRACTIONS,
        ]]
        if advanced:
            phases.append({
                "phase": 3,
                "name": "Advanced Capabilities",
                "timeline": "18-36 months",
                "investments": [o.name for o in advanced[:2]],
                "expected_impact": "Transformative improvements enabling new paradigms",
            })
        
        return phases
    
    def _compute_expected_acceleration(
        self,
        top_investments: List[InvestmentOpportunity],
        framework
    ) -> Dict[str, float]:
        """Compute expected acceleration from top investments."""
        expected = {loop: 1.0 for loop in framework.loops}
        
        for opp in top_investments:
            for loop_name in opp.affected_loops:
                if loop_name in expected:
                    # Simple model: acceleration = 1 + impact × (1 - maturity)
                    boost = opp.impact_score * (1 - opp.maturity) * 0.3
                    expected[loop_name] *= (1 + boost)
        
        return expected
    
    def compare_strategies(
        self,
        framework,
        strategies: List[List[str]]
    ) -> List[Dict[str, Any]]:
        """
        Compare different investment strategies.
        
        Args:
            framework: RAF instance
            strategies: List of investment name lists
            
        Returns:
            Comparison of strategies
        """
        comparisons = []
        
        for i, strategy in enumerate(strategies):
            # Find matching opportunities
            selected = [
                o for o in self.opportunities
                if o.name in strategy
            ]
            
            if not selected:
                continue
            
            # Compute metrics
            total_impact = sum(o.impact_score for o in selected)
            total_effort = sum(o.effort for o in selected)
            avg_roi = np.mean([o.roi_score for o in selected])
            
            # Affected loops
            affected = set()
            for o in selected:
                affected.update(o.affected_loops)
            
            comparisons.append({
                "strategy_id": i + 1,
                "investments": strategy,
                "total_impact": total_impact,
                "total_effort": total_effort,
                "average_roi": avg_roi,
                "loop_coverage": len(affected & set(framework.loops.keys())),
                "efficiency": total_impact / total_effort if total_effort > 0 else 0,
            })
        
        return sorted(comparisons, key=lambda c: c["efficiency"], reverse=True)
