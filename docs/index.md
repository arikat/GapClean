# GapClean

Clean up large gappy multiple sequence alignments with memory-efficient processing.

## Why GapClean?

- **Memory Efficient**: Process massive alignments with 2D chunking algorithm
- **Fast**: Optimized NumPy operations for gap detection
- **Flexible**: Three removal modes (threshold, seed, entropy)
- **Cross-Platform**: Pure Python implementation (Windows, macOS, Linux)

## Quick Example

```bash
# Remove columns with >75% gaps
gapclean -i alignment.fa -o cleaned.fa -t 75

# Remove gaps relative to first sequence
gapclean -i alignment.fa -o cleaned.fa -s 0

# Remove low-entropy columns
gapclean -i alignment.fa -o cleaned.fa -e 1.5
```

## Features

### Threshold Mode
Remove columns exceeding a gap percentage threshold.

```bash
gapclean -i input.fa -o output.fa -t 75
```

### Seed Mode
Remove gaps relative to a reference sequence.

```bash
gapclean -i input.fa -o output.fa -s 0
```

### Entropy Mode
Remove low-diversity columns using Shannon entropy.

```bash
gapclean -i input.fa -o output.fa -e 1.5
```

## How It Works

GapClean uses a **2D chunking algorithm** that processes alignments in rectangular blocks. This means you can clean alignments larger than your available RAM by processing rows (sequences) and columns in manageable chunks.

[Get Started →](quickstart.md){ .md-button .md-button--primary }
[View on GitHub →](https://github.com/arikat/GapClean){ .md-button }

## Use Cases

- **Phylogenetic Analysis**: Remove gappy columns before tree building
- **Structural Analysis**: Clean alignments for structure prediction
- **Conservation Analysis**: Remove low-information columns
- **Visualization**: Create cleaner, more readable alignments

## Installation

```bash
pip install gapclean
```

## Quick Start

```bash
# Basic usage with threshold mode
gapclean -i my_alignment.fasta -o cleaned.fasta -t 50

# Check the help
gapclean -h
```

See the [Quick Start Guide](quickstart.md) for detailed examples.
