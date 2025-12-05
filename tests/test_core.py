"""
Tests for RAF core components.
"""

import pytest
from datetime import datetime

from raf.core.framework import ReciprocalAccelerationFramework
from raf.core.loop import AccelerationLoop, LoopLevel, LoopState, LoopStatus
from raf.core.metrics import (
    AccelerationMetric,
    BottleneckIndicator,
    BottleneckSeverity,
    CrossLoopCoupling,
    ProgressMetric,
    MetricsAggregator,
)


class TestAccelerationMetric:
    """Tests for AccelerationMetric."""
    
    def test_creation(self):
        metric = AccelerationMetric(
            name="test_metric",
            value=1.5,
            baseline=1.0,
        )
        assert metric.name == "test_metric"
        assert metric.value == 1.5
        assert metric.baseline == 1.0
    
    def test_acceleration_ratio(self):
        metric = AccelerationMetric(name="test", value=1.5, baseline=1.0)
        assert metric.acceleration_ratio == 1.5
        
        metric2 = AccelerationMetric(name="test", value=0.8, baseline=1.0)
        assert metric2.acceleration_ratio == 0.8
    
    def test_is_accelerating(self):
        accelerating = AccelerationMetric(name="test", value=1.2, baseline=1.0)
        assert accelerating.is_accelerating is True
        
        decelerating = AccelerationMetric(name="test", value=0.9, baseline=1.0)
        assert decelerating.is_accelerating is False
    
    def test_to_dict(self):
        metric = AccelerationMetric(name="test", value=1.5, baseline=1.0)
        d = metric.to_dict()
        assert d["name"] == "test"
        assert d["value"] == 1.5
        assert d["acceleration_ratio"] == 1.5
        assert d["is_accelerating"] is True


class TestBottleneckIndicator:
    """Tests for BottleneckIndicator."""
    
    def test_creation(self):
        bottleneck = BottleneckIndicator(
            name="test_bottleneck",
            description="A test bottleneck",
            severity=BottleneckSeverity.HIGH,
            loop_name="test_loop",
            constraint_type="compute",
            current_value=3.0,
            threshold=2.0,
        )
        assert bottleneck.name == "test_bottleneck"
        assert bottleneck.severity == BottleneckSeverity.HIGH
    
    def test_is_active(self):
        active = BottleneckIndicator(
            name="active",
            description="",
            severity=BottleneckSeverity.HIGH,
            loop_name="test",
            constraint_type="compute",
            current_value=3.0,
            threshold=2.0,
        )
        assert active.is_active is True
        
        inactive = BottleneckIndicator(
            name="inactive",
            description="",
            severity=BottleneckSeverity.LOW,
            loop_name="test",
            constraint_type="compute",
            current_value=1.0,
            threshold=2.0,
        )
        assert inactive.is_active is False
    
    def test_severity_score(self):
        low = BottleneckIndicator(
            name="low", description="", severity=BottleneckSeverity.LOW,
            loop_name="test", constraint_type="compute"
        )
        assert low.severity_score == 0.25
        
        critical = BottleneckIndicator(
            name="critical", description="", severity=BottleneckSeverity.CRITICAL,
            loop_name="test", constraint_type="compute"
        )
        assert critical.severity_score == 1.0
    
    def test_priority_score(self):
        bottleneck = BottleneckIndicator(
            name="test",
            description="",
            severity=BottleneckSeverity.HIGH,
            loop_name="test",
            constraint_type="compute",
            addressability_score=0.8,
        )
        # priority = severity_score * addressability = 0.75 * 0.8 = 0.6
        assert bottleneck.priority_score == pytest.approx(0.6)


class TestCrossLoopCoupling:
    """Tests for CrossLoopCoupling."""
    
    def test_creation(self):
        coupling = CrossLoopCoupling(
            source_loop="loop_a",
            target_loop="loop_b",
            coupling_strength=0.7,
            coupling_type="direct",
        )
        assert coupling.source_loop == "loop_a"
        assert coupling.target_loop == "loop_b"
        assert coupling.coupling_strength == 0.7
    
    def test_invalid_strength(self):
        with pytest.raises(ValueError):
            CrossLoopCoupling(
                source_loop="a",
                target_loop="b",
                coupling_strength=1.5,  # Invalid: > 1
                coupling_type="direct",
            )
    
    def test_is_strong(self):
        strong = CrossLoopCoupling(
            source_loop="a", target_loop="b",
            coupling_strength=0.7, coupling_type="direct"
        )
        assert strong.is_strong is True
        
        weak = CrossLoopCoupling(
            source_loop="a", target_loop="b",
            coupling_strength=0.3, coupling_type="direct"
        )
        assert weak.is_strong is False


