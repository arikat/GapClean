# Memory Management

Understanding and optimizing GapClean's memory usage.

## Memory Architecture

GapClean uses three memory areas:

1. **Input buffer**: Reading sequences from disk
2. **Processing buffer**: 2D chunks during gap removal
3. **Output buffer**: Writing cleaned sequences

The largest is the processing buffer, controlled by chunk sizes.

## Memory Requirements

### Minimum

```
RAM = row_chunk_size × col_chunk_size × 2 bytes + overhead
```

Overhead includes:
- Python interpreter: ~100 MB
- NumPy arrays: ~50 MB
- Temporary files (on disk, not RAM)
- Input/output buffers: ~10 MB

**Example with defaults (5000 × 5000)**:
```
RAM = 5000 × 5000 × 2 + 160 MB
    = 50 MB + 160 MB  
    = ~210 MB total
```

### Recommended

**2× minimum** for comfortable operation:
- Defaults (5000 × 5000): **512 MB RAM**
- Small chunks (1000 × 1000): **256 MB RAM**
- Large chunks (10000 × 10000): **1 GB RAM**

## Memory Profiles by Alignment Size

### Small Alignments (< 1 MB)

- **Sequences**: < 1,000
- **Positions**: < 10,000
- **Memory**: < 256 MB
- **Settings**: Use defaults

```bash
gapclean -i small.fa -o cleaned.fa -t 75
```

### Medium Alignments (1-100 MB)

- **Sequences**: 1,000 - 10,000
- **Positions**: 10,000 - 100,000
- **Memory**: 256 MB - 2 GB
- **Settings**: Use defaults or slightly larger

```bash
gapclean -i medium.fa -o cleaned.fa -t 75 \
  --row-chunk-size 5000 --col-chunk-size 5000
```

### Large Alignments (100 MB - 1 GB)

- **Sequences**: 10,000 - 100,000
- **Positions**: 100,000 - 1,000,000
- **Memory**: 512 MB - 4 GB
- **Settings**: Adjust based on available RAM

```bash
# If you have 8 GB RAM
gapclean -i large.fa -o cleaned.fa -t 75 \
  --row-chunk-size 5000 --col-chunk-size 5000

# If you have 4 GB RAM
gapclean -i large.fa -o cleaned.fa -t 75 \
  --row-chunk-size 3000 --col-chunk-size 3000
```

### Very Large Alignments (> 1 GB)

- **Sequences**: > 100,000
- **Positions**: > 1,000,000  
- **Memory**: 512 MB - 8 GB
- **Settings**: Conservative chunks

```bash
# Conservative settings
gapclean -i huge.fa -o cleaned.fa -t 75 \
  --row-chunk-size 2000 --col-chunk-size 2000
```

## Calculating Optimal Chunk Sizes

### Formula

```
chunk_size = sqrt(available_RAM_MB × 500,000)
```

Then use same size for both row and column chunks.

**Examples**:

```python
# 2 GB available RAM
chunk = sqrt(2000 × 500,000) = sqrt(1,000,000,000) ≈ 31,600

# 512 MB available RAM
chunk = sqrt(512 × 500,000) = sqrt(256,000,000) ≈ 16,000

# 256 MB available RAM
chunk = sqrt(256 × 500,000) = sqrt(128,000,000) ≈ 11,300
```

### Quick Reference Table

| Available RAM | Recommended Chunk Size |
|--------------|------------------------|
| 256 MB | 1,000 × 1,000 |
| 512 MB | 3,000 × 3,000 |
| 1 GB | 5,000 × 5,000 (default) |
| 2 GB | 10,000 × 10,000 |
| 4 GB | 15,000 × 15,000 |
| 8 GB | 20,000 × 20,000 |

## Monitoring Memory Usage

### During Execution

#### Linux

```bash
# Monitor memory in real-time
watch -n 1 'ps aux | grep gapclean'

# Or use top
top -p $(pgrep -f gapclean)
```

#### macOS

```bash
# Monitor memory
top | grep gapclean

# Or use Activity Monitor (GUI)
```

