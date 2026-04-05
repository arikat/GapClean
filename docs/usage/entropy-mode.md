# Entropy-based Gap Removal

Remove columns based on Shannon entropy (information content).

## Usage

```bash
gapclean -i alignment.fa -o output.fa -e THRESHOLD
```

Where `THRESHOLD` is entropy in bits.

## What is Entropy?

Entropy measures the diversity of characters in a column:

- **Low entropy (0)**: All characters the same (conserved)
- **High entropy**: Many different characters (variable)

Shannon entropy formula: `H = -Σ p(char) * log2(p(char))`

## How It Works

GapClean calculates entropy for each column and removes columns below your threshold.

**Example:**

```
Column 1: AAAA (all same) → entropy = 0 bits
Column 2: AATT (half A, half T) → entropy = 1.0 bits  
Column 3: ATCG (equal mix) → entropy = 2.0 bits
```

With `-e 1.5`:
- Column 1 removed (0 < 1.5)
- Column 2 removed (1.0 < 1.5)
- Column 3 kept (2.0 >= 1.5)

## Entropy Ranges

### DNA/RNA Alignments

Maximum entropy: ~2.0 bits (4 nucleotides)

```bash
# Conservative: remove only highly conserved positions
gapclean -i dna.fa -o variable.fa -e 0.5

# Moderate: keep moderately variable positions
gapclean -i dna.fa -o variable.fa -e 1.0

# Aggressive: keep only highly variable positions
gapclean -i dna.fa -o variable.fa -e 1.5
```

### Protein Alignments

Maximum entropy: ~4.32 bits (20 amino acids)

```bash
# Conservative: remove only highly conserved positions
gapclean -i protein.fa -o variable.fa -e 1.0

# Moderate: keep moderately variable positions
gapclean -i protein.fa -o variable.fa -e 2.0

# Aggressive: keep only highly variable positions
gapclean -i protein.fa -o variable.fa -e 3.0
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

### Identify Variable Regions

```bash
# DNA: keep positions with >1 bit entropy
gapclean -i alignment.fa -o variable_sites.fa -e 1.0
```

**Use when**: Looking for hypervariable regions, SNPs, or polymorphic sites.

### Remove Conserved Regions

```bash
# Protein: remove highly conserved columns
gapclean -i protein.fa -o variable.fa -e 2.0
```

**Use when**: Focusing on variable regions for diversity studies.

### Phylogenetic Informative Sites

```bash
# Keep moderately variable positions
gapclean -i alignment.fa -o informative.fa -e 1.2
```

**Use when**: Preparing alignments for phylogenetic analysis.

## Choosing the Right Threshold

| Threshold | DNA/RNA | Protein | Interpretation |
|-----------|---------|---------|----------------|
| 0.0 - 0.5 | Very conserved | Very conserved | Almost all same character |
| 0.5 - 1.0 | Somewhat variable | Conserved | Some variation |
| 1.0 - 1.5 | Moderately variable | Somewhat variable | Good diversity |
| 1.5 - 2.0 | Highly variable | Moderately variable | High diversity |
| > 2.0 | N/A | Highly variable | Maximum diversity |

## Examples by Analysis Type

### SNP Detection (DNA)

```bash
# Keep variable positions, remove conserved
gapclean -i population.fa -o snps.fa -e 0.5
```

### Antigenic Variation (Protein)

```bash
# Identify hypervariable regions
gapclean -i antigen.fa -o variable_epitopes.fa -e 2.5
```

### Conservation Analysis (DNA or Protein)

```bash
# Inverse: identify conserved regions by removing variable ones
# (You'd want LOW entropy, so use a high threshold to keep only low-entropy columns)
# Note: For this, threshold mode might be more intuitive
```

## Tips

- Check the "Average entropy" in output to understand your alignment
- Start with middle values (1.0 for DNA, 2.0 for protein)
- Higher threshold = keep fewer, more variable columns
- Entropy considers ALL characters (including gaps)
- Gaps count as a separate character class

## Entropy vs. Threshold Mode

| Entropy Mode | Threshold Mode |
|--------------|----------------|
| Measures diversity | Measures gap percentage |
| Keeps variable regions | Removes gappy regions |
| Good for SNP analysis | Good for alignment cleaning |
| Considers all characters | Considers only gaps |
| More computationally intensive | Faster |

## Performance Note

Entropy calculation is more computationally intensive than threshold mode, but GapClean's 2D chunking keeps it efficient even for large alignments.

Expected performance: ~10-20% slower than threshold mode.
