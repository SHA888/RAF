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

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all public functions/classes
- Format code with `black`
- Sort imports with `isort`

### Testing

- Write tests for new features
- Ensure all tests pass before submitting
- Aim for >80% code coverage

### Documentation

- Update README.md if needed
- Add docstrings to new code
- Update examples if API changes

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/RAF.git
cd RAF

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Format code
black raf/
isort raf/
```

## Areas for Contribution

- **New Loop Types**: Implement additional acceleration loops
- **Analysis Tools**: Enhance bottleneck detection and prioritization
- **Visualization**: Improve plots and dashboards
- **Documentation**: Tutorials, examples, API docs
- **Integration**: Connect with quantum computing frameworks (Qiskit, PennyLane)
- **Benchmarks**: Create standardized benchmarks for loop evaluation

## Code of Conduct

Be respectful and inclusive. We welcome contributors from all backgrounds.

## Questions?

Open an issue or reach out to the maintainers.
