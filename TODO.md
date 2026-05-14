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

- [x] Implement `PennyLaneBackend` for gradient-based optimization
- [x] Support for `default.qubit`, `lightning.qubit`, and `qiskit.ibmq`

### 1.3 Dependencies Update

- [x] Add `qiskit`, `qiskit-aer`, `qiskit-ibm-runtime` to requirements
- [x] Add `pennylane`, `pennylane-qiskit` (optional)
- [x] Update `pyproject.toml` with new dependencies

---

## Phase 2: Realistic Noise Simulation (Days 3-5)

### 2.1 Noise Model Calibration

- [x] Fetch real device calibration data (via AWS Braket and published specs)
- [x] Implement `NoiseModelBuilder` using device T1, T2, gate errors
- [x] Create noise profiles for superconducting (IBM) and trapped-ion (simulated IonQ-like)
- [x] Validate noise models against published device specifications (IonQ, Quantinuum, Rigetti, IQM, Google)

### 2.2 Error Mitigation Loop - Empirical Study

- [x] Implement VQE circuits for H2, LiH molecules (small, tractable)
- [x] Run circuits with/without ML-based error mitigation
- [x] Measure: raw expectation values, mitigated values, ideal values
- [x] Compute acceleration metrics from real/simulated data
- [x] Generate plots: mitigation accuracy vs. circuit depth, acceleration over iterations

### 2.3 Metrics from Real Data

- [x] Replace simulated `AccelerationMetric` values with measured data
- [x] Implement `ExperimentalMetricsCollector` class
- [x] Track: fidelity improvement, overhead reduction, iteration speedup

---

## Phase 3: Ansatz Design Loop - Simulation Study (Days 5-8)

### 3.1 Neural Surrogate Implementation

- [x] Implement simple MLP surrogate for circuit performance prediction
- [x] Train on simulated VQE results (1000+ circuits)
- [x] Measure surrogate accuracy vs. actual circuit evaluation

### 3.2 QAS Experiment (Simulated with Realistic Noise)

- [x] Implement simple evolutionary QAS algorithm
- [x] Run architecture search on noisy simulator
- [x] Track: circuits evaluated, best performance found, search efficiency
- [x] Compare: random search vs. surrogate-guided search
- [x] Measure acceleration: iterations to convergence, evaluations saved

### 3.3 Hardware Heterogeneity Study

- [x] Run same QAS on 2-3 different noise profiles (manila, kolkata, ionq)
- [x] Quantify performance degradation across "devices"
- [x] Validate bottleneck: hardware heterogeneity limits transfer

---

## Phase 4: Calibration-Control Loop - Demonstration (Days 8-10)

### 4.1 Drift Simulation

- [x] Implement time-varying noise model (simulated drift)
- [x] Create `DriftingNoiseModel` with configurable drift rate

### 4.2 ML-Based Calibration Tracking

- [x] Implement simple LSTM/MLP for noise parameter prediction
- [x] Train on synthetic drift trajectories
- [x] Measure: prediction accuracy, recalibration frequency reduction

### 4.3 Control Optimization (Simplified)

- [x] Implement pulse-level optimization using Qiskit Pulse (if feasible)
- [x] OR: Gate-level optimization with noise-aware compilation
- [x] Measure: gate fidelity improvement, circuit depth reduction

---

## Phase 5: Cross-Loop Validation (Days 10-11)

### 5.1 Integrated Experiment

- [x] Run combined experiment: better calibration → better mitigation → larger circuits
- [x] Quantify cross-loop coupling from experimental data
- [x] Validate: improvements in one loop benefit others

### 5.2 Bottleneck Validation

- [x] Artificially introduce bottlenecks (e.g., limit calibration data)
- [x] Measure impact on loop acceleration
- [x] Compare predicted vs. observed bottleneck effects

---

## Phase 6: Paper Updates (Days 11-13)

### 6.1 Fix References

- [x] Replace `arXiv:2501.xxxxx` placeholders with real arXiv IDs
- [x] Verify all 19 references are complete and accurate
- [x] Add any new references from empirical work

