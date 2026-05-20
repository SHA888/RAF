# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Reference

### Install and Test

```bash
uv sync --all-extras                          # Install dev environment with all backends
uv run pytest tests/                          # Run all tests (includes coverage)
uv run pytest tests/ -k test_name             # Run specific test by keyword
uv run pre-commit run --all-files             # Lint gate: black + isort + ruff + mypy
uv run mypy raf/ --strict                     # Type checking (JOSS requirement)
make reproduce                                # Smoke-test empirical validation (~3-5 min)
make test                                     # All tests with coverage (gate: ≥40%)
make help                                     # See all Makefile targets
```

### Source of Truth

This project has pivoted significantly. **Consult these before acting:**

- **`README.md`** (v4) — accurate project description. Backend table corrected for May 2026 reality. Every superseded tagline/section/example lives verbatim in HTML comments (`<!-- ... -->`), do not delete them.
- **`TODO.md`** (v4) — the binding active plan. Sections: `## Active Goal & Timeline`, `## Status`, `## Execution Order` (gate structure), `Phase 10.x` / `Phase 11.x` task lists. Superseded plans preserved in HTML comments.
- **`REPRODUCIBILITY.md`** — one-command reproduction with pinned versions and environment specs (Phase 11.4 requirement).
- **`CONTRIBUTING.md`** — contributor guidelines (Python 3.12+ syntax, strict type checking).

Both README and TODO follow **"latest decision visible, verbatim history in HTML comments"** convention. Only the active version renders; never delete historical blocks.

## What This Is

**Reciprocal Acceleration Framework (RAF)** — open-source Python reference implementation of QC-ML co-evolutionary frameworks (Singh 2025, Shukla 2025, Maes 2025). Not a novel framework; RAF fills the implementation gap by making those frameworks _runnable_: three task-based acceleration loops, explicit configurable coupling parameters, and multi-vendor quantum backend abstraction.

**Active goal:** JOSS (Journal of Open Source Software) submission (~Aug–Sep 2026). JOSS reviewers _run the software_; usability, documentation, automated tests, and reproducibility are the quality gates, not empirical novelty.

**Execution is strictly linear and code-first.** See `TODO.md ## Execution Order`:
- **Stage 1** (codebase completion): Phase 11.1–11.4 + Phase 10.1 Stage A backend audit → fresh-container GATE
- **Stage 2** (JOSS meta-prep): Phase 10.1 Stage B → paper-ready GATE
- **Stage 3** (paper drafting): Phase 10.2 → submission

Do not draft paper text describing code that is still changing; only the positioning-driven Statement of Need may be sketched during Stage 1.

## Scientific Honesty Constraints (Non-Negotiable — Phase 11)

JOSS acceptance depends on the implementation honestly describing what it does. **Never undo or paper over these.**

### Coupling Parameters Are Assumed, Not Measured

- **File:** `raf/experiments/cross_loop_validation.py`, `raf/core/framework.py`
- **Status:** Phase 11.1 in progress (reframe hardcoded factors as `assumed_coupling_strength` config)
- **Action:** Expose coupling dials as configurable (dataclass + config file + `--coupling-strength` CLI flag), document as assumptions drawn from source papers
- **Never:** Describe coupling results as "measured" or "empirically validated"
- **Why:** Honesty about assumptions is the reference-implementation's core feature, not a flaw to hide

### Error-Mitigation Path Is Idealized Upper Bound, Not Learned ML-QEM

- **File:** `raf/experiments/error_mitigation.py`, `_simulate_mitigation()` function
- **Status:** Phase 11.2 Path B required for JOSS (rename to `_simulated_idealized_mitigation`, add honest docstring)
- **What's happening:** Oracle access to ideal expectation (`noise_error = noisy_exp - ideal_exp`); ~1.86× acceleration is artifact of deterministic schedule, not measurement
- **Scaffold vs. Real:** `CDRMitigator` class exists but unused; real CDR deferred to v0.3.0 (post-JOSS)
- **Never:** Claim ML-learned error mitigation without showing the learning machinery

### Tests and Reproducibility Are Submission Blockers

- **Coverage gate:** ≥40% with CI `--cov-fail-under` enforced in `pyproject.toml`
- **Reproducibility:** One-command reproducibility (`uv sync --all-extras && python examples/empirical_validation.py --mode quick`) must be documented in `REPRODUCIBILITY.md`
- **Seeding:** All experiment scripts use `raf.utils.set_all_seeds()` and `persist_run_config()`; preserve when touching experiments
- **Never lower these bars.**

