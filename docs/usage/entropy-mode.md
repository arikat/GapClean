# Entropy-based Gap Removal

Remove columns based on Shannon entropy (information content).

## Two Approaches

GapClean offers two entropy-based filtering modes:

### Remove Conserved Regions (--entropy-min)
```bash
gapclean -i alignment.fa -o output.fa --entropy-min THRESHOLD
```

Removes columns with entropy **< threshold** (removes conserved, keeps variable).

**Use case**: SNP detection, diversity studies, finding hypervariable regions

### Remove Variable Regions (--entropy-max)
```bash
gapclean -i alignment.fa -o output.fa --entropy-max THRESHOLD
```

Removes columns with entropy **> threshold** (removes variable, keeps conserved).

**Use case**: Alignment cleaning, focusing on conserved functional regions

## What is Entropy?

Entropy measures the diversity of characters in a column:

- **Low entropy (0)**: All characters the same (conserved)
- **High entropy**: Many different characters (variable)

Shannon entropy formula: `H = -Σ p(char) * log2(p(char))`

## How It Works

GapClean calculates Shannon entropy for each column:

**Example columns:**

```
Column 1: AAAA (all same) → entropy = 0 bits (conserved)
Column 2: AATT (half A, half T) → entropy = 1.0 bits (moderate)
Column 3: ATCG (equal mix) → entropy = 2.0 bits (variable)
```

**With `--entropy-min 1.5`** (remove conserved, keep variable):
- Column 1 removed (0 < 1.5) - too conserved
- Column 2 removed (1.0 < 1.5) - too conserved
- Column 3 kept (2.0 >= 1.5) - variable enough

**With `--entropy-max 1.5`** (remove variable, keep conserved):
- Column 1 kept (0 < 1.5) - conserved
- Column 2 kept (1.0 < 1.5) - conserved
- Column 3 removed (2.0 > 1.5) - too variable

## Entropy Ranges

### DNA/RNA Alignments

Maximum entropy: ~2.0 bits (4 nucleotides)

**For finding variable regions (SNPs, diversity):**
```bash
# Keep only variable positions
gapclean -i dna.fa -o variable.fa --entropy-min 1.0

# Keep highly variable positions only
gapclean -i dna.fa -o hypervariable.fa --entropy-min 1.5
```

**For alignment cleaning (keep conserved):**
```bash
# Remove noisy/hypervariable columns
gapclean -i dna.fa -o conserved.fa --entropy-max 1.5

# Remove moderately variable columns
gapclean -i dna.fa -o highly_conserved.fa --entropy-max 1.0
```

### Protein Alignments

Maximum entropy: ~4.32 bits (20 amino acids)

**For finding variable regions:**
```bash
# Keep variable positions
gapclean -i protein.fa -o variable.fa --entropy-min 2.0

# Keep highly variable positions
gapclean -i protein.fa -o hypervariable.fa --entropy-min 3.0
```

**For alignment cleaning (keep conserved):**
```bash
# Remove noisy columns
gapclean -i protein.fa -o conserved.fa --entropy-max 3.0

# Keep only highly conserved positions
gapclean -i protein.fa -o highly_conserved.fa --entropy-max 2.0
```

## Understanding the Output

```
[GAPCLEAN] Calculating entropy: 100%|████████| 5000/5000
[GAPCLEAN] Average entropy: 1.75 bits
[GAPCLEAN] Removed 1230 columns with entropy < 1.5
[GAPCLEAN] Final alignment length: 3770 columns (was 5000)
```

The average entropy tells you about overall alignment diversity.

## Common Use Cases

### Use Case 1: SNP Detection (Keep Variable)

```bash
# DNA: keep positions with >1 bit entropy (variable regions)
gapclean -i population.fa -o snps.fa --entropy-min 1.0
```

**Goal**: Find polymorphic sites for diversity analysis

**Result**: Removes conserved positions, keeps sites with variation

### Use Case 2: Alignment Cleaning (Keep Conserved)

```bash
# Remove noisy/hypervariable columns for cleaner alignment
gapclean -i alignment.fa -o cleaned.fa --entropy-max 1.5
```

