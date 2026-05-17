# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Source of truth: read these first

This project has pivoted significantly. **`README.md` and `TODO.md` are the living source of truth — consult them before acting; this file only captures what is stable across the pivot.**

- **`README.md`** — current, accurate project description. The HTML comment block at the top is an intentional version changelog (v2/v3/v4); keep it, don't delete it. README v4 is the corrected backend reality (May 2026).
- **`TODO.md`** — the active plan. Read the latest `Status` block (currently **v4**) and the **`Phase 10 v3`** (active) and **`Phase 11`** sections. Superseded sections (Goal v0, Phase 10 v1/v2) are kept verbatim for traceability — do not act on them, and do not delete them.

## What this is (post-pivot framing — v3/v4)

**Reciprocal Acceleration Framework (RAF)** is an open-source Python **reference implementation** of QC-ML co-evolutionary frameworks (Singh 2025, Shukla 2025, Maes 2025). It is **not** a novel/competing framework — the conceptual phase of this subfield is closing; RAF fills the implementation gap by making those frameworks *runnable*: three task-based acceleration loops (Error Mitigation, Ansatz Design, Calibration-Control), explicit configurable coupling parameters, and a multi-vendor quantum backend abstraction.

**Active goal: a JOSS (Journal of Open Source Software) submission (~Aug–Sep 2026).** JOSS reviewers *run the software* — usability, documentation, automated tests, and reproducibility are the actual quality gates, not empirical novelty. This shapes every decision below.

## Scientific-honesty constraints (non-negotiable — Phase 11)

JOSS acceptance depends on the implementation honestly describing what it does. Do not undo or paper over these:

- **Coupling parameters are *assumed*, not measured.** `raf/experiments/cross_loop_validation.py` has hardcoded factors (e.g. `actual_improvement * 0.3`); Phase 11.1 reframes these as `assumed_coupling_strength` config (dataclass + config file, with `--coupling-strength` CLI flag), documented as assumptions drawn from prior literature. Never describe coupling results as "measured." Exposing these as configurable dials is the *intended core feature* of a reference implementation, not a flaw to hide.
- **The error-mitigation path is an idealized upper bound, not learned ML-QEM.** `raf/experiments/error_mitigation.py` `_simulate_mitigation` uses oracle access to the ideal expectation (`noise_error = noisy_exp - ideal_exp`). The headline ~1.86× acceleration is an artifact of a deterministic schedule, not a measurement. Phase 11.2 Path B (required for JOSS) renames it `_simulated_idealized_mitigation` with an honest docstring. `CDRMitigator` is scaffolded but unused; real CDR (Path A) is deferred to v0.3.0, post-JOSS.
- **Tests and reproducibility are submission blockers.** Coverage must reach ≥40% with a CI `--cov-fail-under` gate (Phase 11.3); reproducibility must be one-command and documented (Phase 11.4). Don't lower these bars.

When in doubt, prefer honest, hedged language in docstrings/docs over impressive-sounding claims.

## Tooling

`uv` is primary (`uv.lock` committed; Python 3.12–3.13 only). Prefer `uv` over pip.

```bash
uv sync --all-extras                       # full dev env (quantum + braket + azure + dev + docs)
uv run pytest tests/                       # all tests (coverage runs automatically, see gotchas)
uv run pytest tests/test_loops.py -v       # single file
uv run pytest tests/ -k error_mitigation   # single test by keyword
uv run pre-commit run --all-files          # black + isort + ruff (canonical lint gate)
uv run mypy raf/ --strict                  # type check (CONTRIBUTING expects --strict)
uv run python examples/empirical_validation.py --mode quick   # smoke-test empirical path (<5 min)
```

Example scripts that actually exist: `examples/basic_usage.py`, `empirical_validation.py`, `simulation_study.py`, `multi_vendor_validation.py`.

## Architecture

Small core with an enforced extension contract:

- **`raf/core/loop.py`** — `AccelerationLoop` (ABC). Every loop MUST implement five members: `stages`, `bottleneck_types`, `compute_acceleration()`, `identify_bottlenecks()`, `get_recommendations()`. `iterate()` is the engine (bumps iteration, computes acceleration, records bottlenecks, recomputes the `LoopStatus` state machine in `_update_status`, fires callbacks). Subclasses should not override `iterate()`.
- **`raf/loops/`** — the three concrete loops. Add a new loop type here by subclassing `AccelerationLoop`.
- **`raf/core/framework.py`** — `ReciprocalAccelerationFramework` orchestrates loops; `analyze()` aggregates per-loop summaries into a `FrameworkAnalysis`. **Model assumptions live here as class constants**: `DEFAULT_COUPLINGS` (6 directed loop→loop strengths from the source papers) and `HIGH_LEVERAGE_INVESTMENTS`. Changing assumptions means editing these constants, not the logic — and per the honesty constraints, document them as assumptions.
- **`raf/core/metrics.py`** — `AccelerationMetric`, `BottleneckIndicator`, `CrossLoopCoupling`, `MetricsAggregator`. A loop is "accelerating" when `acceleration_ratio > 1`.
- **`raf/backends/`** — quantum hardware abstraction (`QuantumBackend` base). Used only by `raf/experiments/`; core loop/analysis code has no quantum dependency. `__init__.py` imports every optional vendor under `try/except ImportError` — a missing backend degrades gracefully; never make a core import depend on a vendor SDK.
- **`raf/experiments/`** — empirical validation harnesses (the files under the honesty constraints above live here).
- **`raf/analysis/`, `raf/visualization/`, `raf/utils/`** — analyzers, plots/dashboard, config + reproducibility helpers.

Flow: `ReciprocalAccelerationFramework()` → `add_loop(...)` (default couplings auto-wired in `__init__`) → `iterate_all()` → `analyze()`.

## Project-specific gotchas

- **Backend extras are NOT all in `pyproject.toml`.** Defined extras: only `quantum`, `braket`, `azure`, `dev`, `docs`, `all` (= quantum+braket+azure+dev+docs). README's `uv sync --extra ibm|iqm|pennylane` / `raf[all-backends]` will fail — those backends have hard dependency conflicts (`ibm-platform-services` build failure; IQM needs `qiskit<1.3` vs. repo's `qiskit>=2.0`) and **must be installed in separate venvs**.
- **README ↔ backend-code drift is a known, tracked issue.** README v4 corrected device strings (Brisbane/Kyoto/Osaka retired; OQC removed from Braket; `ionq_harmony`→`ionq_forte`; etc.), but `raf/backends/*.py` has *not* yet been reconciled (Phase 10 v3 .1 "Backend currency audit"). If you touch backends, expect stale device strings and align code to README v4, not the reverse.
- **`uv run pytest` always runs coverage.** `addopts` forces `--cov=raf --cov-report=term-missing`; expect coverage output even on a single-test run.
- **`raf` console script is broken.** `pyproject.toml` declares `raf = "raf.cli:main"` but `raf/cli.py` does not exist. Use example scripts, not a `raf` CLI, unless you're adding that module.
- **Tooling target-version mismatch.** `requires-python` is `>=3.12`, but black/ruff/mypy are configured for `py39` while pre-commit's black pins `python3.12`. CONTRIBUTING mandates 3.12+ syntax (`dict[K,V]`, `T | None`). Match existing code; don't downgrade syntax to satisfy the stale `py39` config.
- **Reproducibility is explicit and required.** Experiment scripts use `raf.utils.set_all_seeds` and `persist_run_config`; seeded run configs live in `run_configs/`. Preserve seeding when touching experiment code.
