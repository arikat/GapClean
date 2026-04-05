# Changelog

All notable changes to GapClean will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.3] - 2026-04-05

### Added

- **Entropy-based gap removal mode** (`-e/--entropy` flag)
  - Calculate Shannon entropy for each column
  - Remove columns below entropy threshold
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

### From 1.0.2 to 1.0.3

**Breaking Changes:** None! All existing commands work identically.

**New Features:**
- New `-e/--entropy` flag (optional)
- Better error messages (automatic)
- Windows support without installing `awk` (automatic)

**Recommendations:**
- Windows users: No need to install `awk` anymore!
- All users: Try the new entropy mode for variable region detection
- Developers: Update imports if using GapClean as a library (new exception classes)

### Example Migration

```bash
# Old command (still works)
gapclean -i alignment.fa -o cleaned.fa -t 75

# New entropy mode option
gapclean -i alignment.fa -o cleaned.fa -e 1.5
```

No changes needed to existing scripts!
