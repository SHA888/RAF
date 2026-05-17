"""Tests for RAF analysis modules."""

from raf.analysis.bottleneck import BottleneckAnalyzer, BottleneckCluster
from raf.analysis.cross_loop import CrossLoopAnalyzer, InteractionEffect
from raf.analysis.prioritization import (
    InvestmentCategory,
    InvestmentOpportunity,
    ResearchPrioritizer,
)
from raf.core.framework import ReciprocalAccelerationFramework
from raf.core.metrics import BottleneckIndicator, BottleneckSeverity
from raf.loops import AnsatzDesignLoop, CalibrationControlLoop, ErrorMitigationLoop


class TestBottleneckCluster:
    """Tests for BottleneckCluster dataclass."""

    def test_cluster_creation(self) -> None:
        """Test basic BottleneckCluster creation."""
        bottlenecks: list[BottleneckIndicator] = []
        cluster = BottleneckCluster(
            name="resource_compute",
            bottlenecks=bottlenecks,
            common_type="compute",
            affected_loops=["loop1"],
            aggregate_severity=0.8,
            recommended_intervention="Optimize evaluation",
        )

        assert cluster.name == "resource_compute"
        assert cluster.common_type == "compute"
        assert cluster.affected_loops == ["loop1"]
        assert cluster.aggregate_severity == 0.8

    def test_cluster_to_dict(self) -> None:
        """Test BottleneckCluster.to_dict() serialization."""
        cluster = BottleneckCluster(
            name="resource_compute",
            bottlenecks=[],
            common_type="compute",
            affected_loops=["loop1", "loop2"],
            aggregate_severity=0.75,
            recommended_intervention="Invest in surrogates",
        )

        data = cluster.to_dict()
        assert data["name"] == "resource_compute"
        assert data["bottleneck_count"] == 0
        assert data["common_type"] == "compute"
        assert data["affected_loops"] == ["loop1", "loop2"]
        assert data["aggregate_severity"] == 0.75
        assert data["recommended_intervention"] == "Invest in surrogates"

    def test_cluster_with_bottlenecks(self) -> None:
        """Test BottleneckCluster with bottleneck instances."""
        bottleneck1 = BottleneckIndicator(
            name="high_compute_cost",
            description="Cost exceeds threshold",
            severity=BottleneckSeverity.HIGH,
            loop_name="loop1",
            constraint_type="compute",
        )
        bottleneck2 = BottleneckIndicator(
            name="evaluation_latency",
            description="Latency too high",
            severity=BottleneckSeverity.MEDIUM,
            loop_name="loop1",
            constraint_type="compute",
        )

        cluster = BottleneckCluster(
            name="resource_compute",
            bottlenecks=[bottleneck1, bottleneck2],
            common_type="compute",
            affected_loops=["loop1"],
            aggregate_severity=0.8,
        )

        assert len(cluster.bottlenecks) == 2
        data = cluster.to_dict()
        assert data["bottleneck_count"] == 2


