# Changelog

All notable changes to GapClean will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.4] - 2026-04-05

### Added

- **High-level Python API** - New `clean_alignment()` function for easy programmatic use
  - Simple one-function interface: `from gapclean import clean_alignment`
  - Automatic temp file management (no manual cleanup needed)
  - Returns statistics dict with alignment metrics and timing
  - Optional `verbose` parameter for quiet operation in pipelines
  - Full docstring with examples for all modes
  - Perfect for Jupyter notebooks and bioinformatics pipelines
- **Exception classes exported from package root** for better error handling
  - `from gapclean import GapCleanError, InputValidationError, AlignmentError`
- **Updated visualization tutorial** - Jupyter notebook using new Python API
  - Demonstrates integration with matplotlib, Plotly, WebLogo
  - Shows Python API usage patterns
  - Example bioinformatics pipeline

### Changed

- **Simplified imports** - Clean API design
  - Old: `from gapclean.gapclean import ...` (still works)
  - New: `from gapclean import clean_alignment` (recommended)
- **Updated documentation** with Python API examples throughout
- **Version bump** to 1.0.4 in all version strings

### Improved

- **Much easier integration** into Python scripts and Jupyter notebooks
- **No need to manage temporary files** manually
- **Pythonic API design** following best practices
- **Better developer experience** with statistics return values

### Developer Notes

The CLI remains completely unchanged. This is a purely additive release for Python users.

**Migration Example:**

```python
# Old approach (still works, but more complex)
import tempfile
from gapclean.gapclean import flatten_fasta, gapclean_2d_chunk, ...

# New approach (recommended)
from gapclean import clean_alignment

stats = clean_alignment('input.fa', 'output.fa', threshold=50)
print(f"Removed {stats['columns_removed']} columns")
```

---

## [1.0.3] - 2026-04-05

### Added

- **Entropy-based gap removal modes** (`--entropy-min` and `--entropy-max` flags)
  - Calculate Shannon entropy for each column
  - `--entropy-min`: Remove conserved columns (keep variable regions) - for SNP detection
  - `--entropy-max`: Remove variable columns (keep conserved regions) - for alignment cleaning
  - Can use both flags together to keep moderate range
  - Useful for identifying variable/conserved regions
- **Comprehensive input validation**
  - File existence and readability checks
  - FASTA format validation
  - Parameter bounds checking
  - Clear, actionable error messages
- **Type hints** throughout codebase
  - Full Python type annotations
  - Better IDE support and autocomplete
  - Static type checking with mypy
- **Comprehensive test suite**
  - 48+ unit and integration tests
  - 69% code coverage
  - Tests for all three modes (threshold, seed, entropy)
  - Edge case testing
- **GitHub Actions CI/CD**
  - Automated testing on Windows, macOS, Linux
  - Python 3.8-3.12 compatibility testing
  - Automated PyPI publishing on tagged releases
  - Documentation deployment to GitHub Pages
- **Professional documentation**
  - Material for MkDocs documentation site
  - Comprehensive usage guides for all three modes
  - Advanced topics (chunking algorithm, performance, memory)
  - API reference for programmatic use
- **Custom exception classes**
  - `GapCleanError`: Base exception
  - `InputValidationError`: Input validation failures
  - `AlignmentError`: Alignment processing failures

### Changed

- **Removed `awk` dependency** - Now pure Python!
  - Cross-platform compatible (Windows, macOS, Linux)
  - `flatten_fasta()` rewritten in pure Python
  - 100% Python implementation
- **Improved error messages**
  - Contextual error messages with suggestions
  - Clear indication of what went wrong and how to fix it
  - Better error handling in `main()`
- **Updated version display** to 1.0.3 in CLI
- **Dynamic version management**
  - Version now read from `__init__.py` by `pyproject.toml`
  - Single source of truth for version number

### Fixed

- Windows compatibility (no longer requires `awk`)
- Better handling of edge cases (empty files, single sequences)
- More descriptive alignment validation errors

### Development

- Added development dependencies (`pytest`, `mypy`, `black`, `ruff`)
- Added documentation dependencies (`mkdocs-material`, `mkdocstrings`)
- Configured pytest, mypy, black, and ruff in `pyproject.toml`
- Set up pre-commit hooks (optional)

---

## [1.0.2] - 2026-02-15

### Changed

- Minor changes to help function
- README formatting improvements

### Fixed

- Minor bug fixes in `pyproject.toml`

---

## [1.0.1] - 2026-02-10

### Changed

- Migrated from `setup.py` to `pyproject.toml`
- Modern Python packaging standards

---

## [1.0.0] - 2026-01-20

### Added

- Initial release
- Threshold-based gap removal (`-t` flag)
- Seed-based gap removal (`-s` flag)
- 2D chunking algorithm for memory efficiency
- Progress bars with tqdm
- NumPy-based gap detection
- PyPI package availability

### Features

- Memory-efficient processing of large alignments
- Two gap removal modes
- Configurable chunk sizes
- Cross-platform (with `awk` dependency)

---

## Future Plans

### Planned for v1.1.0

- Improved test coverage (target: >90%)
- Performance optimizations
- Adaptive chunk sizing based on available RAM
- Optional parallel processing
- More output formats

### Potential Future Features

- GPU acceleration for gap counting
- Streaming mode for ultra-large alignments
- Additional entropy measures (besides Shannon)
- Quality score-based filtering
- Conservation analysis tools
- Alignment statistics reporting

---

## Links

- [GitHub Repository](https://github.com/arikat/GapClean)
- [PyPI Package](https://pypi.org/project/gapclean/)
- [Documentation](https://arikat.github.io/GapClean/)
- [Issue Tracker](https://github.com/arikat/GapClean/issues)

---

## How to Upgrade

```bash
pip install --upgrade gapclean
```

## Migration Notes

### From 1.0.3 to 1.0.4

**Breaking Changes:** None! All existing code works identically.

**New Features:**
- Python API with `clean_alignment()` function
- Statistics returned as dict
- Auto-managed temp files

**Recommendations:**
- Python users: Switch to `clean_alignment()` for simpler code
- Jupyter users: See the updated visualization tutorial
- Pipeline developers: Use `verbose=False` for cleaner logs

### Example Migration - Python

```python
# Old approach (still works)
import tempfile
from gapclean.gapclean import flatten_fasta, split_headers_vs_sequences, gapclean_2d_chunk, recombine_headers_and_sequences

# Manual temp file management
with tempfile.TemporaryDirectory() as tmpdir:
    # ... many lines of boilerplate ...

# New approach (recommended)
from gapclean import clean_alignment

stats = clean_alignment('input.fa', 'output.fa', threshold=50)
```

**CLI unchanged** - All bash commands work exactly the same!

### From 1.0.2 to 1.0.3

**Breaking Changes:** None! All existing commands work identically.

**New Features:**
- New `--entropy-min` and `--entropy-max` flags (optional)
- Better error messages (automatic)
- Windows support without installing `awk` (automatic)

**Recommendations:**
- Windows users: No need to install `awk` anymore!
- All users: Try the new entropy mode for variable region detection
- Developers: Update imports if using GapClean as a library (new exception classes)

### Example Migration - CLI

```bash
# Old command (still works)
gapclean -i alignment.fa -o cleaned.fa -t 75

# New entropy mode options
gapclean -i alignment.fa -o cleaned.fa --entropy-max 1.5
gapclean -i alignment.fa -o cleaned.fa --entropy-min 1.0
```

No changes needed to existing scripts!
