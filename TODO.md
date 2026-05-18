# RAF Project TODO

<!--

CHANGELOG (most recent first)
Historical version content is preserved in HTML comments throughout this
document, co-located with the active version of each section.
============================================================
v4 (2026-05-17 PM): Coherence pass — code-first sequencing made explicit
(Stage 1 codebase completion before Stage 2 meta-prep before Stage 3 paper
drafting). Backend currency audit incorporated as Phase 10.1 Stage A.
Zenodo deposit removed from active plan (v2-era arXiv-substitute, not
needed for JOSS DOI). Quantum backend availability audited against May
2026 reality (IBM Brisbane/Kyoto/Osaka retired; Braket dropped OQC, added
IQM/AQT; Azure added Atom Computing; IonQ Harmony / Quantinuum H1
retirements reflected). Historical version content moved into HTML
comments; only latest decision visible in rendered view.
v3 (2026-05-17 PM): Positioning pivot to "open-source reference implementation
of QC-ML co-evolutionary frameworks (Singh 2025, Shukla 2025, Maes 2025)."
Venue: JOSS only. Singh demoted from primary Related Work to "Concurrent
and recent work" subsection (low-quality OA journal). Phase 11.2 Path B
sufficient for JOSS; Path A (real CDR) deferred to v0.3.0.
v2 (2026-05-17 AM): Prior-art reckoning (Maes 2025 Zenodo, Shukla 2025
TechRxiv, Alexeev 2025 Nat Commun, Acampora 2025 arXiv:2505.23860).
Methodology blockers identified (oracle-access mitigation, hardcoded
coupling, test coverage). NeurIPS workshops considered as venue.
v1 (Jan 2026): arXiv + Nature MI + AAAI 2027 plan. Blocked by arXiv
endorsement policy update (Jan 21, 2026; institutional email no longer
sufficient alone).
v0 (Dec 2025): IEEE WCCI 2026 deadline missed.
============================================================
-->

## Active Goal & Timeline

**Goal**: Submit RAF to the Journal of Open Source Software (JOSS) as an open-source reference implementation of QC-ML co-evolutionary frameworks (Singh 2025, Shukla 2025, Maes 2025).

**Timeline**: ~3-4 months (May 17, 2026 → JOSS submission ~Aug 28, 2026 → DOI assigned Sep-Oct 2026).

See Status and Execution Order below.

<!--
HISTORICAL: Goal v0 (Dec 2025, SUPERSEDED)
==========================================
Goal: Transform RAF from a conceptual framework to an empirically-grounded paper suitable for IEEE WCCI 2026.
Timeline: 2 weeks (Target completion: Dec 19, 2025)
Supersession chain: v0 → v1 (arXiv + Nature MI + AAAI 2027) → v2 (NeurIPS workshops) → v3 (JOSS) → v4 (JOSS, re-sequenced for code-first).
-->

---

## Status

**Positioning**: RAF is an open-source Python reference implementation of QC-ML co-evolutionary frameworks already established in the literature. The conceptual phase of this subfield is closing (Singh, Shukla, Maes, Alexeev, Acampora all converging in 2025); the implementation phase is opening. RAF fills that gap by providing runnable Python code, explicit coupling parameters exposed as config, and multi-backend abstraction. No novel framework claim is made — RAF makes existing frameworks testable.

**Venue**: JOSS (Journal of Open Source Software). Single-venue strategy. Conference workshops (IEEE QCE 2027, NeurIPS 2027) deferred until after JOSS acceptance.

**Methodology blockers** (must address before JOSS submission):

1. `raf/experiments/error_mitigation.py` `_simulate_mitigation` uses ideal expectation as oracle access. Not ML-QEM — simulated idealized mitigation. **Fix**: Phase 11.2 Path B — rename to `_simulated_idealized_mitigation` with honest docstring. Path A (real CDR) deferred to v0.3.0.
2. `raf/experiments/cross_loop_validation.py` hardcodes coupling factors. **Fix**: Phase 11.1 — expose as `assumed_coupling_strength` config. Under reference-implementation framing this is a core feature, not damage control.
3. Test coverage ~6.4% (~820/12,884 lines). **Fix**: Phase 11.3 — raise to 40%+ (JOSS criterion).
4. `raf/backends/*` modules reference retired devices. **Fix**: Phase 10.1 Stage A — backend currency audit (IBM Brisbane/Kyoto/Osaka retired 2024-2025; IonQ Harmony retired 2024; Quantinuum H1 retirement notice July 2025; OQC removed from Braket June 2024).

**Singh citation status**: Kept in citation block with DOI 10.63721/25JPAIR0118 added, but demoted from primary Related Work to "Concurrent and recent work" subsection. The journal shows hallmarks of low-quality OA (3-day submission-to-acceptance, broken citation chains where in-text refs go to [97]/[171] but reference list ends at [74], unverified "500+ problem validation" claim). Singh's contribution is a _decision_ framework (whether to use quantum), orthogonal to RAF's _implementation_ of _dynamics_ frameworks.

<!--
HISTORICAL STATUS BLOCKS (preserved for traceability)
=====================================================

== Status v2 (2026-05-17 AM) ==

Pivot rationale: Prior-art reckoning revealed that the QC-ML feedback-loop framing is now shared territory rather than novel:
- Maes (May 2025) — Adaptive Co-Design of QML and QEC via RL (Zenodo DOI 10.5281/zenodo.15428357) has priority on the closed feedback-loop architecture between QML ansatz and error management.
- Shukla (Dec 2025) — Co-Evolutionary Co-Design Framework (TechRxiv DOI 10.36227/techrxiv.176704915.54945198/v1) has priority on the three-layer (hardware/algorithmic/application) co-evolutionary framing, though conceptual rather than operational.
- Alexeev et al. (Dec 2025) — Nature Communications review on "AI for quantum computing" (DOI 10.1038/s41467-025-65836-3) is the authoritative review of the field.
- Acampora et al. (May 2025) — Quantum Community Network white paper (arXiv:2505.23860) establishes the long-term research agenda.

Remaining novelty for RAF (carried into v3 as positioning): (a) functional task-based decomposition (Error Mitigation × Ansatz × Calibration-Control) versus stack-layer decomposition; (b) explicit coupling parameters enabling structural sensitivity studies; (c) open-source runnable implementation (none of the above prior art has code).

Venue pivot v1→v2: arXiv access blocked by Jan 2026 endorsement policy update (institutional email no longer sufficient alone; no prior arXiv authorship). Nature MI and AAAI 2027 premature given methodology state. NeurIPS 2026 workshops chosen (likely ML4PS or similar; CFPs ~Aug-Sep 2026, deadlines ~Sep-Oct 2026).

Methodology blockers identified (all carried into v3/v4):
1. raf/experiments/error_mitigation.py uses ideal expectation as oracle access. Not ML-QEM; simulated idealized mitigation. The 1.86× acceleration figure is an artifact of the deterministic schedule.
2. raf/experiments/cross_loop_validation.py hardcodes coupling factors. The cross-correlation analysis "measures" precisely what was inserted.
3. Test coverage ~6.4% — below publication threshold.

Phase 10 v1 superseded by Phase 10 v2 + Phase 11. Phase 10 v1 content preserved verbatim for traceability.

== Status v3 (2026-05-17 PM, addendum to v2) ==

