# gapclean/gapclean.py

import argparse
import os
import sys
import time
import tempfile
import shutil
from typing import Optional
from tqdm import tqdm
import numpy as np


# Custom exception classes
class GapCleanError(Exception):
    """Base exception for GapClean errors."""
    pass


class InputValidationError(GapCleanError):
    """Raised when input validation fails."""
    pass


class AlignmentError(GapCleanError):
    """Raised when alignment processing fails."""
    pass


# Validation functions
def validate_input_file(filepath: str) -> None:
    """Validate that input file exists and is readable."""
    if not os.path.exists(filepath):
        raise InputValidationError(
            f"\n[ERROR] Input file not found: {filepath}\n"
            f"  Please check the file path and try again."
        )
    if not os.path.isfile(filepath):
        raise InputValidationError(
            f"\n[ERROR] Input path is not a file: {filepath}\n"
            f"  Please provide a valid FASTA file."
        )
    if not os.access(filepath, os.R_OK):
        raise InputValidationError(
            f"\n[ERROR] Cannot read input file: {filepath}\n"
            f"  Please check file permissions."
        )


def validate_output_path(filepath: str) -> None:
    """Validate that output file path is writable."""
    output_dir = os.path.dirname(filepath) or '.'
    if not os.path.exists(output_dir):
        raise InputValidationError(
            f"\n[ERROR] Output directory does not exist: {output_dir}\n"
            f"  Please create the directory first."
        )
    if not os.access(output_dir, os.W_OK):
        raise InputValidationError(
            f"\n[ERROR] Cannot write to output directory: {output_dir}\n"
            f"  Please check directory permissions."
        )
    if os.path.exists(filepath) and not os.access(filepath, os.W_OK):
        raise InputValidationError(
            f"\n[ERROR] Cannot overwrite output file: {filepath}\n"
            f"  Please check file permissions."
        )


def validate_fasta_format(filepath: str) -> None:
    """Validate basic FASTA format."""
    with open(filepath, 'r') as f:
        first_char = f.read(1)
        if not first_char:
            raise InputValidationError(
                f"\n[ERROR] Input file is empty: {filepath}\n"
                f"  Please provide a valid FASTA file with sequences."
            )
        if first_char != '>':
            raise InputValidationError(
                f"\n[ERROR] Input file does not appear to be FASTA format: {filepath}\n"
                f"  FASTA files must start with '>' character.\n"
                f"  First character found: '{first_char}'"
            )

        # Count sequences
        f.seek(0)
        num_sequences = sum(1 for line in f if line.startswith('>'))
        if num_sequences == 0:
            raise InputValidationError(
                f"\n[ERROR] No sequences found in input file: {filepath}\n"
                f"  FASTA files must contain at least one sequence."
            )


def validate_threshold(threshold: Optional[int]) -> None:
    """Validate threshold parameter."""
    if threshold is not None:
        if threshold < 0 or threshold > 100:
            raise InputValidationError(
                f"\n[ERROR] Threshold must be between 0 and 100, got: {threshold}\n"
                f"  Example: -t 75 removes columns with >75% gaps."
            )


def validate_seed_index(seed_index: Optional[int], num_sequences: int) -> None:
    """Validate seed index parameter."""
    if seed_index is not None:
        if seed_index < 0:
            raise InputValidationError(
                f"\n[ERROR] Seed index must be non-negative, got: {seed_index}\n"
                f"  Seed indices are 0-based (first sequence is index 0)."
            )
        if seed_index >= num_sequences:
            raise InputValidationError(
                f"\n[ERROR] Seed index {seed_index} out of range.\n"
                f"  File contains {num_sequences} sequences (valid indices: 0-{num_sequences-1})."
            )