When in doubt, prefer honest, hedged language in docstrings/docs over impressive-sounding claims.

## Architecture

Small core with enforced extension contract:

- **`raf/core/loop.py`** — `AccelerationLoop` (ABC). Every loop MUST implement five members: `stages`, `bottleneck_types`, `compute_acceleration()`, `identify_bottlenecks()`, `get_recommendations()`. `iterate()` is the state-machine engine (bumps iteration, computes acceleration, records bottlenecks, recomputes `LoopStatus`, fires callbacks). Subclasses should not override `iterate()`.
- **`raf/loops/`** — three concrete loops (Error Mitigation, Ansatz Design, Calibration-Control). Add new loop by subclassing `AccelerationLoop`.
- **`raf/core/framework.py`** — `ReciprocalAccelerationFramework` orchestrates loops; `analyze()` aggregates summaries into `FrameworkAnalysis`. **Model assumptions live here as class constants:** `DEFAULT_COUPLINGS` (6 directed loop→loop strengths from papers) and `HIGH_LEVERAGE_INVESTMENTS`. Changing assumptions means editing constants, not logic — and per honesty constraints, document as assumptions.
- **`raf/core/metrics.py`** — `AccelerationMetric`, `BottleneckIndicator`, `CrossLoopCoupling`, `MetricsAggregator`. A loop "accelerates" when `acceleration_ratio > 1`.
- **`raf/backends/`** — quantum hardware abstraction (`QuantumBackend` base). Used only by `raf/experiments/`; core loop/analysis code has no quantum dependency. Every optional vendor imported under `try/except ImportError` in `__init__.py` — missing backend degrades gracefully; never make a core import depend on vendor SDK.
- **`raf/experiments/`** — empirical validation harnesses. Subject to honesty constraints above.
- **`raf/analysis/`, `raf/visualization/`, `raf/utils/`** — analysis tools, plots/dashboard, config + reproducibility helpers.

**Flow:** `ReciprocalAccelerationFramework()` → `add_loop(...)` (default couplings auto-wired) → `iterate_all()` → `analyze()`.

## Project-Specific Gotchas

### Backend Extras

- **Defined extras in `pyproject.toml`:** only `quantum`, `braket`, `azure`, `dev`, `docs`, `all`
- **What will fail:** `uv sync --extra ibm|iqm|pennylane` or `raf[all-backends]` — those backends have unresolvable hard conflicts
  - IBM: `ibm-platform-services` build failure
  - IQM: needs `qiskit<1.3` vs. repo's `qiskit>=2.0`
- **Solution:** Install conflicting backends in separate venvs

### Backend Device String Currency ⚠️ Active Issue

- **Status:** Phase 10.1 Stage A "Backend currency audit" — blocking Stage 1 GATE
- **Problem:** README v4 corrected device strings (Brisbane/Kyoto/Osaka retired; OQC removed; `ionq_harmony`→`ionq_forte`; etc.), but `raf/backends/*.py` has not yet been reconciled
- **Action required:** Either update code to match README v4, or update README to match what code accepts — **agreement, not direction, is the gate**
- **When to worry:** If you touch backends code, expect stale device strings

### Test Coverage Is Enforced

- **How:** `uv run pytest tests/` forces `--cov=raf --cov-report=term-missing --cov-fail-under=40` (see `pyproject.toml`)
- **Expect:** Coverage output even on single-test run
- **Gate:** Must ≥40% or CI fails

### `raf` Console Script Does Not Exist

- `pyproject.toml` declares `raf = "raf.cli:main"` but `raf/cli.py` does not exist
- Use example scripts (`examples/basic_usage.py`, `empirical_validation.py`, etc.), not a CLI, unless you add the module

### Tooling Version Mismatches

- `requires-python = ">=3.12"`, but black/ruff/mypy still configured for `py39` in some places (legacy)
- pre-commit's black explicitly pins `python3.12`
- **Action:** Match existing code; use 3.12+ syntax (`dict[K,V]`, `T | None`), don't downgrade to satisfy stale configs

### Reproducibility Is Explicit and Required

- Experiment scripts use `raf.utils.set_all_seeds()` and `persist_run_config()`
- Seeded run configs live in `run_configs/`
- **Preserve seeding when touching experiment code** — reproducibility is a JOSS gate