### 6.2 Add Validation Roadmap Section

- [x] Write Section V.D: "Empirical Validation Methodology"
- [x] Describe experimental setup (devices, noise models, circuits)
- [x] Present quantitative results from Phase 2-5
- [x] Discuss limitations and future validation opportunities

### 6.3 Update Results Section

- [x] Add Figure: Acceleration dynamics from real/simulated data
- [x] Add Table: Bottleneck validation results
- [x] Add Figure: Cross-loop coupling measured vs. predicted

### 6.4 Emphasize Codebase Contribution

- [x] Add paragraph on open-source implementation
- [x] Include GitHub repository link (placeholder for now)
- [x] Describe how practitioners can extend the framework

---

## Phase 7: Final Polish (Days 13-14)

### 7.1 Code Quality

- [x] Add integration tests for Qiskit backend
- [x] Update README with empirical examples
- [x] Create `examples/empirical_validation.py` script
- [x] Ensure all experiments are reproducible
  - [x] Add global reproducibility utility (set_all_seeds: numpy/random/torch, Qiskit seed_simulator/seed_transpiler)
  - [x] Expose seed param on experiment constructors/runs and route to all RNG paths (SimulatedLoop, CrossLoop, ControlOptimization, mitigation/train)
  - [x] Persist run configs (seed + params) for replayability
  - [x] Replace hardcoded seeds (e.g., np.random.seed(42) in NeuralSurrogate) with passed-in seeds
  - [x] CLI/config: global seed flag and run-config persistence in examples

### 7.2 Paper Finalization

- [x] Proofread entire manuscript
- [x] Check IEEE WCCI formatting requirements
- [x] Prepare supplementary materials (code, data)
- [x] Generate final figures in publication quality

### 7.3 Submission Preparation (UPDATED: Post-WCCI)

- [x] Create camera-ready PDF → DEFER to 7.4 (arXiv first)
- [x] Prepare author information
- [x] Write cover letter → Need for Nature MI submission (Phase 10)
- [x] IEEE WCCI 2026 → ❌ MISSED (Jan 31 deadline passed)

**New Path**: arXiv + Nature MI + AAAI 2027 (see Phase 10)

---

## Phase 8: Multi-Vendor Hardware Validation (DEFERRED - Future Work)

> **Status**: Deferred due to vendor account access issues. Current simulation-based
> validation is scientifically valid. Real hardware validation planned for future work.

### 8.1 Azure Quantum Setup (Deferred)

- [ ] Create Azure account and Quantum workspace
- [ ] Configure `azure-quantum` credentials
- [ ] Test connection with IonQ simulator

### 8.2 AWS Braket Setup (Deferred)

- [ ] Create AWS account with Braket access
- [ ] Configure AWS credentials
- [ ] Test connection with IonQ/Rigetti simulators

### 8.3 Cross-Vendor Validation Experiments (Deferred)

- [ ] Run Error Mitigation loop on IonQ (trapped-ion)
- [ ] Run Error Mitigation loop on Rigetti (superconducting)
- [ ] Compare acceleration dynamics across hardware types
- [ ] Measure hardware-specific bottleneck effects

### 8.4 Paper Enhancement (Deferred)

- [ ] Add Table: Cross-vendor acceleration comparison
- [ ] Add Figure: Hardware heterogeneity impact on loop dynamics
- [ ] Update Section V.D with real hardware results
- [ ] Strengthen "hardware-agnostic" claims with empirical evidence

---

## Phase 10: arXiv + Journal Submission (PRIORITY - START NOW)

**Goal**: Publish preprint on arXiv by June 1, 2026 + formal venue submission by July 1, 2026

**Timeline**: 3 weeks (May 15 - Jun 5, 2026)

---

### Phase 10.1: Manuscript Finalization (Week 1-2, May 15-29)

**Deliverables**: Publication-ready manuscript + figures

