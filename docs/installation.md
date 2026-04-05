# Installation

## Prerequisites

- Python 3.8 or higher
- pip package manager

## Install from PyPI

The easiest way to install GapClean is via pip:

```bash
pip install gapclean
```

## Install from Source

For development or the latest features:

```bash
# Clone the repository
git clone https://github.com/arikat/GapClean.git
cd GapClean

# Install in editable mode
pip install -e .
```

## Development Installation

To install with development dependencies for testing and documentation:

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Install with documentation dependencies
pip install -e ".[docs]"

# Install both
pip install -e ".[dev,docs]"
```

## Verify Installation

Check that GapClean is installed correctly:

```bash
gapclean -h
```

You should see the help message with version 1.0.3.

## Upgrading

To upgrade to the latest version:

```bash
pip install --upgrade gapclean
```

## Uninstalling

To remove GapClean:

```bash
pip uninstall gapclean
```

## Dependencies

GapClean has minimal dependencies:

- **numpy**: For efficient numerical operations
- **tqdm**: For progress bars

These are automatically installed when you install GapClean.
