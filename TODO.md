# RAF Empirical Validation TODO

**Goal**: Transform RAF from a conceptual framework to an empirically-grounded paper suitable for IEEE WCCI 2026.

**Timeline**: 2 weeks (Target completion: Dec 19, 2025)

---

## Status (v2 — 2026-05-17)

**Pivot rationale**: Prior-art reckoning revealed that the QC-ML feedback-loop framing is now shared territory rather than novel. Specifically:

- **Maes (May 2025)** — Adaptive Co-Design of QML and QEC via RL (Zenodo DOI 10.5281/zenodo.15428357) has priority on the closed feedback-loop architecture between QML ansatz and error management.
- **Shukla (Dec 2025)** — Co-Evolutionary Co-Design Framework (TechRxiv DOI 10.36227/techrxiv.176704915.54945198/v1) has priority on the three-layer (hardware/algorithmic/application) co-evolutionary framing, though it is conceptual rather than operational.
- **Alexeev et al. (Dec 2025)** — Nature Communications review on "AI for quantum computing" (DOI 10.1038/s41467-025-65836-3) is the authoritative review of the field that any RAF paper must cite.
- **Acampora et al. (May 2025)** — Quantum Community Network white paper (arXiv:2505.23860) establishes the long-term research agenda.

**Remaining novelty for RAF**: (a) functional task-based decomposition (Error Mitigation × Ansatz × Calibration-Control) versus stack-layer decomposition; (b) explicit coupling parameters enabling structural sensitivity studies; (c) open-source runnable implementation (none of the above prior art has code).

**Venue pivot**: arXiv access remains blocked by the January 2026 endorsement policy update (institutional email no longer sufficient alone; no prior arXiv authorship to claim). Nature MI and AAAI 2027 are premature given current methodology state. **New target: NeurIPS 2026 workshops** (likely ML4PS or similar; CFPs typically open Aug-Sep 2026, deadlines Sep-Oct 2026). 4-5 months runway permits actual methodology fixes rather than just reframing.

**Methodology blockers that must be fixed before submission**:

1. `raf/experiments/error_mitigation.py` uses ideal expectation as oracle access (`noise_error = noisy_exp - ideal_exp; correction = noise_error * mitigation_strength`). This is not ML-QEM; it is simulated idealized mitigation. The 1.86× acceleration figure is an artifact of the deterministic schedule, not a measurement.
2. `raf/experiments/cross_loop_validation.py` hardcodes coupling factors (`fidelity_improvement = actual_improvement * 0.3`). The cross-correlation analysis "measures" precisely what was inserted.
3. Test coverage at ~6.4% (~820/12,884 lines) is below publication threshold.

**Phase 10 v1 superseded by Phase 10 v2 + Phase 11** (added below). Phase 10 v1 content preserved verbatim for traceability.

---

## Status (v3 — 2026-05-17, addendum to v2)

**Positioning pivot**: After review of the Singh (2025) framework paper, recognized that RAF's strongest position is as a _reference implementation_ of QC-ML co-evolutionary frameworks already well-established in the literature, rather than as a competing framework. The conceptual phase of this subfield is closing (Singh, Shukla, Maes, Alexeev, Acampora all converging in 2025); the implementation phase is opening. RAF fills that gap. This eliminates the "differentiation argument" — RAF no longer needs to argue against prior work, only to honestly implement what prior work described.

**Venue change**: **JOSS (Journal of Open Source Software) becomes the primary target**. JOSS accepts open-source software with novel research value; review criteria focus on usability, documentation, and tests rather than empirical novelty claims. JOSS papers are short (250-1000 words) summary papers that point to the repo where the substance lives. Fast review cycle (typically 4-8 weeks), peer-reviewed, real DOI (10.21105/joss.NNNNN), indexed in CrossRef. **Single-venue strategy: JOSS only**; NeurIPS workshops and conference venues deferred until after JOSS acceptance.

**Methodology blockers re-prioritized under reference-implementation framing**:

- **Phase 11.1** (rename hardcoded coupling factors to `assumed_coupling_strength` config) becomes the _core feature_ of the reference implementation, not damage control. **Highest priority.** Under the new framing, "coupling parameters drawn from prior literature, exposed as configurable so users can vary them" is the correct behavior for a reference implementation. RAF is not claiming to have measured the coupling; it provides the dials so researchers can test alternative coupling assumptions from Singh/Shukla/Maes against each other.
- **Phase 11.2** (real CDR mitigation replacing oracle-access mitigation) **demoted to v0.3.0 goal**, not a JOSS prerequisite. JOSS reviewers will check that the implementation is honestly documented, not that empirical claims are validated. If we rename `_simulate_mitigation` to `_simulated_idealized_mitigation` with clear docstrings (Phase 11.2 Path B), JOSS acceptance is unblocked. Path A (real CDR) becomes a post-JOSS enhancement that strengthens the next version.
- **Phase 11.3** (test coverage 40%+) **still required**. JOSS explicitly requires "automated tests" with reasonable coverage as a submission criterion.
- **Phase 11.4** (reproducibility hardening) **still required**. JOSS reviewers run the software; reproducibility is checked.

**Singh demoted to concurrent work** (per Option B agreed in conversation): Verified the Singh (2025) paper exists with DOI 10.63721/25JPAIR0118, but the journal shows hallmarks of low-quality open-access publishing (3-day submission-to-acceptance, broken citation chains where in-text refs go to [97] and [171] but reference list ends at [74], unverified "validation across 500+ real-world problems" claim with no methods or data). Citing Singh as a _foundational_ reference in a JOSS submission risks reviewer skepticism. Singh's actual contribution is a _decision_ framework (whether to use quantum), which is orthogonal to RAF's _implementation_ of _dynamics_ frameworks. Singh moves from primary Related Work to Concurrent and recent work in README v3; bibtex retained with DOI added for completeness.

**Active plan**: Phase 10 v3 (JOSS submission, below) replaces Phase 10 v2 (NeurIPS workshops, marked superseded below). Phase 11 priorities re-ordered per v3 addendum at top of that phase.

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

## Phase 10 v1 (SUPERSEDED 2026-05-17 — kept for traceability): arXiv + Journal Submission (PRIORITY - START NOW)

> **Supersession rationale**: arXiv endorsement policy update of Jan 21, 2026 blocks submission path; Nature MI / AAAI 2027 premature given prior-art reckoning. See `Status (v2)` at top of file. Active plan now in Phase 10 v2 and Phase 11 below.

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

## Phase 10 v2 (SUPERSEDED 2026-05-17 by Phase 10 v3 — kept for traceability): NeurIPS 2026 Workshops Target

> **Supersession rationale**: Positioning pivot to reference implementation (see `Status (v3)`) makes JOSS a stronger venue match than NeurIPS workshops. JOSS reviewers explicitly evaluate open-source software with research value; NeurIPS workshops still require framework-novelty claims that RAF doesn't make under v3 framing. Active plan now in Phase 10 v3 below.

**Goal**: Submit to a NeurIPS 2026 workshop (likely ML4PS, "Machine Learning and the Physical Sciences") with a manuscript reframed around RAF's actual contribution: an operational structural model with explicit coupling parameters, complementing prior conceptual frameworks (Maes 2025, Shukla 2025).

**Timeline**: ~5 months (May 17, 2026 → Oct ~10, 2026 estimated workshop deadline). NeurIPS 2026 main conference is December; workshop CFPs typically open Aug-Sep with deadlines Sep-Oct. Conservative planning assumes ~Oct 10, 2026 deadline.

**Sequencing**: Phase 11 (Methodology Fixes) is a prerequisite. Without it, the paper cannot honestly claim measured acceleration or measured cross-loop coupling. Phase 11 estimated 6-10 weeks; manuscript drafting estimated 4-6 weeks; together fits comfortably in 5-month window.

---

### Phase 10 v2 .1: CFP Monitoring & Venue Selection (June-August 2026)

**Deliverables**: Confirmed target workshop with verified deadline

