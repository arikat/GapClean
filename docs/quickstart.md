# Quick Start

GapClean can be used from the command line or as a Python library.

## Command Line Interface

Let's clean a gappy alignment using threshold mode:

```bash
gapclean -i input.fa -o output.fa -t 75
```

This removes columns where >75% of sequences have gaps.

## Python API (NEW!)

Or use it programmatically in Python:

```python
from gapclean import clean_alignment

stats = clean_alignment(
    input_file='input.fa',
    output_file='output.fa',
    threshold=75
)

print(f"Removed {stats['columns_removed']} columns in {stats['elapsed_seconds']:.1f}s")
```

Perfect for Jupyter notebooks and bioinformatics pipelines!

## Understanding the Output

GapClean provides progress information during execution:

```
====================================================
                 GapClean (v1.0.4)
                 Aarya Venkat, PhD
====================================================

[GAPCLEAN] (1) Flattening input FASTA...
[GAPCLEAN] (2) Splitting headers and sequence bodies...
[GAPCLEAN] (3) It's Gappin' Time...

[GAPCLEAN] Number of Sequences = 100
[GAPCLEAN] Alignment Length = 5000
[GAPCLEAN] Removing columns with > 75% gaps

[GAPCLEAN] Counting gaps: 100%|████████| 5000/5000
[GAPCLEAN] Cleaning gaps: 100%|████████| 5000/5000

[GAPCLEAN] Final alignment length: 3420 columns (was 5000)

[GAPCLEAN] (4) Stitching back headers to sequence bodies...
[GAPCLEAN] took 5s to complete. Cleaned alignment located at output.fa.
```

## Command Line Options

### Required Arguments

- `-i, --input`: Input FASTA file (aligned sequences)
- `-o, --output`: Output FASTA file (cleaned sequences)

### Gap Removal Mode (choose one)

- `-t, --threshold`: Percentage threshold (0-100)
- `-s, --seed`: Seed sequence index (0-based)
- `-e, --entropy`: Entropy threshold (bits)

### Optional Arguments

- `--row-chunk-size`: Sequences to process at once (default: 5000)
- `--col-chunk-size`: Columns to process at once (default: 5000)

## Common Examples

### Example 1: Threshold Mode

Remove columns with more than 50% gaps:

```bash
gapclean -i alignment.fa -o cleaned.fa -t 50
```

### Example 2: Seed Mode

Remove gaps relative to the first sequence:

```bash
gapclean -i alignment.fa -o cleaned.fa -s 0
```

Use the third sequence as seed:

```bash
gapclean -i alignment.fa -o cleaned.fa -s 2
```

### Example 3: Entropy Mode

Remove columns with low sequence diversity:

```bash
# DNA alignment
gapclean -i dna_alignment.fa -o variable_positions.fa -e 1.0

# Protein alignment
gapclean -i protein_alignment.fa -o variable_positions.fa -e 2.0
```

### Example 4: Memory-Constrained Systems

For very large alignments on systems with limited RAM:

```bash
gapclean -i huge_alignment.fa -o cleaned.fa -t 75 \
  --row-chunk-size 1000 --col-chunk-size 1000
```

## Python API Examples

### Basic Usage

```python
from gapclean import clean_alignment

# Threshold mode
stats = clean_alignment('input.fa', 'output.fa', threshold=50)

# Seed mode
stats = clean_alignment('input.fa', 'output.fa', seed_index=0)

# Entropy mode - keep conserved regions
stats = clean_alignment('input.fa', 'output.fa', entropy_max=1.5)

# Entropy mode - keep variable regions
stats = clean_alignment('input.fa', 'output.fa', entropy_min=1.0)
```

### Using Statistics

The function returns a dictionary with useful metrics:

```python
stats = clean_alignment('input.fa', 'output.fa', threshold=75)

print(f"Input: {stats['input_sequences']} sequences")
print(f"Original length: {stats['input_length']}")
print(f"Cleaned length: {stats['output_length']}")
print(f"Removed: {stats['columns_removed']} columns")
print(f"Time: {stats['elapsed_seconds']:.2f} seconds")
```

### Quiet Mode for Pipelines

Disable progress output:

```python
stats = clean_alignment(
    'input.fa',
    'output.fa',
    threshold=75,
    verbose=False  # No output
)
```

### In a Loop

Process multiple alignments:

```python
from pathlib import Path

input_dir = Path('alignments')
output_dir = Path('cleaned')
output_dir.mkdir(exist_ok=True)

for fasta_file in input_dir.glob('*.fa'):
    stats = clean_alignment(
        input_file=str(fasta_file),
        output_file=str(output_dir / fasta_file.name),
        threshold=50,
        verbose=False
    )
    print(f"{fasta_file.name}: removed {stats['columns_removed']} columns")
```

### Error Handling

```python
from gapclean import clean_alignment, GapCleanError

try:
    stats = clean_alignment('input.fa', 'output.fa', threshold=50)
except GapCleanError as e:
    print(f"Error: {e}")
```

## Next Steps

- [Python API Reference](api/reference.md) - Full API documentation
- [Threshold Mode Guide](usage/threshold-mode.md)
- [Seed Mode Guide](usage/seed-mode.md)
- [Entropy Mode Guide](usage/entropy-mode.md)
- [Performance Tuning](advanced/performance.md)
