# GapClean (v1.0.3) 
###### Written by Aarya Venkat, PhD

<img src="gapclean.png" width="350">

[![Tests](https://github.com/arikat/GapClean/workflows/Tests/badge.svg)](https://github.com/arikat/GapClean/actions)
[![PyPI version](https://badge.fury.io/py/gapclean.svg)](https://pypi.org/project/gapclean/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Description

GapClean is a memory-efficient tool for cleaning gappy multiple sequence alignments in FASTA format. It offers three powerful modes for gap removal:

- **Threshold Mode**: Remove columns exceeding a gap percentage
- **Seed Mode**: Remove gaps relative to a reference sequence
- **Entropy Mode**: Remove low-diversity columns using Shannon entropy

**NEW in v1.0.3:**
- Entropy-based gap removal mode
- Pure Python implementation (Windows compatible, no `awk` required!)
- Comprehensive input validation
- Full type hints
- Extensive test coverage
- Professional documentation site

## Features

- **Memory Efficient**: Process alignments larger than RAM using 2D chunking
- **Fast**: Optimized NumPy operations for gap detection
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Flexible**: Three gap removal modes for different use cases
- **Well-Tested**: 48+ tests ensuring reliability

## Installation

```bash
pip install gapclean
```

**Requirements**: Python 3.8+

## Quick Start

### Threshold Mode
Remove columns with >75% gaps:
```bash
gapclean -i input.fa -o output.fa -t 75
```

### Seed Mode
Remove gaps relative to first sequence:
```bash
gapclean -i input.fa -o output.fa -s 0
```

### Entropy Mode (NEW!)
Remove low-entropy (conserved) columns:
```bash
gapclean -i input.fa -o output.fa -e 1.5
```

## Usage

```
gapclean [options]

Required Arguments:
  -i, --input    Input aligned FASTA file
  -o, --output   Output cleaned FASTA file

Gap Removal Mode (choose one):
  -t, --threshold    Percentage threshold (0-100)
  -s, --seed         Seed sequence index (0-based)
  -e, --entropy      Entropy threshold (bits)

Optional Arguments:
  --row-chunk-size   Sequences per chunk (default: 5000)
  --col-chunk-size   Columns per chunk (default: 5000)
  -h, --help         Show help message
```

## Examples

### Phylogenetic Analysis
```bash
# Remove very gappy columns before tree building
gapclean -i gene_alignment.fa -o cleaned.fa -t 80
```

### Variant Analysis
```bash
# Remove gaps relative to reference genome (first sequence)
gapclean -i variants.fa -o positions.fa -s 0
```

### SNP Detection
```bash
# Keep only variable positions (DNA)
gapclean -i population.fa -o snps.fa -e 1.0
```

### Memory-Constrained Systems
```bash
# Process large alignment with limited RAM
gapclean -i huge_alignment.fa -o cleaned.fa -t 75 \
  --row-chunk-size 1000 --col-chunk-size 1000
```

## Documentation

**Full documentation available at: [https://arikat.github.io/GapClean/](https://arikat.github.io/GapClean/)**

- [Installation Guide](https://arikat.github.io/GapClean/installation/)
- [Quick Start Tutorial](https://arikat.github.io/GapClean/quickstart/)
- [Usage Guides](https://arikat.github.io/GapClean/usage/threshold-mode/)
- [Advanced Topics](https://arikat.github.io/GapClean/advanced/chunking/)
- [API Reference](https://arikat.github.io/GapClean/api/reference/)

## What's New in v1.0.3

- **Entropy-based gap removal**: Identify variable and conserved regions
- **Windows compatibility**: Pure Python, no external dependencies
- **Better error messages**: Clear, actionable feedback
- **Type hints**: Full type annotations for better IDE support
- **Comprehensive tests**: 48+ tests for reliability
- **Professional docs**: Beautiful Material for MkDocs site
- **CI/CD**: Automated testing on Windows, macOS, Linux

See [CHANGELOG](https://arikat.github.io/GapClean/changelog/) for full details.

## Citation

If you use GapClean in your research, please cite:

```
Venkat, A. (2026). GapClean: Memory-efficient gap removal for multiple sequence alignments.
https://github.com/arikat/GapClean
```

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](https://arikat.github.io/GapClean/contributing/) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: https://arikat.github.io/GapClean/
- **Issues**: https://github.com/arikat/GapClean/issues
- **PyPI**: https://pypi.org/project/gapclean/

---

Thank Gappy for his service. He is a retired detective.