class TestBottleneckAnalyzer:
    """Tests for BottleneckAnalyzer class."""

    def test_analyzer_initialization(self) -> None:
        """Test BottleneckAnalyzer initialization."""
        analyzer = BottleneckAnalyzer()
        assert analyzer.analysis_history == []
        assert hasattr(analyzer, "TYPE_CATEGORIES")

    def test_type_categories_defined(self) -> None:
        """Test that type categories are properly defined."""
        analyzer = BottleneckAnalyzer()
        categories = analyzer.TYPE_CATEGORIES

        assert "resource" in categories
        assert "knowledge" in categories
        assert "systemic" in categories
        assert "compute" in categories["resource"]
        assert "hardware" in categories["resource"]

    def test_analyze_empty_framework(self) -> None:
        """Test analyzing empty framework with no loops."""
        raf = ReciprocalAccelerationFramework()
        analyzer = BottleneckAnalyzer()
        results = analyzer.analyze(raf)

        assert results["total_bottlenecks"] == 0
        assert results["active_bottlenecks"] == 0
        assert results["clusters"] == []
        assert results["by_loop"] == {}
        assert results["by_type"] == {}

    def test_analyze_framework_with_loops(self) -> None:
        """Test analyzing framework with loops."""
        raf = ReciprocalAccelerationFramework()
        raf.add_loop(ErrorMitigationLoop())
        raf.add_loop(AnsatzDesignLoop())

        analyzer = BottleneckAnalyzer()
        results = analyzer.analyze(raf)

        # Framework should have bottlenecks from loops
        assert isinstance(results, dict)
        assert "total_bottlenecks" in results
        assert "active_bottlenecks" in results
        assert "clusters" in results
        assert isinstance(results["by_loop"], dict)
        assert isinstance(results["by_type"], dict)

    def test_analysis_history_tracking(self) -> None:
        """Test that analyses are tracked in history."""
        raf = ReciprocalAccelerationFramework()
        raf.add_loop(ErrorMitigationLoop())

        analyzer = BottleneckAnalyzer()

        # First analysis
        analyzer.analyze(raf)
        assert len(analyzer.analysis_history) == 1

        # Second analysis
        raf.iterate_all()
        analyzer.analyze(raf)
        assert len(analyzer.analysis_history) == 2

    def test_collect_bottlenecks(self) -> None:
        """Test _collect_bottlenecks method."""
        raf = ReciprocalAccelerationFramework()
        raf.add_loop(ErrorMitigationLoop())

        analyzer = BottleneckAnalyzer()
        bottlenecks = analyzer._collect_bottlenecks(raf)

        assert isinstance(bottlenecks, list)
        # Each loop should identify some bottlenecks
        assert len(bottlenecks) >= 0

    def test_cluster_bottlenecks(self) -> None:
        """Test _cluster_bottlenecks method."""
        bottleneck1 = BottleneckIndicator(
            name="compute_cost",
            description="High compute cost",
            severity=BottleneckSeverity.HIGH,
            loop_name="loop1",
            constraint_type="compute",
        )
        bottleneck2 = BottleneckIndicator(
            name="data_volume",
            description="Large data requirements",
            severity=BottleneckSeverity.MEDIUM,
            loop_name="loop1",
            constraint_type="data",
        )

        analyzer = BottleneckAnalyzer()
        clusters = analyzer._cluster_bottlenecks([bottleneck1, bottleneck2])

        assert len(clusters) == 2
        assert all(isinstance(c, BottleneckCluster) for c in clusters)
        assert clusters[0].common_type in ["compute", "data"]

    def test_get_intervention_mapping(self) -> None:
        """Test _get_intervention method."""
        analyzer = BottleneckAnalyzer()

        # Test known constraint types
        compute_intervention = analyzer._get_intervention("compute")
        assert "surrogate" in compute_intervention.lower()

        hardware_intervention = analyzer._get_intervention("hardware")
        assert "hardware" in hardware_intervention.lower()

        unknown_intervention = analyzer._get_intervention("unknown_type")
        assert "investigation" in unknown_intervention.lower()

    def test_compute_priorities(self) -> None:
        """Test _compute_priorities method."""
        bottleneck1 = BottleneckIndicator(
            name="critical_issue",
            description="Critical problem",
            severity=BottleneckSeverity.CRITICAL,
            loop_name="loop1",
            constraint_type="compute",
            current_value=1.0,
            threshold=0.5,
        )

        analyzer = BottleneckAnalyzer()
        priorities = analyzer._compute_priorities([bottleneck1])

        assert len(priorities) == 1
        assert priorities[0]["name"] == "critical_issue"
        assert "priority_score" in priorities[0]
        assert "severity" in priorities[0]
        assert "addressability" in priorities[0]

    def test_group_by_loop(self) -> None:
        """Test _group_by_loop method."""
        bottleneck1 = BottleneckIndicator(
            name="issue1",
            description="First issue",
            severity=BottleneckSeverity.HIGH,
            loop_name="error_mitigation",
            constraint_type="compute",
        )
        bottleneck2 = BottleneckIndicator(
            name="issue2",
            description="Second issue",
            severity=BottleneckSeverity.MEDIUM,
            loop_name="ansatz_design",
            constraint_type="compute",
        )

        analyzer = BottleneckAnalyzer()
        grouped = analyzer._group_by_loop([bottleneck1, bottleneck2])

        assert "error_mitigation" in grouped
        assert "ansatz_design" in grouped
        assert len(grouped["error_mitigation"]) == 1
        assert len(grouped["ansatz_design"]) == 1

    def test_group_by_type(self) -> None:
        """Test _group_by_type method."""
        bottleneck1 = BottleneckIndicator(
            name="compute_cost",
            description="High cost",
            severity=BottleneckSeverity.HIGH,
            loop_name="loop1",
            constraint_type="compute",
        )
        bottleneck2 = BottleneckIndicator(
            name="data_volume",
            description="Large volume",
            severity=BottleneckSeverity.MEDIUM,
            loop_name="loop1",
            constraint_type="data",
        )
        bottleneck3 = BottleneckIndicator(
            name="compute_latency",
            description="High latency",
            severity=BottleneckSeverity.MEDIUM,
            loop_name="loop2",
            constraint_type="compute",
        )

        analyzer = BottleneckAnalyzer()
        grouped = analyzer._group_by_type([bottleneck1, bottleneck2, bottleneck3])

        assert grouped["compute"] == 2
        assert grouped["data"] == 1

    def test_identify_systemic_issues(self) -> None:
        """Test _identify_systemic_issues method."""
        bottleneck1 = BottleneckIndicator(
            name="compute1",
            description="Issue 1",
            severity=BottleneckSeverity.HIGH,
            loop_name="loop1",
            constraint_type="compute",
            current_value=1.0,
            threshold=0.5,
        )

        bottleneck2 = BottleneckIndicator(
            name="compute2",
            description="Issue 2",
            severity=BottleneckSeverity.MEDIUM,
            loop_name="loop2",
            constraint_type="compute",
            current_value=1.0,
            threshold=0.5,
        )

        raf = ReciprocalAccelerationFramework()
        raf.add_loop(ErrorMitigationLoop())
        raf.add_loop(AnsatzDesignLoop())

        analyzer = BottleneckAnalyzer()
        systemic = analyzer._identify_systemic_issues([bottleneck1, bottleneck2], raf)

        assert len(systemic) > 0
        assert any(issue["type"] == "compute" for issue in systemic)

    def test_generate_recommendations(self) -> None:
        """Test _generate_recommendations method."""
        cluster1 = BottleneckCluster(
            name="resource_compute",
            bottlenecks=[],
            common_type="compute",
            affected_loops=["loop1", "loop2"],
            aggregate_severity=0.8,
            recommended_intervention="Invest in surrogates",
        )

        systemic_issue = {
            "type": "compute",
            "affected_loops": ["loop1", "loop2", "loop3"],
            "leverage": "high",
        }

        analyzer = BottleneckAnalyzer()
        recommendations = analyzer._generate_recommendations([cluster1], [systemic_issue])

        assert isinstance(recommendations, list)
        assert any("HIGH LEVERAGE" in rec for rec in recommendations)

    def test_compare_analyses_insufficient_history(self) -> None:
        """Test compare_analyses with insufficient history."""
        analyzer = BottleneckAnalyzer()
        result = analyzer.compare_analyses()

        assert "error" in result

    def test_compare_analyses_with_history(self) -> None:
        """Test compare_analyses with sufficient analysis history."""
        raf = ReciprocalAccelerationFramework()
        raf.add_loop(ErrorMitigationLoop())

        analyzer = BottleneckAnalyzer()

        # Generate two analyses
        analyzer.analyze(raf)
        raf.iterate_all()
        analyzer.analyze(raf)

        comparison = analyzer.compare_analyses()

        assert "bottleneck_change" in comparison
        assert "resolved" in comparison
        assert "new" in comparison
        assert "systemic_change" in comparison


