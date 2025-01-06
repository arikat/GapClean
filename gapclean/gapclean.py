# gapclean/gapclean.py

import argparse
import os
import sys
import time
import tempfile
import shutil
import subprocess
from tqdm import tqdm
import numpy as np


def flatten_fasta(input_file, output_file):
    cmd = [
        "awk",
        '/^>/{if (NR>1) printf("\\n"); print; next} {printf $0}'
    ]
    with open(input_file, "rb") as fin, open(output_file, "wb") as fout:
        proc = subprocess.Popen(cmd, stdin=fin, stdout=fout)
        proc.wait()
        if proc.returncode != 0:
            raise subprocess.CalledProcessError(proc.returncode, cmd)


def split_headers_vs_sequences(input_file, headers_file, sequences_file):
    with open(input_file, 'r') as fin, \
         open(headers_file, 'w') as fhdr, \
         open(sequences_file, 'w') as fseq:

        for line in fin:
            if line.startswith('>'):
                fhdr.write(line)
            else:
                fseq.write(line)


def gapclean_2d_chunk(
    input_sequences_file,
    output_sequences_file,
    threshold=None,
    seed_index=None,
    row_chunk_size=5000,
    col_chunk_size=5000
):
    
    """
    2D chunking over rows (sequences) and columns. Basically imagine a square (or rectangle) maneuvering over the alignment, one chunk at a time.
    I did this in order to limit the amount of sequences the computer is holding in memory (programming on a potato over here.) This results in a 
    fairly efficient search space for gaps across massive alignments. 

    - threshold: columns with > threshold% gaps are removed
    - seed_index: columns with gaps in seed row are removed
    - row_chunk_size: how many rows (sequences) to handle at once
    - col_chunk_size: how many columns to handle at once
    """

    sequences = []
    with open(input_sequences_file, 'r') as fin:
        for line in fin:
            seq = line.strip()
            if seq:
                sequences.append(seq)

    num_seq = len(sequences)
    if num_seq == 0:
        print("[GAPCLEAN] Warning: No sequences found in input file!")
        with open(output_sequences_file, 'w'):
            pass
        return

    seq_len = len(sequences[0])
    for idx, seq in enumerate(sequences):
        if len(seq) != seq_len:
            raise ValueError(
                f"[ERROR] Sequence {idx} length {len(seq)} != expected {seq_len}."
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

    # Future -- add an option C for entropy-based gap removal

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


def recombine_headers_and_sequences(headers_file, sequences_file, output_fasta):

    with open(headers_file, 'r') as fh, \
         open(sequences_file, 'r') as fs, \
         open(output_fasta, 'w') as fout:

        for hdr_line, seq_line in zip(fh, fs):
            fout.write(hdr_line.rstrip('\n') + "\n")
            fout.write(seq_line.rstrip('\n') + "\n")


def main():
    parser = argparse.ArgumentParser(
    description="""\n                               
    =============================================\n
    GapClean (v1.0), written by Aarya Venkat, PhD\n 
    =============================================\n                                                              
    Process a sequence file to either remove gaps in columns exceeding a certain\n
    threshold across all sequences or based on gaps in a specified seed sequence.""", 
    formatter_class=argparse.RawTextHelpFormatter
    )


    parser.add_argument('-i', '--input',  help='Input FASTA', required=True)
    parser.add_argument('-o', '--output', help='Output FASTA', required=True)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-t', '--threshold', help='Threshold for gap removal across all sequences (eg -t 60 for 60 percent threshold)', type=int)
    group.add_argument('-s', '--seed', help='Index of the seed sequence (0-based) for gap removal based on this sequence only', type=int)

    parser.add_argument('--row-chunk-size', type=int, default=5000)
    parser.add_argument('--col-chunk-size', type=int, default=5000)

    args = parser.parse_args()

    start_time = time.time()

    print()
    print("  ====================================================  ")
    print("                      GapClean (v1.0)                   ")
    print("                     Aarya Venkat, PhD                  ")
    print("  ====================================================  ")
    print()

    # 1) Flatten multiline FASTA with AWK
    tmpdir = tempfile.mkdtemp(prefix="gapclean_awk_")
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

    finally:
        print("[GAPCLEAN] Removing temporary files... Remember to thank Gappy for his service.")
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    main()