- [ ] Extract quantitative results from experiments
  - [ ] Run: `python examples/empirical_validation.py --mode full`
  - [ ] Collect all outputs to `results/`
  - [ ] Extract: mitigation_accuracy, experiment_scale, acceleration_metrics

- [ ] Generate publication-quality figures (5-7 total)
  - [ ] Figure 1: The Three Acceleration Loops (diagram)
  - [ ] Figure 2: Error Mitigation Loop acceleration dynamics (line plot)
  - [ ] Figure 3: Cross-loop coupling matrix (heatmap)
  - [ ] Figure 4: Bottleneck validation results (bar chart)
  - [ ] Table 1: Empirical results summary (acceleration_rate, bottleneck_type, recommendation)
  - [ ] Table 2: Hardware heterogeneity impact (loop_name, device, acceleration_rate, bottleneck)

- [ ] Write manuscript sections
  - [ ] Abstract (max 250 words) — state 3 main findings
  - [ ] Introduction (1 page) — motivation, problem, contributions
  - [ ] Related Work (1 page) — Singh 2025, AlphaQubit, GP-QML, position of RAF
  - [ ] Framework (2-3 pages) — loop formalization, metrics, coupling, bottlenecks
  - [ ] Empirical Validation (2-3 pages) — experimental setup, results by loop, cross-loop findings
  - [ ] Discussion (1-2 pages) — findings summary, limitations (simulation-only, 5-qubit scale), future work
  - [ ] Conclusion (0.5 page)
  - [ ] References (1 page) — verify all DOIs/URLs

- [ ] Format for submission
  - [ ] Choose format: IEEE 2-column OR NIPS format
  - [ ] Use Overleaf.com (free, no install) OR local LaTeX
  - [ ] Compile to PDF with all figures embedded
  - [ ] Page limit: 6-12 pages (depending on venue)

**Effort**: ~40 hours (writing) + 10 hours (figures) = 50 hours total

**Validation**:
```bash
# Verify empirical data is ready
python examples/empirical_validation.py --mode quick
# Manual check: all figures are high-res (300+ dpi)
# Manual check: all citations have DOIs
```

---

### Phase 10.2: arXiv Submission (Week 2, May 22-29)

**Deliverables**: Preprint on arXiv with public GitHub link

- [ ] Create arXiv account: https://arxiv.org/user/register
- [ ] Prepare arXiv submission package
  - [ ] `paper.pdf` (compiled, all figures embedded)
  - [ ] `source.tar.gz` (LaTeX source, figures, bib file)
  - [ ] Verify: No author names if anonymized (arXiv allows names for this)

- [ ] Select categories
  - [ ] Primary: cs.LG (Machine Learning)
  - [ ] Secondary: quant-ph (Quantum Physics)
  - [ ] Tertiary: cs.SY (Systems & Control)

- [ ] Submit to arXiv via https://arxiv.org/submit
  - [ ] Get arXiv ID (format: 2605.xxxxx)
  - [ ] Expected publication: 24-48 hours

- [ ] Post-publication
  - [ ] Update GitHub README.md with arXiv link
    ```markdown
    ## Preprint

    This work is available on arXiv: [arXiv:2605.xxxxx](https://arxiv.org/abs/2605.xxxxx)
    ```
  - [ ] Tweet/announce: "RAF paper available at arXiv:2605.xxxxx"
  - [ ] Share on Reddit r/quantum, r/MachineLearning, Quantum Computing Slack
  - [ ] Solicit feedback from quantum computing community

**Effort**: ~5 hours (formatting + upload)

**Timeline**: arXiv ID in hand by **June 1, 2026**

---

### Phase 10.3: Formal Journal Submission (Week 3-4, May 29 - Jun 12)

**Deliverables**: Submitted manuscript to Nature Machine Intelligence OR Quantum Science & Technology

#### 10.3.1 Nature Machine Intelligence (PRIMARY TARGET)

