"""
Tests for RAF acceleration loops.
"""

import pytest

from raf.core.loop import LoopLevel
from raf.core.metrics import BottleneckSeverity
from raf.loops import AnsatzDesignLoop, CalibrationControlLoop, ErrorMitigationLoop


class TestErrorMitigationLoop:
    """Tests for ErrorMitigationLoop."""

    def test_creation(self) -> None:
        loop = ErrorMitigationLoop()
        assert loop.name == "error_mitigation"
        assert loop.level == LoopLevel.APPLICATION

    def test_custom_initialization(self) -> None:
        loop = ErrorMitigationLoop(
            name="custom_em",
            initial_accuracy=0.7,
            initial_scale=50.0,
        )
        assert loop.name == "custom_em"
        assert loop.em_state.mitigation_accuracy == 0.7
        assert loop.em_state.experiment_scale == 50.0

    def test_stages(self) -> None:
        loop = ErrorMitigationLoop()
        assert len(loop.stages) == 5
        assert "ml_qem" in loop.stages
        assert "cleaner_outputs" in loop.stages

    def test_set_mitigation_accuracy(self) -> None:
        loop = ErrorMitigationLoop()
        loop.set_mitigation_accuracy(0.8)
        assert loop.em_state.mitigation_accuracy == 0.8

        # Test clamping
        loop.set_mitigation_accuracy(1.5)
        assert loop.em_state.mitigation_accuracy == 1.0

    def test_compute_acceleration(self) -> None:
        loop = ErrorMitigationLoop(initial_accuracy=0.5)

        # Record initial state
        loop.set_mitigation_accuracy(0.5)
        loop.set_experiment_scale(10.0)

        # Improve state
        loop.set_mitigation_accuracy(0.6)
        loop.set_experiment_scale(15.0)

        accel = loop.compute_acceleration()
        assert accel.value > 0

    def test_identify_bottlenecks(self) -> None:
        loop = ErrorMitigationLoop()
        loop.set_calibration_cost(5.0)  # High cost

        bottlenecks = loop.identify_bottlenecks()

        # Should identify high calibration cost
        cost_bottleneck = [b for b in bottlenecks if b.name == "high_calibration_cost"]
        assert len(cost_bottleneck) == 1
        assert cost_bottleneck[0].is_active

    def test_simulate_iteration(self) -> None:
        loop = ErrorMitigationLoop(initial_accuracy=0.5, initial_scale=10.0)

        initial_accuracy = loop.em_state.mitigation_accuracy
        initial_scale = loop.em_state.experiment_scale

        state = loop.simulate_iteration()

        assert loop.em_state.mitigation_accuracy > initial_accuracy
        assert loop.em_state.experiment_scale > initial_scale
        assert state.iteration == 1

    def test_get_recommendations(self) -> None:
        loop = ErrorMitigationLoop(initial_accuracy=0.4)
        recs = loop.get_recommendations()
        assert len(recs) > 0


class TestAnsatzDesignLoop:
    """Tests for AnsatzDesignLoop."""

    def test_creation(self) -> None:
        loop = AnsatzDesignLoop()
        assert loop.name == "ansatz_design"
        assert loop.level == LoopLevel.ALGORITHM

    def test_custom_initialization(self) -> None:
        loop = AnsatzDesignLoop(
            initial_quality=0.6,
            initial_surrogate_accuracy=0.5,
            search_strategy="reinforcement_learning",
        )
        assert loop.ad_state.circuit_quality == 0.6
        assert loop.ad_state.surrogate_accuracy == 0.5
        assert loop.search_strategy == "reinforcement_learning"

    def test_stages(self) -> None:
        loop = AnsatzDesignLoop()
        assert len(loop.stages) == 5
        assert "qas" in loop.stages
        assert "neural_surrogates" in loop.stages

    def test_set_surrogate_accuracy(self) -> None:
        loop = AnsatzDesignLoop()
        loop.set_surrogate_accuracy(0.7)
        assert loop.ad_state.surrogate_accuracy == 0.7

    def test_identify_bottlenecks_evaluation_cost(self) -> None:
        loop = AnsatzDesignLoop()
        loop.set_evaluation_cost(15.0)  # Very high (>10 triggers CRITICAL)

        bottlenecks = loop.identify_bottlenecks()

        cost_bottleneck = [b for b in bottlenecks if b.name == "high_evaluation_cost"]
        assert len(cost_bottleneck) == 1
        assert cost_bottleneck[0].severity == BottleneckSeverity.CRITICAL

    def test_identify_bottlenecks_surrogate(self) -> None:
        loop = AnsatzDesignLoop(initial_surrogate_accuracy=0.3)

        bottlenecks = loop.identify_bottlenecks()

        surrogate_bottleneck = [b for b in bottlenecks if b.name == "low_surrogate_accuracy"]
        assert len(surrogate_bottleneck) == 1

    def test_simulate_iteration(self) -> None:
        loop = AnsatzDesignLoop(initial_quality=0.4, initial_surrogate_accuracy=0.3)

        initial_quality = loop.ad_state.circuit_quality
        initial_surrogate = loop.ad_state.surrogate_accuracy

        loop.simulate_iteration()

        assert loop.ad_state.circuit_quality > initial_quality
        assert loop.ad_state.surrogate_accuracy > initial_surrogate