def validate_entropy_threshold(entropy_min: Optional[float], entropy_max: Optional[float]) -> None:
    """Validate entropy threshold parameters."""
    if entropy_min is not None:
        if entropy_min < 0:
            raise InputValidationError(
                f"\n[ERROR] Entropy minimum must be non-negative, got: {entropy_min}\n"
                f"  Example: --entropy-min 1.5 removes columns with entropy < 1.5 bits."
            )
    if entropy_max is not None:
        if entropy_max < 0:
            raise InputValidationError(
                f"\n[ERROR] Entropy maximum must be non-negative, got: {entropy_max}\n"
                f"  Example: --entropy-max 1.5 removes columns with entropy > 1.5 bits."
            )
    if entropy_min is not None and entropy_max is not None:
        if entropy_min >= entropy_max:
            raise InputValidationError(
                f"\n[ERROR] Entropy minimum ({entropy_min}) must be less than maximum ({entropy_max})"
            )


def validate_chunk_sizes(row_chunk_size: int, col_chunk_size: int) -> None:
    """Validate chunk size parameters."""
    if row_chunk_size <= 0:
        raise InputValidationError(
            f"\n[ERROR] Row chunk size must be positive, got: {row_chunk_size}"
        )
    if col_chunk_size <= 0:
        raise InputValidationError(
            f"\n[ERROR] Column chunk size must be positive, got: {col_chunk_size}"
        )


def flatten_fasta(input_file: str, output_file: str) -> None:
    """
    Flatten multiline FASTA to single-line format.

    Converts:
        >seq1
        ATCG
        ATCG
        >seq2
        GCTA

    To:
        >seq1
        ATCGATCG
        >seq2
        GCTA

    Args:
        input_file: Path to input FASTA file (may have multiline sequences)
        output_file: Path to output FASTA file (single-line sequences)
    """
    with open(input_file, 'r') as fin, open(output_file, 'w') as fout:
        current_header = None
        current_sequence = []

        for line in fin:
            line = line.rstrip('\n')

            if line.startswith('>'):
                # Write previous sequence if exists
                if current_header is not None:
                    fout.write(current_header + '\n')
                    fout.write(''.join(current_sequence) + '\n')

                # Start new sequence
                current_header = line
                current_sequence = []
            else:
                # Accumulate sequence line
                current_sequence.append(line)

        # Write final sequence
        if current_header is not None:
            fout.write(current_header + '\n')
            fout.write(''.join(current_sequence) + '\n')


def split_headers_vs_sequences(input_file: str, headers_file: str, sequences_file: str) -> None:
    """
    Separate FASTA headers from sequence bodies.

    Args:
        input_file: Path to input FASTA file
        headers_file: Path to output file for headers
        sequences_file: Path to output file for sequences
    """
    with open(input_file, 'r') as fin, \
         open(headers_file, 'w') as fhdr, \
         open(sequences_file, 'w') as fseq:

        for line in fin:
            if line.startswith('>'):
                fhdr.write(line)
            else:
                fseq.write(line)


def calculate_column_entropy(column_chars: np.ndarray) -> float:
    """
    Calculate Shannon entropy for a column of characters.

    Args:
        column_chars: numpy array of ASCII values for one column

    Returns:
        Shannon entropy value in bits (higher = more diverse)
    """
    # Count character frequencies
    unique, counts = np.unique(column_chars, return_counts=True)

    # Calculate probabilities
    total = len(column_chars)
    probabilities = counts / total

    # Calculate Shannon entropy: -Σ p(x) * log2(p(x))
    # Use log2 for bits of information
    entropy = -np.sum(probabilities * np.log2(probabilities))

    return entropy