- [ ] Create author account at https://www.nature.com/natmachintell/
- [ ] Reformat as perspective piece (3-4k words)
  - [ ] Shorten to 3,500 words (perspective format)
  - [ ] Focus on "why this matters" over experimental details
  - [ ] Remove some empirical results, emphasize insights

- [ ] Write cover letter
  - [ ] 1-2 paragraphs explaining significance
  - [ ] Highlight: novel framework, multiple acceleration loops, cross-loop coupling
  - [ ] Mention arXiv preprint for full details

- [ ] Submit via https://www.nature.com/natmachintell/
  - [ ] Include: manuscript PDF, figures, author info, suggested reviewers
  - [ ] Expected review time: 2-3 months
  - [ ] Expected decision: **October-November 2026**

**Effort**: ~10 hours (reformat + cover letter)

#### 10.3.2 Backup: Quantum Science & Technology (if Nature rejects)

- [ ] Create author account at https://iopscience.iop.org/journal/2058-9565
- [ ] Keep full technical manuscript (6-8 pages)
- [ ] Write cover letter (same as Nature MI)
- [ ] Submit with same figures + tables
- [ ] Expected review time: 2-3 months
- [ ] Expected decision: **December 2026** (faster track available)

**Effort**: ~2 hours (already formatted)

---

### Phase 10.4: Conference Submission (Week 4, Jun 5-12)

**Deliverables**: Submitted manuscript to AAAI 2027

#### 10.4.1 AAAI 2027 (RECOMMENDED CONFERENCE)

- [ ] Create AAAI 2027 account (opens ~June 2026)
- [ ] Reformat as technical conference paper
  - [ ] Shorten to 8 pages + references
  - [ ] Focus on empirical validation results
  - [ ] Include all figures + tables

- [ ] Write cover letter
  - [ ] Position as "framework for understanding QC-ML acceleration"
  - [ ] Mention prior work (Singh 2025, etc.)
  - [ ] Highlight novelty: first empirical validation of cross-loop coupling

- [ ] Submit before deadline (assumed **August 15, 2026**)
  - [ ] Early submission (by June-July) may get faster review
  - [ ] Expected decision: **October-November 2026**

**Timeline**:
- Deadline: ~Aug 15, 2026
- Review period: Aug-Oct 2026
- Decision: Late October 2026
- Conference: Feb 2027

**Effort**: ~5 hours (reformat + cover letter)

---

### Phase 10.5: Parallel Actions (During Review)

**While waiting for responses (Jun-Oct 2026)**:

- [ ] GitHub engagement
  - [ ] Create GitHub Issues for extension ideas
  - [ ] Ask for Stars/citations in README
  - [ ] Welcome community contributions

- [ ] Community outreach
  - [ ] Post on quantum computing forums (Reddit, Slack, Discourse)
  - [ ] Link to arXiv preprint
  - [ ] Solicit feedback for revision

- [ ] Code improvements (if time allows)
  - [ ] Increase test coverage to 85%+
  - [ ] Complete Phase 9.4 (type hints modernization)
  - [ ] Add interactive dashboard for experiments

**Effort**: ~10 hours (optional, flexibility based on review feedback)

---

## Resource Requirements

### Accounts Needed (Choose One)

- [x] **Qiskit Aer** (default): No account needed - local simulation with device-calibrated noise models ✓ USING THIS
- [ ] **Azure Quantum**: $500 free credits, access to IonQ + Quantinuum (portal.azure.com) - deferred
- [ ] **AWS Braket**: Free credits for new users, access to IonQ + Rigetti (aws.amazon.com/braket) - deferred
- [ ] **IBM Quantum**: 10 min/month free tier (quantum.cloud.ibm.com) - login issues encountered

> **Note**: Simulation with device-calibrated noise models is scientifically valid and commonly
> accepted in quantum computing literature. Real hardware validation deferred to future work.

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

- [x] All three loops with simulation experiments
- [x] Cross-loop coupling validation
- [x] Validation with device-calibrated noise models (real hardware deferred)
- [x] Publication-quality figures

### Stretch (Nice to Have)