#### Windows

```powershell
# Task Manager or:
Get-Process python | Select-Object -Property Name,CPU,Memory
```

### Post-Execution Analysis

```bash
# Linux
/usr/bin/time -v gapclean -i alignment.fa -o output.fa -t 75

# macOS
/usr/bin/time -l gapclean -i alignment.fa -o output.fa -t 75
```

Look for "Maximum resident set size".

## Memory Optimization Strategies

### Strategy 1: Reduce Chunk Sizes

**When**: Running out of memory

```bash
# Current settings cause OOM
gapclean -i alignment.fa -o output.fa -t 75 \
  --row-chunk-size 10000 --col-chunk-size 10000  # ✗ OOM

# Reduce chunks
gapclean -i alignment.fa -o output.fa -t 75 \
  --row-chunk-size 2000 --col-chunk-size 2000    # ✓ Works
```

### Strategy 2: Use Disk Temp Space

**When**: Have fast SSD but limited RAM

```bash
# Use SSD for temp files
export TMPDIR=/mnt/fast_ssd/tmp
gapclean -i alignment.fa -o output.fa -t 75 \
  --row-chunk-size 1000 --col-chunk-size 1000
```

### Strategy 3: Split Large Alignments

**When**: Alignment is huge and you have very limited RAM

```bash
# Split alignment into chunks
split -l 20000 alignment.fa chunk_

# Process each chunk
for chunk in chunk_*; do
  gapclean -i "$chunk" -o "cleaned_$chunk" -t 75
done

# Merge results
cat cleaned_chunk_* > final_cleaned.fa
```

### Strategy 4: Use Seed Mode

**When**: Don't need gap statistics, just reference-based cleaning

```bash
# Seed mode uses less memory
gapclean -i alignment.fa -o output.fa -s 0
```

## Memory Troubleshooting

### Problem: Out of Memory (OOM) Error

**Symptoms**:
```
MemoryError: Unable to allocate array
```

**Solutions** (in order of preference):

1. Reduce chunk sizes:
   ```bash
   --row-chunk-size 1000 --col-chunk-size 1000
   ```

2. Close other applications

3. Use seed mode instead of threshold mode

4. Split the alignment into smaller pieces

### Problem: Swap Thrashing

**Symptoms**:
- System becomes very slow
- Disk activity LED constantly on
- Process takes 10× longer than expected

**Solutions**:

1. Reduce chunk sizes significantly:
   ```bash
   --row-chunk-size 500 --col-chunk-size 500
   ```

2. Close other applications

3. Increase system swap space (if possible)

### Problem: Python Crashes Without Error

**Symptoms**:
- Process terminates suddenly
- No error message
- System log shows OOM killer

**Solutions**:

1. **Linux**: Check `dmesg | grep -i oom`
2. Reduce chunk sizes drastically
3. Add more RAM or use a different machine

## Memory vs. Speed Trade-offs

| Chunk Size | Memory Usage | Speed | Use When |
|-----------|--------------|-------|----------|
| 500 × 500 | Very Low (1 MB) | Slower | RAM < 256 MB |
| 1000 × 1000 | Low (2 MB) | Moderate | RAM < 512 MB |
| 5000 × 5000 | Medium (50 MB) | Fast | RAM ≥ 1 GB |
| 10000 × 10000 | High (200 MB) | Faster | RAM ≥ 2 GB |
| 20000 × 20000 | Very High (800 MB) | Fastest | RAM ≥ 4 GB |

## Best Practices

1. **Start with defaults** (5000 × 5000) and adjust if needed
2. **Monitor first run** to understand memory usage
3. **Leave headroom**: Don't use 100% of available RAM
4. **Consider other processes**: Leave RAM for OS and other apps
5. **Use SSD**: Compensates for slower processing from small chunks

## Future Memory Optimizations

Potential improvements in future versions:

- Automatic chunk size selection based on available RAM
- Disk-backed arrays for extreme cases
- Compressed in-memory representation
- Streaming mode for ultra-low memory
- GPU acceleration for reduced CPU memory usage