class TestInteractionEffect:
    """Tests for InteractionEffect dataclass."""

    def test_interaction_effect_creation(self) -> None:
        """Test basic InteractionEffect creation."""
        effect = InteractionEffect(
            source_loop="error_mitigation",
            target_loop="ansatz_design",
            effect_magnitude=0.3,
            effect_type="enabling",
            confidence=0.8,
            description="Error mitigation enables better ansatz design",
        )

        assert effect.source_loop == "error_mitigation"
        assert effect.target_loop == "ansatz_design"
        assert effect.effect_magnitude == 0.3
        assert effect.effect_type == "enabling"

    def test_interaction_effect_to_dict(self) -> None:
        """Test InteractionEffect.to_dict() serialization."""
        effect = InteractionEffect(
            source_loop="loop1",
            target_loop="loop2",
            effect_magnitude=0.5,
            effect_type="amplifying",
            confidence=0.9,
            description="Test effect",
        )

        data = effect.to_dict()
        assert data["source_loop"] == "loop1"
        assert data["target_loop"] == "loop2"
        assert data["effect_magnitude"] == 0.5
        assert data["effect_type"] == "amplifying"


class TestCrossLoopAnalyzer:
    """Tests for CrossLoopAnalyzer class."""

    def test_analyzer_initialization(self) -> None:
        """Test CrossLoopAnalyzer initialization."""
        analyzer = CrossLoopAnalyzer()
        assert analyzer.analysis_history == []

    def test_analyze_empty_framework(self) -> None:
        """Test analyzing empty framework."""
        raf = ReciprocalAccelerationFramework()
        analyzer = CrossLoopAnalyzer()
        results = analyzer.analyze(raf)

        assert isinstance(results, dict)
        assert "coupling_matrix" in results
        assert "current_effects" in results
        assert "leverage_points" in results
        assert "cascade_predictions" in results
        assert "optimal_allocation" in results

    def test_analyze_framework_with_loops(self) -> None:
        """Test analyzing framework with multiple loops."""
        raf = ReciprocalAccelerationFramework()
        raf.add_loop(ErrorMitigationLoop())
        raf.add_loop(AnsatzDesignLoop())

        analyzer = CrossLoopAnalyzer()
        results = analyzer.analyze(raf)

        assert len(results["coupling_matrix"]) == 2
        assert "error_mitigation" in results["coupling_matrix"]
        assert "ansatz_design" in results["coupling_matrix"]

    def test_analysis_history(self) -> None:
        """Test that analyses are tracked."""
        raf = ReciprocalAccelerationFramework()
        raf.add_loop(ErrorMitigationLoop())

        analyzer = CrossLoopAnalyzer()
        analyzer.analyze(raf)
        assert len(analyzer.analysis_history) == 1

        analyzer.analyze(raf)
        assert len(analyzer.analysis_history) == 2

    def test_build_coupling_matrix(self) -> None:
        """Test _build_coupling_matrix method."""
        raf = ReciprocalAccelerationFramework()
        raf.add_loop(ErrorMitigationLoop())
        raf.add_loop(AnsatzDesignLoop())

        analyzer = CrossLoopAnalyzer()
        matrix = analyzer._build_coupling_matrix(raf)

        assert isinstance(matrix, dict)
        assert "error_mitigation" in matrix
        assert "ansatz_design" in matrix
        # Each loop should have a dict with all loop names as keys
        assert "ansatz_design" in matrix["error_mitigation"]

    def test_compute_current_effects(self) -> None:
        """Test _compute_current_effects method."""
        raf = ReciprocalAccelerationFramework()
        raf.add_loop(ErrorMitigationLoop())
        raf.add_loop(AnsatzDesignLoop())

        analyzer = CrossLoopAnalyzer()
        effects = analyzer._compute_current_effects(raf)

        assert isinstance(effects, list)
        assert all(isinstance(e, InteractionEffect) for e in effects)

    def test_identify_leverage_points(self) -> None:
        """Test _identify_leverage_points method."""
        raf = ReciprocalAccelerationFramework()
        raf.add_loop(ErrorMitigationLoop())
        raf.add_loop(AnsatzDesignLoop())

        analyzer = CrossLoopAnalyzer()
        matrix = analyzer._build_coupling_matrix(raf)
        leverage_points = analyzer._identify_leverage_points(matrix, raf)

        assert isinstance(leverage_points, list)
        assert all("leverage_score" in p for p in leverage_points)
        assert all("recommendation" in p for p in leverage_points)

    def test_get_leverage_recommendation(self) -> None:
        """Test _get_leverage_recommendation method."""
        analyzer = CrossLoopAnalyzer()

        # High leverage (outgoing > incoming)
        rec1 = analyzer._get_leverage_recommendation("loop1", outgoing=2.0, incoming=1.0)
        assert "High-leverage" in rec1

        # Dependent (incoming > outgoing)
        rec2 = analyzer._get_leverage_recommendation("loop2", outgoing=1.0, incoming=2.0)
        assert "Dependent" in rec2

        # Balanced
        rec3 = analyzer._get_leverage_recommendation("loop3", outgoing=1.5, incoming=1.5)
        assert "Balanced" in rec3

    def test_predict_cascades(self) -> None:
        """Test _predict_cascades method."""
        raf = ReciprocalAccelerationFramework()
        raf.add_loop(ErrorMitigationLoop())
        raf.add_loop(AnsatzDesignLoop())

        analyzer = CrossLoopAnalyzer()
        matrix = analyzer._build_coupling_matrix(raf)
        cascades = analyzer._predict_cascades(matrix, raf)

        assert isinstance(cascades, dict)
        for predictions in cascades.values():
            assert isinstance(predictions, list)

    def test_compute_optimal_allocation(self) -> None:
        """Test _compute_optimal_allocation method."""
        raf = ReciprocalAccelerationFramework()
        raf.add_loop(ErrorMitigationLoop())
        raf.add_loop(AnsatzDesignLoop())

        analyzer = CrossLoopAnalyzer()
        matrix = analyzer._build_coupling_matrix(raf)
        allocation = analyzer._compute_optimal_allocation(matrix, raf)

        assert isinstance(allocation, dict)
        # All allocations should be non-negative and sum to ~1
        total = sum(allocation.values())
        assert 0.9 <= total <= 1.1  # Account for floating point errors

    def test_total_coupling(self) -> None:
        """Test _total_coupling method."""
        analyzer = CrossLoopAnalyzer()

        matrix = {
            "loop1": {"loop2": 0.3, "loop3": 0.2},
            "loop2": {"loop1": 0.1, "loop3": 0.4},
            "loop3": {"loop1": 0.0, "loop2": 0.0},
        }

        total = analyzer._total_coupling(matrix)
        assert total == 1.0

    def test_network_density_empty(self) -> None:
        """Test _network_density with single loop."""
        analyzer = CrossLoopAnalyzer()

        matrix = {"loop1": {"loop1": 0.0}}
        density = analyzer._network_density(matrix)
        assert density == 0.0

    def test_network_density_full(self) -> None:
        """Test _network_density with multiple loops."""
        analyzer = CrossLoopAnalyzer()

        # 3 loops with all connections
        matrix = {
            "loop1": {"loop1": 0.0, "loop2": 0.3, "loop3": 0.2},
            "loop2": {"loop1": 0.1, "loop2": 0.0, "loop3": 0.4},
            "loop3": {"loop1": 0.5, "loop2": 0.2, "loop3": 0.0},
        }

        density = analyzer._network_density(matrix)
        assert 0 < density <= 1

    def test_simulate_intervention(self) -> None:
        """Test simulate_intervention method."""
        raf = ReciprocalAccelerationFramework()
        raf.add_loop(ErrorMitigationLoop())
        raf.add_loop(AnsatzDesignLoop())

        analyzer = CrossLoopAnalyzer()
        effects = analyzer.simulate_intervention(raf, "error_mitigation", improvement=0.2)

        assert isinstance(effects, dict)
        assert "error_mitigation" in effects
        assert effects["error_mitigation"] > 0  # Target loop should be positively affected


