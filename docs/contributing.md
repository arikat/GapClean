# Contributing to GapClean

Thank you for your interest in contributing to GapClean! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- pip

### Development Setup

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/GapClean.git
   cd GapClean
   ```

3. **Install in development mode**:
   ```bash
   pip install -e ".[dev,docs]"
   ```

4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Making Changes

1. **Write your code**
   - Follow existing code style
   - Add type hints to all functions
   - Keep functions focused and well-documented

2. **Write tests**
   - Add tests for new functionality
   - Ensure existing tests still pass
   - Aim for >90% code coverage

3. **Run tests**:
   ```bash
   pytest tests/ -v --cov=gapclean --cov-report=term
   ```

4. **Check types**:
   ```bash
   mypy gapclean
   ```

5. **Format code**:
   ```bash
   black gapclean tests
   ruff check gapclean tests
   ```

### Testing

We use pytest for testing. All tests must pass before submitting a pull request.

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=gapclean --cov-report=term

# Run specific test file
pytest tests/test_validation.py

# Run specific test
pytest tests/test_validation.py::test_validate_input_file_exists
```

### Code Style

We follow PEP 8 with some modifications:

- Line length: 88 characters (Black default)
- Type hints required for all functions
- Docstrings required for public functions

**Automated formatting**:
```bash
# Format with Black
black gapclean tests

# Lint with Ruff
ruff check gapclean tests
```

### Type Checking

All code must pass mypy type checking:

```bash
mypy gapclean
```

## Pull Request Process

1. **Update documentation**
   - Add docstrings to new functions
   - Update relevant `.md` files in `docs/`
   - Update `CHANGELOG.md` with your changes

2. **Ensure tests pass**
   - All existing tests must pass
   - New features must have tests
   - Coverage should not decrease

3. **Submit your pull request**
   - Provide a clear description of changes
   - Reference any related issues
   - Include examples if applicable

4. **Code review**
   - Address reviewer feedback
   - Make requested changes
   - Keep discussion professional and constructive

5. **Merge**
   - Maintainers will merge when approved
   - Delete your branch after merge

## Coding Guidelines

### Function Structure

```python
def function_name(param1: str, param2: int = 5) -> None:
    """
    Brief description of what the function does.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 5)

    Returns:
        Description of return value (if applicable)

    Raises:
        ErrorType: When this error occurs
    """
    # Implementation
    pass
```

### Error Handling

Use custom exception classes:

```python
from gapclean.gapclean import InputValidationError, AlignmentError

# Validation errors
if not os.path.exists(filepath):
    raise InputValidationError(
        f"\n[ERROR] File not found: {filepath}\n"
        f"  Suggestion: Check the file path and try again."
    )

# Processing errors
if len(seq) != expected_len:
    raise AlignmentError(
        f"\n[ERROR] Sequence length mismatch\n"
        f"  Expected: {expected_len}\n"
        f"  Got: {len(seq)}"
    )
```

### Adding Tests

Create tests in the appropriate file in `tests/`:

```python
# tests/test_new_feature.py

import pytest
from gapclean.gapclean import new_function, InputValidationError

def test_new_function_success(valid_alignment):
    """Test new function with valid input."""
    result = new_function(valid_alignment)
    assert result is not None

def test_new_function_invalid_input():
    """Test new function with invalid input."""
    with pytest.raises(InputValidationError):
        new_function("invalid")
```

## Documentation

### Building Documentation

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Serve locally
mkdocs serve

# Build static site
mkdocs build
```

Documentation is written in Markdown and built with MkDocs Material.

### Adding Documentation Pages

1. Create `.md` file in `docs/` directory
2. Add to navigation in `mkdocs.yml`
3. Follow existing page structure
4. Include code examples

## Release Process

(For maintainers)

1. **Update version**:
   - Edit `gapclean/__init__.py`
   - Update `CHANGELOG.md`

2. **Create release commit**:
   ```bash
   git add gapclean/__init__.py CHANGELOG.md
   git commit -m "Release v1.0.X"
   git push origin main
   ```

3. **Tag release**:
   ```bash
   git tag -a v1.0.X -m "Release v1.0.X"
   git push origin v1.0.X
   ```

4. **GitHub Actions** will automatically:
   - Run tests on all platforms
   - Build package
   - Publish to PyPI

## Reporting Issues

### Bug Reports

Include:

- GapClean version (`gapclean --version` or `import gapclean; print(gapclean.__version__)`)
- Python version
- Operating system
- Steps to reproduce
- Expected vs. actual behavior
- Error messages (if any)

### Feature Requests

Include:

- Use case description
- Why existing features don't solve the problem
- Proposed solution (if any)
- Examples of how it would be used

## Community Guidelines

- Be respectful and professional
- Provide constructive feedback
- Help others learn
- Credit others' work
- Follow the code of conduct

## Questions?

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: [Maintainer email if applicable]

## License

By contributing to GapClean, you agree that your contributions will be licensed under the MIT License.

## Acknowledgments

Thank you to all contributors who help make GapClean better!

---

**Happy coding!**
