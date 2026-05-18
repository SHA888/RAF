# Reproducibility Guide for RAF

This document provides step-by-step instructions to reproduce the results published in the RAF preprint, ensuring byte-for-byte identical outputs across different environments.

## Environment Specifications

### Minimum Requirements

- **OS**: Linux (tested on WSL2/Ubuntu 22.04), macOS 12+, or Windows 10+ with WSL2
- **Python**: 3.12 or 3.13
- **Package Manager**: `uv` (v0.4.0+)
- **Disk Space**: ~2 GB for full env with all backends
- **RAM**: 8 GB minimum (16+ GB recommended for parallel test runs)

### Tested Configuration

- **OS**: Linux (WSL2 on Windows 10)
- **Python**: 3.12.7
- **uv**: 0.4.11 or later
- **Key Dependencies** (see `pyproject.toml` for full list):
  - numpy==2.4.4
  - scipy==1.17.1
  - matplotlib==3.10.9
  - pandas==3.0.3
  - pydantic==2.13.4
  - networkx==3.6.1
  - rich==15.0.0
  - qiskit>=2.0,<2.2
  - qiskit-aer~=0.17.2

## Quick Start (One Command)

```bash
uv sync --all-extras
python examples/empirical_validation.py --mode quick
```

Expected runtime: **< 5 minutes** on a modern CPU
Expected output: Summary table with acceleration metrics for all three loops

## Detailed Reproduction Steps

### Step 1: Clone and Environment Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/RAF.git
cd RAF

# Checkout the preprint snapshot tag
git checkout preprint/v0.1.0

# Install all dependencies with pinned versions
uv sync --all-extras

# Verify installation
python -c "import raf; print(raf.__version__)"
```

### Step 2: Run Core Reproducibility Validation

The empirical validation script reproduces the three core loops with simulated noise:

```bash
# Quick validation (~3-5 min)
python examples/empirical_validation.py --mode quick

# Full validation with extended noise sampling (~30-45 min)
python examples/empirical_validation.py --mode full
```

**Expected Output** (quick mode):
```
════════════════════════════════════════════════════════════════════════════════════════════════════════════════
                              RAF: Empirical Validation Results
════════════════════════════════════════════════════════════════════════════════════════════════════════════════

                                  Loop Performance Summary
──────────────────────────────────────────────────────────────────────────────────────────────────────────────
 Loop Name              Acceleration    Iterations  Bottleneck Type    Coupling Contribution   Status
──────────────────────────────────────────────────────────────────────────────────────────────────────────────
 ErrorMitigation                1.86            4       MITIGATION          0.30 (assumed)     ✓ Pass
 AnsatzDesign                   1.42            5       EXPRESSIVITY        0.25 (assumed)     ✓ Pass
 CalibrationControl             1.24            5       CALIBRATION         0.20 (assumed)     ✓ Pass
──────────────────────────────────────────────────────────────────────────────────────────────────────────────

  Cross-Loop Coupling Validation
  ────────────────────────────────
  ✓ All coupling strengths within bounds [0.0, 1.0]
  ✓ Coupling matrix stable (operator norm: 1.96)
```

### Step 3: Run Full Test Suite

```bash
# Run all tests with coverage
uv run pytest tests/ -v --cov=raf --cov-report=term-missing

# Expected: 321 tests passing, coverage ≥ 40%
```

### Step 4: Run All Example Scripts

Each example script documents a specific capability:

```bash
# 1. Basic loop usage and status reporting
python examples/basic_usage.py

# 2. Simulation study with multiple noise models
python examples/simulation_study.py

# 3. Multi-vendor backend validation (requires credentials)
python examples/multi_vendor_validation.py

# 4. Cross-loop coupling analysis
python examples/cross_loop_validation.py
```

## Reproducibility Guarantees

### Determinism via Seeding

All experiments use `raf.utils.set_all_seeds(seed=42)` to ensure reproducibility:

```python
from raf.utils import set_all_seeds

# Set global seed once at script start
set_all_seeds(seed=42)

# From here, all randomness is deterministic:
# - numpy random operations
# - scipy random operations
# - Python's random module
```

### Configuration Snapshot

Run configurations used in the preprint are stored in `run_configs/`:

```bash
ls -la run_configs/
```

Each JSON file captures:
- **timestamp**: when the run was executed
- **seed**: global random seed
- **system_info**: Python version, OS, CPU count
- **hyperparameters**: loop-specific parameters
- **results**: numeric outputs (acceleration ratios, bottleneck classifications)

Example config structure:
```json
{
  "timestamp": "2026-05-18T14:30:00",
  "seed": 42,
  "system_info": {
    "python_version": "3.12.7",
    "platform": "linux",
    "cpu_count": 8
  },
  "hyperparameters": {
    "error_mitigation": {
      "max_iterations": 10,
      "coupling_strength": 0.3
    }
  },
  "results": {
    "acceleration_ratio": 1.86,
    "final_status": "accelerating"
  }
}
```

## Troubleshooting

### Issue: `uv sync` fails with version conflicts

**Solution**: Clear cache and retry
```bash
rm -rf ~/.cache/uv
uv sync --all-extras
```

### Issue: Qiskit/Aer won't import

**Solution**: Verify Qiskit version (must be 2.0+)
```bash
python -c "import qiskit; print(qiskit.__version__)"
# Expected: 2.0.x or 2.1.x
```

### Issue: Tests show inconsistent random outputs

**Cause**: Seed not being set before imports
**Solution**: Ensure `set_all_seeds` is called first in your script:
```python
from raf.utils import set_all_seeds
set_all_seeds(seed=42)  # Must come before other imports

# Now safe to use random operations
```

### Issue: Performance varies significantly between runs

**Possible causes**:
1. System load (background processes consuming CPU)
2. Thermal throttling (CPU overheating under sustained load)
3. Different Python optimization level (use same `-O` flags)

**Verification**:
```bash
# Run in isolated environment with minimal background services
nohup python examples/empirical_validation.py --mode quick > run.log 2>&1 &
```

## Validation Checklist

- [ ] Python version is 3.12 or 3.13: `python --version`
- [ ] Checkout preprint tag: `git rev-parse HEAD` matches tag commit
- [ ] `uv sync --all-extras` completes without errors
- [ ] `python -c "import raf; print(raf.__version__)"` succeeds
- [ ] `python examples/empirical_validation.py --mode quick` completes with ✓ Pass status
- [ ] All 321 tests pass: `pytest tests/ --cov=raf --cov-fail-under=40`
- [ ] Coverage ≥ 40%: shown in pytest output

## Publication Snapshot

The preprint snapshot (`preprint/v0.1.0` tag) freezes:
- **Dependency versions**: All direct and transitive dependencies exact-pinned
- **Code state**: Exact codebase at publication time
- **Configuration**: Run configs in `run_configs/` for reference

To validate this exact snapshot:
```bash
git checkout preprint/v0.1.0
uv sync --all-extras
uv run pytest tests/ --cov=raf --cov-fail-under=40
uv run python examples/empirical_validation.py --mode quick
```

## Questions or Issues?

If reproduction fails on your system:
1. Document your environment (see "Environment Specifications" above)
2. Share the error output and reproduction steps
3. Open an issue at: https://github.com/yourusername/RAF/issues

---

**Last Verified**: May 18, 2026
**RAF Version**: 0.1.0
**Python**: 3.12.7
**uv**: 0.4.11
