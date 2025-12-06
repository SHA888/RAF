# RAF Empirical Validation TODO

**Goal**: Transform RAF from a conceptual framework to an empirically-grounded paper suitable for IEEE WCCI 2026.

**Timeline**: 2 weeks (Target completion: Dec 19, 2025)

---

## Phase 1: Infrastructure & Integration (Days 1-3)

### 1.1 Qiskit Integration
- [x] Create `raf/backends/` module for quantum hardware abstraction
- [x] Implement `IBMQuantumBackend` class wrapping IBM Quantum access
- [x] Implement `AerBackend` class for realistic noise simulation
- [x] Add device-calibrated noise models (FakeManilaV2, FakeKolkataV2, etc.)
- [x] Create unified `QuantumExecutor` interface
- [x] Add `BraketBackend` for AWS (IonQ, Rigetti, OQC, QuEra)
- [x] Add `AzureQuantumBackend` for Azure (IonQ, Quantinuum, Rigetti, PASQAL)
- [x] Add `IQMBackend` for IQM European hardware

### 1.2 PennyLane Integration (Optional, if time permits)
- [ ] Implement `PennyLaneBackend` for gradient-based optimization
- [ ] Support for `default.qubit`, `lightning.qubit`, and `qiskit.ibmq`

### 1.3 Dependencies Update
- [x] Add `qiskit`, `qiskit-aer`, `qiskit-ibm-runtime` to requirements
- [x] Add `pennylane`, `pennylane-qiskit` (optional)
- [x] Update `pyproject.toml` with new dependencies

---

## Phase 2: Realistic Noise Simulation (Days 3-5)

### 2.1 Noise Model Calibration
- [ ] Fetch real device calibration data from IBM Quantum
- [x] Implement `NoiseModelBuilder` using device T1, T2, gate errors
- [x] Create noise profiles for superconducting (IBM) and trapped-ion (simulated IonQ-like)
- [ ] Validate noise models against published device specifications

### 2.2 Error Mitigation Loop - Empirical Study
- [x] Implement VQE circuits for H2, LiH molecules (small, tractable)
- [x] Run circuits with/without ML-based error mitigation
- [x] Measure: raw expectation values, mitigated values, ideal values
- [x] Compute acceleration metrics from real/simulated data
- [ ] Generate plots: mitigation accuracy vs. circuit depth, acceleration over iterations

### 2.3 Metrics from Real Data
- [ ] Replace simulated `AccelerationMetric` values with measured data
- [x] Implement `ExperimentalMetricsCollector` class
- [x] Track: fidelity improvement, overhead reduction, iteration speedup

---

## Phase 3: Ansatz Design Loop - Simulation Study (Days 5-8)

### 3.1 Neural Surrogate Implementation
- [ ] Implement simple MLP surrogate for circuit performance prediction
- [ ] Train on simulated VQE results (1000+ circuits)
- [ ] Measure surrogate accuracy vs. actual circuit evaluation

### 3.2 QAS Experiment (Simulated with Realistic Noise)
- [ ] Implement simple evolutionary QAS algorithm
- [ ] Run architecture search on noisy simulator
- [ ] Track: circuits evaluated, best performance found, search efficiency
- [ ] Compare: random search vs. surrogate-guided search
- [ ] Measure acceleration: iterations to convergence, evaluations saved

### 3.3 Hardware Heterogeneity Study
- [ ] Run same QAS on 2-3 different noise profiles
- [ ] Quantify performance degradation across "devices"
- [ ] Validate bottleneck: hardware heterogeneity limits transfer

---

## Phase 4: Calibration-Control Loop - Demonstration (Days 8-10)

### 4.1 Drift Simulation
- [ ] Implement time-varying noise model (simulated drift)
- [ ] Create `DriftingNoiseModel` with configurable drift rate

### 4.2 ML-Based Calibration Tracking
- [ ] Implement simple LSTM/MLP for noise parameter prediction
- [ ] Train on synthetic drift trajectories
- [ ] Measure: prediction accuracy, recalibration frequency reduction

### 4.3 Control Optimization (Simplified)
- [ ] Implement pulse-level optimization using Qiskit Pulse (if feasible)
- [ ] OR: Gate-level optimization with noise-aware compilation
- [ ] Measure: gate fidelity improvement, circuit depth reduction

---

## Phase 5: Cross-Loop Validation (Days 10-11)

### 5.1 Integrated Experiment
- [ ] Run combined experiment: better calibration → better mitigation → larger circuits
- [ ] Quantify cross-loop coupling from experimental data
- [ ] Validate: improvements in one loop benefit others

