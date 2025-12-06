# RAF Quantum Backends

RAF provides a unified interface for multiple quantum hardware vendors and simulators, enabling seamless switching between development (simulation) and production (real hardware) environments.

## Overview

| Backend | Provider | Type | Install Command |
|---------|----------|------|-----------------|
| `AerBackend` | Qiskit Aer | Simulator | `pip install raf[quantum]` |
| `IBMQuantumBackend` | IBM Quantum | Hardware | `pip install raf[ibm]` |
| `BraketBackend` | AWS Braket | Hardware/Simulator | `pip install raf[braket]` |
| `AzureQuantumBackend` | Azure Quantum | Hardware/Simulator | `pip install raf[azure]` |
| `IQMBackend` | IQM | Hardware | `pip install raf[iqm]` |

Install all backends: `pip install raf[all-backends]`

## Quick Start

```python
from raf.backends import list_available_backends, create_backend

# Check available backends
print(list_available_backends())

# Create a noisy simulator (always available)
backend = create_backend("manila")

# Execute a circuit
from qiskit import QuantumCircuit
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

result = backend.execute(qc, shots=1024)
print(result.counts)
```

---

## AerBackend (Local Simulation)

Qiskit Aer provides high-performance local simulation with optional realistic noise models.

### Installation

```bash
pip install raf[quantum]
```

### Usage

```python
from raf.backends import AerBackend, create_backend, DeviceNoiseProfile

# Ideal simulation (no noise)
backend = create_backend("ideal")

# Noisy simulation with device-calibrated noise
backend = create_backend("manila")      # IBM Manila-like
backend = create_backend("kolkata")     # IBM Kolkata-like
backend = create_backend("ionq")        # IonQ Harmony-like
backend = create_backend("sycamore")    # Google Sycamore-like

# Custom noise profile
profile = DeviceNoiseProfile(
    name="custom",
    device_type=DeviceType.SUPERCONDUCTING,
    num_qubits=10,
    t1_us=80.0,
    t2_us=60.0,
    single_qubit_error=5e-4,
    two_qubit_error=1.5e-2,
    readout_error=2e-2,
)
backend = AerBackend(noise_profile=profile)
```

### Available Noise Profiles

| Profile | Type | Qubits | T1 (μs) | T2 (μs) | 2Q Error |
|---------|------|--------|---------|---------|----------|
| `manila` | Superconducting | 5 | 100 | 80 | 1.0% |
| `kolkata` | Superconducting | 27 | 120 | 100 | 0.8% |
| `ionq` | Trapped Ion | 11 | 10,000 | 1,000 | 0.5% |
| `sycamore` | Superconducting | 53 | 15 | 20 | 0.6% |

---

## IBMQuantumBackend

Access IBM Quantum hardware through the IBM Quantum Platform.

### Installation

```bash
pip install raf[ibm]
```

### Setup

