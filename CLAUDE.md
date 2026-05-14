# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

**Reciprocal Acceleration Framework (RAF)** — A research framework for understanding and accelerating co-evolutionary dynamics between Quantum Computing (QC) and Machine Learning (ML). The framework formalizes three primary acceleration loops:

1. **Error Mitigation Loop** — ML-based quantum error mitigation at the output level
2. **Ansatz Design Loop** — Quantum architecture search via neural surrogates at the circuit level
3. **Calibration-Control Loop** — ML noise models and optimized control at the hardware level

## Quick Start

### Using `uv` (Recommended)

```bash
# Install with all quantum extras and development tools
uv sync --all-extras

# Run tests
pytest tests/ -v

# Format and lint
uv run black raf/ && uv run isort raf/ && uv run ruff check raf/ --fix

# Or use pre-commit hooks
uv run pre-commit run --all-files

# Run a basic example
python examples/basic_usage.py

# Run empirical validation with quantum simulation
python examples/empirical_validation.py --mode quick
```

### Using pip (Traditional)

```bash
# Install in development mode
pip install -e ".[dev,quantum]"

# Run tests
pytest tests/ -v

# Format and lint
black raf/ && isort raf/ && ruff check raf/ --fix

# Run a basic example
python examples/basic_usage.py

# Run empirical validation with quantum simulation
python examples/empirical_validation.py --mode quick
```

## Project Structure

```
raf/
├── core/              # Framework orchestration and base classes
│   ├── framework.py   # ReciprocalAccelerationFramework (main class)
│   ├── loop.py        # AccelerationLoop base class and LoopState/LoopMetrics
│   └── metrics.py     # AccelerationMetric, BottleneckIndicator, CrossLoopCoupling
├── loops/             # Three acceleration loop implementations
│   ├── error_mitigation.py
│   ├── ansatz_design.py
│   └── calibration_control.py
├── backends/          # Multi-vendor quantum backend abstraction
│   ├── base.py        # QuantumBackend base class
│   ├── aer.py         # Qiskit Aer local simulation
│   └── noise_models.py # Predefined device noise profiles (manila, kolkata, ionq, sycamore)
├── experiments/       # Empirical validation framework
│   ├── error_mitigation.py # ErrorMitigationExperiment
│   └── metrics_collector.py
├── analysis/          # Analysis tools
│   ├── bottleneck.py  # BottleneckAnalyzer
│   ├── cross_loop.py  # CrossLoopAnalyzer
│   └── prioritization.py # ResearchPrioritizer
├── visualization/     # Plotting and dashboard utilities
│   ├── loop_dynamics.py # LoopDynamicsVisualizer
│   └── dashboard.py    # RAFDashboard (interactive)
└── utils/             # Config and utilities
    └── config.py      # Configuration management
```

## Architecture Patterns

### The Framework Flow

1. **Framework Creation** — `ReciprocalAccelerationFramework()` orchestrates analysis
2. **Loop Addition** — Each loop inherits `AccelerationLoop`, implements:
   - `compute_acceleration()` → returns `AccelerationMetric` (quantifies loop acceleration)
   - `identify_bottlenecks()` → returns `List[BottleneckIndicator]` (what limits progress)
   - `get_recommendations()` → prioritized action items
3. **Cross-Loop Analysis** — `DEFAULT_COUPLINGS` define how loops affect each other
4. **Unified Analysis** — `raf.analyze()` aggregates all loop dynamics into `FrameworkAnalysis`

### Key Classes

- `ReciprocalAccelerationFramework` — Central orchestrator; holds loops, runs analysis
- `AccelerationLoop` — Base class for loop implementations; defines the interface
- `LoopState` — Dataclass tracking loop metrics across iterations (accuracy, cost, scale, etc.)
- `FrameworkAnalysis` — Results object containing bottlenecks, recommendations, cross-loop effects
- `QuantumBackend` — Abstract interface for quantum providers (Aer, IBM, Braket, Azure, IQM, PennyLane)

### Backend Selection & Availability

**Main Environment (uv sync --all-extras)**:
- ✅ `quantum` extra: Qiskit Aer (local noisy simulation) — always available
- ✅ `braket` extra: AWS Braket (IonQ, Rigetti, OQC, QuEra) — works in main environment
- ✅ `azure` extra: Azure Quantum (IonQ, Quantinuum, Rigetti, PASQAL) — works in main environment

**Separate Environments** (due to dependency conflicts):
- 🔴 **IBM Quantum**: Requires separate venv due to `ibm-platform-services` build failures
  ```bash
  python -m venv venv-ibm
  source venv-ibm/bin/activate
  pip install qiskit-ibm-runtime
  ```

- 🔴 **IQM (trapped-ion)**: Requires separate venv with `qiskit<1.3` (incompatible with qiskit 2.x)
  ```bash
  python -m venv venv-iqm
  source venv-iqm/bin/activate
  pip install qiskit-iqm "qiskit<1.3"
  ```

- 🔴 **PennyLane**: Requires separate venv (transitive `ibm-platform-services` dependency)
  ```bash
  python -m venv venv-pennylane
  source venv-pennylane/bin/activate
  pip install pennylane pennylane-qiskit
  ```