- [ ] Watch ML4PS website (https://ml4physicalsciences.github.io/) for NeurIPS 2026 CFP
- [ ] Watch NeurIPS 2026 workshops list (https://neurips.cc/Conferences/2026) once posted
- [ ] Candidate workshops to monitor (in priority order):
  - [ ] **ML4PS** (Machine Learning and the Physical Sciences) — primary target; QC-ML is a natural fit
  - [ ] **AI4Science** (AI for Science) — broader scope; check if held at NeurIPS 2026
  - [ ] **Quantum AI / Quantum ML workshops** — check if NeurIPS 2026 has one
- [ ] Backup workshops outside NeurIPS:
  - [ ] AAAI 2027 workshops (deadlines typically Oct-Nov 2026)
  - [ ] ICLR 2027 workshops (deadlines typically Jan 2027)
- [ ] When CFP is posted: record exact deadline, page limit, format requirements, archival status (NeurIPS workshops are typically non-archival OpenReview; some have archival proceedings)
- [ ] Decision deadline: select target workshop by **Sep 1, 2026**

---

### Phase 10 v2 .2: Manuscript Drafting (August-September 2026)

**Deliverables**: Workshop-format manuscript (typically 4-9 pages depending on venue)

- [ ] Confirm Phase 11 is complete or substantially complete before drafting empirical sections
- [ ] Manuscript structure (NeurIPS workshop format, 4-pg, 6-pg, or 9-pg variants):
  - [ ] **Abstract** (~150-200 words): operational three-loop structural model with explicit coupling parameters; not a novel framework concept but a novel operationalization; sensitivity study of cascade dynamics under varied coupling assumptions
  - [ ] **§1 Introduction**: motivation, RAF as operational instantiation, explicit citation of Maes/Shukla/Alexeev/Acampora prior work in the intro itself (not just Related Work)
  - [ ] **§2 Related Work**: explicit positioning relative to (a) Maes' two-loop RL co-design, (b) Shukla's three-layer taxonomy, (c) Alexeev's stack-wide review, (d) Acampora's research agenda; clearly state what RAF adds
  - [ ] **§3 Framework**: three operational loops with task-based decomposition; metric definitions; coupling matrix as parameterized structural model
  - [ ] **§4 Simulated Dynamics under Assumed Coupling**: HONEST reframing — present the simulation as exploring sensitivity to coupling assumptions drawn from prior literature, not as measurement of empirical coupling
  - [ ] **§5 Discussion & Limitations**: name limitations first (simulated coupling, idealized mitigation if not replaced in Phase 11, small qubit scale, simulation-only)
  - [ ] **§6 Conclusion & Future Work**: real-hardware validation, learned coupling estimation, integration with Maes-style RL co-design
- [ ] If Phase 11.2 (real CDR) succeeds, paper can claim "learned error mitigation integrated into the structural model" as additional contribution
- [ ] If Phase 11.2 does not succeed, paper claims only "structural sensitivity analysis with explicit coupling parameters"

---

### Phase 10 v2 .3: Zenodo Deposit as Priority Substitute (after manuscript drafted, ~Sept 2026)

**Deliverables**: Versioned Zenodo deposit with DOI (substitute for arXiv since arXiv access blocked)

- [ ] Confirm Zenodo deposit policy with GitHub integration (https://zenodo.org/account/settings/github/)
- [ ] Tag a GitHub release of RAF (e.g., `v0.2.0-preprint`)
- [ ] Trigger Zenodo deposit via GitHub release hook
- [ ] Record Zenodo DOI; reference it in the workshop submission cover letter as "preprint available at DOI: 10.5281/zenodo.xxxxxxx"
- [ ] Update README citation block to include Zenodo DOI

---

### Phase 10 v2 .4: Workshop Submission (Sep-Oct 2026)

**Deliverables**: Submitted manuscript to selected NeurIPS 2026 workshop

- [ ] Reformat to workshop-required template (typically NeurIPS LaTeX style)
- [ ] Compile final PDF; check page limit
- [ ] Prepare cover letter referencing Zenodo deposit
- [ ] Submit via OpenReview (standard NeurIPS workshop platform) before deadline
- [ ] Track reviewer feedback in OpenReview; respond during rebuttal period if applicable
- [ ] Expected decision: typically 4-6 weeks after deadline (~Nov 2026)
- [ ] If accepted: prepare camera-ready, plan workshop attendance (Dec 2026)
- [ ] If rejected: incorporate reviewer feedback, retarget AAAI 2027 workshops or ICLR 2027 workshops

---

## Phase 10 v3: JOSS Submission Target (ACTIVE — added 2026-05-17)

**Goal**: Submit RAF to the Journal of Open Source Software (JOSS) as an open-source reference implementation of QC-ML co-evolutionary frameworks. Single-venue strategy: fast, clean, low-risk. Conference workshops deferred until after JOSS acceptance.

**Why JOSS**: JOSS publishes short summary papers about scholarly open-source software. Review criteria are explicit and software-focused: license, installation, examples, automated tests, community guidelines, documentation, statement of need. There is no empirical-novelty pressure — implementation papers about established frameworks are exactly the type of contribution JOSS exists to recognize. Fast review cycle (typically 4-8 weeks), peer-reviewed, real DOI (`10.21105/joss.NNNNN`), indexed in CrossRef. JOSS reviewers run the software, so reproducibility and tests are the actual quality gates.

**Timeline**: ~3-4 months (May 17, 2026 → Aug-Sep 2026 submission window), with Phase 11.1, 11.3, 11.4 as prerequisites. Phase 11.2 (real CDR) deferred to v0.3.0, post-JOSS.

---

### Phase 10 v3 .1: Repo Preparation for JOSS Submission Criteria (June 2026, ~2 weeks)

**Deliverables**: RAF repo meets all JOSS submission criteria before drafting paper

JOSS submission criteria reference: https://joss.readthedocs.io/en/latest/submitting.html

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

### Phase 10 v3 .2: JOSS Paper Drafting (July 2026, ~1-2 weeks)

**Deliverables**: `paper.md` and `paper.bib` in repo root, ready for `whedon`/`editorialbot` to compile

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

### Phase 10 v3 .3: JOSS Submission via openjournals (Late July - Aug 2026)

**Deliverables**: Active JOSS review at https://joss.theoj.org/papers/

- [ ] Register at JOSS submission portal: https://joss.theoj.org/papers/new
- [ ] Submit: provide repo URL, branch with `paper.md`, software version tag
- [ ] Pre-review check by `editorialbot`: automated checks on repo (license file present, tests pass, paper compiles)
- [ ] Editor assignment (~1 week)
- [ ] Reviewers assigned (typically 2 reviewers, open-source practitioners in the domain)
- [ ] Reviewers conduct review _on the repo itself_ via GitHub issue checklist (this is unique to JOSS — reviewers run the software, file issues, and check items off a list)

---

### Phase 10 v3 .4: Review Response (Aug-Sep 2026, ~4-8 weeks total cycle)

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
- [ ] Tag Zenodo release with same version for archival redundancy

---

### Phase 10 v3 .5: Post-Acceptance (Sep-Oct 2026 onward, optional)

**Deliverables**: Leverage JOSS publication for downstream venues

- [ ] Announce JOSS publication on GitHub release notes, social channels
- [ ] Consider expanding to a longer conference paper for IEEE QCE 2027, NeurIPS 2027 workshops, or similar — building on the JOSS-published version as the canonical reference implementation
- [ ] Continue v0.3.0 development incorporating Phase 11.2 (real CDR) for a future version

---

## Phase 11: Methodology Fixes (PREREQUISITE for Phase 10 v2 — added 2026-05-17)

> **v3 priority re-ordering (2026-05-17)** — under JOSS-first strategy (Phase 10 v3 supersedes Phase 10 v2):
>
> - **Phase 11.1** (rename to `assumed_coupling_strength` config): **promoted to core feature** of the reference implementation. Highest priority. Under reference-implementation framing, exposing coupling as configurable is the _correct design_, not damage control.
> - **Phase 11.2** (real CDR mitigation): **demoted to v0.3.0 goal**, post-JOSS. For JOSS submission, executing Path B only (rename `_simulate_mitigation` → `_simulated_idealized_mitigation` with honest docstring) is sufficient. Path A (full CDR implementation) becomes a next-version enhancement.
> - **Phase 11.3** (test coverage 40%+): **still required** — JOSS explicitly requires automated tests.
> - **Phase 11.4** (reproducibility hardening): **still required** — JOSS reviewers run the software.
>
> The original Phase 11 content below remains accurate; only the priority and the "Definition of Done" change.

**Goal**: Fix three concrete methodology issues so that the workshop paper can honestly claim what it presents. Without these, no submission is defensible.

**Timeline**: ~6-10 weeks (May 17, 2026 → ~July 31, 2026), running in parallel with Phase 10 v2 .1 CFP monitoring.

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

**Path A (preferred if time permits, ~30-60 hours)**: Wire up real CDR.

- [ ] Implement training-circuit generation via near-Clifford substitutions on the VQE ansatz (Clifford gates allow classical simulation for ideal expectation values)
- [ ] Train `CDRMitigator` on the generated training set per device noise profile
- [ ] Replace `_simulate_mitigation` calls in `error_mitigation.py` with calls to the trained `CDRMitigator`
- [ ] Validate: compare CDR-mitigated values to ideal values on held-out test circuits (this is legitimate; held-out test does not leak ideal into training)
- [ ] Replace the deterministic 0.30→0.80 schedule with measured per-iteration error reduction from real CDR
- [ ] Expected outcome: mitigation accuracy depends on noise profile and training-set size, no longer deterministic
- [ ] Add unit tests for `CDRMitigator` training and inference

**Path B (fallback if Path A is too costly, ~5-10 hours)**: Rename and disclose.

- [ ] Rename `_simulate_mitigation` → `_simulated_idealized_mitigation`
- [ ] Update docstring to explicitly state: "This function models the _upper bound_ of what a perfect mitigator could achieve given oracle access to the ideal expectation. It is a structural placeholder for benchmarking framework dynamics, NOT a learned ML-QEM method."
- [ ] Update all callers to use the renamed function
- [ ] In the paper, present results as "framework dynamics under idealized mitigation upper bound"
- [ ] This path is defensible but weaker; reviewers will note the limitation

**Recommendation**: Attempt Path A first; fall back to Path B if blocked by week 4.

---

### Phase 11.3: Raise test coverage 6.4% → 40-50% (Week 3-7, ~15-25 hours)

**Current state**: Test coverage estimated ~6.4% (~820/12,884 lines). Far below publication threshold for a code-contribution paper.

**Required changes**:

- [ ] Run `pytest --cov=raf --cov-report=term-missing` and confirm current baseline
- [ ] Prioritize modules to test in this order:
  - [ ] `raf/core/metrics.py` — metric computation correctness
  - [ ] `raf/core/loop.py` — loop base class behavior
  - [ ] `raf/core/framework.py` — framework integration
  - [ ] `raf/loops/error_mitigation.py`, `ansatz_design.py`, `calibration_control.py` — each loop's correctness
  - [ ] `raf/analysis/bottleneck.py`, `cross_loop.py`, `prioritization.py` — analysis correctness
  - [ ] `raf/backends/aer.py`, `noise_models.py` — backend basics
- [ ] Add property-based tests via `hypothesis` for metric monotonicity, coupling parameter bounds, etc.
- [ ] Add reproducibility tests: same seed → same output (across SimulatedLoop, CrossLoop, ControlOptimization)
- [ ] Target: 40-50% coverage by Week 7; 85% (Phase 9.5 target) deferred until after submission
- [ ] Add coverage gate to `pyproject.toml`: `[tool.coverage.report]` fail_under = 40

**Validation**: `pytest --cov=raf --cov-fail-under=40` passes.

---

### Phase 11.4: Reproducibility hardening (Week 7-8, ~8 hours)

**Current state**: Phase 7.1 added seed plumbing; Phase 9.3 will pin deps. Need a one-command reproducibility validation.

**Required changes**:

- [ ] Pin all direct dependencies in `pyproject.toml` with `==` for the preprint snapshot (loosen to `>=` for ongoing development on a `dev` branch)
- [ ] Commit a `uv.lock` snapshot under a `preprint/` git tag
- [ ] Verify on a fresh container: `uv sync && python examples/empirical_validation.py --mode quick` reproduces published numbers byte-for-byte
- [ ] Write `REPRODUCIBILITY.md` at repo root: exact commands, expected outputs, environment specs (OS, Python version, key dependency versions), seed values used, runtime expectations
- [ ] Add a `make reproduce` target (or `uv` task equivalent) wrapping the canonical reproduction command
- [ ] CI: add a GitHub Actions job that runs the reproduction on every push to `main`

**Validation**: A new collaborator can clone, `uv sync`, run one command, and get identical numbers to those in the paper.

---

### Phase 11 — Definition of Done (updated 2026-05-17 for v3 / JOSS)

- [ ] Phase 11.1 complete: coupling exposed as `assumed_coupling_strength` config — **REQUIRED for JOSS** (core feature of reference implementation)
- [ ] Phase 11.2 Path B complete: oracle-access mitigation renamed to `_simulated_idealized_mitigation` with honest docstring — **REQUIRED for JOSS** (Path A may be deferred to v0.3.0)
- [ ] Phase 11.3 complete: test coverage ≥ 40%, `pytest --cov-fail-under=40` in CI — **REQUIRED for JOSS** (automated tests are a JOSS criterion)
- [ ] Phase 11.4 complete: reproducibility validated, `REPRODUCIBILITY.md` present, deps pinned — **REQUIRED for JOSS** (reviewers run the software)
- [ ] `docs/SCIENTIFIC_REVIEW.md` updated to reflect what changed and what remains as assumed
- [ ] JOSS paper claim, with full honesty: "open-source Python reference implementation of QC-ML co-evolutionary frameworks (Singh 2025, Shukla 2025, Maes 2025) with explicit coupling parameters, multi-backend abstraction, and structural sensitivity studies"

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

## Revised Publication Timeline v1 (Post-WCCI) — SUPERSEDED 2026-05-17

> Superseded by Phase 10 v2 timeline below; kept for traceability.

| Week  | Dates        | Focus                   | Deliverables                         |
| ----- | ------------ | ----------------------- | ------------------------------------ |
| 1     | May 15-22    | Manuscript finalization | Draft + figures complete             |
| 2     | May 22-29    | arXiv submission        | Preprint online (arXiv ID obtained)  |
| 3     | May 29-Jun 5 | Journal submission      | Submitted to Nature MI + AAAI 2027   |
| 4-10  | Jun-Aug      | Review phase            | Community feedback on preprint       |
| 11-14 | Aug-Oct      | Revision phase          | Address reviewer comments            |
| 15+   | Oct-Dec 2026 | Publication             | Expected acceptance + publication ✅ |

---

## Revised Publication Timeline v2 (NeurIPS 2026 Workshops) — SUPERSEDED 2026-05-17 by v3

> Superseded by Timeline v3 below; kept for traceability.

| Phase  | Dates           | Focus                     | Deliverables                                                              |
| ------ | --------------- | ------------------------- | ------------------------------------------------------------------------- |
| 11.1   | May 17-31       | Cross-loop reframing      | `assumed_coupling_strength` config; sensitivity-study framing             |
| 11.2   | Jun 1 - Jul 15  | Real CDR (or rename)      | CDR-mitigated values OR explicit `_simulated_idealized_mitigation` rename |
| 11.3   | Jun 15 - Jul 31 | Test coverage 40%+        | Coverage gate in CI; property-based tests                                 |
| 11.4   | Jul 15 - Jul 31 | Reproducibility hardening | `REPRODUCIBILITY.md`; pinned `uv.lock`; CI reproduction job               |
| 10v2.1 | Jun - Aug       | CFP monitoring            | Target workshop confirmed by Sep 1, 2026                                  |
| 10v2.2 | Aug - Sep       | Manuscript drafting       | Workshop-format draft with revised framing                                |
| 10v2.3 | Sep             | Zenodo deposit            | DOI assigned as preprint substitute                                       |
| 10v2.4 | Sep - Oct       | Workshop submission       | Submitted via OpenReview                                                  |
| —      | Nov             | Review decision           | Accept / revise / reject                                                  |
| —      | Dec 2026        | NeurIPS attendance        | Workshop presentation (if accepted)                                       |

---

## Revised Publication Timeline v3 (JOSS) — ACTIVE

| Phase             | Dates               | Focus                       | Deliverables                                                              |
| ----------------- | ------------------- | --------------------------- | ------------------------------------------------------------------------- |
| 11.1              | May 17-31           | Coupling as core feature    | `assumed_coupling_strength` config (JOSS prereq)                          |
| 11.2 Path B       | Jun 1-15            | Honest rename               | `_simulated_idealized_mitigation` with disclosure docstring (JOSS prereq) |
| 11.3              | Jun 1 - Jul 15      | Test coverage 40%+          | Coverage gate in CI (JOSS prereq)                                         |
| 11.4              | Jul 1 - Jul 31      | Reproducibility hardening   | `REPRODUCIBILITY.md`; pinned `uv.lock`; CI reproduction job (JOSS prereq) |
| 10v3.1            | Jun 2026            | Repo prep for JOSS criteria | ORCID, license, CoC, issue templates, CI green                            |
| 10v3.2            | Jul 2026            | JOSS paper drafting         | `paper.md` + `paper.bib` in repo root, 250-1000 words                     |
| 10v3.3            | Late Jul - Aug 2026 | JOSS submission             | Active review at joss.theoj.org/papers                                    |
| 10v3.4            | Aug - Sep 2026      | Review response             | Address reviewer issues via GitHub thread                                 |
| —                 | Sep - Oct 2026      | Acceptance                  | JOSS DOI assigned (10.21105/joss.NNNNN)                                   |
| 10v3.5            | Oct 2026 onward     | Post-acceptance             | Optional expansion to IEEE QCE 2027 / NeurIPS 2027                        |
| Phase 11.2 Path A | Sep 2026 onward     | Real CDR for v0.3.0         | Post-JOSS enhancement                                                     |

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

## Timeline Summary v1: arXiv + Multi-Venue Strategy — SUPERSEDED 2026-05-17

> Superseded by Timeline Summary v2 below; kept for traceability.

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

## Timeline Summary v2: NeurIPS 2026 Workshops Strategy — SUPERSEDED 2026-05-17 by v3

> Superseded by Timeline Summary v3 below; kept for traceability.

**Immediate Priority** (Weeks 1-10, May-July 2026):

- Phase 11.1: reframe coupling factors as `assumed_coupling_strength` config (Week 1-2)
- Phase 11.2: real CDR mitigation or honest rename (Week 2-6)
- Phase 11.3: test coverage 40%+ (Week 3-7)
- Phase 11.4: reproducibility hardening (Week 7-8)

**Secondary Priority** (Weeks 11-20, Aug-Sep 2026):

- Phase 10 v2 .1: CFP monitoring + workshop selection
- Phase 10 v2 .2: manuscript drafting with revised framing (cite Maes/Shukla/Alexeev/Acampora prominently)
- Phase 10 v2 .3: Zenodo deposit as arXiv substitute

**Final Push** (Weeks 21-22, Sep-Oct 2026):

- Phase 10 v2 .4: workshop submission via OpenReview

**Expected Outcome** (Q4 2026 - Q1 2027):

- Workshop submission: ~Oct 10, 2026 (estimated; depends on CFP)
- Decision: ~Nov 2026
- NeurIPS 2026 workshop presentation: Dec 2026 (if accepted)
- Alternative venues if rejected: AAAI 2027 workshops (Nov 2026 deadline) or ICLR 2027 workshops (Jan 2027 deadline)

---

## Timeline Summary v3: JOSS Strategy — ACTIVE

**Immediate Priority** (Weeks 1-10, May-July 2026):

- Phase 11.1: coupling as core feature (Week 1-2) — JOSS prereq
- Phase 11.2 Path B: honest rename (Week 3-4) — JOSS prereq (Path A deferred to v0.3.0)
- Phase 11.3: test coverage 40%+ (Week 3-7) — JOSS prereq
- Phase 11.4: reproducibility hardening (Week 7-8) — JOSS prereq

**Secondary Priority** (Weeks 10-12, July-early Aug 2026):

- Phase 10 v3 .1: repo prep for JOSS criteria (ORCID, license, CoC, CI green)
- Phase 10 v3 .2: JOSS paper drafting (`paper.md` 250-1000 words, `paper.bib`)

**Submission Push** (Weeks 13-14, late July - Aug 2026):

- Phase 10 v3 .3: submit via https://joss.theoj.org/papers/new

**Expected Outcome** (Q3 - Q4 2026):

- JOSS submission: late July - August 2026
- Review cycle: 4-8 weeks
- JOSS DOI assigned: September - October 2026 ✅
- Optional follow-on: IEEE QCE 2027 / NeurIPS 2027 workshop expansion (post-acceptance)

---

## Critical Path Dependencies (v2 — updated 2026-05-17)

```
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
NeurIPS 2026 Workshop Presentation (Dec 2026) ✅
```

---

## Critical Path Dependencies (v3 — updated 2026-05-17, supersedes v2 above)

```
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
JOSS Acceptance + DOI assigned ← MILESTONE: Sep-Oct 2026 ✅
    ↓
[Optional, post-acceptance]
Phase 10 v3 .5 (Expansion to IEEE QCE 2027 / NeurIPS 2027)
    ↓
Phase 11.2 Path A (real CDR) for v0.3.0
```

---

## Notes (v2 additions — 2026-05-17)

- **No arXiv-first**: arXiv endorsement policy update of Jan 21, 2026 blocks submission without prior co-authored arXiv paper. Zenodo deposit substitutes for priority stamping.
- **Methodology first, paper second**: The two hardcoded-coupling/oracle-mitigation issues are show-stoppers for any honest empirical claim. Phase 11 is non-negotiable.
- **Prior art reckoning**: Maes 2025 and Shukla 2025 hold priority on the conceptual framing. RAF's claim must be operational instantiation + explicit coupling parameters + open-source code, not framework novelty.
- **Workshop > journal for first publication**: Workshops accept smaller, well-scoped contributions. Nature MI/AAAI 2027 require a stronger work than RAF currently is.
- **Non-archival workshops are still citable**: Some NeurIPS workshops use OpenReview only (non-archival); papers remain citable by OpenReview URL. Combined with a Zenodo DOI, the citation footprint is solid.

---

## Notes (v3 additions — 2026-05-17)

- **JOSS over workshop**: JOSS is a peer-reviewed academic venue with a real DOI and CrossRef indexing. It is a strictly stronger publication artifact than a non-archival workshop paper for an open-source software contribution. Workshop presentation can come later as expansion.
- **Reference implementation framing eliminates the differentiation argument**: RAF no longer needs to argue it is different from Singh/Shukla/Maes — it implements them. This is a much more defensible claim.
- **Singh demoted but cited**: Singh stays in citation block (DOI added: 10.63721/25JPAIR0118) but moves from "builds upon and extends" primary Related Work to "Concurrent and recent work" subsection. Singh's contribution is a _decision_ framework, orthogonal to RAF's _implementation_ of _dynamics_ frameworks.
- **Phase 11.2 Path B is sufficient for JOSS**: Rename + honest docstring closes the methodology gap for JOSS purposes. Path A (real CDR) is post-JOSS work for v0.3.0.
- **JOSS reviewers run the software**: Reproducibility (Phase 11.4) and tests (Phase 11.3) are checked by reviewers in practice, not just declared. Tight CI gating prevents review-cycle delays.
- **JOSS submission process is GitHub-native**: Reviews happen in GitHub issue threads on the openjournals/joss-reviews repo. No separate manuscript tracking system.

---

## Notes (v1 — preserved verbatim)

- **arXiv first**: Stamps priority, allows parallel submissions
- **Parallel venues**: Nature MI (primary) + AAAI 2027 (conference backup) maximizes coverage
- **Simulation is valid**: Device-calibrated noise accepted at top venues; real hardware as future work
- **Test coverage critical**: Ensure 85%+ before final submission
- **Community feedback**: Use arXiv comments to improve before journal review
- **Documentation**: Phase 10.5 includes code improvements during review phase
