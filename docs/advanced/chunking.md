# 2D Chunking Algorithm

Understanding GapClean's memory-efficient processing.

## The Problem

Large multiple sequence alignments can exceed available RAM:

- 10,000 sequences × 100,000 positions = 1 GB of data
- Loading everything at once causes memory errors
- Traditional tools fail on memory-constrained systems

## The Solution: 2D Chunking

GapClean processes alignments in rectangular blocks, handling both rows (sequences) and columns in chunks.

```
┌─────────────────────────┐
│ ████░░░░░░░░░░░░░░░░░░░ │ ← Row chunks
│ ████░░░░░░░░░░░░░░░░░░░ │   (5000 sequences)
│ ████░░░░░░░░░░░░░░░░░░░ │
│ ░░░░░░░░░░░░░░░░░░░░░░░ │
└─────────────────────────┘
  ↑
  Column chunks (5000 positions)
```

## How It Works

### Step 1: Divide into Chunks

The alignment is divided into:

- **Row chunks**: Groups of sequences (default: 5000)
- **Column chunks**: Groups of alignment positions (default: 5000)

### Step 2: Process Block by Block

For threshold mode:

1. For each column chunk:
   - For each row chunk:
     - Count gaps in the current block
   - Accumulate gap counts across all row chunks
2. Determine which columns to remove based on gap percentages
3. For each column chunk:
   - For each row chunk:
     - Apply the mask to keep/remove columns

This way, only a small portion of data is in memory at once.

## Example

Alignment: 10,000 sequences × 50,000 positions

With default chunks (5000 × 5000):

1. **Row chunks**: 10,000 / 5000 = 2 chunks
2. **Column chunks**: 50,000 / 5000 = 10 chunks
3. **Total blocks**: 2 × 10 = 20 blocks processed

Memory usage: ~5000 × 5000 = 25M positions at once (vs. 500M for full alignment)

## Chunk Size Selection

### Default (5000 × 5000)
```bash
gapclean -i alignment.fa -o output.fa -t 75
```

**Good for**: Most alignments on standard computers (8-16 GB RAM)

### Small Chunks (Memory-Constrained)
```bash
gapclean -i alignment.fa -o output.fa -t 75 \
  --row-chunk-size 1000 --col-chunk-size 1000
```

**Good for**:
- Very large alignments
- Systems with limited RAM (< 4 GB)
- Running on shared systems

**Trade-off**: Slightly slower due to more I/O operations

### Large Chunks (High-Memory Systems)
```bash
gapclean -i alignment.fa -o output.fa -t 75 \
  --row-chunk-size 10000 --col-chunk-size 10000
```

**Good for**:
- Systems with lots of RAM (> 32 GB)
- Smaller alignments
- Faster processing

**Trade-off**: Higher memory usage

## Performance Characteristics

### Time Complexity

- Threshold mode: O(n × m) where n = sequences, m = positions
- Seed mode: O(m) - just checks one sequence
- Entropy mode: O(n × m) - must examine all positions

All modes benefit equally from chunking.

### Memory Complexity

Without chunking: O(n × m)

With chunking: O(row_chunk × col_chunk)

**Example**:
- Alignment: 10,000 × 100,000 = 1 GB
- With chunks 5000 × 5000: 25 MB peak memory
- **40× reduction** in memory usage!

## Algorithm Details

### Phase 1: Gap Counting (Threshold Mode)

```python
gap_counts = zeros(num_columns)

for col_chunk in column_chunks:
    for row_chunk in row_chunks:
        # Load small block
        block = load_block(row_chunk, col_chunk)
        # Count gaps in block
        gap_counts[col_chunk] += count_gaps(block)

# Determine which columns to remove
mask = gap_counts / num_sequences > threshold
```

### Phase 2: Filtering

```python
filtered = []

for col_chunk in column_chunks:
    for row_chunk in row_chunks:
        # Load small block
        block = load_block(row_chunk, col_chunk)
        # Apply mask to keep/remove columns
        filtered_block = block[:, mask[col_chunk]]
        filtered.append(filtered_block)
```

## Tips for Optimization

### Estimate Memory Usage

```
memory_mb = (row_chunk_size × col_chunk_size) / 1,000,000
```

For default 5000 × 5000 = ~25 MB

### Balance Speed vs. Memory

- Larger chunks = faster, more memory
- Smaller chunks = slower, less memory
- Sweet spot: chunks that fit in L3 cache (few MB)

### Rule of Thumb

Set chunks so that `row_chunk × col_chunk < available_RAM / 10`

Example with 8 GB RAM:
- Available: ~800 MB for chunks
- Max chunk: sqrt(800M) ≈ 28,000
- Safe default: 5,000 × 5,000 = 25M ✓

## Why 2D Chunking?

### Alternative: 1D Chunking (Rows Only)

```python
for row_chunk in row_chunks:
    load_all_columns(row_chunk)  # Still uses lots of memory!
```

Problem: Must load all columns for each row chunk.

### Alternative: Streaming

```python
for row in sequences:
    process(row)  # Process one at a time
```

Problem: Can't accumulate statistics across sequences efficiently.

### 2D Chunking: Best of Both

- Processes rows in chunks (like streaming)
- Processes columns in chunks (memory efficient)
- Can still accumulate statistics (unlike pure streaming)
- Cache-friendly access patterns

## Future Optimizations

Potential improvements:

- Adaptive chunk sizing based on available RAM
- Parallel processing of independent chunks
- Disk-based processing for extreme cases
- GPU acceleration for gap counting

The current implementation prioritizes simplicity and reliability while maintaining excellent performance for typical use cases.
