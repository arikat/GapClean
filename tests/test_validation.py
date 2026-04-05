# tests/test_validation.py

import pytest
import os
from gapclean.gapclean import (
    validate_input_file,
    validate_output_path,
    validate_fasta_format,
    validate_threshold,
    validate_seed_index,
    validate_entropy_threshold,
    validate_chunk_sizes,
    InputValidationError
)


def test_validate_input_file_exists(valid_alignment):
    """Test validation passes for existing file."""
    validate_input_file(valid_alignment)  # Should not raise


def test_validate_input_file_not_exists():
    """Test validation fails for non-existent file."""
    with pytest.raises(InputValidationError, match="not found"):
        validate_input_file("/nonexistent/file.fa")


def test_validate_output_path_valid(tmp_path):
    """Test validation passes for valid output path."""
    output = str(tmp_path / "output.fa")
    validate_output_path(output)  # Should not raise


def test_validate_output_path_invalid_dir():
    """Test validation fails for non-existent directory."""
    with pytest.raises(InputValidationError, match="does not exist"):
        validate_output_path("/nonexistent/dir/output.fa")


def test_validate_fasta_format_valid(valid_alignment):
    """Test validation passes for valid FASTA."""
    validate_fasta_format(valid_alignment)  # Should not raise


def test_validate_fasta_format_empty(empty_file):
    """Test validation fails for empty file."""
    with pytest.raises(InputValidationError, match="empty"):
        validate_fasta_format(empty_file)


def test_validate_fasta_format_invalid(invalid_format):
    """Test validation fails for non-FASTA file."""
    with pytest.raises(InputValidationError, match="does not appear to be FASTA"):
        validate_fasta_format(invalid_format)


def test_validate_threshold_valid():
    """Test validation passes for valid thresholds."""
    validate_threshold(0)
    validate_threshold(50)
    validate_threshold(100)


def test_validate_threshold_negative():
    """Test validation fails for negative threshold."""
    with pytest.raises(InputValidationError, match="between 0 and 100"):
        validate_threshold(-1)


def test_validate_threshold_too_high():
    """Test validation fails for threshold > 100."""
    with pytest.raises(InputValidationError, match="between 0 and 100"):
        validate_threshold(101)


def test_validate_threshold_none():
    """Test validation passes for None threshold."""
    validate_threshold(None)  # Should not raise


def test_validate_seed_index_valid():
    """Test validation passes for valid seed indices."""
    validate_seed_index(0, 10)
    validate_seed_index(5, 10)
    validate_seed_index(9, 10)


def test_validate_seed_index_negative():
    """Test validation fails for negative seed index."""
    with pytest.raises(InputValidationError, match="non-negative"):
        validate_seed_index(-1, 10)


def test_validate_seed_index_out_of_range():
    """Test validation fails for out-of-range seed index."""
    with pytest.raises(InputValidationError, match="out of range"):
        validate_seed_index(10, 10)


def test_validate_seed_index_none():
    """Test validation passes for None seed index."""
    validate_seed_index(None, 10)  # Should not raise


def test_validate_entropy_threshold_valid():
    """Test validation passes for valid entropy thresholds."""
    validate_entropy_threshold(0.0)
    validate_entropy_threshold(1.5)
    validate_entropy_threshold(4.0)


def test_validate_entropy_threshold_negative():
    """Test validation fails for negative entropy threshold."""
    with pytest.raises(InputValidationError, match="non-negative"):
        validate_entropy_threshold(-0.1)


def test_validate_entropy_threshold_none():
    """Test validation passes for None entropy threshold."""
    validate_entropy_threshold(None)  # Should not raise


def test_validate_chunk_sizes_valid():
    """Test validation passes for valid chunk sizes."""
    validate_chunk_sizes(1000, 1000)
    validate_chunk_sizes(5000, 5000)


def test_validate_chunk_sizes_zero():
    """Test validation fails for zero chunk size."""
    with pytest.raises(InputValidationError, match="positive"):
        validate_chunk_sizes(0, 1000)

    with pytest.raises(InputValidationError, match="positive"):
        validate_chunk_sizes(1000, 0)


def test_validate_chunk_sizes_negative():
    """Test validation fails for negative chunk size."""
    with pytest.raises(InputValidationError, match="positive"):
        validate_chunk_sizes(-1000, 1000)

    with pytest.raises(InputValidationError, match="positive"):
        validate_chunk_sizes(1000, -1000)
