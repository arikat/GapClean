# tests/test_integration.py

import pytest
import subprocess
import sys


def test_cli_threshold_mode(valid_alignment, output_file):
    """Test CLI with threshold mode."""
    result = subprocess.run(
        [sys.executable, "-m", "gapclean.gapclean", "-i", valid_alignment, "-o", output_file, "-t", "50"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "GapClean (v1.0.3)" in result.stdout
    assert "Final alignment length" in result.stdout

    # Check output file was created
    with open(output_file, 'r') as f:
        content = f.read()
    assert ">seq1" in content
    assert ">seq2" in content
    assert ">seq3" in content


def test_cli_seed_mode(valid_alignment, output_file):
    """Test CLI with seed mode."""
    result = subprocess.run(
        [sys.executable, "-m", "gapclean.gapclean", "-i", valid_alignment, "-o", output_file, "-s", "0"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "GapClean (v1.0.3)" in result.stdout
    assert "seed seq index=0" in result.stdout


def test_cli_entropy_min_mode(valid_alignment, output_file):
    """Test CLI with entropy-min mode."""
    result = subprocess.run(
        [sys.executable, "-m", "gapclean.gapclean", "-i", valid_alignment, "-o", output_file, "--entropy-min", "1.0"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "GapClean (v1.0.3)" in result.stdout
    assert "entropy" in result.stdout.lower()


def test_cli_entropy_max_mode(valid_alignment, output_file):
    """Test CLI with entropy-max mode."""
    result = subprocess.run(
        [sys.executable, "-m", "gapclean.gapclean", "-i", valid_alignment, "-o", output_file, "--entropy-max", "1.0"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "GapClean (v1.0.3)" in result.stdout
    assert "entropy" in result.stdout.lower()


def test_cli_invalid_input_file(output_file):
    """Test CLI with non-existent input file."""
    result = subprocess.run(
        [sys.executable, "-m", "gapclean.gapclean", "-i", "/nonexistent.fa", "-o", output_file, "-t", "50"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 1
    assert "not found" in result.stderr


def test_cli_invalid_threshold(valid_alignment, output_file):
    """Test CLI with invalid threshold."""
    result = subprocess.run(
        [sys.executable, "-m", "gapclean.gapclean", "-i", valid_alignment, "-o", output_file, "-t", "150"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 1
    assert "between 0 and 100" in result.stderr


def test_cli_help():
    """Test CLI help message."""
    result = subprocess.run(
        [sys.executable, "-m", "gapclean.gapclean", "-h"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "GapClean" in result.stdout
    assert "--threshold" in result.stdout
    assert "--seed" in result.stdout
    assert "--entropy-min" in result.stdout
    assert "--entropy-max" in result.stdout
