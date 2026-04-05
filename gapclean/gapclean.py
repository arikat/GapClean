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


def validate_entropy_threshold(entropy_threshold: Optional[float]) -> None:
    """Validate entropy threshold parameter."""
    if entropy_threshold is not None:
        if entropy_threshold < 0:
            raise InputValidationError(
                f"\n[ERROR] Entropy threshold must be non-negative, got: {entropy_threshold}\n"
                f"  Example: -e 1.5 removes columns with entropy < 1.5 bits."
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
    entropy_threshold: Optional[float] = None,
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
        entropy_threshold: Remove columns with entropy < threshold bits (mutually exclusive)
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
    elif entropy_threshold is not None:
        print(f"[GAPCLEAN] Removing columns with entropy < {entropy_threshold} bits.\n")
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

        # Remove columns below threshold
        remove_cols = (entropy_values < entropy_threshold)
        mask[remove_cols] = False

        print(f"[GAPCLEAN] Average entropy: {np.mean(entropy_values):.3f} bits")
        print(f"[GAPCLEAN] Removed {np.sum(remove_cols)} columns with entropy < {entropy_threshold}\n")

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


def main() -> None:
    """Main entry point for GapClean CLI."""
    parser = argparse.ArgumentParser(
    description="""\n
    ===============================================\n
    GapClean (v1.0.3), written by Aarya Venkat, PhD\n
    ===============================================\n
    Process a sequence file to remove gaps using threshold, seed, or entropy-based methods.""",
    formatter_class=argparse.RawTextHelpFormatter
    )


    parser.add_argument('-i', '--input',  help='Input aligned fasta', required=True)
    parser.add_argument('-o', '--output', help='Output gapcleaned fasta', required=True)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-t', '--threshold', help='Threshold for gap removal (eg -t 60 for 60 percent)', type=int)
    group.add_argument('-s', '--seed', help='Index of the seed sequence (0-based) for gap removal based on this sequence only', type=int)
    group.add_argument('-e', '--entropy', help='Entropy threshold for column removal (eg -e 1.5)', type=float)

    parser.add_argument('--row-chunk-size', help='number of sequences to hold in memory at once (default 5000)', type=int, default=5000)
    parser.add_argument('--col-chunk-size', help='number of columns to hold in memory at once (default 5000)', type=int, default=5000)

    args = parser.parse_args()

    # Validate inputs early
    try:
        validate_input_file(args.input)
        validate_output_path(args.output)
        validate_fasta_format(args.input)
        validate_threshold(args.threshold)
        validate_entropy_threshold(args.entropy)
        validate_chunk_sizes(args.row_chunk_size, args.col_chunk_size)

        # Count sequences for seed validation
        if args.seed is not None:
            with open(args.input, 'r') as f:
                num_sequences = sum(1 for line in f if line.startswith('>'))
            validate_seed_index(args.seed, num_sequences)

    except GapCleanError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    start_time = time.time()

    print()
    print("  ====================================================  ")
    print("                     GapClean (v1.0.3)                  ")
    print("                     Aarya Venkat, PhD                  ")
    print("  ====================================================  ")
    print()

    # 1) Flatten multiline fasta (pure Python for cross-platform compatibility)
    tmpdir = tempfile.mkdtemp(prefix="gapclean_tmp_")
    FLATTENED_FASTA = os.path.join(tmpdir, "flattened.fa")
    HEADERS_TMP = os.path.join(tmpdir, "headers.fa")
    SEQS_TMP = os.path.join(tmpdir, "seqs.fa")
    PROCESSED_SEQ_TMP = os.path.join(tmpdir, "processed.fa")

    try:
        print("[GAPCLEAN] (1) Flattening input FASTA (takes a bit for larger alignments)...")
        flatten_fasta(args.input, FLATTENED_FASTA)

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
            entropy_threshold=args.entropy,
            row_chunk_size=args.row_chunk_size,
            col_chunk_size=args.col_chunk_size
        )

        # 4) Recombine headers + cleaned sequences
        print("[GAPCLEAN] (4) Stitching back headers to sequence bodies... \n")
        recombine_headers_and_sequences(HEADERS_TMP, PROCESSED_SEQ_TMP, args.output)

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
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[GAPCLEAN] Operation cancelled by user.", file=sys.stderr)
        shutil.rmtree(tmpdir, ignore_errors=True)
        sys.exit(130)
    except Exception as e:
        print(
            f"\n[GAPCLEAN] Unexpected error occurred:\n{e}\n"
            f"Please report this issue at: https://github.com/arikat/GapClean/issues\n",
            file=sys.stderr
        )
        shutil.rmtree(tmpdir, ignore_errors=True)
        sys.exit(1)
    finally:
        print("[GAPCLEAN] Removing temporary files... Remember to thank Gappy for his service.")
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    main()