# tests/test_edge_cases.py

import pytest
from gapclean.gapclean import (
    gapclean_2d_chunk,
    split_headers_vs_sequences,
    flatten_fasta,
    AlignmentError
)


def test_empty_sequences_file(output_file, tmp_path):
    """Test handling of empty sequences file."""
    empty_seqs = str(tmp_path / "empty_seqs.fa")
    with open(empty_seqs, 'w') as f:
        f.write("")

    # Should handle gracefully
    gapclean_2d_chunk(empty_seqs, output_file, threshold=50)

    with open(output_file, 'r') as f:
        content = f.read()
    assert content == ""


def test_single_sequence_alignment(single_sequence, output_file, tmp_path):
    """Test alignment with single sequence."""
    flat_file = str(tmp_path / "flat.fa")
    headers_file = str(tmp_path / "headers.fa")
    seqs_file = str(tmp_path / "seqs.fa")

    flatten_fasta(single_sequence, flat_file)
    split_headers_vs_sequences(flat_file, headers_file, seqs_file)

    # Should work fine with single sequence
    gapclean_2d_chunk(seqs_file, output_file, threshold=50)

    with open(output_file, 'r') as f:
        lines = f.readlines()

    assert len(lines) == 1
    assert len(lines[0].strip()) > 0


def test_all_gaps_column_removed(all_gaps_column, output_file, tmp_path):
    """Test that column with 100% gaps is removed."""
    flat_file = str(tmp_path / "flat.fa")
    headers_file = str(tmp_path / "headers.fa")
    seqs_file = str(tmp_path / "seqs.fa")

    flatten_fasta(all_gaps_column, flat_file)
    split_headers_vs_sequences(flat_file, headers_file, seqs_file)

    # Threshold of 0% should remove the gap column
    gapclean_2d_chunk(seqs_file, output_file, threshold=0)

    with open(output_file, 'r') as f:
        lines = f.readlines()

    # Original is 4 columns (A-CG), should remove the gap column
    assert all(len(line.strip()) == 3 for line in lines)
    assert all('-' not in line for line in lines)


def test_no_gaps_alignment_unchanged(no_gaps_alignment, output_file, tmp_path):
    """Test that alignment with no gaps is unchanged."""
    flat_file = str(tmp_path / "flat.fa")
    headers_file = str(tmp_path / "headers.fa")
    seqs_file = str(tmp_path / "seqs.fa")

    flatten_fasta(no_gaps_alignment, flat_file)
    split_headers_vs_sequences(flat_file, headers_file, seqs_file)

    # Any threshold should keep all columns
    gapclean_2d_chunk(seqs_file, output_file, threshold=50)

    with open(output_file, 'r') as f:
        lines = f.readlines()

    # Should keep all 4 columns
    assert all(len(line.strip()) == 4 for line in lines)


def test_unaligned_sequences_raises_error(unaligned_sequences, output_file, tmp_path):
    """Test that unaligned sequences raise appropriate error."""
    flat_file = str(tmp_path / "flat.fa")
    headers_file = str(tmp_path / "headers.fa")
    seqs_file = str(tmp_path / "seqs.fa")

    flatten_fasta(unaligned_sequences, flat_file)
    split_headers_vs_sequences(flat_file, headers_file, seqs_file)

    # Should raise AlignmentError
    with pytest.raises(AlignmentError, match="not aligned"):
        gapclean_2d_chunk(seqs_file, output_file, threshold=50)


def test_small_chunk_size(valid_alignment, output_file, tmp_path):
    """Test with chunk size smaller than alignment."""
    flat_file = str(tmp_path / "flat.fa")
    headers_file = str(tmp_path / "headers.fa")
    seqs_file = str(tmp_path / "seqs.fa")

    flatten_fasta(valid_alignment, flat_file)
    split_headers_vs_sequences(flat_file, headers_file, seqs_file)

    # Use very small chunk sizes
    gapclean_2d_chunk(seqs_file, output_file, threshold=50, row_chunk_size=1, col_chunk_size=2)

    with open(output_file, 'r') as f:
        lines = f.readlines()

    # Should still work correctly
    assert len(lines) == 3
    assert all(len(line.strip()) == 8 for line in lines)


def test_large_chunk_size(valid_alignment, output_file, tmp_path):
    """Test with chunk size larger than alignment."""
    flat_file = str(tmp_path / "flat.fa")
    headers_file = str(tmp_path / "headers.fa")
    seqs_file = str(tmp_path / "seqs.fa")

    flatten_fasta(valid_alignment, flat_file)
    split_headers_vs_sequences(flat_file, headers_file, seqs_file)

    # Use very large chunk sizes
    gapclean_2d_chunk(seqs_file, output_file, threshold=50, row_chunk_size=10000, col_chunk_size=10000)

    with open(output_file, 'r') as f:
        lines = f.readlines()

    # Should still work correctly
    assert len(lines) == 3
    assert all(len(line.strip()) == 8 for line in lines)
