# tests/test_gapclean_threshold.py

import pytest
from gapclean.gapclean import gapclean_2d_chunk, split_headers_vs_sequences, flatten_fasta, recombine_headers_and_sequences


def test_threshold_mode_removes_gappy_columns(valid_alignment, output_file, tmp_path):
    """Test that threshold mode removes columns with > threshold% gaps."""
    # The valid_alignment has columns 4 and 5 with 66% gaps (2/3 sequences have gaps)
    # So threshold of 50% should remove those columns

    # First flatten and split
    flat_file = str(tmp_path / "flat.fa")
    headers_file = str(tmp_path / "headers.fa")
    seqs_file = str(tmp_path / "seqs.fa")

    flatten_fasta(valid_alignment, flat_file)
    split_headers_vs_sequences(flat_file, headers_file, seqs_file)

    # Run gap cleaning with 50% threshold
    gapclean_2d_chunk(seqs_file, output_file, threshold=50)

    # Check output
    with open(output_file, 'r') as f:
        lines = f.readlines()

    # All sequences should be shorter (original 10 chars, should remove 2 gap columns)
    assert all(len(line.strip()) == 8 for line in lines)


def test_threshold_100_keeps_all(valid_alignment, output_file, tmp_path):
    """Test that threshold of 100% keeps all columns."""
    flat_file = str(tmp_path / "flat.fa")
    headers_file = str(tmp_path / "headers.fa")
    seqs_file = str(tmp_path / "seqs.fa")

    flatten_fasta(valid_alignment, flat_file)
    split_headers_vs_sequences(flat_file, headers_file, seqs_file)

    # 100% threshold means only remove if ALL are gaps (which we don't have)
    gapclean_2d_chunk(seqs_file, output_file, threshold=100)

    with open(output_file, 'r') as f:
        lines = f.readlines()

    # Should keep all 10 columns
    assert all(len(line.strip()) == 10 for line in lines)


def test_threshold_0_removes_any_gaps(valid_alignment, output_file, tmp_path):
    """Test that threshold of 0% removes columns with any gaps."""
    flat_file = str(tmp_path / "flat.fa")
    headers_file = str(tmp_path / "headers.fa")
    seqs_file = str(tmp_path / "seqs.fa")

    flatten_fasta(valid_alignment, flat_file)
    split_headers_vs_sequences(flat_file, headers_file, seqs_file)

    # 0% threshold means remove if ANY sequence has a gap
    gapclean_2d_chunk(seqs_file, output_file, threshold=0)

    with open(output_file, 'r') as f:
        lines = f.readlines()

    # Should remove the 2 gap columns, leaving 8
    assert all(len(line.strip()) == 8 for line in lines)
