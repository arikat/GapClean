# tests/test_gapclean_seed.py

import pytest
from gapclean.gapclean import gapclean_2d_chunk, split_headers_vs_sequences, flatten_fasta


def test_seed_mode_removes_gaps_in_seed(valid_alignment, output_file, tmp_path):
    """Test that seed mode removes columns with gaps in seed sequence."""
    flat_file = str(tmp_path / "flat.fa")
    headers_file = str(tmp_path / "headers.fa")
    seqs_file = str(tmp_path / "seqs.fa")

    flatten_fasta(valid_alignment, flat_file)
    split_headers_vs_sequences(flat_file, headers_file, seqs_file)

    # Use first sequence (index 0) as seed
    # seq1: ATCG--ATCG (has gaps at positions 4-5)
    gapclean_2d_chunk(seqs_file, output_file, seed_index=0)

    with open(output_file, 'r') as f:
        lines = f.readlines()

    # Should remove 2 gap columns from seed
    assert all(len(line.strip()) == 8 for line in lines)
    # First sequence should have no gaps
    assert '-' not in lines[0]


def test_seed_mode_different_seed(valid_alignment, output_file, tmp_path):
    """Test seed mode with different seed sequence."""
    flat_file = str(tmp_path / "flat.fa")
    headers_file = str(tmp_path / "headers.fa")
    seqs_file = str(tmp_path / "seqs.fa")

    flatten_fasta(valid_alignment, flat_file)
    split_headers_vs_sequences(flat_file, headers_file, seqs_file)

    # Use second sequence (index 1) as seed
    # seq2: ATCGATATCG (no gaps)
    gapclean_2d_chunk(seqs_file, output_file, seed_index=1)

    with open(output_file, 'r') as f:
        lines = f.readlines()

    # Should keep all columns (seed has no gaps)
    assert all(len(line.strip()) == 10 for line in lines)
