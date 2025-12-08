# Supplementary Materials

## Reciprocal Acceleration Framework (RAF)

This directory contains supplementary materials for the IEEE WCCI 2026 paper:
"Reciprocal Acceleration: Formalizing Co-Evolutionary Dynamics in Quantum-Classical Machine Learning"

## Contents

### 1. Code Repository
- **Full implementation**: https://github.com/SHA888/RAF
- **License**: MIT
- **Requirements**: Python 3.9+, Qiskit 1.0+

### 2. Experimental Data

#### Error Mitigation Loop Results
- `../results/error_mitigation/em_experiment_results.json`
- 50 experimental runs across 5 iterations
- Metrics: error reduction (30% → 80%), acceleration factor (2.0-2.5x)

#### Ansatz Design Results
- `../results/ansatz_design/ad_experiment_results.json`
- `../results/ansatz_design/heterogeneity_study.json`

#### Bottleneck Validation Results
- `../results/bottleneck_validation/bottleneck_results.json`
- 6 bottleneck scenarios tested
- 91.3% average prediction accuracy

### 3. Figures (Publication Quality)

| Figure | File | Description |
|--------|------|-------------|
| Figure 1 | `../figures/em_acceleration_dynamics.png` | Acceleration dynamics across iterations |
| Table I | `../figures/bottleneck_validation_table.png` | Bottleneck validation results |
| Figure 2 | `../figures/cross_loop_coupling.png` | Cross-loop coupling analysis |

### 4. Reproducing Results

```bash
# Clone repository
git clone https://github.com/SHA888/RAF.git
cd RAF

# Install dependencies
pip install -e .

# Run error mitigation experiment
python examples/error_mitigation_experiment.py

# Run bottleneck validation
python -c "
from raf.experiments import BottleneckValidationExperiment
exp = BottleneckValidationExperiment(random_seed=42)
result = exp.run_full_validation(verbose=True)
print(result.summary())
"

# Run cross-loop validation
python -c "
from raf.experiments import CrossLoopValidationExperiment
exp = CrossLoopValidationExperiment(random_seed=42)
result = exp.run_integrated_experiment(n_iterations=5, verbose=True)
"
```

### 5. Noise Model Specifications

Device-calibrated noise models based on published specifications:

| Device | T1 (μs) | T2 (μs) | 1Q Error | 2Q Error | Readout Error |
|--------|---------|---------|----------|----------|---------------|
| IBM Manila | 100 | 80 | 0.0003 | 0.01 | 0.02 |
| IBM Kolkata | 150 | 120 | 0.0002 | 0.008 | 0.015 |
| IonQ Harmony | 10000 | 1000 | 0.0005 | 0.02 | 0.005 |
| Google Sycamore | 20 | 15 | 0.001 | 0.006 | 0.03 |

### 6. Extended Loop Characterizations

See `../raf/loops/` for detailed implementations:
- `error_mitigation.py` - Error Mitigation Loop
- `ansatz_design.py` - Ansatz Design Loop
- `calibration_control.py` - Calibration-Control Loop

### 7. Contact

For questions about this work, please open an issue at:
https://github.com/SHA888/RAF/issues
