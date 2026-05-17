"""Tests for type definitions and aliases."""

from datetime import datetime

from raf.core.metrics import (
    AccelerationMetric,
    BottleneckIndicator,
    BottleneckSeverity,
    CrossLoopCoupling,
    MetricsAggregator,
    ProgressMetric,
)
from raf.types import BottleneckMap, ConfigDict, LoopMetrics


class TestTypeAliases:
    """Tests for type alias definitions."""

    def test_loop_metrics_type_usage(self) -> None:
        """Test that LoopMetrics alias works correctly."""
        metrics: LoopMetrics = {
            "loop1": AccelerationMetric(name="loop1_metric", value=1.5, baseline=1.0),
            "loop2": AccelerationMetric(name="loop2_metric", value=1.2, baseline=1.0),
        }

        assert len(metrics) == 2
        assert "loop1" in metrics
        assert isinstance(metrics["loop1"], AccelerationMetric)
        assert metrics["loop1"].acceleration_ratio == 1.5

    def test_bottleneck_map_type_usage(self) -> None:
        """Test that BottleneckMap alias works correctly."""
        bottlenecks: BottleneckMap = {
            "loop1": [
                BottleneckIndicator(
                    name="hardware_drift",
                    description="Hardware drift detected",
                    severity=BottleneckSeverity.HIGH,
                    loop_name="loop1",
                    constraint_type="hardware",
                )
            ],
            "loop2": [
                BottleneckIndicator(
                    name="evaluation_cost",
                    description="High evaluation cost",
                    severity=BottleneckSeverity.MEDIUM,
                    loop_name="loop2",
                    constraint_type="compute",
                )
            ],
        }

        assert len(bottlenecks) == 2
        assert "loop1" in bottlenecks
        assert isinstance(bottlenecks["loop1"], list)
        assert len(bottlenecks["loop1"]) == 1

    def test_config_dict_type_usage(self) -> None:
        """Test that ConfigDict TypedDict works correctly."""
        config: ConfigDict = {
            "example_key": "test_value",
        }

        assert config["example_key"] == "test_value"
        assert "example_key" in config


class TestAccelerationMetricEdgeCases:
    """Test edge cases for AccelerationMetric."""

    def test_acceleration_ratio_with_zero_baseline_positive_value(self) -> None:
        """Test acceleration_ratio when baseline=0 and value>0 returns inf."""
        metric = AccelerationMetric(name="test", value=1.5, baseline=0.0)
        assert metric.acceleration_ratio == float("inf")

    def test_acceleration_ratio_with_zero_baseline_zero_value(self) -> None:
        """Test acceleration_ratio when baseline=0 and value=0 returns 0."""
        metric = AccelerationMetric(name="test", value=0.0, baseline=0.0)
        assert metric.acceleration_ratio == 0.0

    def test_acceleration_metric_to_dict(self) -> None:
        """Test AccelerationMetric serialization to dict."""
        metric = AccelerationMetric(
            name="test_metric",
            value=2.5,
            baseline=1.0,
            iteration=5,
        )
        result = metric.to_dict()

        assert result["name"] == "test_metric"
        assert result["value"] == 2.5
        assert result["baseline"] == 1.0
        assert result["acceleration_ratio"] == 2.5
        assert result["iteration"] == 5
        assert "timestamp" in result


class TestCrossLoopCouplingEdgeCases:
    """Test edge cases for CrossLoopCoupling."""

    def test_cross_loop_coupling_invalid_strength_too_high(self) -> None:
        """Test that coupling_strength > 1 raises ValueError."""
        import pytest

        with pytest.raises(ValueError, match="coupling_strength must be in"):
            CrossLoopCoupling(
                source_loop="loop1",
                target_loop="loop2",
                coupling_strength=1.5,
                coupling_type="direct",
            )

    def test_cross_loop_coupling_invalid_strength_negative(self) -> None:
        """Test that coupling_strength < 0 raises ValueError."""
        import pytest

        with pytest.raises(ValueError, match="coupling_strength must be in"):
            CrossLoopCoupling(
                source_loop="loop1",
                target_loop="loop2",
                coupling_strength=-0.1,
                coupling_type="direct",
            )

    def test_cross_loop_coupling_to_dict(self) -> None:
        """Test CrossLoopCoupling serialization to dict."""
        coupling = CrossLoopCoupling(
            source_loop="error_mitigation",
            target_loop="ansatz_design",
            coupling_strength=0.7,
            coupling_type="amplifying",
            lag_iterations=2,
            description="EM improvements amplify AD progress",
        )
        result = coupling.to_dict()

        assert result["source_loop"] == "error_mitigation"
        assert result["target_loop"] == "ansatz_design"
        assert result["coupling_strength"] == 0.7
        assert result["is_strong"] is True
        assert result["lag_iterations"] == 2


class TestProgressMetricEdgeCases:
    """Test edge cases for ProgressMetric."""

    def test_progress_ratio_lower_direction_zero_target_zero_current(self) -> None:
        """Test progress_ratio when target_value=0, current=0, direction='lower'."""
        metric = ProgressMetric(
            domain="error_rate",
            current_value=0.0,
            target_value=0.0,
            direction="lower",
        )
        assert metric.progress_ratio == 1.0

    def test_progress_ratio_lower_direction_zero_target_positive_current(self) -> None:
        """Test progress_ratio when target_value=0, current>0, direction='lower'."""
        metric = ProgressMetric(
            domain="error_rate",
            current_value=0.5,
            target_value=0.0,
            direction="lower",
        )
        assert metric.progress_ratio == 0.0

    def test_progress_ratio_higher_direction_zero_target_positive_current(self) -> None:
        """Test progress_ratio when target_value=0, current>0, direction='higher'."""
        metric = ProgressMetric(
            domain="fidelity",
            current_value=0.5,
            target_value=0.0,
            direction="higher",
        )
        assert metric.progress_ratio == float("inf")

    def test_progress_ratio_higher_direction_zero_target_zero_current(self) -> None:
        """Test progress_ratio when target_value=0, current=0, direction='higher'."""
        metric = ProgressMetric(
            domain="fidelity",
            current_value=0.0,
            target_value=0.0,
            direction="higher",
        )
        assert metric.progress_ratio == 0.0

    def test_trend_with_insufficient_history(self) -> None:
        """Test trend property returns None with < 2 history points."""
        metric = ProgressMetric(
            domain="test",
            current_value=1.0,
            target_value=2.0,
        )
        metric.record(1.5, timestamp=datetime(2026, 1, 1))
        assert metric.trend is None

    def test_progress_metric_to_dict(self) -> None:
        """Test ProgressMetric serialization to dict."""
        metric = ProgressMetric(
            domain="circuit_depth",
            current_value=50.0,
            target_value=100.0,
            unit="gates",
            direction="lower",
        )
        result = metric.to_dict()

        assert result["domain"] == "circuit_depth"
        assert result["current_value"] == 50.0
        assert result["target_value"] == 100.0
        assert result["unit"] == "gates"
        assert "progress_ratio" in result
        assert "trend" in result
        assert "history_length" in result


class TestMetricsAggregator:
    """Test MetricsAggregator functionality."""

    def test_aggregator_add_progress_metric(self) -> None:
        """Test adding a progress metric to aggregator."""
        agg = MetricsAggregator()
        metric = ProgressMetric(
            domain="test_domain",
            current_value=1.0,
            target_value=2.0,
        )
        agg.add_progress_metric(metric)

        assert "test_domain" in agg.progress_metrics
        assert agg.progress_metrics["test_domain"] is metric
