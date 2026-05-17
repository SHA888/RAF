<!--
v4 (2026-05-17): Quantum backend availability corrected against May 2026 reality.
                  IBM row: Brisbane/Kyoto/Osaka all retired (Aug 2024, Aug 2024, Nov 2025);
                    replaced with Heron r1/r2/r3 (Aachen/Boston/Torino) and Nighthawk (Miami).
                  Braket row: OQC removed (access ended June 2024); IQM and AQT added (current providers).
                  Azure row: Atom Computing added.
                  IQM row: Emerald (54q, July 2025) added alongside Garnet; noted IQM Resonance cloud.
                  Code examples updated: ionq_harmony (retired) → ionq_forte; quantinuum.qpu.h1-1
                    (H1 retirement announced July 2025) → quantinuum.qpu.h2-1; IQMBackend("resonance")
                    (platform name, not device) → IQMBackend("garnet"). Device names in code examples
                    are illustrative; verify against your raf.backends module's actual accepted strings.
v3 (2026-05-17): Positioning pivot — RAF reframed as open-source reference implementation
                  of QC-ML co-evolutionary frameworks (Singh 2025, Shukla 2025, Maes 2025), not a
                  competing framework. Tagline rewritten. Overview opening rewritten. New
                  "Positioning" section added between Overview and Installation. Singh demoted
                  from primary Related Work list to Concurrent and recent work subsection. DOI
                  added to Singh bibtex (10.63721/25JPAIR0118). raf2026 bibtex venue updated from
                  NeurIPS Workshops to Journal of Open Source Software (JOSS).
v2 (2026-05-17): Related Work expanded with concurrent/prior work (Acampora 2025, Maes 2025,
                  Alexeev 2025, Shukla 2025); raf2026 bibtex venue updated from IEEE WCCI to
                  NeurIPS 2026 Workshops (target). All other sections preserved verbatim.
-->