class TestCalibrationControlLoop:
    """Tests for CalibrationControlLoop."""

    def test_creation(self) -> None:
        loop = CalibrationControlLoop()
        assert loop.name == "calibration_control"
        assert loop.level == LoopLevel.HARDWARE

    def test_hardware_modality_defaults(self) -> None:
        sc_loop = CalibrationControlLoop(hardware_modality="superconducting")
        assert sc_loop.cc_state.coherence_time == 50.0

        ion_loop = CalibrationControlLoop(hardware_modality="trapped_ion")
        assert ion_loop.cc_state.coherence_time == 1000.0

    def test_stages(self) -> None:
        loop = CalibrationControlLoop()
        assert len(loop.stages) == 6
        assert "ml_noise_models" in loop.stages
        assert "optimized_control" in loop.stages

    def test_set_gate_fidelity(self) -> None:
        loop = CalibrationControlLoop()
        loop.set_gate_fidelity(0.998)
        assert loop.cc_state.gate_fidelity == 0.998

        # Test clamping
        loop.set_gate_fidelity(1.0)
        assert loop.cc_state.gate_fidelity == 0.9999

    def test_identify_bottlenecks_drift(self) -> None:
        loop = CalibrationControlLoop()
        loop.set_drift_rate(4.0)  # Very fast drift

        bottlenecks = loop.identify_bottlenecks()

        drift_bottleneck = [b for b in bottlenecks if b.name == "fast_drift"]
        assert len(drift_bottleneck) == 1
        assert drift_bottleneck[0].severity == BottleneckSeverity.CRITICAL

    def test_compute_effective_quantum_volume(self) -> None:
        loop = CalibrationControlLoop(initial_gate_fidelity=0.999)
        loop.set_max_circuit_depth(1000)

        qv = loop.compute_effective_quantum_volume()
        assert qv > 0

    def test_simulate_iteration(self) -> None:
        loop = CalibrationControlLoop(
            initial_model_accuracy=0.4,
            initial_gate_fidelity=0.99,
        )

        initial_model = loop.cc_state.noise_model_accuracy
        initial_fidelity = loop.cc_state.gate_fidelity

        loop.simulate_iteration()

        assert loop.cc_state.noise_model_accuracy > initial_model
        assert loop.cc_state.gate_fidelity > initial_fidelity


class TestLoopIntegration:
    """Integration tests for loops working together."""

    def test_all_loops_iterate(self) -> None:
        """Test that all loops can iterate without errors."""
        loops = [
            ErrorMitigationLoop(),
            AnsatzDesignLoop(),
            CalibrationControlLoop(),
        ]

        for loop in loops:
            for _ in range(5):
                state = loop.iterate()
                assert state.iteration > 0

    def test_all_loops_identify_bottlenecks(self) -> None:
        """Test that all loops can identify bottlenecks."""
        loops = [
            ErrorMitigationLoop(),
            AnsatzDesignLoop(),
            CalibrationControlLoop(),
        ]

        for loop in loops:
            bottlenecks = loop.identify_bottlenecks()
            # Should return a list (possibly empty)
            assert isinstance(bottlenecks, list)

    def test_all_loops_get_recommendations(self) -> None:
        """Test that all loops can generate recommendations."""
        loops = [
            ErrorMitigationLoop(),
            AnsatzDesignLoop(),
            CalibrationControlLoop(),
        ]

        for loop in loops:
            recs = loop.get_recommendations()
            assert isinstance(recs, list)
            assert len(recs) > 0

    def test_loop_summary(self) -> None:
        """Test that all loops can generate summaries."""
        loops = [
            ErrorMitigationLoop(),
            AnsatzDesignLoop(),
            CalibrationControlLoop(),
        ]

        for loop in loops:
            summary = loop.summary()
            assert "name" in summary
            assert "level" in summary
            assert "state" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
