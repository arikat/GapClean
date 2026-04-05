# tests/test_gapclean_entropy.py

import pytest
import numpy as np
from gapclean.gapclean import (
    calculate_column_entropy,
    gapclean_2d_chunk,
    split_headers_vs_sequences,
    flatten_fasta
)


def test_calculate_entropy_all_same():
    """Test entropy calculation for column with all same character."""
    # All 'A's should have entropy of 0
    column = np.array([ord('A')] * 10, dtype=np.uint8)
    entropy = calculate_column_entropy(column)
    assert entropy == 0.0


def test_calculate_entropy_two_chars():
    """Test entropy calculation for column with two characters."""
    # Half A's, half T's: should have entropy of 1.0 bit
    column = np.array([ord('A')] * 5 + [ord('T')] * 5, dtype=np.uint8)
    entropy = calculate_column_entropy(column)
    assert abs(entropy - 1.0) < 0.001


def test_calculate_entropy_four_chars():
    """Test entropy calculation for column with four characters."""
    # Equal distribution of 4 nucleotides: should have max entropy ~2.0 bits
    column = np.array([ord('A')] * 25 + [ord('T')] * 25 + [ord('C')] * 25 + [ord('G')] * 25, dtype=np.uint8)
    entropy = calculate_column_entropy(column)
    assert abs(entropy - 2.0) < 0.001


def test_entropy_mode_removes_low_entropy_columns(conserved_alignment, output_file, tmp_path):
    """Test that entropy mode removes low entropy (conserved) columns."""
    flat_file = str(tmp_path / "flat.fa")
    headers_file = str(tmp_path / "headers.fa")
    seqs_file = str(tmp_path / "seqs.fa")

    flatten_fasta(conserved_alignment, flat_file)
    split_headers_vs_sequences(flat_file, headers_file, seqs_file)

    # conserved_alignment has all same characters (entropy = 0)
    # Remove columns with entropy < 0.5
    gapclean_2d_chunk(seqs_file, output_file, entropy_threshold=0.5)

    with open(output_file, 'r') as f:
        lines = f.readlines()

    # All columns should be removed (all have entropy 0)
    assert all(len(line.strip()) == 0 for line in lines)


def test_entropy_mode_keeps_high_entropy_columns(variable_alignment, output_file, tmp_path):
    """Test that entropy mode keeps high entropy (variable) columns."""
    flat_file = str(tmp_path / "flat.fa")
    headers_file = str(tmp_path / "headers.fa")
    seqs_file = str(tmp_path / "seqs.fa")

    flatten_fasta(variable_alignment, flat_file)
    split_headers_vs_sequences(flat_file, headers_file, seqs_file)

    # variable_alignment has 4 different chars each column (entropy = 2.0)
    # Keep columns with entropy >= 0.5
    gapclean_2d_chunk(seqs_file, output_file, entropy_threshold=0.5)

    with open(output_file, 'r') as f:
        lines = f.readlines()

    # All columns should be kept (all have high entropy)
    assert all(len(line.strip()) == 8 for line in lines)