# Reciprocal Acceleration Framework (RAF)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12-3.13](https://img.shields.io/badge/python-3.12%E2%80%933.13-blue.svg)](https://www.python.org/downloads/)
[![Open Science](https://img.shields.io/badge/Open-Science-green.svg)](https://opensource.org/)

Open-source Python reference implementation of QC-ML co-evolutionary frameworks (Singh 2025, Shukla 2025, Maes 2025).

## Overview

The Reciprocal Acceleration Framework provides an open-source Python reference implementation of QC-ML co-evolutionary frameworks described in Singh (2025), Shukla (2025), Maes (2025), and related work. It operationalizes their feedback-loop dynamics through three task-based acceleration loops:

1. **Error Mitigation Loop** - Operating at the output/application level
2. **Ansatz Design Loop** - Operating at the algorithm/circuit level
3. **Calibration-Control Loop** - Operating at the hardware/physics level

This implementation provides tools for:

- Analyzing feedback dynamics in QC-ML systems
- Identifying rate-limiting bottlenecks
- Guiding research prioritization
- Visualizing co-evolutionary progress

## Positioning

The QC-ML feedback-loop concept has been articulated across multiple recent works:

- Singh (2025) — decision framework for assessing quantum advantage
- Shukla (2025) — three-layer co-evolutionary co-design framework
- Maes (2025) — adaptive co-design of QML and QEC via reinforcement learning
- Alexeev et al. (2025) — comprehensive review of AI for quantum computing
- Acampora et al. (2025) — Quantum Community Network white paper on QC-AI

These works describe the _what_ and _why_ of QC-ML co-evolution at the conceptual level. RAF complements them by providing the _how_ — a runnable Python implementation that lets researchers:

- Run sensitivity studies over the coupling parameters that the conceptual frameworks discuss qualitatively
- Compare alternative coupling assumptions across formulations
- Build empirical methods on top of a tested, multi-backend substrate
- Reproduce framework behavior from a single `uv sync` command

RAF makes no novel framework claim. It exists to make the existing frameworks testable.

## Installation

### Using `uv` (Recommended - Modern Python Tooling)

```bash
# Clone the repository
git clone https://github.com/yourusername/RAF.git
cd RAF

# Install with uv (creates venv automatically)
uv sync
```

### Using pip (Traditional)

```bash
# Clone the repository
git clone https://github.com/yourusername/RAF.git
cd RAF

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Quick Start

```python
from raf import ReciprocalAccelerationFramework
from raf.loops import ErrorMitigationLoop, AnsatzDesignLoop, CalibrationControlLoop

# Initialize the framework
raf = ReciprocalAccelerationFramework()

# Add acceleration loops
raf.add_loop(ErrorMitigationLoop())
raf.add_loop(AnsatzDesignLoop())
raf.add_loop(CalibrationControlLoop())

# Analyze current state
analysis = raf.analyze()
print(analysis.bottlenecks)
print(analysis.recommendations)

# Visualize loop dynamics
raf.visualize()
```

## Empirical Validation

RAF includes tools for empirical validation using realistic quantum simulation and real hardware:

```bash
# Using uv (recommended)
uv sync --all-extras
python examples/empirical_validation.py --mode quick

# Or using pip
pip install -e ".[quantum]"
python examples/empirical_validation.py --mode quick
```

### Supported Quantum Backends

RAF supports multiple quantum hardware vendors through a unified interface:

| Backend               | Provider      | Install                     | Devices                                                    |
| --------------------- | ------------- | --------------------------- | ---------------------------------------------------------- |
| `AerBackend`          | Local         | `uv sync --extra quantum`   | Simulators with realistic noise                            |
| `IBMQuantumBackend`   | IBM Quantum   | `uv sync --extra ibm`       | Heron r1/r2/r3 (Aachen, Boston, Torino), Nighthawk (Miami) |
| `BraketBackend`       | AWS Braket    | `uv sync --extra braket`    | IonQ, Rigetti, QuEra, IQM, AQT                             |
| `AzureQuantumBackend` | Azure Quantum | `uv sync --extra azure`     | IonQ, Quantinuum, Rigetti, PASQAL, Atom Computing          |
| `IQMBackend`          | IQM           | `uv sync --extra iqm`       | Garnet (20q), Emerald (54q) via IQM Resonance              |
| `PennyLaneBackend`    | PennyLane     | `uv sync --extra pennylane` | Gradient-based VQA optimization                            |

Install all backends: `uv sync --all-extras`

Or with pip: `pip install raf[all-backends]`

### Backend Usage Examples

```python
from raf.backends import list_available_backends

# Check which backends are installed
print(list_available_backends())

# Local simulation with realistic noise (always available)
from raf.backends import create_backend
backend = create_backend("manila")  # IBM Manila-like noise

# AWS Braket (IonQ trapped ion)
from raf.backends import BraketBackend
backend = BraketBackend("ionq_forte")  # Forte-1; also "ionq_aria_1", "ionq_aria_2", "ionq_forte_enterprise"

# Azure Quantum (Quantinuum)
from raf.backends import AzureQuantumBackend
backend = AzureQuantumBackend("quantinuum.qpu.h2-1")  # 56-qubit H2; H1 retirement announced July 2025

# IQM European hardware (via IQM Resonance cloud)
from raf.backends import IQMBackend
backend = IQMBackend("garnet")  # 20-qubit Crystal 20; or "emerald" for 54-qubit Crystal 54

# PennyLane for gradient-based optimization
from raf.backends import PennyLaneBackend
backend = PennyLaneBackend("default.qubit", wires=4)
```

### Supported Noise Profiles (Simulation)

| Profile    | Device Type     | Qubits | Description          |
| ---------- | --------------- | ------ | -------------------- |
| `manila`   | Superconducting | 5      | IBM Manila-like      |
| `kolkata`  | Superconducting | 27     | IBM Kolkata-like     |
| `ionq`     | Trapped Ion     | 11     | IonQ Harmony-like    |
| `sycamore` | Superconducting | 53     | Google Sycamore-like |

### Example: Error Mitigation Experiment

```python
from raf.experiments import ErrorMitigationExperiment

# Run experiment with realistic noise
experiment = ErrorMitigationExperiment(noise_profile_name="manila")
results = experiment.run_acceleration_study(
    num_iterations=5,
    circuits_per_iteration=10,
    depths=[3, 5, 7, 10],
)

print(f"Acceleration: {results['acceleration_metrics']['overall_acceleration']:.2f}")
print(f"Final error reduction: {results['acceleration_metrics']['final_error_reduction']:.1%}")
```

## Framework Architecture

```
RAF/
├── raf/                          # Core package
│   ├── __init__.py
│   ├── core/                     # Core framework components
│   │   ├── __init__.py
│   │   ├── framework.py          # Main RAF class
│   │   ├── loop.py               # Base acceleration loop
│   │   └── metrics.py            # Metrics and measurements
│   ├── loops/                    # Acceleration loop implementations
│   │   ├── __init__.py
│   │   ├── error_mitigation.py   # Error Mitigation Loop
│   │   ├── ansatz_design.py      # Ansatz Design Loop
│   │   └── calibration_control.py # Calibration-Control Loop
│   ├── backends/                 # Quantum backend abstraction
│   │   ├── __init__.py
│   │   ├── base.py               # Base backend classes
│   │   ├── aer.py                # Qiskit Aer backend
│   │   └── noise_models.py       # Device noise profiles
│   ├── experiments/              # Empirical validation
│   │   ├── __init__.py
│   │   ├── error_mitigation.py   # Error mitigation experiments
│   │   └── metrics_collector.py  # Experimental metrics
│   ├── analysis/                 # Analysis tools
│   │   ├── __init__.py
│   │   ├── bottleneck.py         # Bottleneck identification
│   │   ├── cross_loop.py         # Cross-loop interaction analysis
│   │   └── prioritization.py     # Research prioritization
│   ├── visualization/            # Visualization tools
│   │   ├── __init__.py
│   │   ├── loop_dynamics.py      # Loop dynamics plots
│   │   └── dashboard.py          # Interactive dashboard
│   └── utils/                    # Utilities
│       ├── __init__.py
│       └── config.py             # Configuration management
├── examples/                     # Example notebooks and scripts
├── tests/                        # Unit tests
├── docs/                         # Documentation
└── data/                         # Sample data and benchmarks
```

## The Three Acceleration Loops

### 1. Error Mitigation Loop

```
ML-QEM → Cleaner Outputs → Larger QML Experiments → More Training Data → Improved ML-QEM
```

**Bottlenecks:**

- Calibration data acquisition cost
- Generalization limits across devices
- Diminishing returns near fundamental limits

### 2. Ansatz Design Loop

```
QAS → Improved Circuits → Better QML Results → Training Signal → Neural Surrogates → Efficient QAS
```

**Bottlenecks:**

- Evaluation cost (quantum circuit execution)
- Surrogate model accuracy
- Hardware heterogeneity

### 3. Calibration-Control Loop

```
ML Noise Models → Optimized Control → Lower Error Rates → Deeper Circuits → Richer Data → Refined Models
```

**Bottlenecks:**

- Model complexity for non-Markovian noise
- Drift timescales
- Control bandwidth limitations

## Key Concepts

### Acceleration Mechanism

A loop exhibits **acceleration** when each iteration increases the rate of progress in subsequent iterations—a positive feedback dynamic.

### Cross-Loop Coupling

The three loops exhibit significant cross-loop coupling:

- Improvements in Calibration-Control → Benefits Error Mitigation and Ansatz Design
- Better ansatz designs → Reduced noise sensitivity → Eases demands on mitigation and calibration

### High-Leverage Investments

Based on loop analysis:

1. **Surrogate Model Development** - Accelerates all three loops
2. **Standardized Benchmarks** - Enables systematic progress tracking
3. **Cross-Platform Abstractions** - Reduces redundant effort

## Citation

If you use this framework in your research, please cite:

```bibtex
@article{singh2025quantum,
  title={Quantum-AI Synergy and the Framework for Assessing Quantum Advantage},
  author={Singh, Amit},
  journal={Journal of Pioneering Artificial Intelligence Research},
  volume={1},
  number={4},
  pages={1--28},
  year={2025},
  doi={10.63721/25JPAIR0118}
}

@article{raf2026,
  title={RAF: A Python Reference Implementation of QC-ML Co-Evolutionary Frameworks},
  author={[Authors]},
  journal={Journal of Open Source Software},
  year={2026},
  note={Submission in preparation}
}
```

## Related Work

This framework implements concepts from and builds upon:

- AlphaQubit (DeepMind) - Neural network quantum error decoding
- GP-QML (Los Alamos) - Gaussian processes for quantum ML

### Concurrent and recent work (added v2, 2026-05-17; updated v3)

The bidirectional AI–QC relationship has attracted substantial recent attention. RAF positions itself as an operational, task-decomposed reference implementation that complements the following:

- **Singh (2025)** — _Quantum-AI Synergy and the Framework for Assessing Quantum Advantage_ (DOI 10.63721/25JPAIR0118). Decision framework for assessing whether a given problem is suitable for quantum acceleration, with four-dimensional evaluation criteria (problem sizing, resource estimation, advantage assessment, paradigm selection). Singh's contribution is a _decision_ framework (whether to use quantum); RAF implements _dynamics_ frameworks (how feedback loops compose). The two are orthogonal and complementary.
- **Acampora et al. (2025)** — _Quantum computing and artificial intelligence: status and perspectives_ (arXiv:2505.23860). 38-author Quantum Community Network white paper establishing the long-term research agenda for "Quantum for AI" and "AI for Quantum."
- **Maes (2025)** — _Adaptive Co-Design of Quantum Machine Learning Algorithms and Error Correction Protocols using Reinforcement Learning_ (Zenodo, DOI 10.5281/zenodo.15428357). Proposes a closed feedback loop between QML ansatz and QEC strategy via a single RL agent.
- **Alexeev et al. (2025)** — _Artificial intelligence for quantum computing_, Nature Communications **16**:10829 (DOI 10.1038/s41467-025-65836-3). Comprehensive 28-author review of AI applications across the QC stack (device design, preprocessing, control, QEC, postprocessing).
- **Shukla (2025)** — _AI and Quantum Computing: A Co-Evolutionary Co-Design Framework and Systematic Review of Synergistic Benefits_ (TechRxiv, DOI 10.36227/techrxiv.176704915.54945198/v1). Conceptual three-layer (hardware/algorithmic/application) co-evolutionary framework, intended as analytical taxonomy.

RAF complements these contributions in three respects: (1) functional task-based decomposition into Error Mitigation × Ansatz Design × Calibration-Control loops, implementable from the conceptual layered descriptions; (2) explicit coupling parameters exposed as configuration, enabling sensitivity studies across formulations; (3) open-source Python implementation with multi-backend abstraction (Aer, IBM Quantum, AWS Braket, Azure Quantum, IQM, PennyLane).

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

This work is part of the open science initiative for quantum-AI research reproducibility.
