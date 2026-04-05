# Changelog

All notable changes to GapClean will be documented in this file.

## [1.0.3] - 2026-04-05

### Added
- Entropy-based gap removal mode (`-e/--entropy` flag)
- Comprehensive input validation with clear error messages
- Type hints throughout codebase
- Comprehensive test suite (48+ tests)
- GitHub Actions CI/CD (Windows, macOS, Linux × Python 3.8-3.12)
- Professional documentation with MkDocs Material
- Custom exception classes (GapCleanError, InputValidationError, AlignmentError)

### Changed
- Removed `awk` dependency - pure Python implementation
- Improved error messages with context and suggestions
- Dynamic version management (single source of truth)

### Fixed
- Windows compatibility (no longer requires `awk`)
- Better handling of edge cases

## [1.0.2] - 2026-02-15

### Changed
- Minor changes to help function
- README formatting improvements

## [1.0.1] - 2026-02-10

### Changed
- Migrated from `setup.py` to `pyproject.toml`

## [1.0.0] - 2026-01-20

### Added
- Initial release
- Threshold-based gap removal
- Seed-based gap removal
- 2D chunking algorithm
- PyPI package
