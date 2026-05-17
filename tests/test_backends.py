"""
Tests for RAF quantum backends.
"""

import pytest


class TestDeviceNoiseProfile:
    """Tests for DeviceNoiseProfile."""

    def test_ibm_manila_like(self) -> None:
        from raf.backends import DeviceNoiseProfile

        profile = DeviceNoiseProfile.ibm_manila_like()

        assert profile.name == "ibm_manila_like"
        assert profile.num_qubits == 5
        assert profile.t1_us == 100.0
        assert profile.t2_us == 80.0
        assert profile.single_qubit_error == 3e-4
        assert profile.two_qubit_error == 1e-2
        assert profile.readout_error == 2e-2

    def test_ionq_harmony_like(self) -> None:
        from raf.backends import DeviceNoiseProfile

        profile = DeviceNoiseProfile.ionq_harmony_like()

        assert profile.name == "ionq_harmony_like"
        assert profile.num_qubits == 11
        assert profile.t1_us == 10000.0  # Much longer coherence
        assert profile.single_qubit_error < profile.two_qubit_error

    def test_to_dict(self) -> None:
        from raf.backends import DeviceNoiseProfile

        profile = DeviceNoiseProfile.ibm_manila_like()
        d = profile.to_dict()

        assert "name" in d
        assert "num_qubits" in d
        assert "t1_us" in d
        assert d["device_type"] == "superconducting"


class TestNoiseModelBuilder:
    """Tests for NoiseModelBuilder."""

    @pytest.mark.skipif(  # type: ignore[misc]
        not pytest.importorskip("qiskit_aer", reason="qiskit-aer not installed"),
        reason="qiskit-aer not installed",
    )
    def test_build_noise_model(self) -> None:
        from raf.backends import DeviceNoiseProfile, NoiseModelBuilder

        profile = DeviceNoiseProfile.ibm_manila_like()
        builder = NoiseModelBuilder(profile)

        noise_model = builder.build()

        assert noise_model is not None
        # Check that noise model has quantum errors
        assert len(noise_model.noise_instructions) > 0

    @pytest.mark.skipif(  # type: ignore[misc]
        not pytest.importorskip("qiskit_aer", reason="qiskit-aer not installed"),
        reason="qiskit-aer not installed",
    )
    def test_build_with_drift(self) -> None:
        from raf.backends import DeviceNoiseProfile, NoiseModelBuilder

        profile = DeviceNoiseProfile.ibm_manila_like()
        builder = NoiseModelBuilder(profile)

        # Build with drift
        drifted_model = builder.build_with_drift(drift_factor=1.0, time_elapsed_hours=12.0)

        assert drifted_model is not None


class TestEstimateFidelity:
    """Tests for fidelity estimation."""

    def test_estimate_circuit_fidelity(self) -> None:
        from raf.backends import DeviceNoiseProfile
        from raf.backends.noise_models import estimate_circuit_fidelity

        profile = DeviceNoiseProfile.ibm_manila_like()

        # Shallow circuit should have high fidelity
        fidelity_shallow = estimate_circuit_fidelity(
            circuit_depth=5, num_two_qubit_gates=2, profile=profile
        )

        # Deep circuit should have lower fidelity
        fidelity_deep = estimate_circuit_fidelity(
            circuit_depth=50, num_two_qubit_gates=20, profile=profile
        )

        assert 0 < fidelity_shallow <= 1
        assert 0 < fidelity_deep <= 1
        assert fidelity_shallow > fidelity_deep


@pytest.mark.skipif(
    not pytest.importorskip("qiskit_aer", reason="qiskit-aer not installed"),
    reason="qiskit-aer not installed",
)
class TestAerBackend:
    """Tests for AerBackend."""

    def test_create_ideal_backend(self) -> None:
        from raf.backends import create_backend

        backend = create_backend("ideal")

        assert backend.name == "aer_simulator"
        assert backend.noise_profile is None

    def test_create_noisy_backend(self) -> None:
        from raf.backends import create_backend

        backend = create_backend("manila")

        assert "noisy" in backend.name
        assert backend.noise_profile is not None

    def test_execute_circuit(self) -> None:
        from qiskit import QuantumCircuit

        from raf.backends import create_backend

        backend = create_backend("ideal")

        # Create simple circuit
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure_all()

        result = backend.execute(qc, shots=100)

        assert result.shots == 100
        assert len(result.counts) > 0
        assert sum(result.counts.values()) == 100

    def test_execute_noisy_circuit(self) -> None:
        from qiskit import QuantumCircuit

        from raf.backends import create_backend

        backend = create_backend("manila")

        # Create simple circuit
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure_all()

        result = backend.execute(qc, shots=100)

        assert result.shots == 100
        assert result.error_rate_estimate is not None

    def test_backend_statistics(self) -> None:
        from qiskit import QuantumCircuit

        from raf.backends import create_backend

        backend = create_backend("ideal")
        backend.reset_statistics()

        qc = QuantumCircuit(1)
        qc.h(0)
        qc.measure_all()

        backend.execute(qc, shots=100)
        backend.execute(qc, shots=200)

        stats = backend.statistics

        assert stats["executions"] == 2
        assert stats["total_shots"] == 300


class TestExecutionResult:
    """Tests for ExecutionResult."""

    def test_probabilities(self) -> None:
        from raf.backends.base import BackendType, ExecutionResult

        result = ExecutionResult(
            counts={"00": 60, "11": 40},
            shots=100,
            backend_name="test",
            backend_type=BackendType.SIMULATOR,
            execution_time_ms=10.0,
        )

        probs = result.probabilities

        assert probs["00"] == pytest.approx(0.6)
        assert probs["11"] == pytest.approx(0.4)


class TestCircuitMetrics:
    """Tests for CircuitMetrics."""

    @pytest.mark.skipif(  # type: ignore[misc]
        not pytest.importorskip("qiskit", reason="qiskit not installed"),
        reason="qiskit not installed",
    )
    def test_from_qiskit_circuit(self) -> None:
        from qiskit import QuantumCircuit

        from raf.backends.base import CircuitMetrics

        qc = QuantumCircuit(3)
        qc.h(0)
        qc.h(1)
        qc.cx(0, 1)
        qc.cx(1, 2)
        qc.rz(0.5, 0)

        metrics = CircuitMetrics.from_qiskit_circuit(qc)

        assert metrics.num_qubits == 3
        assert metrics.two_qubit_gate_count == 2
        assert metrics.total_gates == 5
        assert "h" in metrics.gate_counts
        assert "cx" in metrics.gate_counts