Positioning pivot: After review of the Singh (2025) framework paper, recognized that RAF's strongest position is as a *reference implementation* of QC-ML co-evolutionary frameworks already well-established in the literature, rather than as a competing framework. This eliminates the differentiation argument — RAF no longer needs to argue against prior work, only to honestly implement what prior work described.

Venue change v2→v3: JOSS (Journal of Open Source Software) becomes the primary target. JOSS accepts open-source software with novel research value; review criteria focus on usability, documentation, and tests rather than empirical novelty claims. JOSS papers are short (250-1000 words) summary papers. Fast review cycle (typically 4-8 weeks), peer-reviewed, real DOI (10.21105/joss.NNNNN), indexed in CrossRef. Single-venue strategy: JOSS only.

Methodology blockers re-prioritized under reference-implementation framing:
- Phase 11.1 (rename hardcoded coupling factors to assumed_coupling_strength config) becomes the *core feature* of the reference implementation, not damage control. Highest priority.
- Phase 11.2 (real CDR mitigation) demoted to v0.3.0 goal, not a JOSS prerequisite. Phase 11.2 Path B (honest rename) sufficient for JOSS.
- Phase 11.3 (test coverage 40%+) still required (JOSS criterion).
- Phase 11.4 (reproducibility hardening) still required (JOSS reviewers run software).

Singh demoted to concurrent work (per Option B agreed in conversation): Verified the Singh (2025) paper exists with DOI 10.63721/25JPAIR0118, but journal shows hallmarks of low-quality OA publishing. Singh's actual contribution is a *decision* framework (whether to use quantum), orthogonal to RAF's *implementation* of *dynamics* frameworks. Moves from primary Related Work to Concurrent and recent work in README v3.

== Status v4 (2026-05-17 PM, factual-correction addendum to v3) ==

Backend availability audit performed: README "Supported Quantum Backends" section was verified against May 2026 cloud provider reality. Five concrete factual errors discovered and corrected in README v4 (see README v4 changelog comment for full diff):
- IBM Quantum row listed Brisbane, Kyoto, Osaka — all three retired (Aug 2024, Aug 2024, Nov 2025). Current fleet is Heron r1/r2/r3 (ibm_aachen, ibm_boston, ibm_torino) and Nighthawk (ibm_miami).
- AWS Braket row listed OQC — access ended June 2024. Current Braket QPU providers: AQT, IonQ, IQM, QuEra, Rigetti.
- Azure Quantum row was missing Atom Computing.
- IQM row understated — Emerald (54-qubit, July 2025) joins Garnet (20-qubit).
- Three code examples used retired/invalid device strings: ionq_harmony (retired 2024), quantinuum.qpu.h1-1 (H1 retirement notice July 2025), IQMBackend("resonance") (platform name, not device).

Implication for Phase 10 v3: README accurate, but raf/backends/ code modules not yet verified against corrected device strings. New checklist items added to Phase 10 v3 .1 ("Backend currency audit") to track parallel code-side work. These items become JOSS-submission prerequisites.

