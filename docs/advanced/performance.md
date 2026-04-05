# Performance Tuning

Optimize GapClean for your specific use case.

## Benchmarks

Typical performance on modern hardware (M1 Mac, 16 GB RAM):

| Alignment Size | Sequences | Positions | Time | Memory |
|---------------|-----------|-----------|------|--------|
| Small | 100 | 1,000 | < 1s | < 100 MB |
| Medium | 1,000 | 10,000 | ~5s | < 500 MB |
| Large | 10,000 | 100,000 | ~60s | < 2 GB |
| Very Large | 100,000 | 100,000 | ~15min | < 5 GB |

## Speed Optimization

### Choose the Right Mode

Fastest to slowest:

1. **Seed mode**: Only checks one sequence
2. **Threshold mode**: Counts gaps across all sequences
3. **Entropy mode**: Calculates entropy for each column

```bash
# Fastest
gapclean -i alignment.fa -o output.fa -s 0

# Fast
gapclean -i alignment.fa -o output.fa -t 75

# Slower (but still efficient)
gapclean -i alignment.fa -o output.fa -e 1.5
```

### Optimize Chunk Sizes

#### For Speed (If You Have RAM)

```bash
# Larger chunks = fewer iterations = faster
gapclean -i alignment.fa -o output.fa -t 75 \
  --row-chunk-size 10000 --col-chunk-size 10000
```

#### For Memory (If RAM is Limited)

```bash
# Smaller chunks = more iterations = slower but less memory
gapclean -i alignment.fa -o output.fa -t 75 \
  --row-chunk-size 1000 --col-chunk-size 1000
```

### Use Threshold Mode When Possible

If your goal is just to remove gappy columns, threshold mode is faster than entropy mode:

```bash
# Instead of this (slower):
gapclean -i alignment.fa -o output.fa -e 0.1

# Consider this (faster):
gapclean -i alignment.fa -o output.fa -t 75
```

## Memory Optimization

### Estimate Memory Usage

Peak memory ≈ row_chunk_size × col_chunk_size × 2 bytes

```bash
# 5000 × 5000 × 2 = 50 MB peak memory
gapclean -i alignment.fa -o output.fa -t 75 \
  --row-chunk-size 5000 --col-chunk-size 5000

# 1000 × 1000 × 2 = 2 MB peak memory
gapclean -i alignment.fa -o output.fa -t 75 \
  --row-chunk-size 1000 --col-chunk-size 1000
```

### For Very Large Alignments

```bash
# 100,000 sequences × 500,000 positions
# Use conservative chunk sizes
gapclean -i huge.fa -o cleaned.fa -t 75 \
  --row-chunk-size 2000 --col-chunk-size 2000
```

Memory usage: ~8 MB peak (vs. 100 GB without chunking!)

### Monitor Memory Usage

On Unix systems:
```bash
# Run GapClean and monitor memory
/usr/bin/time -v gapclean -i alignment.fa -o output.fa -t 75
```

On macOS:
```bash
/usr/bin/time -l gapclean -i alignment.fa -o output.fa -t 75
```

## Disk I/O Optimization

### Use Fast Storage

- **SSD**: 5-10× faster than HDD
- **NVMe SSD**: 2× faster than SATA SSD
- **RAM disk**: Fastest (for temp files)

### Reduce Disk I/O

GapClean uses temporary files. Set temp directory to fast storage:

```bash
# Linux/macOS
export TMPDIR=/path/to/fast/ssd
gapclean -i alignment.fa -o output.fa -t 75

# Windows
set TEMP=C:\fast\ssd
gapclean -i alignment.fa -o output.fa -t 75
```

## Parallel Processing

Current version: Serial processing

For multiple alignments, parallelize externally:

```bash
# GNU Parallel
parallel -j 4 'gapclean -i {} -o {.}_cleaned.fa -t 75' ::: *.fa

# Simple shell loop with background jobs
for file in *.fa; do
  gapclean -i "$file" -o "${file%.fa}_cleaned.fa" -t 75 &
done
wait
```

## Profiling

### Check Which Step is Slow

GapClean shows progress for each step:

```
[GAPCLEAN] (1) Flattening input FASTA...     ← Fast
[GAPCLEAN] (2) Splitting headers...           ← Fast
[GAPCLEAN] (3) It's Gappin' Time...
  [GAPCLEAN] Counting gaps: 100%              ← May be slow for large alignments
  [GAPCLEAN] Cleaning gaps: 100%              ← May be slow for large alignments
[GAPCLEAN] (4) Stitching back headers...      ← Fast
```

## Performance Tips Summary

### For Maximum Speed

1. Use seed mode if possible
2. Use large chunk sizes (if RAM allows)
3. Use SSD storage
4. Process multiple files in parallel

### For Minimum Memory

1. Use small chunk sizes (1000 × 1000)
2. Process one file at a time
3. Close other applications

### For Balance

1. Use default settings (5000 × 5000)
2. Monitor first run to adjust if needed
3. Threshold mode for most use cases

## Expected Performance

### Scaling Behavior

- **Sequences**: Linear scaling O(n)
- **Positions**: Linear scaling O(m)
- **Overall**: O(n × m) for threshold/entropy modes

Doubling alignment size ≈ doubles runtime (very predictable!)

### Comparison with Other Tools

GapClean is competitive with specialized tools:

- Faster than pure Python tools (uses NumPy)
- Comparable to C-based tools for typical alignments
- Better memory efficiency than most alternatives

## Troubleshooting Slow Performance

### Problem: Very slow on small alignment

**Likely cause**: Disk I/O (slow storage)

**Solution**: Move files to SSD or use RAM disk

### Problem: Slow on large alignment

**Likely cause**: Normal behavior for large data

**Solutions**:
- Increase chunk sizes if you have RAM
- Use threshold mode instead of entropy mode
- Ensure you're using SSD storage

### Problem: Out of memory error

**Solution**: Reduce chunk sizes

```bash
gapclean -i alignment.fa -o output.fa -t 75 \
  --row-chunk-size 500 --col-chunk-size 500
```

### Problem: Taking too long

**Check**: Is your alignment unexpectedly large?

```bash
# Count sequences
grep -c "^>" alignment.fa

# Check file size
ls -lh alignment.fa
```

Expected time: ~1 minute per 1,000,000,000 characters on modern hardware.
