# tests/conftest.py

import pytest
from pathlib import Path


@pytest.fixture
def valid_alignment(tmp_path):
    """Create a valid aligned FASTA file for testing."""
    fasta_content = """>seq1
ATCG--ATCG
>seq2
ATCGATATCG
>seq3
ATCG--ATCG
"""
    fasta_file = tmp_path / "test.fa"
    fasta_file.write_text(fasta_content)
    return str(fasta_file)


@pytest.fixture
def multiline_alignment(tmp_path):
    """Create a multiline FASTA file."""
    fasta_content = """>seq1
ATCG
ATCG
>seq2
ATCG
ATCG
"""
    fasta_file = tmp_path / "multiline.fa"
    fasta_file.write_text(fasta_content)
    return str(fasta_file)


@pytest.fixture
def unaligned_sequences(tmp_path):
    """Create FASTA with sequences of different lengths."""
    fasta_content = """>seq1
ATCG
>seq2
ATCGATCG
>seq3
ATCG
"""
    fasta_file = tmp_path / "unaligned.fa"
    fasta_file.write_text(fasta_content)
    return str(fasta_file)


@pytest.fixture
def empty_file(tmp_path):
    """Create an empty file."""
    empty_file = tmp_path / "empty.fa"
    empty_file.write_text("")
    return str(empty_file)


@pytest.fixture
def invalid_format(tmp_path):
    """Create a non-FASTA file."""
    invalid_file = tmp_path / "invalid.txt"
    invalid_file.write_text("This is not a FASTA file\nJust some text")
    return str(invalid_file)


@pytest.fixture
def single_sequence(tmp_path):
    """Create FASTA with a single sequence."""
    fasta_content = """>seq1
ATCGATCG
"""
    fasta_file = tmp_path / "single.fa"
    fasta_file.write_text(fasta_content)
    return str(fasta_file)


@pytest.fixture
def all_gaps_column(tmp_path):
    """Create alignment with a column that is 100% gaps."""
    fasta_content = """>seq1
A-CG
>seq2
A-CG
>seq3
A-CG
"""
    fasta_file = tmp_path / "all_gaps.fa"
    fasta_file.write_text(fasta_content)
    return str(fasta_file)


@pytest.fixture
def no_gaps_alignment(tmp_path):
    """Create alignment with no gaps."""
    fasta_content = """>seq1
ATCG
>seq2
ATCG
>seq3
ATCG
"""
    fasta_file = tmp_path / "no_gaps.fa"
    fasta_file.write_text(fasta_content)
    return str(fasta_file)


@pytest.fixture
def output_file(tmp_path):
    """Provide a path for output file."""
    return str(tmp_path / "output.fa")


@pytest.fixture
def conserved_alignment(tmp_path):
    """Create alignment with conserved (low entropy) columns."""
    fasta_content = """>seq1
AAAABBBB
>seq2
AAAABBBB
>seq3
AAAABBBB
>seq4
AAAABBBB
"""
    fasta_file = tmp_path / "conserved.fa"
    fasta_file.write_text(fasta_content)
    return str(fasta_file)


@pytest.fixture
def variable_alignment(tmp_path):
    """Create alignment with variable (high entropy) columns."""
    fasta_content = """>seq1
ATCGATCG
>seq2
GCTAGCTA
>seq3
TAGCTAGC
>seq4
CGATCGAT
"""
    fasta_file = tmp_path / "variable.fa"
    fasta_file.write_text(fasta_content)
    return str(fasta_file)