### 5.2 Bottleneck Validation
- [ ] Artificially introduce bottlenecks (e.g., limit calibration data)
- [ ] Measure impact on loop acceleration
- [ ] Compare predicted vs. observed bottleneck effects

---

## Phase 6: Paper Updates (Days 11-13)

### 6.1 Fix References
- [x] Replace `arXiv:2501.xxxxx` placeholders with real arXiv IDs
- [ ] Verify all 19 references are complete and accurate
- [ ] Add any new references from empirical work

### 6.2 Add Validation Roadmap Section
- [x] Write Section V.D: "Empirical Validation Methodology"
- [x] Describe experimental setup (devices, noise models, circuits)
- [x] Present quantitative results from Phase 2-5
- [x] Discuss limitations and future validation opportunities

### 6.3 Update Results Section
- [ ] Add Figure: Acceleration dynamics from real/simulated data
- [ ] Add Table: Bottleneck validation results
- [ ] Add Figure: Cross-loop coupling measured vs. predicted

### 6.4 Emphasize Codebase Contribution
- [ ] Add paragraph on open-source implementation
- [ ] Include GitHub repository link (placeholder for now)
- [ ] Describe how practitioners can extend the framework

---

## Phase 7: Final Polish (Days 13-14)

### 7.1 Code Quality
- [x] Add integration tests for Qiskit backend
- [x] Update README with empirical examples
- [x] Create `examples/empirical_validation.py` script
- [ ] Ensure all experiments are reproducible

### 7.2 Paper Finalization
- [ ] Proofread entire manuscript
- [ ] Check IEEE WCCI formatting requirements
- [ ] Prepare supplementary materials (code, data)
- [ ] Generate final figures in publication quality

### 7.3 Submission Preparation
- [ ] Create camera-ready PDF
- [ ] Prepare author information
- [ ] Write cover letter (if required)
- [ ] Submit to IEEE WCCI 2026

---

## Resource Requirements

### Accounts Needed
- [ ] IBM Quantum account (free tier sufficient for small experiments)
- [ ] Optional: IBM Quantum Network access for faster queue times

### Compute Resources
- Local machine with GPU (for surrogate training)
- ~10-20 hours of IBM Quantum credits (free tier provides ~10 min/month real hardware)

### Fallback Strategy
If real hardware access is limited:
1. Use Qiskit Aer with `FakeBackendV2` (device-calibrated noise)
2. Clearly state "simulated with realistic noise models" in paper
3. Add "Future Work" section for full hardware validation

---

## Success Criteria

### Minimum Viable (Must Have)
- [x] Qiskit integration with noise simulation
- [x] One complete Error Mitigation loop experiment
- [x] Measured acceleration metrics (not just simulated)
- [x] Fixed references in paper
- [x] Validation roadmap section added

### Target (Should Have)
- [ ] All three loops with simulation experiments
- [ ] Cross-loop coupling validation
- [ ] At least one real IBM Quantum hardware run
- [ ] Publication-quality figures

### Stretch (Nice to Have)
- [ ] PennyLane integration
- [ ] Multiple hardware backends comparison
- [ ] Interactive dashboard for experiments
- [ ] Pre-trained surrogate models included

---

## Daily Schedule (Suggested)

| Day | Focus | Deliverables |
|-----|-------|--------------|
| 1 | Setup | Qiskit installed, IBM account, backend abstraction |
| 2 | Backend | `QiskitBackend`, `AerBackend` complete |
| 3 | Noise | Noise models calibrated, basic circuits running |
| 4 | EM Loop | VQE circuits, mitigation experiment design |
| 5 | EM Loop | Data collection, acceleration metrics |
| 6 | AD Loop | Surrogate model implementation |
| 7 | AD Loop | QAS experiment running |
| 8 | AD Loop | Results analysis, heterogeneity study |
| 9 | CC Loop | Drift simulation, ML tracking |
| 10 | CC Loop | Control optimization, results |
| 11 | Cross-Loop | Integrated experiment, validation |
| 12 | Paper | References fixed, roadmap written |
| 13 | Paper | Results section updated, figures |
| 14 | Polish | Final review, submission prep |

---

## Notes

- Queue times on IBM Quantum can be unpredictable; submit jobs early
- Focus on Error Mitigation loop first (most feasible, clearest signal)
- Noise simulation with FakeBackends is scientifically valid and commonly used
- Keep experiments small (2-5 qubits) to ensure tractability
- Document all experimental parameters for reproducibility
