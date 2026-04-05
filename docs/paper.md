# Technical Paper

## GapClean: Memory-Efficient Gap Removal for Large-Scale Multiple Sequence Alignments

**Author:** Aarya Venkat, PhD

### Abstract

Multiple sequence alignments (MSAs) are fundamental to evolutionary analysis, yet large alignments often contain extensive gap-rich regions that obscure meaningful patterns and hinder visualization. We present GapClean, a memory-efficient tool implementing a novel 2D chunking algorithm for processing alignments exceeding available RAM. Using NumPy's vectorized operations, GapClean processes alignments in rectangular blocks, enabling gap removal on million-sequence datasets while maintaining O(nm) time complexity with O(rc) memory complexity, where r,c are user-defined chunk dimensions.

### Download

[**Download PDF**](paper.pdf){ .md-button .md-button--primary }

### Key Contributions

- **Novel 2D Chunking Algorithm**: Decouples memory requirements from alignment size
- **Three Filtering Modes**: Threshold-based, reference-based (seed), and entropy-based
- **Proven Scalability**: Linear scaling demonstrated on datasets from 931 to 1,051,876 sequences

### Benchmarks

The paper includes comprehensive benchmarks on real Pfam protein family alignments:

| Scale | Pfam | Sequences | Length | Time | Size |
|-------|------|-----------|--------|------|------|
| Tiny | PF15608 | 931 | 148 | <0.1s | 215 KB |
| Small | PF00637 | 38,583 | 648 | 2s | 27 MB |
| Medium | PF00535 | 157,052 | 1,285 | 11s | 206 MB |
| Large | PF00069 | **1,051,876** | 3,667 | 35s | **7 GB** |

All benchmarks performed on Apple M1 with 70% gap threshold.

### Citation

If you use GapClean in your research, please cite:

```
Venkat, A. (2026). GapClean: Memory-efficient gap removal for multiple sequence alignments.
https://github.com/arikat/GapClean
```