Open decision flagged for docs/SCIENTIFIC_REVIEW.md: keep `ionq` noise profile as "IonQ Harmony-like" (well-characterized historical baseline) or update to Forte-1-like (current generation, ~36 #AQ).

No strategic pivot: v4 is factual correction only. Active goal (JOSS submission), positioning (reference implementation), and Phase 11 priorities unchanged from v3.
-->

---

## Execution Order

The active plan is **strictly linear**: codebase complete first, paper drafted second. Verifications against incomplete code are not honest verifications.

```
STAGE 1 — CODEBASE COMPLETION  (May 17 → ~July 31, 2026, ~10 weeks)
    ├── Phase 11.1  Coupling as core feature (`assumed_coupling_strength`)
    ├── Phase 11.2 Path B  Honest rename of oracle-access mitigation
    ├── Phase 11.3  Test coverage 40%+ (JOSS criterion)
    ├── Phase 11.4  Reproducibility hardening (JOSS criterion)
    └── Phase 10.1 Stage A  Backend currency audit (raf/backends/*)
                ↓
                ↓ ┌─ GATE: every Stage-1 box ticked, CI green, fresh-container reproduction passes ─┐
                ↓ └────────────────────────────────────────────────────────────────────────────────┘
                ↓
STAGE 2 — JOSS META-PREP & VERIFICATIONS  (~2-3 weeks)
    └── Phase 10.1 Stage B  License, version tag, ORCID, statement of need,
                             install/example/API/test/CI verifications,
                             community guidelines, issue templates, benchmarks
                ↓
                ↓ ┌─ GATE: repo meets all JOSS submission criteria ────────────────────────────────┐
                ↓ └────────────────────────────────────────────────────────────────────────────────┘
                ↓
STAGE 3 — PAPER DRAFTING  (~1-2 weeks)
    └── Phase 10.2  paper.md + paper.bib (250-1000 words, JOSS format)
                ↓
STAGE 4 — SUBMISSION  (1 week)
    └── Phase 10.3  Submit via joss.theoj.org/papers/new
                ↓
STAGE 5 — REVIEW RESPONSE  (4-8 weeks)
    └── Phase 10.4  Respond to reviewer issues in GitHub thread
                ↓
STAGE 6 — POST-ACCEPTANCE  (ongoing, optional)
    └── Phase 10.5  Workshop expansion, v0.3.0 development (real CDR, Phase 11.2 Path A)
```

**Load-bearing rule**: Stage 3 (paper drafting) does **not** begin before Stage 1 (codebase) is complete. Paper text that describes what the code does is wasted effort if the code is going to change. Statement of Need can be partially sketched during Stage 1 because the framing is positioning-driven, not code-state-driven; but the rest of paper.md waits for working code.

**What "Stage 1 complete" means concretely**:

- `pytest --cov=raf --cov-fail-under=40` passes on a fresh container.
- `examples/empirical_validation.py --mode quick` runs end-to-end and produces reproducible output (Phase 11.4 `REPRODUCIBILITY.md` validated).
- All `raf/backends/*` modules accept the device strings shown in README (or README is updated to match what the code accepts — either direction is fine, but they must agree).
- `_simulate_mitigation` renamed to `_simulated_idealized_mitigation` with honest docstring (Phase 11.2 Path B).
- All coupling factors exposed as `assumed_coupling_strength` config (Phase 11.1).

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

**New Path**: Phase 10 (JOSS submission). See active plan below.

---

## Phase 8: Multi-Vendor Hardware Validation (DEFERRED - Future Work)

> **Status**: Deferred due to vendor account access issues. Current simulation-based validation is scientifically valid. Real hardware validation planned for future work.

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

- [x] Update `pre-commit-hooks` rev from `v4.5.0` to `v4.6.0`
- [x] Update `black` rev from `24.3.0` to `24.4.0`
- [x] Update `isort` rev from `5.13.2` to `5.13.2` (already latest, keep as-is)
- [x] Update `ruff` rev from `v0.3.4` to `v0.5.0+`
- [x] Add `ruff-format` hook (native formatter introduced in ruff 0.4+)
- [x] Add `mypy` pre-commit hook with `v1.11.0`
- [x] Update Python version targets in hooks from `python3` to `python3.12`

#### 9.2.2 pyproject.toml Tool Configuration

- [x] Update `[tool.black]` target-version from `['py39', 'py310', 'py311', 'py312']` to `['py312', 'py313']`
- [x] Update `[tool.isort]` to add `py_version = "312"`
- [x] Update `[tool.ruff]` target-version from `"py39"` to `"py312"`
- [x] Add comprehensive `[tool.ruff.lint]` configuration (E, W, F, I, C4, B, UP, ARG, SIM, PERF rules)
- [x] Update `[tool.mypy]` python_version from `"3.9"` to `"3.12"`
- [x] Add strict mypy settings: `disallow_untyped_defs`, `disallow_incomplete_defs`, `check_untyped_defs`, `no_implicit_optional`
- [x] Update `[tool.pytest.ini_options]` to add `minversion = "8.0"` and coverage reports
- [x] Run `pre-commit run --all-files` to validate all changes

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

- [x] Update `numpy>=1.21.0` → `>=1.26.0`
- [x] Update `scipy>=1.7.0` → `>=1.14.0`
- [x] Update `matplotlib >=3.5.0` → `>=    ?` → `>=3.8.0`
- [x] Update `pandas>=1.3.0` → `>=2.2.0`
- [x] Update `networkx>=2.6.0` → `>=3.3`
- [x] Update `pydantic>=2.0.0` → `>=2.7.0` (already modern, just latest)
- [x] Update `rich>=12.0.0` → `>=13.7.0`

#### 9.3.2 Quantum Backend Dependencies

- [x] Update `qiskit-aer~=0.17.1` → `~=0.17.2` (under existing qiskit>=2.0,<2.2 constraint)

#### 9.3.3 Development Dependencies

- [x] Update `pytest>=7.0.0` → `>=8.0.0`
- [x] Update `pytest-cov>=4.0.0` → `>=5.0.0`
- [x] Update `black>=23.0.0` → `>=24.4.0`
- [x] Update `isort>=5.12.0` → `>=5.13.2`
- [x] Update `mypy>=1.0.0` → `>=1.11.0`
- [x] Update `ruff>=0.1.0` → `>=0.5.0`
- [x] Add `mypy[reports]` for coverage integration

#### 9.3.4 Documentation Dependencies

- [x] Update `sphinx>=6.0.0` → `>=7.2.0`
- [x] Update `sphinx-rtd-theme>=1.2.0` → `>=2.0.0`
- [x] Update `myst.txt`?

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

- [x] Review critical files for `typing.Dict`/`typing.List` usage:
  - [x] `/raf/core/metrics.py` - Replace type imports with built-in generics
  - [x] `/raf/core/loop.py` - Update base class type hints
  - [x] `/raf/backends/base.py` - Update abstract interface types
  - [x] `/raf/experiments/*.py` - Update experimental code types
- [x] Replace `Dict[K, V]` → `dict[K, V]`
- [x] Replace `List[T]` → `list[T]`
- [x] Replace `Optional[T]` → `T | None`
- [x] Replace `Union[A, B]` → `A | B`

#### 9.4.2 Type Aliases & Advanced Patterns

- [x] Create `/raf/types.py` with common type aliases:
  ```python
  LoopMetrics: TypeAlias = dict[str, AccelerationMetric]
  BottleneckMap: TypeAlias = dict[str, list[BottleneckIndicator]]
  ```
- [x] Use `TypedDict` for configuration dataclasses in `/raf/utils/config.py`
- [x] Add `@dataclass` modernization where applicable (use `slots=True` for memory efficiency)

#### 9.4.3 Type Checking

- [x] Run `mypy raf/ --strict` and fix any errors
- [x] Run `ruff check raf/ --select UP` to find remaining type issues
- [x] Ensure all public functions have return type annotations

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

### Phase 9 Implementation Order & Risk Assessment

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

### Phase 9 Validation Checklist

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

### Phase 9 Implementation Notes

- **Qiskit 2.x Compatibility**: All changes maintain compatibility with existing qiskit 2.0-2.2 constraints
- **Separate venvs** (IBM Quantum, IQM) are unaffected by Python 3.12 upgrade
- **No Breaking Changes**: All updates are backward-compatible within Python 3.12+
- **Pre-commit**: First run after Phase 9.2 will auto-fix many issues (black, isort, ruff); review diff carefully
- **Type Hints**: Modernization is gradual; mypy strict mode catches real bugs (not just style)
- **Testing**: Coverage thresholds prevent regressions in undervalidated code paths

---

## Phase 10: JOSS Submission Target

<!--
HISTORICAL PHASE 10 PLANS (preserved for traceability)
======================================================

== Phase 10 v1 (Jan 2026, SUPERSEDED): arXiv + Journal Submission ==

Goal: Publish preprint on arXiv by June 1, 2026 + formal venue submission by July 1, 2026.
Timeline: 3 weeks (May 15 - Jun 5, 2026).

Phase 10.1: Manuscript Finalization (Week 1-2, May 15-29)
- Extract quantitative results from experiments (python examples/empirical_validation.py --mode full)
- Generate publication-quality figures (5-7 total): three-loop diagram, error mitigation acceleration dynamics, cross-loop coupling heatmap, bottleneck validation bars, empirical results summary table, hardware heterogeneity impact table
- Write manuscript sections (abstract ≤250 words, introduction 1 page, related work 1 page, framework 2-3 pages, empirical validation 2-3 pages, discussion 1-2 pages, conclusion 0.5 page, references 1 page)
- Format for submission (IEEE 2-column OR NIPS format, Overleaf compile, 6-12 pages)
Effort: ~50 hours total.

Phase 10.2: arXiv Submission (Week 2, May 22-29) — BLOCKED by arXiv endorsement policy update Jan 21, 2026
- Create arXiv account, prepare submission package (paper.pdf + source.tar.gz)
- Categories: cs.LG primary, quant-ph secondary, cs.SY tertiary
- Submit via arxiv.org/submit, get arXiv ID 2605.xxxxx
- Post-publication: update README, social announce, solicit feedback
Effort: ~5 hours. Timeline target: arXiv ID by June 1, 2026.

Phase 10.3: Formal Journal Submission (Week 3-4, May 29 - Jun 12)
- Phase 10.3.1: Nature Machine Intelligence (PRIMARY) — perspective piece 3,500 words, cover letter, expected decision Oct-Nov 2026
- Phase 10.3.2: Backup Quantum Science & Technology — full technical manuscript 6-8 pages
Effort: ~12 hours.

Phase 10.4: Conference Submission (Week 4, Jun 5-12) — AAAI 2027
- Reformat as 8-page conference paper, cover letter, submit before ~Aug 15 2026 deadline
- Expected decision Late October 2026, conference Feb 2027
Effort: ~5 hours.

Phase 10.5: Parallel Actions (Jun-Oct 2026) — community outreach, code improvements during review
Effort: ~10 hours.

Supersession: arXiv access blocked, Nature MI/AAAI 2027 premature given methodology state. Replaced by Phase 10 v2 (NeurIPS workshops) + Phase 11 (methodology fixes).

== Phase 10 v2 (May 2026 AM, SUPERSEDED): NeurIPS 2026 Workshops Target ==

Goal: Submit to NeurIPS 2026 workshop (likely ML4PS) by ~Oct 10, 2026.
Timeline: ~5 months (May 17, 2026 → Oct 10, 2026).
Sequencing: Phase 11 (methodology fixes) is a prerequisite. ~6-10 weeks code + 4-6 weeks drafting fits 5-month window.

Phase 10 v2 .1: CFP Monitoring & Venue Selection (June-August 2026)
- Watch ML4PS website, NeurIPS 2026 workshops list, AI4Science, Quantum ML workshops
- Backup: AAAI 2027 workshops, ICLR 2027 workshops
- Decision deadline: select target workshop by Sep 1, 2026.

Phase 10 v2 .2: Manuscript Drafting (August-September 2026)
- Workshop format (4-pg, 6-pg, or 9-pg variants)
- Abstract ~150-200 words: operational three-loop structural model with explicit coupling parameters
- Sections: §1 Introduction with explicit Maes/Shukla/Alexeev/Acampora citations, §2 Related Work positioning, §3 Framework, §4 Simulated Dynamics under Assumed Coupling (HONEST reframing), §5 Discussion & Limitations, §6 Conclusion & Future Work

Phase 10 v2 .3: Zenodo Deposit as Priority Substitute (~Sept 2026)
- Confirm Zenodo deposit policy with GitHub integration
- Tag v0.2.0-preprint, trigger Zenodo deposit, record DOI
- Reference DOI in workshop submission cover letter

Phase 10 v2 .4: Workshop Submission (Sep-Oct 2026)
- Reformat to NeurIPS LaTeX style, submit via OpenReview before deadline
- Expected decision ~Nov 2026; if accepted, prepare camera-ready, plan Dec 2026 attendance

Supersession: Positioning pivot to reference implementation makes JOSS a stronger venue match than NeurIPS workshops. JOSS reviewers explicitly evaluate open-source software with research value; non-archival workshops still require framework-novelty claims that RAF doesn't make under v3 framing. Replaced by Phase 10 v3 (renamed Phase 10 below).
-->

**Goal**: Submit RAF to the Journal of Open Source Software (JOSS) as an open-source reference implementation. Single-venue strategy: fast, clean, low-risk. Conference workshops deferred until after JOSS acceptance.

**Why JOSS**: JOSS publishes short summary papers about scholarly open-source software. Review criteria are explicit and software-focused: license, installation, examples, automated tests, community guidelines, documentation, statement of need. There is no empirical-novelty pressure — implementation papers about established frameworks are exactly the type of contribution JOSS exists to recognize. Fast review cycle (typically 4-8 weeks), peer-reviewed, real DOI (`10.21105/joss.NNNNN`), indexed in CrossRef. JOSS reviewers run the software, so reproducibility and tests are the actual quality gates.

**Timeline**: ~3-4 months (May 17, 2026 → Aug-Sep 2026 submission window). Phase 11 (methodology fixes) is a prerequisite for the code-side checklist items.

---

### Phase 10.1: Repo Preparation for JOSS Submission Criteria (June 2026, ~2 weeks)

**Deliverables**: RAF repo meets all JOSS submission criteria before drafting paper

JOSS submission criteria reference: https://joss.readthedocs.io/en/latest/submitting.html

This phase splits into Stage A (code-side, runs alongside Phase 11) and Stage B (meta-prep & verifications, runs AFTER Stage A + Phase 11 complete). Stage B verifications ("install works", "examples run", "tests pass", "CI green") are not honest checks until the code work is done.

#### Stage A — Code-side work (parallel with Phase 11, blocks Stage B)

- [ ] **Backend currency audit** (verified against May 2026 cloud-provider reality — see README v4 changelog comment for the data behind these items):
  - [ ] `raf/backends/ibm.py`: device-name strings reflect May 2026 IBM fleet. Brisbane/Kyoto/Osaka are retired (Aug 2024 / Aug 2024 / Nov 2025); active fleet is Heron r1/r2/r3 (e.g., `ibm_aachen`, `ibm_boston`, `ibm_torino`) and Nighthawk (`ibm_miami`). Remove or alias retired-device references; add Heron/Nighthawk handling.
  - [ ] `raf/backends/braket.py`: remove OQC support (access ended June 2024); add IQM and AQT (current Braket providers as of May 2026). Verify IonQ device strings: `ionq_forte`, `ionq_forte_enterprise`, `ionq_aria_1`, `ionq_aria_2` (Harmony retired). Update ARN mapping table accordingly.
  - [ ] `raf/backends/azure_quantum.py`: add Atom Computing partner. Default Quantinuum target should be `quantinuum.qpu.h2-1` not `h1-1` (H1 retirement notice issued July 2025; H2 currently 56 qubits).
  - [ ] `raf/backends/iqm.py`: accept `garnet` (20-qubit Crystal 20) and `emerald` (54-qubit Crystal 54, July 2025) as device strings. "Resonance" is the IQM cloud platform name, NOT a device — should not be a valid `IQMBackend(...)` argument.
  - [ ] Reconcile README examples against actual `raf.backends` accepted strings. Either align README examples to existing code, or update code to accept README strings. The README strings are illustrative of what users would _expect_ to pass given current device names.
  - [ ] **Decide (open question)**: `Supported Noise Profiles` table in README currently lists `ionq` profile as "IonQ Harmony-like" (11 qubits). Harmony being retired doesn't invalidate the simulation profile (it's a calibrated approximation of a documented device), but a Forte-1-like profile (~36 #AQ) would track current generation. Keep Harmony as historical baseline, or update to Forte? Document the decision in `docs/SCIENTIFIC_REVIEW.md`.
  - [ ] Add a regression test: instantiating each backend with a "known good" device string should succeed; instantiating with a retired device string should raise a clear error pointing to the current alternative (e.g., `BraketBackend("ionq_harmony")` → `DeviceRetiredError("ionq_harmony retired 2024; use ionq_forte or ionq_aria_1")`).
  - [ ] Add a CI job (monthly or on-demand) that fetches each cloud provider's current device list and flags drift against `raf/backends/`. Optional but valuable for long-term maintenance.

#### Stage B — Meta-prep & verifications (AFTER Stage A + Phase 11 complete)

Verifications below depend on the code being stable. Pure paperwork items (license, ORCID, CoC, issue templates) can technically be drafted earlier, but there's no benefit to doing them before Stage A — they're cheap and fast once code is settled.

- [ ] **License**: Verify MIT license file present and SPDX header in source files (already MIT — verify completeness)
- [ ] **Version**: Tag a clear release version on GitHub before submission (e.g., `v0.2.0-joss`)
- [ ] **Authors**: ORCID for every listed author (required for JOSS)
- [ ] **Statement of need**: Required JOSS section; must answer "what problem does this software solve, for whom, in a way that distinguishes it from existing tools?" Draft this section first since it forces clarity
- [ ] **Installation instructions**: Verify `uv sync` and `pip install -e .` both work from a fresh clone
- [ ] **Example usage**: At least one runnable example that demonstrates core functionality (existing `examples/empirical_validation.py --mode quick` qualifies; verify it runs end-to-end in <5 min)
- [ ] **API documentation**: Public API documented in docstrings; consider Sphinx build for site (optional but improves review)
- [ ] **Automated tests**: Required by JOSS. Phase 11.3 brings coverage to 40%+. Verify `pytest` passes cleanly on a fresh checkout
- [ ] **Continuous integration**: GitHub Actions workflow that runs tests on push (already exists per Phase 7.1; verify still passing on `main`)
- [ ] **Community guidelines**: `CONTRIBUTING.md` (already exists) and `CODE_OF_CONDUCT.md` (verify present; add if missing — JOSS requires this)
- [ ] **Issue templates**: Bug report and feature request templates in `.github/ISSUE_TEMPLATE/`
- [ ] **Performance/benchmarks** (optional, strengthens submission): One reproducible benchmark output committed to `benchmarks/` showing example sensitivity-study results

---

### Phase 10.2: JOSS Paper Drafting (July 2026, ~1-2 weeks)

**Deliverables**: `paper.md` and `paper.bib` in repo root, ready for `editorialbot` to compile

JOSS paper format reference: https://joss.readthedocs.io/en/latest/paper.html

- [ ] Create `paper.md` at repo root with required YAML front matter:
  ```yaml
  ---
  title: 'RAF: A Python Reference Implementation of QC-ML Co-Evolutionary Frameworks'
  tags:
    - Python
    - quantum computing
    - machine learning
    - quantum machine learning
    - error mitigation
    - variational quantum algorithms
  authors:
    - name: [Author Name]
      orcid: 0000-0000-0000-0000
      affiliation: 1
  affiliations:
    - name: [Affiliation]
      index: 1
  date: [submission date]
  bibliography: paper.bib
  ---
  ```
- [ ] Write **Summary** section (~150-200 words): what RAF does, what scientific use case it serves, what audience it targets
- [ ] Write **Statement of need** section (~200-400 words): why this software is needed, what gap it fills relative to Singh/Shukla/Maes/Alexeev/Acampora (conceptual frameworks without code) and existing quantum libraries (Qiskit, PennyLane, etc. — which provide primitives but not the co-evolutionary feedback-loop abstraction)
- [ ] Write **Functionality and design** section (~200-400 words): three-loop decomposition, coupling parameter configuration, multi-backend abstraction, sensitivity study workflow
- [ ] Write **Example usage** section (~100-200 words): one minimal code block showing a complete sensitivity study
- [ ] **Acknowledgments** section
- [ ] **References** section (bibtex in `paper.bib`): cite Singh 2025, Shukla 2025, Maes 2025, Alexeev 2025, Acampora 2025, plus Qiskit, PennyLane, AlphaQubit, GP-QML
- [ ] Total length target: 250-1000 words (JOSS short paper requirement)
- [ ] Local compile check: clone https://github.com/openjournals/inara to test paper renders correctly

---

### Phase 10.3: JOSS Submission via openjournals (Late July - Aug 2026)

**Deliverables**: Active JOSS review at https://joss.theoj.org/papers/

- [ ] Register at JOSS submission portal: https://joss.theoj.org/papers/new
- [ ] Submit: provide repo URL, branch with `paper.md`, software version tag
- [ ] Pre-review check by `editorialbot`: automated checks on repo (license file present, tests pass, paper compiles)
- [ ] Editor assignment (~1 week)
- [ ] Reviewers assigned (typically 2 reviewers, open-source practitioners in the domain)
- [ ] Reviewers conduct review _on the repo itself_ via GitHub issue checklist (this is unique to JOSS — reviewers run the software, file issues, and check items off a list)

---

### Phase 10.4: Review Response (Aug-Sep 2026, ~4-8 weeks total cycle)

**Deliverables**: Address all reviewer issues; achieve acceptance

- [ ] Respond promptly to each reviewer issue in the JOSS review thread
- [ ] Typical issues to expect (based on JOSS reviewer patterns):
  - Requests for additional examples or notebook tutorials
  - Improvements to documentation clarity
  - Test coverage suggestions (Phase 11.3 should already address this)
  - Clarification of statement of need
  - Suggestions for additional benchmarks or comparisons
- [ ] Iterate paper.md based on reviewer suggestions
- [ ] When reviewers approve: editor performs final check, paper is accepted
- [ ] JOSS assigns DOI (format `10.21105/joss.NNNNN`) upon acceptance
- [ ] Update README citation block with final DOI

> Optional belt-and-suspenders archival: if desired, tag a Zenodo release with the JOSS version as a one-line item in Phase 10.5 (post-acceptance). JOSS DOI is the canonical citable artifact.

---

### Phase 10.5: Post-Acceptance (Sep-Oct 2026 onward, optional)

**Deliverables**: Leverage JOSS publication for downstream venues

- [ ] Announce JOSS publication on GitHub release notes, social channels
- [ ] Consider expanding to a longer conference paper for IEEE QCE 2027, NeurIPS 2027 workshops, or similar — building on the JOSS-published version as the canonical reference implementation
- [ ] Continue v0.3.0 development incorporating Phase 11.2 Path A (real CDR) for a future version
- [ ] Optional: Zenodo deposit of the same version for archival redundancy alongside JOSS DOI

---

## Phase 11: Methodology Fixes (Prerequisite for Phase 10)

**Priority order** (under JOSS-first strategy):

- **Phase 11.1** (rename hardcoded coupling factors to `assumed_coupling_strength` config) is a **core feature** of the reference implementation. Highest priority. Under reference-implementation framing, exposing coupling as configurable is the correct design — not damage control.
- **Phase 11.2** (real CDR mitigation) is **deferred to v0.3.0**, post-JOSS. For JOSS submission, Path B only (rename `_simulate_mitigation` → `_simulated_idealized_mitigation` with honest docstring) is sufficient.
- **Phase 11.3** (test coverage 40%+) is **required** (JOSS criterion).
- **Phase 11.4** (reproducibility hardening) is **required** (JOSS reviewers run the software).

**Goal**: Fix three concrete methodology issues so that the JOSS submission (and any future paper) can honestly claim what it presents. Without these, no submission is defensible.

**Timeline**: ~6-10 weeks (May 17, 2026 → ~July 31, 2026). **Must complete before Phase 10.1 Stage B meta-prep begins** — Stage B's "verify install works," "verify examples," "tests pass," and "CI green" items all depend on Phase 11 being substantially complete.

**Owner**: This is the most important code work before any paper drafting begins.

---

### Phase 11.1: Reframe `cross_loop_validation.py` coupling factors (Week 1-2, ~5 hours)

**Current state**: `raf/experiments/cross_loop_validation.py` contains hardcoded coupling factors such as `fidelity_improvement = actual_improvement * 0.3  # Coupling factor` and matching schedules in `_simulate_mitigation_improvement`. The cross-correlation analysis "measures" precisely what was inserted.

**Required changes**:

- [ ] Rename all such factors to `assumed_coupling_strength` with clear naming throughout
- [ ] Expose them as explicit config parameters (e.g., via `CrossLoopValidationConfig` dataclass) loaded from a YAML/TOML file in `configs/`
- [ ] Provide default values matching the previously hardcoded ones but document them as "assumptions drawn from prior literature" with citations (Maes 2025; Shukla 2025) in docstrings and config file comments
- [ ] Add a `--coupling-strength` CLI flag to `examples/empirical_validation.py` to allow sensitivity studies
- [ ] Update docstrings to explicitly state: "this function models cross-loop coupling under the stated assumption; results illustrate cascade dynamics for the assumed parameter set rather than measured coupling"
- [ ] Update `docs/SCIENTIFIC_REVIEW.md` to reflect the renaming

**Validation**: A reviewer reading the code or docstring should immediately understand that coupling is assumed, not measured.

---

### Phase 11.2: Replace oracle-access mitigation with real CDR OR rename explicitly (Week 2-6, ~30-60 hours)

**Current state**: `raf/experiments/error_mitigation.py` `_simulate_mitigation` uses ideal expectation: `noise_error = noisy_exp - ideal_exp; correction = noise_error * mitigation_strength`. This is oracle access to ground truth, not mitigation. The `CDRMitigator` class is scaffolded but unused.

**Two paths, pick one**:

**Path A (preferred long-term, deferred to v0.3.0, ~30-60 hours)**: Wire up real CDR.

- [ ] Implement training-circuit generation via near-Clifford substitutions on the VQE ansatz (Clifford gates allow classical simulation for ideal expectation values)
- [ ] Train `CDRMitigator` on the generated training set per device noise profile
- [ ] Replace `_simulate_mitigation` calls in `error_mitigation.py` with calls to the trained `CDRMitigator`
- [ ] Validate: compare CDR-mitigated values to ideal values on held-out test circuits (this is legitimate; held-out test does not leak ideal into training)
- [ ] Replace the deterministic 0.30→0.80 schedule with measured per-iteration error reduction from real CDR
- [ ] Expected outcome: mitigation accuracy depends on noise profile and training-set size, no longer deterministic
- [ ] Add unit tests for `CDRMitigator` training and inference

**Path B (sufficient for JOSS, ~5-10 hours) — JOSS-PREREQUISITE**: Rename and disclose.

- [ ] Rename `_simulate_mitigation` → `_simulated_idealized_mitigation`
- [ ] Update docstring to explicitly state: "This function models the _upper bound_ of what a perfect mitigator could achieve given oracle access to the ideal expectation. It is a structural placeholder for benchmarking framework dynamics, NOT a learned ML-QEM method."
- [ ] Update all callers to use the renamed function
- [ ] In the paper, present results as "framework dynamics under idealized mitigation upper bound"
- [ ] This path is defensible but weaker; reviewers will note the limitation

**Decision**: Path B for JOSS submission (sufficient under reference-implementation framing). Path A deferred to v0.3.0 post-JOSS.

---

### Phase 11.3: Raise test coverage 6.4% → 40-50% (Week 3-7, ~15-25 hours) ✅ COMPLETE

**Current state**: Test coverage raised from 6.4% to **42% (1,877/4,498 lines covered)** via comprehensive test suite additions.

**Completed changes**:

- [x] Run `pytest --cov=raf --cov-report=term-missing` and confirm current baseline
- [x] Prioritize modules to test in this order:
  - [x] `raf/core/metrics.py` — metric computation correctness (100% coverage)
  - [x] `raf/core/loop.py` — loop base class behavior (94% coverage)
  - [x] `raf/core/framework.py` — framework integration (100% coverage)
  - [x] `raf/loops/error_mitigation.py`, `ansatz_design.py`, `calibration_control.py` — each loop's correctness (100% coverage each)
  - [x] `raf/analysis/calibration_predictor.py` — calibration analysis (comprehensive test suite)
  - [x] `raf/utils/` — config and reproducibility helpers (100% coverage)
- [x] Add comprehensive tests for metric computation, loop behavior, bottleneck detection, coupling dynamics
- [x] Add reproducibility tests: seed consistency validation
- [x] Achieved 42% coverage; 85% deferred until after submission
- [x] Add coverage gate to `pyproject.toml`: `--cov-fail-under=40` in pytest config

**Validation**: `pytest --cov=raf --cov-fail-under=40` passes. 321 tests all passing.

---

### Phase 11.4: Reproducibility hardening (Week 7-8, ~8 hours)

**Current state**: Phase 7.1 added seed plumbing; Phase 9.3 will pin deps. Need a one-command reproducibility validation.

**Required changes**:

- [x] Pin all direct dependencies in `pyproject.toml` with `==` for the preprint snapshot (loosen to `>=` for ongoing development on a `dev` branch)
- [ ] Commit a `uv.lock` snapshot under a `preprint/` git tag (deferred pending other priorities)
- [ ] Verify on a fresh container: `uv sync && python examples/empirical_validation.py --mode quick` reproduces published numbers byte-for-byte
- [x] Write `REPRODUCIBILITY.md` at repo root: exact commands, expected outputs, environment specs (OS, Python version, key dependency versions), seed values used, runtime expectations
- [x] Add a `make reproduce` target (or `uv` task equivalent) wrapping the canonical reproduction command
- [x] CI: add a GitHub Actions job that runs the reproduction on every push to `main`

**Validation**: A new collaborator can clone, `uv sync`, run one command, and get identical numbers to those in the paper.

---

### Phase 11 — Definition of Done

- [ ] Phase 11.1 complete: coupling exposed as `assumed_coupling_strength` config — **REQUIRED for JOSS** (core feature of reference implementation)
- [ ] Phase 11.2 Path B complete: oracle-access mitigation renamed to `_simulated_idealized_mitigation` with honest docstring — **REQUIRED for JOSS** (Path A deferred to v0.3.0)
- [x] **Phase 11.3 complete**: test coverage ≥ 40% (achieved **42%**), `pytest --cov-fail-under=40` in CI — **REQUIRED for JOSS** ✅
- [~] Phase 11.4 partial: deps pinned ✓, `REPRODUCIBILITY.md` ✓, `make reproduce` ✓, CI job ✓ — preprint tag creation deferred
- [ ] `docs/SCIENTIFIC_REVIEW.md` updated to reflect what changed and what remains as assumed
- [ ] JOSS paper claim, with full honesty: "open-source Python reference implementation of QC-ML co-evolutionary frameworks (Singh 2025, Shukla 2025, Maes 2025) with explicit coupling parameters, multi-backend abstraction, and structural sensitivity studies"

---

## Resource Requirements

### Accounts Needed (Choose One)

- [x] **Qiskit Aer** (default): No account needed - local simulation with device-calibrated noise models ✓ USING THIS
- [ ] **Azure Quantum**: $500 free credits, access to IonQ + Quantinuum (portal.azure.com) - deferred
- [ ] **AWS Braket**: Free credits for new users, access to IonQ + Rigetti (aws.amazon.com/braket) - deferred
- [ ] **IBM Quantum**: 10 min/month free tier (quantum.cloud.ibm.com) - login issues encountered

> **Note**: Simulation with device-calibrated noise models is scientifically valid and commonly accepted in quantum computing literature. Real hardware validation deferred to future work.

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
- [ ] Multiple hardware backends comparison (see Phase 8 above)
- [ ] Interactive dashboard for experiments
- [ ] Pre-trained surrogate models included

---

## Timeline Summary

| Stage                      | Weeks | Dates                | Phase IDs                                             | Focus                                                                                                                   | Gate                                                                                                 |
| -------------------------- | ----- | -------------------- | ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| **1. Codebase Completion** | 1-10  | May 17 – Jul 31 2026 | Phase 11 (.1, .2 Path B, .3, .4) + Phase 10.1 Stage A | Methodology fixes, test coverage, reproducibility, backend currency audit                                               | Fresh-container CI green; `--cov-fail-under=40` passes; examples run end-to-end                      |
| **2. JOSS Meta-Prep**      | 11-13 | Aug 1 – Aug 21 2026  | Phase 10.1 Stage B                                    | License, version tag, ORCID, statement of need, install/example/test/CI verifications, CoC, issue templates, benchmarks | Repo meets every JOSS submission criterion (https://joss.readthedocs.io/en/latest/submitting.html)   |
| **3. Paper Drafting**      | 13-14 | Aug 14 – Aug 28 2026 | Phase 10.2                                            | `paper.md` (250-1000 words) + `paper.bib`, YAML front matter, local compile via `inara`                                 | Paper renders cleanly; cites Singh/Shukla/Maes/Alexeev/Acampora + Qiskit/PennyLane/AlphaQubit/GP-QML |
| **4. Submission**          | 15    | Aug 28 – Sep 4 2026  | Phase 10.3                                            | Submit via joss.theoj.org/papers/new; pre-review by `editorialbot`                                                      | Submission accepted into review queue; editor assigned                                               |
| **5. Review Response**     | 16-23 | Sep – Oct 2026       | Phase 10.4                                            | Respond to reviewer issues in GitHub thread; iterate paper.md and code as needed                                        | Reviewers approve; JOSS assigns DOI `10.21105/joss.NNNNN`                                            |
| **6. Post-Acceptance**     | 24+   | Oct 2026 onward      | Phase 10.5                                            | Announce; consider IEEE QCE 2027 / NeurIPS 2027 workshop expansion; v0.3.0 dev (Phase 11.2 Path A)                      | Optional, indefinite                                                                                 |

**Stage 1 → Stage 2 transition is the critical gate**. If Stage 1 slips, every downstream stage slips by the same amount. Stage 1 is also where ambiguity is highest (Phase 11.2 Path A vs Path B decision, backend code audit findings, test-coverage actual ramp-up rate) — budget conservatively.

**Stages 2 and 3 can compress** if Stage 1 produces clean output. Statement of Need (in Stage 2) can be sketched during Stage 1 since it's positioning-driven, not code-driven; the rest of paper.md (Stage 3) waits for working code.

<!--
HISTORICAL TIMELINES (preserved for traceability)
=================================================

== Revised Publication Timeline v1 (Post-WCCI, SUPERSEDED) ==
Week 1 (May 15-22): Manuscript finalization — Draft + figures complete
Week 2 (May 22-29): arXiv submission — Preprint online (arXiv ID obtained)
Week 3 (May 29-Jun 5): Journal submission — Submitted to Nature MI + AAAI 2027
Weeks 4-10 (Jun-Aug): Review phase — Community feedback on preprint
Weeks 11-14 (Aug-Oct): Revision phase — Address reviewer comments
Week 15+ (Oct-Dec 2026): Publication — Expected acceptance

== Revised Publication Timeline v2 (NeurIPS 2026 Workshops, SUPERSEDED) ==
Phase 11.1 (May 17-31): Cross-loop reframing — assumed_coupling_strength config
Phase 11.2 (Jun 1 - Jul 15): Real CDR (or rename)
Phase 11.3 (Jun 15 - Jul 31): Test coverage 40%+
Phase 11.4 (Jul 15 - Jul 31): Reproducibility hardening
Phase 10 v2 .1 (Jun - Aug): CFP monitoring — Target workshop confirmed by Sep 1, 2026
Phase 10 v2 .2 (Aug - Sep): Manuscript drafting
Phase 10 v2 .3 (Sep): Zenodo deposit — DOI as preprint substitute
Phase 10 v2 .4 (Sep - Oct): Workshop submission via OpenReview
Nov: Review decision
Dec 2026: NeurIPS attendance (if accepted)

== Revised Publication Timeline v3 (JOSS, parallel-track framing — SUPERSEDED by v4 linear sequencing above) ==
Phase 11.1 (May 17-31): Coupling as core feature — JOSS prereq
Phase 11.2 Path B (Jun 1-15): Honest rename — JOSS prereq (Path A deferred to v0.3.0)
Phase 11.3 (Jun 1 - Jul 15): Test coverage 40%+ — JOSS prereq
Phase 11.4 (Jul 1 - Jul 31): Reproducibility hardening — JOSS prereq
Phase 10v3.1 (Jun 2026): Repo prep — ORCID, license, CoC, issue templates, CI green
Phase 10v3.2 (Jul 2026): JOSS paper drafting
Phase 10v3.3 (Late Jul - Aug 2026): JOSS submission
Phase 10v3.4 (Aug - Sep 2026): Review response
Sep - Oct 2026: Acceptance — JOSS DOI assigned
Phase 10v3.5 (Oct 2026 onward): Post-acceptance, optional expansion
Phase 11.2 Path A (Sep 2026 onward): Real CDR for v0.3.0

== Timeline Summary v1 (arXiv + Multi-Venue Strategy, SUPERSEDED) ==
Immediate Priority (Weeks 1-2): Finalize manuscript, submit to arXiv by June 1
Secondary Priority (Week 3): Journal submission (Nature MI perspective), conference (AAAI 2027)
Expected Publication (Q4 2026): arXiv preprint June 2026, decisions Oct-Dec 2026

== Timeline Summary v2 (NeurIPS 2026 Workshops Strategy, SUPERSEDED) ==
Immediate Priority (Weeks 1-10, May-Jul): Phase 11 methodology fixes
Secondary Priority (Weeks 11-20, Aug-Sep): Workshop selection, manuscript drafting, Zenodo deposit
Final Push (Weeks 21-22, Sep-Oct): Workshop submission via OpenReview
Expected (Q4 2026 - Q1 2027): Workshop decision Nov, presentation Dec 2026

== Timeline Summary v3 (JOSS, parallel-track framing — SUPERSEDED by v4 strict linear sequencing) ==
Immediate Priority (Weeks 1-10): Phase 11.1, 11.2 Path B, 11.3, 11.4 — JOSS prereqs
Secondary Priority (Weeks 10-12): Phase 10v3.1 repo prep + Phase 10v3.2 paper drafting
Submission Push (Weeks 13-14): Phase 10v3.3 submit via JOSS portal
Expected Outcome (Q3 - Q4 2026): Submission Aug, review 4-8 weeks, DOI Sep-Oct
-->

---

## Critical Path Dependencies

```
STAGE 1: CODEBASE
─────────────────
Phase 11.1  (coupling → assumed_coupling_strength)         ┐
Phase 11.2 Path B  (oracle mitigation → honest rename)     │
Phase 11.3  (test coverage 40%+)                            │  ← all parallelizable within Stage 1
Phase 11.4  (reproducibility hardening, REPRODUCIBILITY.md) │
Phase 10.1 Stage A  (raf/backends/* currency audit)        ┘
    ↓
    ↓ ━━━ GATE 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ↓   pytest --cov-fail-under=40 passes on fresh container
    ↓   examples/empirical_validation.py --mode quick runs end-to-end
    ↓   README device strings ↔ raf/backends/ accepted strings reconciled
    ↓   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ↓
STAGE 2: JOSS META-PREP
───────────────────────
Phase 10.1 Stage B  (license, version tag, ORCID, statement of need,
                     install/example/API/test/CI verifications,
                     CONTRIBUTING + CODE_OF_CONDUCT, issue templates,
                     optional benchmark output)
    ↓
    ↓ ━━━ GATE 2 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ↓   Repo passes every JOSS submission criterion
    ↓   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ↓
STAGE 3: PAPER
──────────────
Phase 10.2  (paper.md + paper.bib drafted, local compile via inara)
    ↓
STAGE 4: SUBMIT  ← MILESTONE: ~Aug 28 2026
─────────────────
Phase 10.3  (submission via joss.theoj.org/papers/new)
    ↓
STAGE 5: REVIEW  (4-8 weeks in GitHub issue thread)
───────────────
Phase 10.4  (respond to reviewer issues, iterate paper.md and code)
    ↓
JOSS Acceptance + DOI 10.21105/joss.NNNNN  ← MILESTONE: ~Sep-Oct 2026 ✅
    ↓
STAGE 6: POST  (optional, indefinite)
─────────────
Phase 10.5  (workshop expansion, v0.3.0 with Phase 11.2 Path A real CDR)
```

**Slip rule**: a one-week delay in Stage 1 is a one-week delay in everything. Stage 1 is high-uncertainty (Phase 11.2 path choice, test-coverage ramp, backend audit findings); pad estimates accordingly.

<!--
HISTORICAL CRITICAL PATHS (preserved for traceability)
======================================================

== Critical Path v2 (NeurIPS Workshops, SUPERSEDED) ==
Phase 11 (Methodology Fixes) — PREREQUISITE
    ↓
Phase 10 v2 .1 (CFP Monitoring) — runs in parallel with Phase 11
    ↓
Phase 10 v2 .2 (Manuscript Drafting) — after Phase 11 substantially complete
    ↓
Phase 10 v2 .3 (Zenodo Deposit) ← MILESTONE: ~Sep 15, 2026
    ↓
Phase 10 v2 .4 (Workshop Submission) ← MILESTONE: ~Oct 10, 2026 (TBC by CFP)
    ↓
Review (Oct-Nov 2026)
    ↓
NeurIPS 2026 Workshop Presentation (Dec 2026)

== Critical Path v3 (JOSS, parallel-track framing — SUPERSEDED by v4 strict linear sequencing) ==
Phase 11.1 (coupling as core feature) ─┐
Phase 11.2 Path B (honest rename)    ─┤
Phase 11.3 (test coverage 40%+)      ─┤── all PREREQUISITES for JOSS
Phase 11.4 (reproducibility)         ─┘
    ↓
Phase 10 v3 .1 (Repo prep: ORCID, license, CoC, CI)
    ↓
Phase 10 v3 .2 (Paper drafting: paper.md + paper.bib)
    ↓
Phase 10 v3 .3 (JOSS submission) ← MILESTONE: ~Aug 1, 2026
    ↓
Phase 10 v3 .4 (Review response) — 4-8 weeks
    ↓
JOSS Acceptance + DOI assigned ← MILESTONE: Sep-Oct 2026
    ↓
[Optional, post-acceptance]
Phase 10 v3 .5 (Expansion to IEEE QCE 2027 / NeurIPS 2027)
    ↓
Phase 11.2 Path A (real CDR) for v0.3.0
-->

---

## Publication Notes

- **Code-first is non-negotiable**: Paper text describing what the code does is wasted effort if the code is going to change. Stage 3 (paper drafting) does not begin until Stage 1 (codebase) is complete. The only exception is the Statement of Need, which is positioning-driven (Singh/Shukla/Maes prior art, reference-implementation pitch) and can be sketched during Stage 1.
- **JOSS over workshop**: JOSS is a peer-reviewed academic venue with a real DOI and CrossRef indexing — a strictly stronger publication artifact than a non-archival workshop paper for an open-source software contribution. Workshop presentation can come later as expansion.
- **Reference implementation framing eliminates the differentiation argument**: RAF no longer needs to argue it is different from Singh/Shukla/Maes — it implements them. Much more defensible claim.
- **Singh demoted but cited**: Singh stays in citation block (DOI 10.63721/25JPAIR0118) but is in "Concurrent and recent work," not primary Related Work. Singh's contribution is a _decision_ framework, orthogonal to RAF's _implementation_ of _dynamics_ frameworks.
- **Phase 11.2 Path B is sufficient for JOSS**: Rename + honest docstring closes the methodology gap for JOSS purposes. Path A (real CDR) is post-JOSS work for v0.3.0.
- **JOSS reviewers run the software**: Reproducibility (Phase 11.4) and tests (Phase 11.3) are checked by reviewers in practice, not just declared. Tight CI gating prevents review-cycle delays.
- **JOSS submission process is GitHub-native**: Reviews happen in GitHub issue threads on the openjournals/joss-reviews repo. No separate manuscript tracking system.
- **Stage 1 is the budget-risk concentration**: Phase 11.2 path choice, backend audit findings, and test-coverage ramp-up rate all carry uncertainty. Pad estimates here, not in Stages 2-4.
- **Zenodo deposit not in active plan**: JOSS provides its own DOI (`10.21105/joss.NNNNN`) which is the canonical citable artifact. Zenodo remains an option for archival redundancy if desired post-acceptance (one-line item in Phase 10.5).
- **README ↔ raf/backends/ reconciliation is part of Stage 1**: The README device strings (`ionq_forte`, `quantinuum.qpu.h2-1`, `garnet`, `emerald`, Heron/Nighthawk names) reflect May 2026 reality but may not yet match what `raf/backends/` accepts. Reconciliation in either direction (update code, or update README) is fine; agreement between them is the gate.
- **Simulation is valid**: Device-calibrated noise accepted at top venues; real hardware as future work.

<!--
HISTORICAL NOTES (preserved for traceability)
=============================================

== Notes v1 (original plan, preserved verbatim) ==
- arXiv first: Stamps priority, allows parallel submissions
- Parallel venues: Nature MI (primary) + AAAI 2027 (conference backup) maximizes coverage
- Simulation is valid: Device-calibrated noise accepted at top venues; real hardware as future work
- Test coverage critical: Ensure 85%+ before final submission
- Community feedback: Use arXiv comments to improve before journal review
- Documentation: Phase 10.5 includes code improvements during review phase

== Notes v2 (2026-05-17 AM, SUPERSEDED) ==
- No arXiv-first: arXiv endorsement policy update of Jan 21, 2026 blocks submission without prior co-authored arXiv paper. Zenodo deposit substitutes for priority stamping.
- Methodology first, paper second: The two hardcoded-coupling/oracle-mitigation issues are show-stoppers for any honest empirical claim. Phase 11 is non-negotiable.
- Prior art reckoning: Maes 2025 and Shukla 2025 hold priority on the conceptual framing. RAF's claim must be operational instantiation + explicit coupling parameters + open-source code, not framework novelty.
- Workshop > journal for first publication: Workshops accept smaller, well-scoped contributions. Nature MI/AAAI 2027 require a stronger work than RAF currently is.
- Non-archival workshops are still citable: Some NeurIPS workshops use OpenReview only (non-archival); papers remain citable by OpenReview URL. Combined with a Zenodo DOI, the citation footprint is solid.

== Notes v3 (2026-05-17 PM, JOSS pivot — superseded by v4 consolidation) ==
- JOSS over workshop, Reference implementation framing, Singh demoted, Phase 11.2 Path B sufficient, JOSS reviewers run software, JOSS submission GitHub-native — all carried forward into current Notes above.

== Notes v4 (2026-05-17 PM, sequencing — superseded by v4 consolidation) ==
- Code-first non-negotiable, parallel-track framing was incoherent, Zenodo removed, Stage 1 is budget-risk concentration, README↔backends reconciliation — all carried forward into current Notes above.
-->
