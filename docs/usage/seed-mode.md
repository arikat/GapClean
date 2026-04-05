# Seed-based Gap Removal

Remove gaps relative to a reference (seed) sequence.

## Usage

```bash
gapclean -i alignment.fa -o output.fa -s INDEX
```

Where `INDEX` is the 0-based position of your seed sequence.

## How It Works

GapClean looks at your chosen seed sequence and removes any column where the seed has a gap. This effectively "projects" the alignment onto your reference sequence.

**Example:**

```
Original alignment:
>seed (index 0)
ATCG--ATCG
>seq2
ATCGATATCG
>seq3
ATCG--GTCG

Result with -s 0:
>seed
ATCGATCG
>seq2
ATCGATCG
>seq3
ATCGGTCG
```

Columns 4 and 5 (where seed has `--`) are removed.

## Choosing a Seed Sequence

### Use the First Sequence
```bash
gapclean -i alignment.fa -o output.fa -s 0
```

**When to use**: When your first sequence is a high-quality reference.

### Use a Reference Genome
If you know sequence 3 is your reference:
```bash
gapclean -i alignment.fa -o output.fa -s 2
```

**When to use**: When you have a known reference sequence.

### Use the Longest Sequence
First, identify which sequence has the fewest gaps, then use it as seed.

**When to use**: When you want maximum coverage.

## Common Use Cases

### Comparing Against a Reference
```bash
# Your reference is the first sequence
gapclean -i query_vs_ref.fa -o cleaned.fa -s 0
```

This is perfect for:
- Variant calling
- Mutation analysis
- Comparing sequences to a reference genome

### Extracting Conserved Positions
```bash
# Use a well-characterized sequence as seed
gapclean -i alignment.fa -o conserved.fa -s 0
```

### Site-wise Mutational Analysis
```bash
# Reference is first, variants follow
gapclean -i variants.fa -o positions.fa -s 0
```

Now each column corresponds to a position in your reference sequence.

## Example Workflow

### Step 1: Identify Your Reference

```bash
# Look at your FASTA file
head alignment.fa
```

```
>ReferenceStrain_NC_12345
ATCGATCG...
>StrainA
ATCGAT-G...
>StrainB
ATC-ATCG...
```

The reference is at index 0 (first sequence).

### Step 2: Clean Alignment

```bash
gapclean -i alignment.fa -o cleaned.fa -s 0
```

### Step 3: Verify

```bash
# Check that the first sequence has no gaps
grep -A 1 "^>ReferenceStrain" cleaned.fa
```

## Tips

- Seed index is 0-based (first sequence = 0, second = 1, etc.)
- Choose a seed with few gaps for maximum coverage
- The seed sequence will have no gaps in the output
- This mode is deterministic: same seed = same result
- Perfect for analyses where position matters

## Comparison with Threshold Mode

| Threshold Mode | Seed Mode |
|---------------|-----------|
| Removes based on gap percentage | Removes where seed has gaps |
| Position-independent | Position matters (relative to seed) |
| Works on all sequences | Focuses on one reference |
| Better for general cleaning | Better for variant analysis |
