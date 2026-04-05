# Changelog

All notable changes to GapClean will be documented in this file.

## [1.0.5] - 2026-04-05

### Added
- **Multi-format support** - Stockholm, Clustal, PHYLIP formats now supported
  - Auto-detect input format from file extension or content
  - Convert between formats: Stockholm (.sto), Clustal (.aln), PHYLIP (.phy), FASTA (.fa)
  - New `--input-format` and `--output-format` CLI flags
  - New `input_format` and `output_format` parameters for `clean_alignment()` API
  - Automatic format conversion handled internally
- **Format auto-detection** - No need to specify format in most cases
  - Detects Stockholm (`# STOCKHOLM` header)
  - Detects FASTA (`>` header)
  - Detects Clustal (`CLUSTAL` header)
  - Detects PHYLIP (numeric first line)
  - Falls back to extension-based detection
- **Progress bars for format conversion** 
  - Shows tqdm progress when converting TO FASTA (per-sequence progress)
  - Time estimates and warnings when converting FROM FASTA to slow formats
  - Prevents users from canceling during long Stockholm conversions

### Changed
- **Added BioPython dependency** (>=1.80) for format conversion
- **Always defaults to FASTA output** for performance
  - Stockholm/Clustal/PHYLIP writers are very slow for large alignments (100K+ sequences)
  - Use `--output-format` explicitly if you need non-FASTA output
  - Warning displayed when requesting non-FASTA format for large datasets
- Format validation now happens after conversion to FASTA
- Temp file cleanup includes converted input files
- Warning message if `--output-format` conflicts with file extension

### Fixed
- **Stockholm format parsing** - Pfam alignments now work correctly
- **Output format auto-detection** - Respects output filename extension instead of defaulting to input format
- Proper sequence counting for non-FASTA inputs
- Better error messages for format conversion failures

### Examples

```bash
# Stockholm input → FASTA output (auto-detected, fast)
gapclean -i pfam_seed.sto -o cleaned.fa -t 75

# Stockholm input → Stockholm output (explicit, slow for large alignments)
gapclean -i pfam_seed.sto -o cleaned.sto --output-format stockholm -t 75

# Python API with Stockholm (defaults to FASTA output)
from gapclean import clean_alignment
stats = clean_alignment('pfam.sto', 'cleaned.fa', threshold=70)
```

### Performance Note

**Stockholm/Clustal/PHYLIP output is significantly slower** than FASTA for large alignments due to BioPython's writer implementations. For the Pfam GT2 family (157K sequences):

- FASTA output: 11 seconds total
- Stockholm output: ~5+ minutes just for format conversion

**Recommendation:** Always use FASTA output unless you specifically need the metadata/markup of other formats.

## [1.0.4] - 2026-04-05

### Added
- **High-level Python API**: New `clean_alignment()` function for easy programmatic use
  - Simple one-function interface: `from gapclean import clean_alignment`
  - Automatic temp file management (no manual cleanup needed)
  - Returns statistics dict with alignment metrics and timing
  - Optional `verbose` parameter for quiet operation in pipelines
  - Full docstring with examples for all modes
- Exception classes now exported from package root for better error handling
- Comprehensive example Jupyter notebook using the new API

### Changed
- Updated visualization tutorial to use new `clean_alignment()` API
- Cleaner imports: `from gapclean import clean_alignment` instead of internal modules

### Improved
- Much easier integration into Python scripts and Jupyter notebooks
- No need to manage temporary files manually
- Pythonic API design following best practices

## [1.0.3] - 2026-04-05

### Added
- Entropy-based gap removal modes (`--entropy-min` and `--entropy-max` flags)
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