def gapclean_2d_chunk(
    input_sequences_file: str,
    output_sequences_file: str,
    threshold: Optional[int] = None,
    seed_index: Optional[int] = None,
    entropy_min: Optional[float] = None,
    entropy_max: Optional[float] = None,
    row_chunk_size: int = 5000,
    col_chunk_size: int = 5000
) -> None:
    """
    2D chunking over rows (sequences) and columns for memory-efficient gap removal.

    Imagine a square (or rectangle) maneuvering over the alignment, one chunk at a time.
    This limits the number of sequences held in memory, enabling processing of massive
    alignments on memory-constrained systems.

    Args:
        input_sequences_file: Path to file containing sequences only (no headers)
        output_sequences_file: Path to output file for cleaned sequences
        threshold: Columns with > threshold% gaps are removed (mutually exclusive)
        seed_index: Remove columns with gaps in seed sequence (mutually exclusive)
        entropy_min: Remove columns with entropy < threshold bits (mutually exclusive)
        entropy_max: Remove columns with entropy > threshold bits (mutually exclusive)
        row_chunk_size: How many sequences to process at once (default 5000)
        col_chunk_size: How many alignment columns to process at once (default 5000)
    """

    sequences = []
    with open(input_sequences_file, 'r') as fin:
        for line in fin:
            seq = line.strip()
            if seq:
                sequences.append(seq)

    num_seq = len(sequences)
    if num_seq == 0:
        print(
            "[GAPCLEAN] WARNING: No sequences found in input file!\n"
            "[GAPCLEAN]   This may indicate an empty file or incorrect format.\n"
            "[GAPCLEAN]   Creating empty output file."
        )
        with open(output_sequences_file, 'w'):
            pass
        return

    seq_len = len(sequences[0])
    for idx, seq in enumerate(sequences):
        if len(seq) != seq_len:
            raise AlignmentError(
                f"\n[ERROR] Alignment validation failed!\n"
                f"  Sequence at position {idx} has length {len(seq)}\n"
                f"  Expected length: {seq_len} (based on first sequence)\n"
                f"  This means your sequences are not aligned.\n"
                f"  GapClean requires all sequences to be the same length.\n"
                f"  Suggestion: Align your sequences first using tools like MAFFT or MUSCLE."
            )

    print(f"[GAPCLEAN] Number of Sequences = {num_seq},\n[GAPCLEAN] Alignment Length = {seq_len},\n[GAPCLEAN] row_chunk_size = {row_chunk_size},\n[GAPCLEAN] col_chunk_size = {col_chunk_size} \n")

    mask = np.ones(seq_len, dtype=bool)

    # (A) Threshold-based gap removal
    if threshold is not None:
        print(f"[GAPCLEAN] Removing columns with > {threshold}% gaps.\n")
        gap_counts = np.zeros(seq_len, dtype=int)
        columns_pbar = tqdm(total=seq_len, desc="[GAPCLEAN] Counting gaps", unit="cols")
        gap_threshold = threshold / 100.0

        for c_start in range(0, seq_len, col_chunk_size):
            c_end = min(c_start + col_chunk_size, seq_len)
            chunk_width = c_end - c_start

            for r_start in range(0, num_seq, row_chunk_size):
                r_end = min(r_start + row_chunk_size, num_seq)

                for row_idx in range(r_start, r_end):
                    row_slice = sequences[row_idx][c_start:c_end]
                    sub_arr = np.frombuffer(row_slice.encode('ascii'), dtype=np.uint8)
                    is_gap = (sub_arr == ord('-')) | (sub_arr == ord('.'))
                    gap_counts[c_start:c_end] += is_gap

            columns_pbar.update(chunk_width)
        columns_pbar.close()

        gap_fraction = gap_counts / num_seq
        remove_cols = (gap_fraction > gap_threshold)
        mask[remove_cols] = False

    # (B) Seed-based gap removal
    elif seed_index is not None:
        print(f"[GAPCLEAN] Removing columns with gaps in seed seq index={seed_index}.\n")
        seed_row = sequences[seed_index]
        sub_arr = np.frombuffer(seed_row.encode('ascii'), dtype=np.uint8)
        remove_cols = (sub_arr == ord('-')) | (sub_arr == ord('.'))
        mask[remove_cols] = False

    # (C) Entropy-based gap removal
    elif entropy_min is not None or entropy_max is not None:
        if entropy_min is not None and entropy_max is not None:
            print(f"[GAPCLEAN] Removing columns with entropy < {entropy_min} or > {entropy_max} bits.\n")
        elif entropy_min is not None:
            print(f"[GAPCLEAN] Removing columns with entropy < {entropy_min} bits (keep variable regions).\n")
        else:
            print(f"[GAPCLEAN] Removing columns with entropy > {entropy_max} bits (keep conserved regions).\n")

        entropy_values = np.zeros(seq_len, dtype=float)
        columns_pbar = tqdm(total=seq_len, desc="[GAPCLEAN] Calculating entropy", unit="cols")

        for c_start in range(0, seq_len, col_chunk_size):
            c_end = min(c_start + col_chunk_size, seq_len)
            chunk_width = c_end - c_start

            # For each column in chunk, calculate entropy
            for col_offset in range(chunk_width):
                col_idx = c_start + col_offset
                column_chars = []

                # Collect all characters in this column
                for r_start in range(0, num_seq, row_chunk_size):
                    r_end = min(r_start + row_chunk_size, num_seq)
                    for row_idx in range(r_start, r_end):
                        char = sequences[row_idx][col_idx]
                        column_chars.append(ord(char))

                # Calculate entropy for this column
                column_array = np.array(column_chars, dtype=np.uint8)
                entropy_values[col_idx] = calculate_column_entropy(column_array)

            columns_pbar.update(chunk_width)
        columns_pbar.close()

        # Remove columns based on entropy thresholds
        remove_cols = np.zeros(seq_len, dtype=bool)
        if entropy_min is not None:
            remove_cols |= (entropy_values < entropy_min)
        if entropy_max is not None:
            remove_cols |= (entropy_values > entropy_max)
        mask[remove_cols] = False

        print(f"[GAPCLEAN] Average entropy: {np.mean(entropy_values):.3f} bits")
        if entropy_min is not None and entropy_max is not None:
            print(f"[GAPCLEAN] Removed {np.sum(remove_cols)} columns (entropy < {entropy_min} or > {entropy_max})\n")
        elif entropy_min is not None:
            print(f"[GAPCLEAN] Removed {np.sum(remove_cols)} columns with entropy < {entropy_min}\n")
        else:
            print(f"[GAPCLEAN] Removed {np.sum(remove_cols)} columns with entropy > {entropy_max}\n")

    # 2) Apply the final mask
    columns_apply_pbar = tqdm(total=seq_len, desc="[GAPCLEAN] Cleaning gaps", unit="cols")
    filtered_sequences = [''] * num_seq

    for c_start in range(0, seq_len, col_chunk_size):
        c_end = min(c_start + col_chunk_size, seq_len)
        chunk_width = c_end - c_start
        mask_chunk = mask[c_start:c_end]

        for r_start in range(0, num_seq, row_chunk_size):
            r_end = min(r_start + row_chunk_size, num_seq)

            for row_idx in range(r_start, r_end):
                row_slice = sequences[row_idx][c_start:c_end]
                sub_arr = np.frombuffer(row_slice.encode('ascii'), dtype=np.uint8)
                kept_chars = sub_arr[mask_chunk]
                filtered_sequences[row_idx] += kept_chars.tobytes().decode('ascii')

        columns_apply_pbar.update(chunk_width)
    columns_apply_pbar.close()

    final_len = np.sum(mask)

    print()
    print(f"[GAPCLEAN] Final alignment length: {final_len} columns (was {seq_len})\n")

    # Write them out
    with open(output_sequences_file, 'w') as fout:
        for seq in filtered_sequences:
            fout.write(seq + "\n")