class TestProgressMetric:
    """Tests for ProgressMetric."""
    
    def test_progress_ratio_higher_better(self):
        metric = ProgressMetric(
            domain="accuracy",
            current_value=0.8,
            target_value=1.0,
            direction="higher",
        )
        assert metric.progress_ratio == 0.8
    
    def test_progress_ratio_lower_better(self):
        metric = ProgressMetric(
            domain="error_rate",
            current_value=0.02,
            target_value=0.01,
            direction="lower",
        )
        # progress = 1 - (current / target) = 1 - 2 = -1
        assert metric.progress_ratio == -1.0
    
    def test_record(self):
        metric = ProgressMetric(
            domain="test",
            current_value=0.5,
            target_value=1.0,
            direction="higher",
        )
        metric.record(0.6)
        assert metric.current_value == 0.6
        assert len(metric.history) == 1


class TestLoopState:
    """Tests for LoopState."""
    
    def test_creation(self):
        state = LoopState()
        assert state.iteration == 0
        assert state.status == LoopStatus.INACTIVE
        assert state.acceleration_rate == 1.0
    
    def test_update(self):
        state = LoopState()
        state.update(iteration=5, acceleration_rate=1.3)
        assert state.iteration == 5
        assert state.acceleration_rate == 1.3
    
    def test_to_dict(self):
        state = LoopState(iteration=3, status=LoopStatus.ACTIVE)
        d = state.to_dict()
        assert d["iteration"] == 3
        assert d["status"] == "active"


class TestReciprocalAccelerationFramework:
    """Tests for the main framework."""
    
    def test_creation(self):
        raf = ReciprocalAccelerationFramework(name="TestRAF")
        assert raf.name == "TestRAF"
        assert len(raf.loops) == 0
    
    def test_default_couplings(self):
        raf = ReciprocalAccelerationFramework()
        assert len(raf.couplings) > 0
    
    def test_add_custom_coupling(self):
        raf = ReciprocalAccelerationFramework()
        initial_count = len(raf.couplings)
        
        coupling = CrossLoopCoupling(
            source_loop="custom_a",
            target_loop="custom_b",
            coupling_strength=0.5,
            coupling_type="custom",
        )
        raf.add_coupling(coupling)
        
        assert len(raf.couplings) == initial_count + 1
    
    def test_coupling_matrix(self):
        raf = ReciprocalAccelerationFramework()
        # Add mock loops
        from raf.loops import ErrorMitigationLoop
        raf.add_loop(ErrorMitigationLoop())
        
        matrix = raf.get_loop_coupling_matrix()
        assert "error_mitigation" in matrix
    
    def test_summary(self):
        raf = ReciprocalAccelerationFramework(name="TestRAF")
        summary = raf.summary()
        assert summary["name"] == "TestRAF"
        assert "loops" in summary


class TestMetricsAggregator:
    """Tests for MetricsAggregator."""
    
    def test_add_acceleration_metric(self):
        agg = MetricsAggregator()
        metric = AccelerationMetric(name="test", value=1.2, baseline=1.0)
        agg.add_acceleration_metric(metric)
        assert "test" in agg.acceleration_metrics
    
    def test_add_bottleneck(self):
        agg = MetricsAggregator()
        bottleneck = BottleneckIndicator(
            name="test", description="", severity=BottleneckSeverity.HIGH,
            loop_name="loop1", constraint_type="compute"
        )
        agg.add_bottleneck(bottleneck)
        assert "loop1" in agg.bottlenecks
    
    def test_get_active_bottlenecks(self):
        agg = MetricsAggregator()
        
        active = BottleneckIndicator(
            name="active", description="", severity=BottleneckSeverity.HIGH,
            loop_name="loop1", constraint_type="compute",
            current_value=3.0, threshold=2.0
        )
        inactive = BottleneckIndicator(
            name="inactive", description="", severity=BottleneckSeverity.LOW,
            loop_name="loop1", constraint_type="data",
            current_value=1.0, threshold=2.0
        )
        
        agg.add_bottleneck(active)
        agg.add_bottleneck(inactive)
        
        active_list = agg.get_active_bottlenecks()
        assert len(active_list) == 1
        assert active_list[0].name == "active"
    
    def test_compute_overall_acceleration(self):
        agg = MetricsAggregator()
        
        agg.add_acceleration_metric(AccelerationMetric(name="a", value=1.2, baseline=1.0))
        agg.add_acceleration_metric(AccelerationMetric(name="b", value=1.4, baseline=1.0))
        
        overall = agg.compute_overall_acceleration()
        assert overall == pytest.approx(1.3, rel=0.01)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