1. Create account at [quantum.ibm.com](https://quantum.ibm.com)
2. Get API token from account settings
3. Set environment variable:
   ```bash
   export IBM_QUANTUM_TOKEN=your_token_here
   ```

### Usage

```python
from raf.backends import IBMQuantumBackend

# Connect to IBM Quantum
backend = IBMQuantumBackend(
    backend_name="ibm_brisbane",
    token="your_token",  # Or use IBM_QUANTUM_TOKEN env var
)

# Execute circuit
result = backend.execute(circuit, shots=1024)

# List available backends
backends = IBMQuantumBackend.list_backends()
```

### Available Backends

- `ibm_brisbane` (127 qubits)
- `ibm_kyoto` (127 qubits)
- `ibm_osaka` (127 qubits)
- And more via `list_backends()`

---

## BraketBackend (AWS)

Access multiple vendors through Amazon Braket: IonQ, Rigetti, OQC, QuEra.

### Installation

```bash
pip install raf[braket]
```

### Setup

1. AWS account with Braket access
2. Configure credentials:
   ```bash
   aws configure
   # Or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
   ```

### Usage

```python
from raf.backends import BraketBackend, BRAKET_DEVICES

# List available devices
print(BRAKET_DEVICES)

# Simulators (free tier)
backend = BraketBackend("sv1")      # State vector simulator
backend = BraketBackend("dm1")      # Density matrix simulator
backend = BraketBackend("tn1")      # Tensor network simulator

# IonQ (trapped ion)
backend = BraketBackend("ionq_harmony")
backend = BraketBackend("ionq_aria")
backend = BraketBackend("ionq_forte")

# Rigetti (superconducting)
backend = BraketBackend("rigetti_aspen_m3")

# IQM via Braket
backend = BraketBackend("iqm_garnet")

# QuEra (neutral atom)
backend = BraketBackend("quera_aquila")

# Execute
result = backend.execute(circuit, shots=1024)
```

### Available Devices

| Device | Type | Qubits | Notes |
|--------|------|--------|-------|
| `sv1` | Simulator | 34 | Free tier |
| `dm1` | Simulator | 17 | Density matrix |
| `tn1` | Simulator | 50 | Tensor network |
| `ionq_harmony` | Trapped Ion | 11 | |
| `ionq_aria` | Trapped Ion | 25 | |
| `ionq_forte` | Trapped Ion | 32 | |
| `rigetti_aspen_m3` | Superconducting | 80 | |
| `iqm_garnet` | Superconducting | 20 | |
| `quera_aquila` | Neutral Atom | 256 | Analog mode |

---

## AzureQuantumBackend

Access multiple vendors through Azure Quantum: IonQ, Quantinuum, Rigetti, PASQAL.

### Installation

```bash
pip install raf[azure]
```

### Setup

1. Azure account with Quantum workspace
2. Set environment variables:
   ```bash
   export AZURE_QUANTUM_SUBSCRIPTION_ID=your_subscription
   export AZURE_QUANTUM_RESOURCE_GROUP=your_resource_group
   export AZURE_QUANTUM_WORKSPACE_NAME=your_workspace
   export AZURE_QUANTUM_LOCATION=eastus
   ```
3. Or use Azure CLI: `az login`

### Usage

```python
from raf.backends import AzureQuantumBackend, AZURE_TARGETS

# List available targets
print(AZURE_TARGETS)

# IonQ
backend = AzureQuantumBackend("ionq.simulator")
backend = AzureQuantumBackend("ionq.qpu")
backend = AzureQuantumBackend("ionq.qpu.aria-1")

# Quantinuum (trapped ion, high fidelity)
backend = AzureQuantumBackend("quantinuum.sim.h1-1sc")  # Syntax checker
backend = AzureQuantumBackend("quantinuum.sim.h1-1e")   # Emulator
backend = AzureQuantumBackend("quantinuum.qpu.h1-1")    # Hardware
backend = AzureQuantumBackend("quantinuum.qpu.h2-1")    # H2 processor

# Rigetti
backend = AzureQuantumBackend("rigetti.sim.qvm")
backend = AzureQuantumBackend("rigetti.qpu.ankaa-2")

# PASQAL (neutral atom)
backend = AzureQuantumBackend("pasqal.sim.emu-tn")

# Cost estimation
estimate = backend.get_cost_estimate(circuit, shots=1024)
```

### Available Targets

| Target | Type | Provider | Notes |
|--------|------|----------|-------|
| `ionq.simulator` | Simulator | IonQ | Free |
| `ionq.qpu` | Hardware | IonQ | 11 qubits |
| `ionq.qpu.aria-1` | Hardware | IonQ | 25 qubits |
| `quantinuum.sim.h1-1sc` | Syntax Check | Quantinuum | Free |
| `quantinuum.sim.h1-1e` | Emulator | Quantinuum | |
| `quantinuum.qpu.h1-1` | Hardware | Quantinuum | 20 qubits |
| `quantinuum.qpu.h2-1` | Hardware | Quantinuum | 32 qubits |
| `rigetti.sim.qvm` | Simulator | Rigetti | Free |
| `rigetti.qpu.ankaa-2` | Hardware | Rigetti | 84 qubits |
| `pasqal.sim.emu-tn` | Emulator | PASQAL | |

---

## IQMBackend

Access IQM quantum computers (European provider).

### Installation

```bash
pip install raf[iqm]
```

### Setup

1. Create account at [resonance.meetiqm.com](https://resonance.meetiqm.com)
2. Get API token from account settings
3. Set environment variable:
   ```bash
   export IQM_TOKEN=your_token_here
   ```

### Usage

```python
from raf.backends import IQMBackend, IQM_SERVERS

# List available servers
print(IQM_SERVERS)

# Connect to IQM Resonance (cloud access)
backend = IQMBackend("resonance")

# Or specify server URL directly
backend = IQMBackend(
    server_url="https://cocos.resonance.meetiqm.com/garnet",
    token="your_token"
)

# Execute
result = backend.execute(circuit, shots=1024)
```

### Available Servers

| Server | URL | Notes |
|--------|-----|-------|
| `resonance` | IQM Resonance cloud | Garnet processor |
| `garnet` | Same as resonance | 20 qubits |
| `demo` | Demo server | For testing |

---

## Unified Interface

All backends implement the same interface:

```python
class QuantumBackend:
    def execute(self, circuit, shots=1024, **kwargs) -> ExecutionResult
    def execute_batch(self, circuits, shots=1024, **kwargs) -> List[ExecutionResult]
    def compute_expectation(self, circuit, observable, shots=1024) -> float

    @property
    def statistics(self) -> Dict[str, Any]
    def reset_statistics(self)
```

### ExecutionResult

```python
@dataclass
class ExecutionResult:
    counts: Dict[str, int]          # Measurement counts
    shots: int                       # Number of shots
    backend_name: str               # Backend identifier
    backend_type: BackendType       # SIMULATOR, NOISY_SIMULATOR, REAL_HARDWARE
    execution_time_ms: float        # Execution time
    error_rate_estimate: float      # Estimated error (if available)
    metadata: Dict[str, Any]        # Backend-specific metadata

    @property
    def probabilities(self) -> Dict[str, float]
```

---

## Environment Variables Summary

| Variable | Backend | Description |
|----------|---------|-------------|
| `IBM_QUANTUM_TOKEN` | IBM | API token |
| `AWS_ACCESS_KEY_ID` | Braket | AWS credentials |
| `AWS_SECRET_ACCESS_KEY` | Braket | AWS credentials |
| `AZURE_QUANTUM_SUBSCRIPTION_ID` | Azure | Subscription ID |
| `AZURE_QUANTUM_RESOURCE_GROUP` | Azure | Resource group |
| `AZURE_QUANTUM_WORKSPACE_NAME` | Azure | Workspace name |
| `AZURE_QUANTUM_LOCATION` | Azure | Region (e.g., eastus) |
| `IQM_TOKEN` | IQM | API token |

---

## Choosing a Backend

| Use Case | Recommended Backend |
|----------|---------------------|
| Development/Testing | `AerBackend` with noise profile |
| High-fidelity gates | Quantinuum (Azure) or IonQ |
| Many qubits | Rigetti, IBM, or QuEra |
| European data residency | IQM |
| Cost-sensitive | AWS Braket simulators (free tier) |
| Gradient-based optimization | Local Aer or IonQ |