def recombine_headers_and_sequences(headers_file: str, sequences_file: str, output_fasta: str) -> None:
    """
    Merge headers and cleaned sequences back into FASTA format.

    Args:
        headers_file: Path to file containing headers
        sequences_file: Path to file containing sequences
        output_fasta: Path to output FASTA file
    """
    with open(headers_file, 'r') as fh, \
         open(sequences_file, 'r') as fs, \
         open(output_fasta, 'w') as fout:

        for hdr_line, seq_line in zip(fh, fs):
            fout.write(hdr_line.rstrip('\n') + "\n")
            fout.write(seq_line.rstrip('\n') + "\n")


def clean_alignment(
    input_file: str,
    output_file: str,
    threshold: Optional[int] = None,
    seed_index: Optional[int] = None,
    entropy_min: Optional[float] = None,
    entropy_max: Optional[float] = None,
    row_chunk_size: int = 5000,
    col_chunk_size: int = 5000,
    verbose: bool = True,
    input_format: Optional[str] = None,
    output_format: Optional[str] = None
) -> dict:
    """
    Clean gaps from a multiple sequence alignment.

    This is the main high-level API for using GapClean programmatically.
    Use this function in Python scripts and Jupyter notebooks for easy
    integration into bioinformatics pipelines.

    Args:
        input_file: Path to input alignment file
        output_file: Path to output cleaned alignment file
        threshold: Remove columns with >X% gaps (0-100). Mutually exclusive with other modes.
        seed_index: Remove gaps relative to sequence at this index (0-based). Mutually exclusive.
        entropy_min: Remove columns with entropy < X bits (keep variable). Mutually exclusive.
        entropy_max: Remove columns with entropy > X bits (keep conserved). Mutually exclusive.
        row_chunk_size: Number of sequences to process at once (default 5000)
        col_chunk_size: Number of alignment columns to process at once (default 5000)
        verbose: Print progress messages (default True)
        input_format: Input format ('fasta', 'stockholm', 'clustal', 'phylip').
                     Auto-detect if None (default).
        output_format: Output format ('fasta', 'stockholm', 'clustal', 'phylip').
                      Defaults to same as input format.

    Returns:
        dict: Statistics about the cleaning operation with keys:
            - 'input_sequences': number of input sequences
            - 'input_length': original alignment length
            - 'output_length': cleaned alignment length
            - 'columns_removed': number of columns removed
            - 'elapsed_seconds': time taken in seconds

    Raises:
        InputValidationError: If input parameters are invalid
        AlignmentError: If alignment processing fails

    Example:
        >>> from gapclean import clean_alignment
        >>>
        >>> # Threshold mode - remove columns with >50% gaps (FASTA)
        >>> stats = clean_alignment('input.fa', 'output.fa', threshold=50)
        >>> print(f"Removed {stats['columns_removed']} columns")
        >>>
        >>> # Stockholm format input (auto-detected)
        >>> stats = clean_alignment('pfam.sto', 'cleaned.fa', threshold=75)
        >>>
        >>> # Explicit format specification
        >>> stats = clean_alignment('input.aln', 'output.sto',
        ...                        threshold=50,
        ...                        input_format='clustal',
        ...                        output_format='stockholm')
        >>>
        >>> # Seed mode - remove gaps relative to first sequence
        >>> stats = clean_alignment('input.fa', 'output.fa', seed_index=0)
        >>>
        >>> # Entropy mode - keep only conserved regions
        >>> stats = clean_alignment('input.fa', 'output.fa', entropy_max=1.5)
        >>>
        >>> # Quiet mode for pipelines
        >>> stats = clean_alignment('input.fa', 'output.fa', threshold=75, verbose=False)
    """
    # Store original print state and optionally suppress output
    import sys
    from io import StringIO
    from gapclean.formats import convert_to_fasta, convert_from_fasta, detect_format

    old_stdout = sys.stdout
    if not verbose:
        sys.stdout = StringIO()

    try:
        # Validate inputs
        validate_input_file(input_file)
        validate_output_path(output_file)
        validate_threshold(threshold)
        validate_entropy_threshold(entropy_min, entropy_max)
        validate_chunk_sizes(row_chunk_size, col_chunk_size)

        # Validate exactly one mode is specified
        modes_specified = sum([
            threshold is not None,
            seed_index is not None,
            entropy_min is not None,
            entropy_max is not None
        ])

        if modes_specified == 0:
            raise InputValidationError(
                "\n[ERROR] No removal mode specified!\n"
                "  Please specify one of: threshold, seed_index, entropy_min, or entropy_max"
            )

        start_time = time.time()

        # Detect and convert input format if needed
        detected_input_format = detect_format(input_file, input_format)
        working_input, is_temp_input = convert_to_fasta(input_file, detected_input_format, verbose=verbose)

        # Determine output format
        if output_format:
            # User explicitly specified output format
            final_output_format = output_format.lower()
        else:
            # Always default to FASTA for performance
            # (Stockholm/Clustal/PHYLIP writers are very slow for large alignments)
            final_output_format = 'fasta'

        # Create temporary directory
        tmpdir = tempfile.mkdtemp(prefix="gapclean_tmp_")
        FLATTENED_FASTA = os.path.join(tmpdir, "flattened.fa")
        HEADERS_TMP = os.path.join(tmpdir, "headers.fa")
        SEQS_TMP = os.path.join(tmpdir, "seqs.fa")
        PROCESSED_SEQ_TMP = os.path.join(tmpdir, "processed.fa")
        TEMP_OUTPUT_FASTA = os.path.join(tmpdir, "output.fa")

        try:
            # Read original alignment stats
            with open(working_input, 'r') as f:
                input_num_sequences = sum(1 for line in f if line.startswith('>'))

            # Count sequences for seed validation
            if seed_index is not None:
                validate_seed_index(seed_index, input_num_sequences)

            # 1) Flatten multiline FASTA
            flatten_fasta(working_input, FLATTENED_FASTA)

            # Get original length
            with open(FLATTENED_FASTA, 'r') as f:
                for line in f:
                    if not line.startswith('>'):
                        input_alignment_length = len(line.strip())
                        break

            # 2) Split headers vs sequences
            split_headers_vs_sequences(FLATTENED_FASTA, HEADERS_TMP, SEQS_TMP)

            # 3) Run 2D-chunk gap removal
            gapclean_2d_chunk(
                input_sequences_file=SEQS_TMP,
                output_sequences_file=PROCESSED_SEQ_TMP,
                threshold=threshold,
                seed_index=seed_index,
                entropy_min=entropy_min,
                entropy_max=entropy_max,
                row_chunk_size=row_chunk_size,
                col_chunk_size=col_chunk_size
            )

            # 4) Recombine headers + cleaned sequences to temp FASTA
            recombine_headers_and_sequences(HEADERS_TMP, PROCESSED_SEQ_TMP, TEMP_OUTPUT_FASTA)

            # Get output length from temp FASTA
            with open(TEMP_OUTPUT_FASTA, 'r') as f:
                for line in f:
                    if not line.startswith('>'):
                        output_alignment_length = len(line.strip())
                        break

            # 5) Convert to final output format if needed
            if final_output_format != 'fasta':
                convert_from_fasta(TEMP_OUTPUT_FASTA, output_file, final_output_format, verbose=verbose)
            else:
                # Just copy FASTA output
                import shutil as sh
                sh.copy(TEMP_OUTPUT_FASTA, output_file)

            elapsed_seconds = time.time() - start_time

            # Return statistics
            return {
                'input_sequences': input_num_sequences,
                'input_length': input_alignment_length,
                'output_length': output_alignment_length,
                'columns_removed': input_alignment_length - output_alignment_length,
                'elapsed_seconds': elapsed_seconds
            }

        finally:
            # Clean up temp directory
            shutil.rmtree(tmpdir, ignore_errors=True)

            # Clean up converted input if it was temporary
            if is_temp_input and os.path.exists(working_input):
                os.remove(working_input)

    finally:
        # Restore stdout
        if not verbose:
            sys.stdout = old_stdout


