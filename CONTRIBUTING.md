# Contributing to RAF

Thank you for your interest in contributing to the Reciprocal Acceleration Framework!

## How to Contribute

### Reporting Issues

- Use the GitHub issue tracker to report bugs
- Describe the issue clearly with steps to reproduce
- Include your Python version and OS

### Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest tests/`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style & Quality

**Python Version & Syntax**
- Minimum Python: 3.12 (no compatibility with earlier versions)
- Use modern Python 3.12+ syntax:
  - `dict[K, V]` instead of `Dict[K, V]`
  - `T | None` instead of `Optional[T]`
  - `list[T]`, `set[T]` instead of `List[T]`, `Set[T]`
  - Named tuples, dataclasses with `slots=True` for efficiency

**Type Hints (Required)**
- All public functions must have type annotations
- All function parameters must have type hints
- All return types must be annotated
- Run `mypy raf/ --strict` to validate (must pass with zero errors)
- Private functions should also have type hints where practical

**Code Formatting & Linting (Enforced by Pre-commit)**
- Format with `black` (v24.4+): `uv run black raf/`
- Sort imports with `isort` (v5.13+): `uv run isort raf/`
- Lint with `ruff` (v0.5+): `uv run ruff check raf/ --fix`
  - Enabled rules: E, W, F, I, C4, B, UP, ARG, SIM, PERF
  - See `pyproject.toml [tool.ruff.lint]` for full configuration
- Type check with `mypy` (v1.11+, strict mode):
  ```bash
  uv run mypy raf/ --strict
  ```
  - This is a JOSS requirement; no exceptions
  - Pre-commit hook enforces it automatically

**Canonical Lint Gate**
Run this before committing to ensure everything passes:
```bash
uv run pre-commit run --all-files
```
This runs (in order): trailing-whitespace, end-of-file-fixer, check-yaml, black, isort, ruff, mypy. Many issues are auto-fixed; review the diff carefully.

### Testing & Coverage

**Coverage Requirement** (JOSS Submission Gate)
- Minimum code coverage: **≥40%** (enforced by CI: `pytest --cov-fail-under=40`)
- Current coverage: **42%** (target for future: 85%+)
- Coverage report: Run `uv run pytest tests/ --cov=raf --cov-report=html` to generate HTML report in `htmlcov/index.html`

**Test Writing Guidelines**
- Write tests for all new public functions and classes
- Test both happy-path and error cases
- For core loop/analysis code: aim for >90% coverage
- For experiment code: ensure seeding is testable (use `raf.utils.set_all_seeds()`)
- All tests must pass before submitting a PR

**Scientific Honesty in Tests**
- Never test oracle-access mitigation as if it were learned ML-QEM
- Test coupling parameters as *assumed* (with config overrides)
- Clearly document what each test validates
- See `CLAUDE.md ## Scientific Honesty Constraints` for non-negotiable requirements

### Documentation

- Update README.md if needed
- Add docstrings to new code
- Update examples if API changes

## Development Setup

**Requirements**
- Python 3.12 or 3.13 (required; no earlier versions supported)
- `uv` package manager (recommended; pip also works but uv is faster)

### Using `uv` (Recommended - Modern Python Tooling)

```bash
# Clone your fork
git clone https://github.com/SHA888/RAF.git
cd RAF

# Verify Python version
python --version  # Should be 3.12.x or 3.13.x

# Install development dependencies (includes all extras: quantum, braket, azure, dev, docs)
uv sync --all-extras

# Run tests with coverage enforcement (gate: ≥40%)
uv run pytest tests/ -v --cov=raf --cov-fail-under=40

# Canonical lint gate (must pass before committing)
uv run pre-commit run --all-files

# Type check (strict mode)
uv run mypy raf/ --strict

# Individual commands (for debugging)
uv run black raf/                    # Format code
uv run isort raf/                    # Sort imports
uv run ruff check raf/ --fix         # Lint and fix
```

### Using pip (Traditional, Not Recommended)

```bash
# Clone your fork
git clone https://github.com/SHA888/RAF.git
cd RAF

# Verify Python version (MUST be 3.12 or 3.13)
python --version

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with all extras
pip install -e ".[dev]"  # or ".[quantum,braket,azure,dev,docs]" for --all-extras equivalent

# Run tests with coverage enforcement
pytest tests/ -v --cov=raf --cov-fail-under=40

# Run pre-commit hook checks
pre-commit run --all-files

# Type check (strict mode)
mypy raf/ --strict

# Format code (individual tools)
black raf/
isort raf/
ruff check raf/ --fix
```

**Note**: `uv` is significantly faster for dependency resolution. If you have `uv` available, prefer the `uv` instructions above.

## Scientific Honesty & Reproducibility

RAF is targeting JOSS (Journal of Open Source Software) submission. Three scientific-honesty constraints are **non-negotiable**:

### 1. Coupling Parameters Are Assumed, Not Measured
- Hardcoded coupling factors must be exposed as configurable parameters
- Document them as assumptions drawn from prior literature (Singh 2025, Shukla 2025, Maes 2025)
- Enable sensitivity studies: `--coupling-strength` CLI flag or config file override
- Never claim "measured" or "empirically validated" coupling — claim "assumed" or "modeled"

### 2. Error Mitigation Path Is Idealized Upper Bound
- Oracle-access mitigation (` _simulate_mitigation`) is **not** learned ML-QEM
- Must be renamed `_simulated_idealized_mitigation` with explicit docstring
- Document that this uses ideal expectation (`noise_error = noisy_exp - ideal_exp`)
- Real ML-learned CDR (ClassicalShadow Regression) is deferred to v0.3.0 post-JOSS
- Refer to `CLAUDE.md ## Scientific Honesty Constraints` for full context

### 3. Reproducibility Is Required
- All experiment scripts must use `raf.utils.set_all_seeds()` before randomness
- Call `persist_run_config()` to save metadata for replayability
- One-command validation: `uv sync --all-extras && python examples/empirical_validation.py --mode quick` (~5 min)
- See `REPRODUCIBILITY.md` for environment specs and expected outputs

**When in doubt, hedge your claims.** "Simulated," "idealized upper bound," "under assumed," and "modeled" are honest descriptions that JOSS reviewers respect. Bold claims about novelty require substantiation that RAF doesn't have.

## Areas for Contribution

- **New Loop Types**: Implement additional acceleration loops (must implement `AccelerationLoop` contract)
- **Analysis Tools**: Enhance bottleneck detection and prioritization
- **Visualization**: Improve plots and dashboards
- **Documentation**: Tutorials, examples, API docs (reference JOSS requirements)
- **Integration**: Connect with quantum computing frameworks (Qiskit, PennyLane)
- **Benchmarks**: Create standardized benchmarks for loop evaluation
- **Real CDR**: Implement ClassicalShadow Regression mitigation (deferred to v0.3.0)
- **Backend Maintenance**: Keep device strings current as vendors retire/add hardware

## Code of Conduct

Be respectful and inclusive. We welcome contributors from all backgrounds.

## Questions?

Open an issue or reach out to the maintainers.
