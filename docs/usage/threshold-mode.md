# Threshold-based Gap Removal

Remove columns based on the percentage of sequences containing gaps.

## Usage

```bash
gapclean -i alignment.fa -o output.fa -t THRESHOLD
```

Where `THRESHOLD` is a percentage value from 0 to 100.

## How It Works

GapClean counts gaps (`-` or `.` characters) in each column. If the percentage of sequences with gaps in a column exceeds your threshold, that column is removed.

**Example:**

If you have 10 sequences and set `-t 50`:
- A column with 6 gaps (60%) will be removed
- A column with 5 gaps (50%) will be kept
- A column with 4 gaps (40%) will be kept

## Common Thresholds

### Conservative (Keep More Columns)
```bash
gapclean -i alignment.fa -o output.fa -t 75
```
Only removes columns where >75% of sequences have gaps.

**Use when**: You want to preserve as much information as possible.

### Moderate
```bash
gapclean -i alignment.fa -o output.fa -t 50
```
Removes columns where more than half the sequences have gaps.

**Use when**: Balancing alignment length with data quality.

### Aggressive (Remove More Columns)
```bash
gapclean -i alignment.fa -o output.fa -t 25
```
Removes columns where >25% of sequences have gaps.

**Use when**: You need high-quality, gap-free regions.

### Very Aggressive
```bash
gapclean -i alignment.fa -o output.fa -t 0
```
Removes any column that contains even a single gap.

**Use when**: You need completely gap-free columns only.

## Examples

### Phylogenetic Analysis
```bash
# Remove very gappy columns before tree building
gapclean -i gene_alignment.fa -o cleaned.fa -t 80
```

### Structural Prediction
```bash
# Keep only high-quality columns
gapclean -i protein_alignment.fa -o cleaned.fa -t 30
```

### Visualization
```bash
# Remove moderately gappy columns for cleaner display
gapclean -i alignment.fa -o display.fa -t 50
```

## Choosing the Right Threshold

Consider these factors:

1. **Alignment Quality**: Lower threshold for poor alignments
2. **Downstream Analysis**: Some tools tolerate gaps better than others
3. **Sequence Number**: More sequences → can use lower threshold
4. **Conservation**: Higher threshold preserves more variable regions

## Tips

- Start with `-t 50` as a reasonable default
- Check the output: "Final alignment length: X columns (was Y)"
- Experiment with different thresholds to see what works best
- For very large alignments, a threshold of 75-90% is often sufficient
