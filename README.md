# Reciprocal Acceleration Framework (RAF)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Open Science](https://img.shields.io/badge/Open-Science-green.svg)](https://opensource.org/)

A systematic framework for understanding and accelerating co-evolutionary dynamics between Quantum Computing (QC) and Machine Learning (ML).

## Overview

The Reciprocal Acceleration Framework formalizes the bidirectional synergy between quantum computing and machine learning, identifying three primary acceleration loops:

1. **Error Mitigation Loop** - Operating at the output/application level
2. **Ansatz Design Loop** - Operating at the algorithm/circuit level  
3. **Calibration-Control Loop** - Operating at the hardware/physics level

This implementation provides tools for:
- Analyzing feedback dynamics in QC-ML systems
- Identifying rate-limiting bottlenecks
- Guiding research prioritization
- Visualizing co-evolutionary progress

## Installation

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

RAF includes tools for empirical validation using realistic quantum simulation:

```bash
# Install quantum dependencies
pip install qiskit qiskit-aer

# Run empirical validation demo
python examples/empirical_validation.py --mode quick
```

### Supported Noise Profiles

| Profile | Device Type | Qubits | Description |
|---------|-------------|--------|-------------|
| `manila` | Superconducting | 5 | IBM Manila-like |
| `kolkata` | Superconducting | 27 | IBM Kolkata-like |
| `ionq` | Trapped Ion | 11 | IonQ Harmony-like |
| `sycamore` | Superconducting | 53 | Google Sycamore-like |

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
  year={2025}
}

@inproceedings{raf2026,
  title={Reciprocal Acceleration: Formalizing Co-Evolutionary Dynamics in Quantum-Classical Machine Learning},
  author={[Authors]},
  booktitle={IEEE World Congress on Computational Intelligence (WCCI)},
  year={2026}
}
```

## Related Work

This framework builds upon and extends:
- Singh (2025) - Quantum-AI Synergy evaluation framework
- AlphaQubit (DeepMind) - Neural network quantum error decoding
- GP-QML (Los Alamos) - Gaussian processes for quantum ML

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

This work is part of the open science initiative for quantum-AI research reproducibility.