**Goal**: Clean alignment for visualization or downstream analysis

**Result**: Removes highly variable/noisy columns, keeps well-conserved positions

### Use Case 3: Functional Region Analysis

```bash
# Protein: keep conserved functional regions
gapclean -i protein.fa -o conserved_functional.fa --entropy-max 2.0
```

**Goal**: Focus on conserved (likely functional) regions

**Result**: Removes variable regions, keeps conserved domains

### Use Case 4: Hypervariable Region Detection

```bash
# Find hypervariable regions (e.g., antibody CDRs)
gapclean -i antibody.fa -o hypervariable.fa --entropy-min 2.5
```

**Goal**: Identify highly diverse regions

**Result**: Keeps only highly variable positions

## Decision Guide

**What do you want to keep?**

| I want to keep... | Use... | Example |
|-------------------|--------|---------|
| Variable regions (SNPs, diversity) | `--entropy-min` | `--entropy-min 1.0` |
| Conserved regions (functional) | `--entropy-max` | `--entropy-max 1.5` |
| Moderately variable positions | Both flags | `--entropy-min 0.5 --entropy-max 1.5` |

## Entropy Reference Table

| Entropy | DNA/RNA | Protein | Character |
|---------|---------|---------|-----------|
| 0.0 - 0.5 | Very conserved | Very conserved | Almost all same |
| 0.5 - 1.0 | Somewhat variable | Conserved | Some variation |
| 1.0 - 1.5 | Moderately variable | Somewhat variable | Good diversity |
| 1.5 - 2.0 | Highly variable | Moderately variable | High diversity |
| > 2.0 | Maximum (4 bases) | Highly variable | Maximum diversity |
| > 4.0 | N/A | Maximum (20 AAs) | Maximum diversity |

## Quick Examples

### Remove Conserved, Keep Variable

```bash
# SNP detection (DNA)
gapclean -i population.fa -o snps.fa --entropy-min 1.0

# Antigenic variation (Protein)
gapclean -i antigen.fa -o variable_epitopes.fa --entropy-min 2.5
```

### Remove Variable, Keep Conserved

```bash
# Alignment cleaning (DNA)
gapclean -i noisy_alignment.fa -o clean.fa --entropy-max 1.5

# Functional conservation (Protein)
gapclean -i protein.fa -o conserved_domains.fa --entropy-max 2.0
```

### Keep Moderate Range

```bash
# Keep moderately informative positions (not too conserved, not too variable)
gapclean -i alignment.fa -o moderate.fa --entropy-min 0.8 --entropy-max 1.8
```

**Note**: When using both flags, columns are removed if they fall **outside** the range.

## Tips

- Check the "Average entropy" in output to understand your alignment
- Start with middle values (1.0 for DNA, 2.0 for protein)
- Higher threshold = keep fewer, more variable columns
- Entropy considers ALL characters (including gaps)
- Gaps count as a separate character class

## Comparison: Entropy vs. Threshold Mode

| Feature | Entropy Mode | Threshold Mode |
|---------|--------------|----------------|
| **What it measures** | Character diversity | Gap percentage |
| **Typical goal** | Find variable/conserved regions | Remove gappy columns |
| **Best for** | SNP analysis, conservation studies | Alignment cleaning |
| **Characters considered** | All characters | Only gaps (`-` or `.`) |
| **Speed** | Slower (more computation) | Faster |
| **Complexity** | Two flags (min/max) for flexibility | Single threshold |

### Which Should I Use?

**Use Threshold Mode (`-t`)** when:
- You want to clean up gappy alignments
- Gaps are your primary concern
- You need faster processing
- Simple gap percentage is sufficient

**Use Entropy Mode (`--entropy-min/--entropy-max`)** when:
- You're analyzing sequence diversity
- You want to find SNPs or conserved regions
- Character variation matters (not just gaps)
- You need fine control over conservation levels

## Performance Note

Entropy calculation is more computationally intensive than threshold mode, but GapClean's 2D chunking keeps it efficient even for large alignments.

Expected performance: ~10-20% slower than threshold mode.