def main() -> None:
    """Main entry point for GapClean CLI."""
    parser = argparse.ArgumentParser(
    description="""\n
    ===============================================\n
    GapClean (v1.0.5), written by Aarya Venkat, PhD\n
    ===============================================\n
    Process a sequence file to remove gaps using threshold, seed, or entropy-based methods.""",
    formatter_class=argparse.RawTextHelpFormatter
    )


    parser.add_argument('-i', '--input',  help='Input aligned fasta', required=True)
    parser.add_argument('-o', '--output', help='Output gapcleaned fasta', required=True)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-t', '--threshold', help='Threshold for gap removal (eg -t 60 for 60 percent)', type=int)
    group.add_argument('-s', '--seed', help='Index of the seed sequence (0-based) for gap removal based on this sequence only', type=int)
    group.add_argument('--entropy-min', help='Remove columns with entropy < threshold (keep variable regions, eg --entropy-min 1.5)', type=float, dest='entropy_min')
    group.add_argument('--entropy-max', help='Remove columns with entropy > threshold (keep conserved regions, eg --entropy-max 1.5)', type=float, dest='entropy_max')

    parser.add_argument('--row-chunk-size', help='number of sequences to hold in memory at once (default 5000)', type=int, default=5000)
    parser.add_argument('--col-chunk-size', help='number of columns to hold in memory at once (default 5000)', type=int, default=5000)

    parser.add_argument('--input-format', help='input format (fasta, stockholm, clustal, phylip) - auto-detect if not specified', type=str, default=None)
    parser.add_argument('--output-format', help='output format (fasta, stockholm, clustal, phylip) - defaults to input format', type=str, default=None)

    args = parser.parse_args()

    # Validate inputs early
    try:
        from gapclean.formats import convert_to_fasta, convert_from_fasta, detect_format

        validate_input_file(args.input)
        validate_output_path(args.output)
        validate_threshold(args.threshold)
        validate_entropy_threshold(args.entropy_min, args.entropy_max)
        validate_chunk_sizes(args.row_chunk_size, args.col_chunk_size)

    except GapCleanError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    start_time = time.time()

    print()
    print("  ====================================================  ")
    print("                     GapClean (v1.0.5)                  ")
    print("                     Aarya Venkat, PhD                  ")
    print("  ====================================================  ")
    print()

    # Detect and convert input format if needed
    detected_input_format = detect_format(args.input, args.input_format)
    working_input, is_temp_input = convert_to_fasta(args.input, detected_input_format, verbose=True)

    # Determine output format
    if args.output_format:
        # User explicitly specified output format
        final_output_format = args.output_format.lower()

        # Warn about slow non-FASTA formats for large alignments
        if final_output_format != 'fasta':
            print(f"[GAPCLEAN] Warning: {final_output_format.upper()} output may be slow for large alignments.")
            print(f"[GAPCLEAN] Consider using FASTA format for better performance.")

        # Warn if extension doesn't match specified format
        detected_from_extension = detect_format(args.output, None)
        if detected_from_extension != final_output_format and detected_from_extension != 'fasta':
            print(f"[GAPCLEAN] Warning: Output file extension suggests {detected_from_extension.upper()} "
                  f"but --output-format specified {final_output_format.upper()}")
    else:
        # Always default to FASTA for performance
        # (Stockholm/Clustal/PHYLIP writers are very slow for large alignments)
        final_output_format = 'fasta'

        detected_output_format = detect_format(args.output, None)
        if detected_output_format != 'fasta' and not args.output.lower().endswith(('.fa', '.fasta', '.fna', '.faa')):
            print(f"[GAPCLEAN] Note: Defaulting to FASTA output for performance.")
            print(f"[GAPCLEAN] Use --output-format {detected_output_format} to explicitly request {detected_output_format.upper()} (slower).")

    # 1) Flatten multiline fasta (pure Python for cross-platform compatibility)
    tmpdir = tempfile.mkdtemp(prefix="gapclean_tmp_")
    FLATTENED_FASTA = os.path.join(tmpdir, "flattened.fa")
    HEADERS_TMP = os.path.join(tmpdir, "headers.fa")
    SEQS_TMP = os.path.join(tmpdir, "seqs.fa")
    PROCESSED_SEQ_TMP = os.path.join(tmpdir, "processed.fa")
    TEMP_OUTPUT_FASTA = os.path.join(tmpdir, "output.fa")

    try:
        # Validate seed index if needed (after conversion so we have FASTA)
        if args.seed is not None:
            with open(working_input, 'r') as f:
                num_sequences = sum(1 for line in f if line.startswith('>'))
            validate_seed_index(args.seed, num_sequences)

        print("[GAPCLEAN] (1) Flattening input FASTA (takes a bit for larger alignments)...")
        flatten_fasta(working_input, FLATTENED_FASTA)

        # 2) Split headers vs. sequences
        print("[GAPCLEAN] (2) Splitting headers and sequence bodies ...")
        split_headers_vs_sequences(FLATTENED_FASTA, HEADERS_TMP, SEQS_TMP)

        # 3) Run 2D-chunk gap removal on the sequences
        print("[GAPCLEAN] (3) It's Gappin' Time...\n")
        gapclean_2d_chunk(
            input_sequences_file=SEQS_TMP,
            output_sequences_file=PROCESSED_SEQ_TMP,
            threshold=args.threshold,
            seed_index=args.seed,
            entropy_min=args.entropy_min,
            entropy_max=args.entropy_max,
            row_chunk_size=args.row_chunk_size,
            col_chunk_size=args.col_chunk_size
        )

        # 4) Recombine headers + cleaned sequences
        print("[GAPCLEAN] (4) Stitching back headers to sequence bodies... \n")
        recombine_headers_and_sequences(HEADERS_TMP, PROCESSED_SEQ_TMP, TEMP_OUTPUT_FASTA)

        # 5) Convert to final output format if needed
        if final_output_format != 'fasta':
            print(f"[GAPCLEAN] (5) Converting output to {final_output_format.upper()} format...\n")
            convert_from_fasta(TEMP_OUTPUT_FASTA, args.output, final_output_format, verbose=True)
        else:
            # Just copy FASTA output
            shutil.copy(TEMP_OUTPUT_FASTA, args.output)

        # Benchmark info here
        elapsed = int(time.time() - start_time)
        hrs = elapsed // 3600
        mins = (elapsed % 3600) // 60
        secs = elapsed % 60
        if hrs > 0:
            print(f"[GAPCLEAN] took {hrs}h {mins}m {secs}s to complete. Cleaned alignment located at {args.output}.\n")
        elif mins > 0:
            print(f"[GAPCLEAN] took {mins}m {secs}s to complete. Cleaned alignment located at {args.output}.\n")
        else:
            print(f"[GAPCLEAN] took {secs}s to complete. Cleaned alignment located at {args.output}. \n")

    except GapCleanError as e:
        print(f"\n{e}\n", file=sys.stderr)
        shutil.rmtree(tmpdir, ignore_errors=True)
        if is_temp_input and os.path.exists(working_input):
            os.remove(working_input)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[GAPCLEAN] Operation cancelled by user.", file=sys.stderr)
        shutil.rmtree(tmpdir, ignore_errors=True)
        if is_temp_input and os.path.exists(working_input):
            os.remove(working_input)
        sys.exit(130)
    except Exception as e:
        print(
            f"\n[GAPCLEAN] Unexpected error occurred:\n{e}\n"
            f"Please report this issue at: https://github.com/arikat/GapClean/issues\n",
            file=sys.stderr
        )
        shutil.rmtree(tmpdir, ignore_errors=True)
        if is_temp_input and os.path.exists(working_input):
            os.remove(working_input)
        sys.exit(1)
    finally:
        print("[GAPCLEAN] Removing temporary files... Remember to thank Gappy for his service.")
        shutil.rmtree(tmpdir, ignore_errors=True)
        if is_temp_input and os.path.exists(working_input):
            os.remove(working_input)


if __name__ == "__main__":
    main()