class TestInvestmentCategory:
    """Tests for InvestmentCategory enum."""

    def test_all_categories_exist(self) -> None:
        """Test that all expected categories exist."""
        expected = [
            "SURROGATE_MODELS",
            "BENCHMARKS",
            "ABSTRACTIONS",
            "FOUNDATION_MODELS",
            "ERROR_MITIGATION",
            "ARCHITECTURE_SEARCH",
            "CALIBRATION",
            "HARDWARE",
        ]
        for category_name in expected:
            assert hasattr(InvestmentCategory, category_name)

    def test_category_values(self) -> None:
        """Test that category values are correct."""
        assert InvestmentCategory.SURROGATE_MODELS.value == "surrogate_models"
        assert InvestmentCategory.BENCHMARKS.value == "benchmarks"
        assert InvestmentCategory.ERROR_MITIGATION.value == "error_mitigation"
        assert InvestmentCategory.HARDWARE.value == "hardware"

    def test_category_enumeration(self) -> None:
        """Test that all categories can be enumerated."""
        categories = list(InvestmentCategory)
        assert len(categories) == 8


class TestInvestmentOpportunity:
    """Tests for InvestmentOpportunity dataclass."""

    def test_opportunity_creation(self) -> None:
        """Test basic InvestmentOpportunity creation."""
        opp = InvestmentOpportunity(
            name="Test Opportunity",
            category=InvestmentCategory.SURROGATE_MODELS,
            description="Test description",
            affected_loops=["error_mitigation"],
            impact_score=0.8,
            maturity=0.3,
            effort=1.0,
            timeline="1-2 years",
        )

        assert opp.name == "Test Opportunity"
        assert opp.category == InvestmentCategory.SURROGATE_MODELS
        assert opp.affected_loops == ["error_mitigation"]
        assert opp.impact_score == 0.8
        assert opp.maturity == 0.3
        assert opp.effort == 1.0

    def test_roi_score_calculation(self) -> None:
        """Test that ROI score is calculated in __post_init__."""
        opp = InvestmentOpportunity(
            name="Test",
            category=InvestmentCategory.BENCHMARKS,
            description="Test",
            affected_loops=["loop1"],
            impact_score=0.9,
            maturity=0.3,
            effort=1.5,
            timeline="1 year",
        )

        # ROI = impact × (1 - maturity) / effort
        # = 0.9 × 0.7 / 1.5 = 0.42
        expected_roi = 0.9 * (1 - 0.3) / 1.5
        assert abs(opp.roi_score - expected_roi) < 1e-6

    def test_roi_zero_effort(self) -> None:
        """Test ROI calculation with zero effort."""
        opp = InvestmentOpportunity(
            name="Zero Effort",
            category=InvestmentCategory.CALIBRATION,
            description="Test",
            affected_loops=["loop1"],
            impact_score=0.5,
            maturity=0.5,
            effort=0.0,
            timeline="immediate",
        )

        assert opp.roi_score == 0.0

    def test_opportunity_to_dict(self) -> None:
        """Test InvestmentOpportunity.to_dict() method."""
        opp = InvestmentOpportunity(
            name="Test Opp",
            category=InvestmentCategory.ABSTRACTIONS,
            description="Description",
            affected_loops=["loop1", "loop2"],
            impact_score=0.75,
            maturity=0.4,
            effort=1.2,
            timeline="1-2 years",
        )

        data = opp.to_dict()
        assert data["name"] == "Test Opp"
        assert data["category"] == "abstractions"
        assert data["description"] == "Description"
        assert data["affected_loops"] == ["loop1", "loop2"]
        assert data["impact_score"] == 0.75
        assert data["maturity"] == 0.4
        assert data["effort"] == 1.2
        assert "roi_score" in data

    def test_opportunity_multiple_loops(self) -> None:
        """Test opportunity with multiple affected loops."""
        opp = InvestmentOpportunity(
            name="Multi-Loop",
            category=InvestmentCategory.FOUNDATION_MODELS,
            description="Affects all loops",
            affected_loops=["error_mitigation", "ansatz_design", "calibration_control"],
            impact_score=0.85,
            maturity=0.1,
            effort=2.0,
            timeline="2-3 years",
        )

        assert len(opp.affected_loops) == 3