- [x] PennyLane integration
- [ ] Multiple hardware backends comparison (see Phase 8 below)
- [ ] Interactive dashboard for experiments
- [ ] Pre-trained surrogate models included

---

## Phase 8: Multi-Vendor Hardware Validation (DEFERRED - Future Work)

> **Status**: Deferred due to vendor account access issues. Current simulation-based
> validation is scientifically valid. Real hardware validation planned for future work.

### 8.1 Azure Quantum Setup (Deferred)

- [ ] Create Azure account and Quantum workspace
- [ ] Configure `azure-quantum` credentials
- [ ] Test connection with IonQ simulator

### 8.2 AWS Braket Setup (Deferred)

- [ ] Create AWS account with Braket access
- [ ] Configure AWS credentials
- [ ] Test connection with IonQ/Rigetti simulators

### 8.3 Cross-Vendor Validation Experiments (Deferred)

- [ ] Run Error Mitigation loop on IonQ (trapped-ion)
- [ ] Run Error Mitigation loop on Rigetti (superconducting)
- [ ] Compare acceleration dynamics across hardware types
- [ ] Measure hardware-specific bottleneck effects

### 8.4 Paper Enhancement (Deferred)

- [ ] Add Table: Cross-vendor acceleration comparison
- [ ] Add Figure: Hardware heterogeneity impact on loop dynamics
- [ ] Update Section V.D with real hardware results
- [ ] Strengthen "hardware-agnostic" claims with empirical evidence

---

## Revised Publication Timeline (Post-WCCI)

| Week | Dates | Focus | Deliverables |
|------|-------|-------|--------------|
| 1 | May 15-22 | Manuscript finalization | Draft + figures complete |
| 2 | May 22-29 | arXiv submission | Preprint online (arXiv ID obtained) |
| 3 | May 29-Jun 5 | Journal submission | Submitted to Nature MI + AAAI 2027 |
| 4-10 | Jun-Aug | Review phase | Community feedback on preprint |
| 11-14 | Aug-Oct | Revision phase | Address reviewer comments |
| 15+ | Oct-Dec 2026 | Publication | Expected acceptance + publication ✅ |

---

---

## Phase 9: Python & Dependency Modernization

**Goal**: Modernize RAF codebase to Python 3.12+ with updated dev tooling and dependencies.

**Timeline**: 6 weeks (distributed, ~14 hours of work)

**Target**: Improve code quality, maintainability, type safety, and align with current ecosystem.

---

### Phase 9.1: Foundation (Python Version & Build System)

- [x] Update `pyproject.toml` `requires-python` from `>=3.9` to `>=3.12,<4.0`
- [x] Update setuptools to `>=72.0` in `[build-system]` section
- [x] Add `py.typed` marker file to `/raf/py.typed`
- [x] Update Python version classifiers (remove 3.9-3.11, add 3.12-3.13)
- [x] Update Python version badge in README.md from 3.9+ to 3.12+
- [x] Remove `from __future__ import annotations` compatibility from files (no longer needed with 3.12+)

**Validation**:

```bash
# Using uv (recommended)
uv sync
python -c "import sys; assert sys.version_info >= (3, 12)"

# Or using pip
python -c "import sys; assert sys.version_info >= (3, 12)" && pip install -e .
```

---

### Phase 9.2: Development Tools Modernization

#### 9.2.1 Pre-commit Hooks

- [ ] Update `pre-commit-hooks` rev from `v4.5.0` to `v4.6.0`
- [ ] Update `black` rev from `24.3.0` to `24.4.0`
- [ ] Update `isort` rev from `5.13.2` to `5.13.2` (already latest, keep as-is)
- [ ] Update `ruff` rev from `v0.3.4` to `v0.5.0+`
- [ ] Add `ruff-format` hook (native formatter introduced in ruff 0.4+)
- [ ] Add `mypy` pre-commit hook with `v1.11.0`
- [ ] Update Python version targets in hooks from `python3` to `python3.12`

#### 9.2.2 pyproject.toml Tool Configuration