## Tooling

`uv` is primary (Python 3.12–3.13 only; `uv.lock` committed). Prefer `uv` over pip.

### Common Commands

```bash
# Environment
uv sync --all-extras                          # Full dev env (quantum + braket + azure + dev + docs)
uv sync                                       # Minimal (core deps only)

# Testing
uv run pytest tests/                          # All tests (auto-collects coverage)
uv run pytest tests/test_loops.py -v          # Single file with verbose output
uv run pytest tests/ -k error_mitigation      # By keyword
make test                                     # Via Makefile (with full coverage report)
make test-quick                               # Quick subset (< 1 min, stops at first failure)

# Linting & Type Checking
uv run pre-commit run --all-files             # Canonical pre-commit gate (black + isort + ruff + mypy)
uv run ruff check raf tests                   # Ruff alone
uv run black raf/ tests/                      # Format with black
uv run isort raf/ tests/                      # Format with isort
uv run mypy raf/ --strict                     # Type check (CONTRIBUTING expects --strict)

# Reproducibility & Examples
uv run python examples/empirical_validation.py --mode quick    # Smoke test (< 5 min)
uv run python examples/empirical_validation.py --mode full     # Full run (~30-45 min)
uv run python examples/basic_usage.py                          # Basic API walkthrough
make reproduce                                # Makefile target for quick validation
make reproduce-full                           # Makefile target for full validation

# Cleanup
make clean                                    # Remove cache, coverage, build artifacts
```

Example scripts that exist: `examples/basic_usage.py`, `empirical_validation.py`, `simulation_study.py`, `multi_vendor_validation.py`.

## Development Workflow

### When Modifying Loops

- Subclass `AccelerationLoop` in `raf/loops/`
- Implement five required members: `stages`, `bottleneck_types`, `compute_acceleration()`, `identify_bottlenecks()`, `get_recommendations()`
- Do not override `iterate()`; it manages the state machine
- Add tests in `tests/test_loops.py`

### When Modifying Framework Assumptions

- Edit `DEFAULT_COUPLINGS` or `HIGH_LEVERAGE_INVESTMENTS` class constants in `raf/core/framework.py`
- Document _why_ the change (source paper, measurement, etc.) in the docstring
- Update `CONTRIBUTING.md` or `README.md` if assumptions are public-facing
- Add a comment linking to the honesty-constraints section above

### When Adding a Backend

- Subclass `QuantumBackend` in `raf/backends/base.py`
- Import in `raf/backends/__init__.py` under `try/except ImportError`
- Test device strings against actual vendor APIs (Phase 10.1 Stage A will audit)
- Never add a hard vendor-SDK dependency to core loop/analysis code

### When Running Experiment Code

- Use `raf.utils.set_all_seeds(seed)` before any randomness
- Call `persist_run_config()` to save experiment metadata
- Verify seeding is preserved in diffs (never strip `set_all_seeds` calls)
- Check coverage stays ≥40% (`make test` will fail if not)

### Pre-Commit Discipline

Run before committing:

```bash
uv run pre-commit run --all-files
```

This is the canonical lint gate for this project (black + isort + ruff + mypy). All must pass; many issues are auto-fixed.

## Phase Milestones and Gates

From `TODO.md ## Execution Order`:

| Phase | Goal | Blocker | Next Stage |
|-------|------|---------|-----------|
| 11.1 | Coupling config (assumed→configurable) | Code review | 11.2 |
| 11.2 | Honest error-mitigation docstrings | Code review | 11.3 |
| 11.3 | Coverage ≥40% + CI gate | CI passing | 11.4 |
| 11.4 | One-command reproducibility | REPRODUCIBILITY.md complete | GATE → Stage 2 |
| 10.1 Stage A | Backend device string audit | Code↔README agreement | GATE → Stage 2 |

**Stage 1 GATE:** All of Phase 11.1–11.4 + Phase 10.1 Stage A must pass on a fresh container before proceeding to Stage 2 (JOSS meta-prep).

---

## Appendix: Known Documentation-Code Drift

- **Backend device strings:** README v4 has correct names (as of May 2026); code may lag. Phase 10.1 Stage A will reconcile.
- **`ionq` noise profile:** Labeled "IonQ Harmony-like" (Harmony retired 2024), but the noise profile is a valid calibrated approximation—historical baselines don't invalidate when hardware retires. Flagged for SCIENTIFIC_REVIEW.md decision.