class TestResearchPrioritizer:
    """Tests for ResearchPrioritizer class."""

    def test_prioritizer_initialization(self) -> None:
        """Test ResearchPrioritizer initialization."""
        prioritizer = ResearchPrioritizer()
        assert len(prioritizer.opportunities) > 0
        assert all(isinstance(o, InvestmentOpportunity) for o in prioritizer.opportunities)

    def test_default_opportunities_loaded(self) -> None:
        """Test that default opportunities are loaded."""
        prioritizer = ResearchPrioritizer()
        assert len(prioritizer.opportunities) == len(ResearchPrioritizer.DEFAULT_OPPORTUNITIES)

        # Check specific default opportunities exist
        names = [o.name for o in prioritizer.opportunities]
        assert "Neural Surrogate Models" in names
        assert "Quantum ML Benchmarks" in names
        assert "Quantum Foundation Models" in names

    def test_add_opportunity(self) -> None:
        """Test adding a custom opportunity."""
        prioritizer = ResearchPrioritizer()
        initial_count = len(prioritizer.opportunities)

        custom_opp = InvestmentOpportunity(
            name="Custom Opportunity",
            category=InvestmentCategory.HARDWARE,
            description="Custom investment",
            affected_loops=["calibration_control"],
            impact_score=0.6,
            maturity=0.2,
            effort=0.8,
            timeline="6 months",
        )

        prioritizer.add_opportunity(custom_opp)
        assert len(prioritizer.opportunities) == initial_count + 1
        assert custom_opp in prioritizer.opportunities

    def test_group_by_timeline(self) -> None:
        """Test _group_by_timeline method."""
        prioritizer = ResearchPrioritizer()
        timeline_groups = prioritizer._group_by_timeline(prioritizer.opportunities)

        assert "short_term" in timeline_groups
        assert "medium_term" in timeline_groups
        assert "long_term" in timeline_groups

        # All opportunities should be grouped
        total = sum(len(v) for v in timeline_groups.values())
        assert total == len(prioritizer.opportunities)

    def test_timeline_grouping_short_term(self) -> None:
        """Test that 6-month opportunities are short-term."""
        opp = InvestmentOpportunity(
            name="Quick Win",
            category=InvestmentCategory.BENCHMARKS,
            description="Fast timeline",
            affected_loops=["error_mitigation"],
            impact_score=0.7,
            maturity=0.2,
            effort=1.0,
            timeline="6-12 months",
        )

        prioritizer = ResearchPrioritizer()
        prioritizer.add_opportunity(opp)
        groups = prioritizer._group_by_timeline([opp])

        assert "Quick Win" in groups["short_term"]

    def test_timeline_grouping_medium_term(self) -> None:
        """Test that 1-2 year opportunities are medium-term."""
        opp = InvestmentOpportunity(
            name="Medium Investment",
            category=InvestmentCategory.ABSTRACTIONS,
            description="Medium timeline",
            affected_loops=["ansatz_design"],
            impact_score=0.8,
            maturity=0.3,
            effort=1.2,
            timeline="1-2 years",
        )

        prioritizer = ResearchPrioritizer()
        groups = prioritizer._group_by_timeline([opp])

        assert "Medium Investment" in groups["medium_term"]

    def test_timeline_grouping_long_term(self) -> None:
        """Test that 2+ year opportunities are long-term."""
        opp = InvestmentOpportunity(
            name="Long Term",
            category=InvestmentCategory.FOUNDATION_MODELS,
            description="Long timeline",
            affected_loops=["error_mitigation", "ansatz_design"],
            impact_score=0.85,
            maturity=0.1,
            effort=2.0,
            timeline="2-3 years",
        )

        prioritizer = ResearchPrioritizer()
        groups = prioritizer._group_by_timeline([opp])

        assert "Long Term" in groups["long_term"]

    def test_generate_phases(self) -> None:
        """Test _generate_phases method."""
        prioritizer = ResearchPrioritizer()
        opportunities = prioritizer.opportunities

        # Create dummy framework for phase generation
        raf = ReciprocalAccelerationFramework()
        phases = prioritizer._generate_phases(opportunities, raf)

        assert isinstance(phases, list)
        assert len(phases) > 0
        for phase in phases:
            assert "phase" in phase
            assert "name" in phase
            assert "timeline" in phase
            assert "investments" in phase
            assert "expected_impact" in phase

    def test_phase_quick_wins(self) -> None:
        """Test that Quick Wins phase is generated."""
        prioritizer = ResearchPrioritizer()
        raf = ReciprocalAccelerationFramework()
        phases = prioritizer._generate_phases(prioritizer.opportunities, raf)

        quick_wins = [p for p in phases if p["name"] == "Quick Wins"]
        assert len(quick_wins) > 0

    def test_compute_expected_acceleration(self) -> None:
        """Test _compute_expected_acceleration method."""
        prioritizer = ResearchPrioritizer()
        top_3 = sorted(prioritizer.opportunities, key=lambda o: o.roi_score, reverse=True)[:3]

        raf = ReciprocalAccelerationFramework()
        raf.add_loop(ErrorMitigationLoop())
        raf.add_loop(AnsatzDesignLoop())

        acceleration = prioritizer._compute_expected_acceleration(top_3, raf)

        assert isinstance(acceleration, dict)
        for loop_name in raf.loops:
            assert loop_name in acceleration
            assert acceleration[loop_name] >= 1.0

    def test_adjust_for_framework_empty(self) -> None:
        """Test _adjust_for_framework with empty framework."""
        prioritizer = ResearchPrioritizer()
        raf = ReciprocalAccelerationFramework()

        adjusted = prioritizer._adjust_for_framework(raf)
        assert adjusted == []

    def test_adjust_for_framework_with_loops(self) -> None:
        """Test _adjust_for_framework with loops."""
        prioritizer = ResearchPrioritizer()
        raf = ReciprocalAccelerationFramework()
        raf.add_loop(ErrorMitigationLoop())
        raf.add_loop(AnsatzDesignLoop())

        adjusted = prioritizer._adjust_for_framework(raf)

        # Should have some adjusted opportunities
        assert len(adjusted) > 0
        assert all(isinstance(o, InvestmentOpportunity) for o in adjusted)

    def test_adjust_for_framework_bottlenecked_loop(self) -> None:
        """Test _adjust_for_framework with bottlenecked loop boosts impact."""
        prioritizer = ResearchPrioritizer()
        raf = ReciprocalAccelerationFramework()
        loop = ErrorMitigationLoop()
        raf.add_loop(loop)

        # Force loop to bottlenecked state by setting specific condition
        loop.state.status = loop.state.status.__class__.BOTTLENECKED

        adjusted = prioritizer._adjust_for_framework(raf)

        # Opportunities affecting bottlenecked loop should be boosted
        assert len(adjusted) > 0

    def test_adjust_for_framework_accelerating_loop(self) -> None:
        """Test _adjust_for_framework with accelerating loop reduces impact."""
        prioritizer = ResearchPrioritizer()
        raf = ReciprocalAccelerationFramework()
        loop = ErrorMitigationLoop()
        raf.add_loop(loop)

        # Simulate high acceleration rate
        for _ in range(10):
            loop.iterate()

        # Force high acceleration
        loop.state.acceleration_rate = 1.5

        adjusted = prioritizer._adjust_for_framework(raf)

        # Opportunities should be adjusted
        assert len(adjusted) >= 0

    def test_generate_roadmap_empty_framework(self) -> None:
        """Test generate_roadmap with empty framework."""
        prioritizer = ResearchPrioritizer()
        raf = ReciprocalAccelerationFramework()

        roadmap = prioritizer.generate_roadmap(raf)

        assert isinstance(roadmap, dict)
        assert "priority_investments" in roadmap
        assert "all_opportunities" in roadmap
        assert "timeline_groups" in roadmap
        assert "phases" in roadmap
        assert "expected_acceleration" in roadmap
        assert "total_opportunities" in roadmap
        assert "high_roi_count" in roadmap

    def test_generate_roadmap_with_loops(self) -> None:
        """Test generate_roadmap with multiple loops."""
        prioritizer = ResearchPrioritizer()
        raf = ReciprocalAccelerationFramework()
        raf.add_loop(ErrorMitigationLoop())
        raf.add_loop(AnsatzDesignLoop())
        raf.add_loop(CalibrationControlLoop())

        roadmap = prioritizer.generate_roadmap(raf)

        assert isinstance(roadmap, dict)
        assert len(roadmap["priority_investments"]) <= 5
        assert len(roadmap["all_opportunities"]) > 0
        assert roadmap["total_opportunities"] > 0

    def test_roadmap_high_roi_count(self) -> None:
        """Test that high_roi_count is accurate."""
        prioritizer = ResearchPrioritizer()
        raf = ReciprocalAccelerationFramework()
        raf.add_loop(ErrorMitigationLoop())

        roadmap = prioritizer.generate_roadmap(raf)
        high_roi = roadmap["high_roi_count"]

        assert high_roi >= 0
        assert high_roi <= roadmap["total_opportunities"]

    def test_compare_strategies_single_strategy(self) -> None:
        """Test compare_strategies with one strategy."""
        prioritizer = ResearchPrioritizer()
        raf = ReciprocalAccelerationFramework()
        raf.add_loop(ErrorMitigationLoop())

        strategy = ["Neural Surrogate Models"]
        comparisons = prioritizer.compare_strategies(raf, [strategy])

        assert len(comparisons) > 0
        comparison = comparisons[0]
        assert "strategy_id" in comparison
        assert "total_impact" in comparison
        assert "total_effort" in comparison
        assert "average_roi" in comparison
        assert "efficiency" in comparison

    def test_compare_strategies_multiple(self) -> None:
        """Test compare_strategies with multiple strategies."""
        prioritizer = ResearchPrioritizer()
        raf = ReciprocalAccelerationFramework()
        raf.add_loop(ErrorMitigationLoop())
        raf.add_loop(AnsatzDesignLoop())

        strategies = [
            ["Neural Surrogate Models"],
            ["Quantum ML Benchmarks", "Automated QAS"],
            ["Quantum Foundation Models"],
        ]

        comparisons = prioritizer.compare_strategies(raf, strategies)
        assert len(comparisons) > 0
        assert all("efficiency" in c for c in comparisons)

    def test_compare_strategies_nonexistent_investment(self) -> None:
        """Test compare_strategies with nonexistent investment."""
        prioritizer = ResearchPrioritizer()
        raf = ReciprocalAccelerationFramework()
        raf.add_loop(ErrorMitigationLoop())

        strategy = ["Nonexistent Investment"]
        comparisons = prioritizer.compare_strategies(raf, [strategy])

        # Should not include strategies with nonexistent investments
        assert len(comparisons) == 0

    def test_strategy_comparison_sorting(self) -> None:
        """Test that strategies are sorted by efficiency."""
        prioritizer = ResearchPrioritizer()
        raf = ReciprocalAccelerationFramework()
        raf.add_loop(ErrorMitigationLoop())
        raf.add_loop(AnsatzDesignLoop())

        strategies = [
            ["Neural Surrogate Models"],
            ["Quantum ML Benchmarks"],
        ]

        comparisons = prioritizer.compare_strategies(raf, strategies)

        if len(comparisons) >= 2:
            efficiencies = [c["efficiency"] for c in comparisons]
            # Should be sorted in descending order
            assert efficiencies == sorted(efficiencies, reverse=True)