- [ ] Update `[tool.black]` target-version from `['py39', 'py310', 'py311', 'py312']` to `['py312', 'py313']`
- [ ] Update `[tool.isort]` to add `py_version = "312"`
- [ ] Update `[tool.ruff]` target-version from `"py39"` to `"py312"`
- [ ] Add comprehensive `[tool.ruff.lint]` configuration (E, W, F, I, C4, B, UP, ARG, SIM, PERF rules)
- [ ] Update `[tool.mypy]` python_version from `"3.9"` to `"3.12"`
- [ ] Add strict mypy settings: `disallow_untyped_defs`, `disallow_incomplete_defs`, `check_untyped_defs`, `no_implicit_optional`
- [ ] Update `[tool.pytest.ini_options]` to add `minversion = "8.0"` and coverage reports
- [ ] Run `pre-commit run --all-files` to validate all changes

**Validation**:

```bash
# Using uv (recommended)
uv run pre-commit run --all-files
uv run pytest tests/
uv run mypy raf/

# Or with pip (tools already installed)
pre-commit run --all-files && pytest tests/ && mypy raf/
```

---

### Phase 9.3: Core Dependencies Update

#### 9.3.1 Scientific Stack

- [ ] Update `numpy>=1.21.0` → `>=1.26.0`
- [ ] Update `scipy>=1.7.0` → `>=1.14.0`
- [ ] Update `matplotlib>=3.5.0` → `>=3.8.0`
- [ ] Update `pandas>=1.3.0` → `>=2.2.0`
- [ ] Update `networkx>=2.6.0` → `>=3.3`
- [ ] Update `pydantic>=2.0.0` → `>=2.7.0` (already modern, just latest)
- [ ] Update `rich>=12.0.0` → `>=13.7.0`

#### 9.3.2 Quantum Backend Dependencies

- [ ] Update `qiskit-aer~=0.17.1` → `~=0.18` (under existing qiskit>=2.0,<2.2 constraint)

#### 9.3.3 Development Dependencies

- [ ] Update `pytest>=7.0.0` → `>=8.0.0`
- [ ] Update `pytest-cov>=4.0.0` → `>=5.0.0`
- [ ] Update `black>=23.0.0` → `>=24.4.0`
- [ ] Update `isort>=5.12.0` → `>=5.13.2`
- [ ] Update `mypy>=1.0.0` → `>=1.11.0`
- [ ] Update `ruff>=0.1.0` → `>=0.5.0`
- [ ] Add `mypy[reports]` for coverage integration

#### 9.3.4 Documentation Dependencies

- [ ] Update `sphinx>=6.0.0` → `>=7.2.0`
- [ ] Update `sphinx-rtd-theme>=1.2.0` → `>=2.0.0`
- [ ] Update `myst-parser>=1.0.0` → `>=2.0.0`

**Testing Strategy** (per-group):

```bash
# Using uv (recommended)
uv sync --extras quantum,dev
pytest tests/ -v

# Validate pandas migration (watch for deprecated API usage)
pytest tests/ -v

# Validate documentation build
uv sync --extras docs
uv run sphinx-build docs/ build/

# Or using pip
pip install "numpy>=1.26" "scipy>=1.14" && pytest tests/ -v
pip install "pandas>=2.2" && pytest tests/ -v
pip install -e ".[docs]" && sphinx-build docs/ build/
```

---

### Phase 9.4: Type Hints Modernization

#### 9.4.1 Syntax Updates

- [ ] Review critical files for `typing.Dict`/`typing.List` usage:
  - [ ] `/raf/core/metrics.py` - Replace type imports with built-in generics
  - [ ] `/raf/core/loop.py` - Update base class type hints
  - [ ] `/raf/backends/base.py` - Update abstract interface types
  - [ ] `/raf/experiments/*.py` - Update experimental code types
- [ ] Replace `Dict[K, V]` → `dict[K, V]`
- [ ] Replace `List[T]` → `list[T]`
- [ ] Replace `Optional[T]` → `T | None`
- [ ] Replace `Union[A, B]` → `A | B`

