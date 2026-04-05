# tests/test_flatten_fasta.py

import pytest
from gapclean.gapclean import flatten_fasta


def test_flatten_multiline_fasta(multiline_alignment, output_file):
    """Test flattening a multiline FASTA file."""
    flatten_fasta(multiline_alignment, output_file)

    with open(output_file, 'r') as f:
        lines = f.readlines()

    assert lines[0].strip() == ">seq1"
    assert lines[1].strip() == "ATCGATCG"
    assert lines[2].strip() == ">seq2"
    assert lines[3].strip() == "ATCGATCG"


def test_flatten_already_flat(valid_alignment, output_file):
    """Test flattening an already flat FASTA file."""
    flatten_fasta(valid_alignment, output_file)

    with open(output_file, 'r') as f:
        lines = f.readlines()

    # Should preserve the content
    assert ">seq1" in lines[0]
    assert ">seq2" in lines[2]
    assert ">seq3" in lines[4]


def test_flatten_single_sequence(single_sequence, output_file):
    """Test flattening a single sequence."""
    flatten_fasta(single_sequence, output_file)

    with open(output_file, 'r') as f:
        lines = f.readlines()

    assert lines[0].strip() == ">seq1"
    assert lines[1].strip() == "ATCGATCG"


def test_flatten_preserves_header(multiline_alignment, output_file):
    """Test that headers are preserved exactly."""
    flatten_fasta(multiline_alignment, output_file)

    with open(output_file, 'r') as f:
        content = f.read()

    assert ">seq1" in content
    assert ">seq2" in content
