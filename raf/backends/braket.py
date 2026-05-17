"""
AWS Braket backend for multi-vendor quantum hardware access.

Provides access to:
    - IonQ (trapped ion)
    - Rigetti (superconducting)
    - OQC (superconducting)
    - QuEra (neutral atom)
    - AWS simulators (SV1, DM1, TN1)

Requires:
    pip install amazon-braket-sdk

Setup:
    1. AWS account with Braket access
    2. Configure AWS credentials: aws configure
    3. Or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env vars
"""

import time
from typing import Any

from .base import BackendType, ExecutionResult, QuantumBackend

# Device ARNs for common backends
BRAKET_DEVICES = {
    # Simulators (free tier available)
    "sv1": "arn:aws:braket:::device/quantum-simulator/amazon/sv1",
    "dm1": "arn:aws:braket:::device/quantum-simulator/amazon/dm1",
    "tn1": "arn:aws:braket:::device/quantum-simulator/amazon/tn1",
    # IonQ (trapped ion)
    "ionq_harmony": "arn:aws:braket:us-east-1::device/qpu/ionq/Harmony",
    "ionq_aria": "arn:aws:braket:us-east-1::device/qpu/ionq/Aria-1",
    "ionq_forte": "arn:aws:braket:us-east-1::device/qpu/ionq/Forte-1",
    # Rigetti (superconducting)
    "rigetti_aspen_m3": "arn:aws:braket:us-west-1::device/qpu/rigetti/Aspen-M-3",
    # IQM (superconducting)
    "iqm_garnet": "arn:aws:braket:eu-north-1::device/qpu/iqm/Garnet",
    # QuEra (neutral atom)
    "quera_aquila": "arn:aws:braket:us-east-1::device/qpu/quera/Aquila",
}


class BraketBackend(QuantumBackend):
    """
    AWS Braket backend for multi-vendor quantum hardware.

    Supports IonQ, Rigetti, IQM, QuEra, and AWS simulators.
    """

    def __init__(
        self,
        device_name: str = "sv1",
        s3_bucket: str | None = None,
        s3_prefix: str = "raf-results",
        region: str | None = None,
    ):
        """
        Initialize AWS Braket backend.

        Args:
            device_name: Device name (e.g., 'sv1', 'ionq_harmony', 'rigetti_aspen_m3')
            s3_bucket: S3 bucket for results (auto-created if None)
            s3_prefix: Prefix for S3 results
            region: AWS region (auto-detected if None)
        """
        backend_type = (
            BackendType.SIMULATOR
            if device_name in ["sv1", "dm1", "tn1"]
            else BackendType.REAL_HARDWARE
        )

        super().__init__(f"braket_{device_name}", backend_type)

        self.device_name = device_name
        self.device_arn = BRAKET_DEVICES.get(device_name, device_name)
        self.s3_bucket = s3_bucket
        self.s3_prefix = s3_prefix
        self.region = region

        self._device: Any = None
        self._s3_location: tuple[str, str] | None = None

    def _initialize(self) -> None:
        """Lazy initialization of Braket device."""
        if self._device is not None:
            return

        try:
            from braket.aws import AwsDevice, AwsSession
            from braket.devices import LocalSimulator
        except ImportError as err:
            raise ImportError(
                "amazon-braket-sdk required. Install with: pip install amazon-braket-sdk"
            ) from err

        # Set up S3 location for results
        if self.s3_bucket:
            self._s3_location = (self.s3_bucket, self.s3_prefix)
        else:
            # Use default Braket bucket
            session = AwsSession()
            self._s3_location = (
                f"amazon-braket-{session.region}-{session.account_id}",
                self.s3_prefix,
            )

        # Initialize device
        if self.device_name == "local":
            self._device = LocalSimulator()
        else:
            self._device = AwsDevice(self.device_arn)

    def _qiskit_to_braket(self, qiskit_circuit: Any) -> Any:
        """Convert Qiskit circuit to Braket circuit."""
        try:
            from qiskit_braket_provider import to_braket

            return to_braket(qiskit_circuit)
        except ImportError:
            # Manual conversion for basic gates
            from braket.circuits import Circuit as BraketCircuit

            braket_circuit = BraketCircuit()

            for instruction in qiskit_circuit.data:
                gate_name = instruction.operation.name
                qubits = [q._index for q in instruction.qubits]
                params = instruction.operation.params

                if gate_name == "h":
                    braket_circuit.h(qubits[0])
                elif gate_name == "x":
                    braket_circuit.x(qubits[0])
                elif gate_name == "y":
                    braket_circuit.y(qubits[0])
                elif gate_name == "z":
                    braket_circuit.z(qubits[0])
                elif gate_name == "cx":
                    braket_circuit.cnot(qubits[0], qubits[1])
                elif gate_name == "cz":
                    braket_circuit.cz(qubits[0], qubits[1])
                elif gate_name == "rx":
                    braket_circuit.rx(qubits[0], params[0])
                elif gate_name == "ry":
                    braket_circuit.ry(qubits[0], params[0])
                elif gate_name == "rz":
                    braket_circuit.rz(qubits[0], params[0])
                elif gate_name == "measure":
                    pass  # Handle measurements separately

            # Add measurements
            braket_circuit.measure(range(qiskit_circuit.num_qubits))

            return braket_circuit

    def execute(self, circuit: Any, shots: int = 1024, **_kwargs: Any) -> ExecutionResult:
        """Execute circuit on AWS Braket device."""
        self._initialize()

        start_time = time.time()

        # Convert Qiskit circuit to Braket if needed
        braket_circuit = self._qiskit_to_braket(circuit) if hasattr(circuit, "data") else circuit

        # Run on device
        assert self._device is not None
        task = self._device.run(
            braket_circuit,
            s3_destination_folder=self._s3_location,
            shots=shots,
        )
        result = task.result()

        execution_time_ms = (time.time() - start_time) * 1000

        # Convert counts format
        counts = dict(result.measurement_counts)

        self._record_execution(shots, execution_time_ms)

        return ExecutionResult(
            counts=counts,
            shots=shots,
            backend_name=self.name,
            backend_type=self.backend_type,
            execution_time_ms=execution_time_ms,
            metadata={
                "task_arn": task.id,
                "device": self.device_name,
            },
        )

    def execute_batch(
        self, circuits: list[Any], shots: int = 1024, **kwargs: Any
    ) -> list[ExecutionResult]:
        """Execute multiple circuits."""
        # Braket supports batch execution for some devices
        return [self.execute(circuit, shots=shots, **kwargs) for circuit in circuits]

    @classmethod
    def list_devices(cls) -> dict[str, str]:
        """List available Braket devices."""
        return BRAKET_DEVICES.copy()

    @classmethod
    def get_device_info(cls, device_name: str) -> dict[str, Any]:
        """Get information about a specific device."""
        try:
            from braket.aws import AwsDevice

            arn = BRAKET_DEVICES.get(device_name, device_name)
            device = AwsDevice(arn)

            return {
                "name": device.name,
                "provider": device.provider_name,
                "type": device.type.value,
                "status": device.status,
                "qubits": (
                    device.properties.paradigm.qubitCount
                    if hasattr(device.properties, "paradigm")
                    else None
                ),
            }
        except Exception as e:
            return {"error": str(e)}