#### 9.4.2 Type Aliases & Advanced Patterns

- [ ] Create `/raf/types.py` with common type aliases:
  ```python
  LoopMetrics: TypeAlias = dict[str, AccelerationMetric]
  BottleneckMap: TypeAlias = dict[str, list[BottleneckIndicator]]
  ```
- [ ] Use `TypedDict` for configuration dataclasses in `/raf/utils/config.py`
- [ ] Add `@dataclass` modernization where applicable (use `slots=True` for memory efficiency)

#### 9.4.3 Type Checking

- [ ] Run `mypy raf/ --strict` and fix any errors
- [ ] Run `ruff check raf/ --select UP` to find remaining type issues
- [ ] Ensure all public functions have return type annotations

**Validation**:

```bash
# Using uv (recommended)
uv run mypy raf/ --strict
uv run ruff check raf/ --select UP

# Or with pip (tools already installed)
mypy raf/ --strict && ruff check raf/ --select UP
```

---

### Phase 9.5: Testing & Fixture Modernization

#### 9.5.1 pytest 8.0+ Patterns

- [ ] Create/update `/tests/conftest.py`:
  - [ ] Add RAF framework fixture with proper setup/teardown
  - [ ] Add parametrize fixtures for loop testing
  - [ ] Add backend fixture that lists available backends
- [ ] Update test parametrization to use `ids` for better test names
- [ ] Add `pytest.mark.parametrize` with enums/constants instead of magic strings
- [ ] Use new pytest 8.0 fixture scoping improvements

#### 9.5.2 Coverage Enhancement

- [ ] Add coverage thresholds to pytest config: `fail_under = 85`
- [ ] Add `[tool.coverage.run]` config with `branch = true`
- [ ] Generate coverage HTML reports: `pytest --cov --cov-report=html`
- [ ] Target: Maintain >=85% code coverage

#### 9.5.3 Test Expansion

- [ ] Add type checking tests: verify mypy passes on examples
- [ ] Add import tests: verify all public APIs are importable
- [ ] Add deprecation warnings test (if any old APIs exist)

**Validation**:

```bash
# Using uv (recommended)
uv run pytest tests/ -v --cov=raf --cov-report=term-missing --cov-report=html
uv run coverage report --fail-under=85

# Or with pip (tools already installed)
pytest tests/ -v --cov=raf --cov-report=term-missing --cov-report=html
coverage report --fail-under=85
```

---

### Phase 9.6: Project Metadata & Documentation

#### 9.6.1 README Updates

- [ ] Replace `https://github.com/yourusername/RAF` with actual repository URL
- [ ] Replace `https://raf.readthedocs.io` with actual docs URL (or remove if not applicable)
- [ ] Update Python version badge: `3.9+` → `3.12+`
- [ ] Add "Modernization 2026" section to changelog if applicable

#### 9.6.2 Classifier Updates

- [ ] Update classifiers in `pyproject.toml`:
  - [ ] Add `"Operating System :: OS Independent"`
  - [ ] Add `"Programming Language :: Python :: 3 :: Only"`
  - [ ] Add `"Typing :: Typed"`
  - [ ] Remove Python 3.9-3.11 classifiers
  - [ ] Add Python 3.12, 3.13 classifiers

#### 9.6.3 CONTRIBUTING.md Update (if exists)

- [ ] Update development setup to reference Python 3.12+
- [ ] Update code quality section to reference ruff v0.5+ and mypy strict mode
- [ ] Add note about type hint expectations

**Validation**:

```bash
# Using uv (recommended)
uv build --sdist
tar -tzf dist/raf-*.tar.gz | head -20

# Or using pip
python -m build --sdist && tar -tzf dist/raf-*.tar.gz | head -20
```

---

## Implementation Order & Risk Assessment