**Recommended Installation**:
```bash
uv sync --all-extras          # Main environment (quantum + Braket + Azure + dev + docs)
```

**If IBM Quantum Needed**:
```bash
# In separate environment:
python -m venv venv-ibm && source venv-ibm/bin/activate
pip install qiskit-ibm-runtime
```

**Root Cause of Separation**:
- `ibm-platform-services` (all versions ≥0.44) has build issues with pkg_resources
- Affects: IBM Quantum, PennyLane (via pennylane-qiskit), and any backend using qiskit-ibm-runtime
- Workaround: Install in isolated environment or use older qiskit-ibm-runtime with complex pinning

## Common Development Tasks

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run a single test file
pytest tests/test_loops.py -v

# Run tests matching a pattern
pytest tests/ -k "error_mitigation" -v

# Run with coverage report
pytest tests/ --cov=raf --cov-report=html
```

### Code Quality

```bash
# Format code
black raf/ tests/

# Sort imports
isort raf/ tests/

# Lint (checks and auto-fixes)
ruff check raf/ tests/ --fix

# Type checking
mypy raf/

# One-shot: format + lint
black raf/ && isort raf/ && ruff check raf/ --fix
```

### Running Examples

```bash
# Basic framework usage (no quantum dependencies required)
python examples/basic_example.py

# Empirical validation with noisy quantum simulation (requires: pip install -e ".[quantum]")
python examples/empirical_validation.py --mode quick
python examples/empirical_validation.py --mode full  # Full study (~5-10 min)

# Multi-vendor hardware validation (requires backend credentials)
python examples/multi_vendor_validation.py --simulators-only
```

### Installation Variants

```bash
# Using uv (recommended):

# Minimal: core framework only (no quantum simulation)
uv sync

# Recommended: includes local quantum simulation + AWS/Azure + dev tools
uv sync --all-extras

# Quantum + dev only (no cloud backends)
uv sync --extras quantum,dev

# Specific backend only
uv sync --extra quantum   # Local simulation (Qiskit Aer)
uv sync --extra braket    # AWS Braket (IonQ, Rigetti, OQC, QuEra)
uv sync --extra azure     # Azure Quantum (IonQ, Quantinuum, Rigetti, PASQAL)

# Using pip (traditional):

# Minimal: core framework only (no quantum simulation)
pip install -e "."

# Recommended: includes local quantum simulation + AWS/Azure + dev tools
pip install -e ".[all]"

# Quantum + dev only (no cloud backends)
pip install -e ".[quantum,dev]"

# IBM Quantum in separate environment (dependency conflicts)
python -m venv venv-ibm && source venv-ibm/bin/activate && pip install -e ".[quantum]" qiskit-ibm-runtime

# IQM in separate environment (Qiskit version constraints)
python -m venv venv-iqm && source venv-iqm/bin/activate && pip install "qiskit<1.3" qiskit-iqm
```

## Error Handling & Debugging

- **Missing backend** — Framework gracefully skips unavailable backends. Check `raf.backends.list_available_backends()`

- **IBM Quantum installation fails** — `ibm-platform-services` has build issues in main environment
  - Solution: Use separate venv as documented in Backend Selection above
  - Test: `python -m venv venv-ibm && source venv-ibm/bin/activate && pip install qiskit-ibm-runtime`

- **IQM hardware unavailable** — Requires `qiskit<1.3` (incompatible with core qiskit 2.x backends)
  - Solution: Create separate environment: `python -m venv venv-iqm && pip install qiskit<1.3 qiskit-iqm`
  - Cannot coexist with qiskit 2.x in same environment

- **PennyLane import fails** — Pulls in ibm-platform-services transitively
  - Solution: Use separate environment or test without PennyLane integration

- **Quantum execution failures** — Examples catch and report cleanly
  - Hardware errors are device-specific (verify provider credentials)
  - Simulation errors usually indicate circuit/backend incompatibility

## Pre-Commit & CI

The repository uses pre-commit hooks (see `.pre-commit-config.yaml`):
```bash
pre-commit run --all-files  # Run all hooks
```

Hooks enforce:
- Trailing whitespace removal
- EOF fixes
- YAML validation
- Black formatting
- isort import sorting
- Ruff linting with auto-fix

## Key Dependencies

Core: `numpy`, `scipy`, `matplotlib`, `networkx`, `pandas`, `pydantic`, `rich`

Optional (per-backend):
- **quantum** → `qiskit 2.0`, `qiskit-aer`
- **ibm** → `qiskit-ibm-runtime`
- **braket** → `amazon-braket-sdk`
- **azure** → `azure-quantum`
- **iqm** → `qiskit-iqm` (note: requires `qiskit<1.3`)
- **pennylane** → `pennylane`, `pennylane-qiskit`

Development: `pytest`, `pytest-cov`, `black`, `isort`, `mypy`, `ruff`

## Testing Strategy

- Unit tests in `tests/` cover core framework, loop implementations, analysis tools
- Integration tests run loops and backends end-to-end
- Empirical validation examples serve as acceptance tests (verify real quantum simulation)
- Backend tests skip gracefully if provider not installed
