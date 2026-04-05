# API Reference

GapClean can be imported as a Python library for programmatic use.

## Installation

```bash
pip install gapclean
```

## Importing

```python
from gapclean.gapclean import (
    flatten_fasta,
    split_headers_vs_sequences,
    gapclean_2d_chunk,
    recombine_headers_and_sequences,
    calculate_column_entropy
)
```

## Functions

### flatten_fasta()

Flatten multiline FASTA to single-line format.

```python
def flatten_fasta(input_file: str, output_file: str) -> None
```

**Parameters:**

- `input_file` (str): Path to input FASTA file (may have multiline sequences)
- `output_file` (str): Path to output FASTA file (single-line sequences)

**Example:**

```python
from gapclean.gapclean import flatten_fasta

flatten_fasta("multiline.fa", "flattened.fa")
```

---

### split_headers_vs_sequences()

Separate FASTA headers from sequence bodies.

```python
def split_headers_vs_sequences(
    input_file: str, 
    headers_file: str, 
    sequences_file: str
) -> None
```

**Parameters:**

- `input_file` (str): Path to input FASTA file
- `headers_file` (str): Path to output file for headers
- `sequences_file` (str): Path to output file for sequences

**Example:**

```python
from gapclean.gapclean import split_headers_vs_sequences

split_headers_vs_sequences("input.fa", "headers.txt", "sequences.txt")
```

---

### gapclean_2d_chunk()

Core gap removal function using 2D chunking.

```python
def gapclean_2d_chunk(
    input_sequences_file: str,
    output_sequences_file: str,
    threshold: Optional[int] = None,
    seed_index: Optional[int] = None,
    entropy_threshold: Optional[float] = None,
    row_chunk_size: int = 5000,
    col_chunk_size: int = 5000
) -> None
```

**Parameters:**

- `input_sequences_file` (str): Path to file containing sequences only (no headers)
- `output_sequences_file` (str): Path to output file for cleaned sequences
- `threshold` (int, optional): Percentage threshold (0-100) for gap removal
- `seed_index` (int, optional): Remove columns with gaps in seed sequence (0-based index)
- `entropy_threshold` (float, optional): Remove columns with entropy < threshold bits
- `row_chunk_size` (int): Number of sequences to process at once (default: 5000)
- `col_chunk_size` (int): Number of alignment columns to process at once (default: 5000)

**Note:** Exactly one of `threshold`, `seed_index`, or `entropy_threshold` must be provided.

**Example:**

```python
from gapclean.gapclean import gapclean_2d_chunk

# Threshold mode
gapclean_2d_chunk(
    "sequences.txt",
    "cleaned_sequences.txt",
    threshold=75
)

# Seed mode
gapclean_2d_chunk(
    "sequences.txt",
    "cleaned_sequences.txt",
    seed_index=0
)

# Entropy mode
gapclean_2d_chunk(
    "sequences.txt",
    "cleaned_sequences.txt",
    entropy_threshold=1.5
)

# Custom chunk sizes
gapclean_2d_chunk(
    "sequences.txt",
    "cleaned_sequences.txt",
    threshold=75,
    row_chunk_size=10000,
    col_chunk_size=10000
)
```

---

### recombine_headers_and_sequences()

Merge headers and cleaned sequences back into FASTA format.

```python
def recombine_headers_and_sequences(
    headers_file: str, 
    sequences_file: str, 
    output_fasta: str
) -> None
```

**Parameters:**

- `headers_file` (str): Path to file containing headers
- `sequences_file` (str): Path to file containing sequences
- `output_fasta` (str): Path to output FASTA file

**Example:**

```python
from gapclean.gapclean import recombine_headers_and_sequences

recombine_headers_and_sequences(
    "headers.txt",
    "cleaned_sequences.txt",
    "output.fa"
)
```

---

### calculate_column_entropy()

Calculate Shannon entropy for a column of characters.

```python
def calculate_column_entropy(column_chars: np.ndarray) -> float
```

**Parameters:**

- `column_chars` (numpy.ndarray): Array of ASCII values for one column

**Returns:**

- `float`: Shannon entropy value in bits (higher = more diverse)

**Example:**

```python
import numpy as np
from gapclean.gapclean import calculate_column_entropy

# Column with all same character (entropy = 0)
column = np.array([ord('A')] * 10, dtype=np.uint8)
entropy = calculate_column_entropy(column)
print(f"Entropy: {entropy}")  # Output: 0.0

# Column with equal mix of 4 characters (entropy ≈ 2.0)
column = np.array(
    [ord('A')] * 25 + [ord('T')] * 25 + 
    [ord('C')] * 25 + [ord('G')] * 25,
    dtype=np.uint8
)
entropy = calculate_column_entropy(column)
print(f"Entropy: {entropy}")  # Output: ~2.0
```

---

## Exception Classes

### GapCleanError

Base exception for GapClean errors.

```python
class GapCleanError(Exception)
```

### InputValidationError

Raised when input validation fails.

```python
class InputValidationError(GapCleanError)
```

### AlignmentError

Raised when alignment processing fails.

```python
class AlignmentError(GapCleanError)
```

**Example:**

```python
from gapclean.gapclean import gapclean_2d_chunk, AlignmentError

try:
    gapclean_2d_chunk("sequences.txt", "output.txt", threshold=75)
except AlignmentError as e:
    print(f"Alignment error: {e}")
```

---

## Complete Workflow Example

```python
import tempfile
import os
from gapclean.gapclean import (
    flatten_fasta,
    split_headers_vs_sequences,
    gapclean_2d_chunk,
    recombine_headers_and_sequences
)

def clean_alignment(input_fasta, output_fasta, threshold=75):
    """Complete gap cleaning workflow."""
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Temporary file paths
        flat_file = os.path.join(tmpdir, "flat.fa")
        headers_file = os.path.join(tmpdir, "headers.txt")
        seqs_file = os.path.join(tmpdir, "sequences.txt")
        cleaned_seqs = os.path.join(tmpdir, "cleaned.txt")
        
        # Step 1: Flatten multiline FASTA
        flatten_fasta(input_fasta, flat_file)
        
        # Step 2: Split headers and sequences
        split_headers_vs_sequences(flat_file, headers_file, seqs_file)
        
        # Step 3: Clean gaps
        gapclean_2d_chunk(
            seqs_file,
            cleaned_seqs,
            threshold=threshold
        )
        
        # Step 4: Recombine
        recombine_headers_and_sequences(
            headers_file,
            cleaned_seqs,
            output_fasta
        )

# Use it
clean_alignment("input.fa", "cleaned.fa", threshold=75)
```

---

## Version Information

```python
import gapclean

print(gapclean.__version__)  # Output: 1.0.3
```

---

## Type Hints

All functions include type hints for better IDE support and type checking:

```python
from typing import Optional
import numpy as np

def gapclean_2d_chunk(
    input_sequences_file: str,
    output_sequences_file: str,
    threshold: Optional[int] = None,
    seed_index: Optional[int] = None,
    entropy_threshold: Optional[float] = None,
    row_chunk_size: int = 5000,
    col_chunk_size: int = 5000
) -> None:
    ...
```

Use mypy for static type checking:

```bash
mypy your_script.py
```