| Phase            | Risk       | Effort  | Validation Time | Dependencies |
| ---------------- | ---------- | ------- | --------------- | ------------ |
| 9.1 Foundation   | None       | 30 min  | 5 min           | None         |
| 9.2 Dev Tools    | Low        | 1.5 hrs | 10 min          | 9.1          |
| 9.3 Dependencies | Medium     | 3 hrs   | 30 min          | 9.1, 9.2     |
| 9.4 Type Hints   | Low-Medium | 2.5 hrs | 15 min          | 9.2, 9.3     |
| 9.5 Testing      | Low        | 2 hrs   | 20 min          | 9.2, 9.3     |
| 9.6 Metadata     | None       | 1 hr    | 5 min           | All above    |

**Total Effort**: ~14 hours of development + 1.5 hours of testing

**Recommended Sequence**:

1. Start with Phase 9.1 (foundation) — zero risk, sets stage
2. Complete Phase 9.2 (dev tools) — validates linting before major changes
3. Run Phase 9.3 (dependencies) incrementally with testing between groups
4. Proceed with 9.4-9.6 (type hints, testing, metadata)

---

## Validation Checklist

- [ ] `requires-python` in pyproject.toml updated
- [ ] `pre-commit run --all-files` passes with zero errors
- [ ] `pytest tests/ -v --cov` shows >=85% coverage
- [ ] `mypy raf/ --strict` passes
- [ ] `ruff check raf/` passes
- [ ] `black --check raf/` passes (already validated by pre-commit)
- [ ] All quantum backend examples still work:
  - [ ] `python examples/basic_usage.py`
  - [ ] `python examples/empirical_validation.py --mode quick`
- [ ] Documentation builds without warnings: `sphinx-build docs/ build/`
- [ ] Quantum backends still available:
  - [ ] `raf.backends.list_available_backends()` includes at least Aer
  - [ ] Optional backends (braket, azure) gracefully skip if not installed

---

## Notes

- **Qiskit 2.x Compatibility**: All changes maintain compatibility with existing qiskit 2.0-2.2 constraints
- **Separate venvs** (IBM Quantum, IQM) are unaffected by Python 3.12 upgrade
- **No Breaking Changes**: All updates are backward-compatible within Python 3.12+
- **Pre-commit**: First run after Phase 9.2 will auto-fix many issues (black, isort, ruff); review diff carefully
- **Type Hints**: Modernization is gradual; mypy strict mode catches real bugs (not just style)
- **Testing**: Coverage thresholds prevent regressions in undervalidated code paths

---

## Timeline Summary: arXiv + Multi-Venue Strategy

**Immediate Priority** (Weeks 1-2):
- Finalize manuscript with empirical results
- Generate publication-quality figures
- Submit to arXiv by June 1, 2026

**Secondary Priority** (Week 3):
- Prepare journal submission (Nature MI perspective)
- Prepare conference submission (AAAI 2027)
- Both in parallel for coverage

**Expected Publication** (Q4 2026):
- arXiv preprint: June 2026 ✅
- Nature MI/journal decision: Oct-Dec 2026
- AAAI 2027 decision: Oct-Nov 2026
- Formal publication: **Dec 2026 or Q1 2027**

---

## Critical Path Dependencies

```
Phase 10.1 (Manuscript)
    ↓
Phase 10.2 (arXiv) ← MILESTONE: June 1, 2026
    ↓
Phase 10.3 (Journal) ← MILESTONE: July 1, 2026
    ↓
Phase 10.4 (Conference) ← MILESTONE: Aug 15, 2026
    ↓
Review & Revision (Aug-Oct 2026)
    ↓
Publication (Oct-Dec 2026) ✅
```

---

## Notes

- **arXiv first**: Stamps priority, allows parallel submissions
- **Parallel venues**: Nature MI (primary) + AAAI 2027 (conference backup) maximizes coverage
- **Simulation is valid**: Device-calibrated noise accepted at top venues; real hardware as future work
- **Test coverage critical**: Ensure 85%+ before final submission
- **Community feedback**: Use arXiv comments to improve before journal review
- **Documentation**: Phase 10.5 includes code improvements during review phase
