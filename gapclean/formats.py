# gapclean/formats.py

"""
Format conversion utilities for GapClean.

Supports conversion between FASTA and other common alignment formats:
- Stockholm (.sto, .stk)
- Clustal (.aln, .clustal)
- PHYLIP (.phy, .phylip)
"""

from typing import Optional, Tuple
import os
import tempfile


def detect_format(filepath: str, format_hint: Optional[str] = None) -> str:
    """
    Detect alignment format from file extension or content.

    Args:
        filepath: Path to alignment file
        format_hint: Optional format hint ('fasta', 'stockholm', 'clustal', 'phylip')

    Returns:
        Detected format string
    """
    if format_hint:
        return format_hint.lower()

    # Try extension-based detection
    ext = os.path.splitext(filepath)[1].lower().lstrip('.')

    format_map = {
        'fa': 'fasta',
        'fasta': 'fasta',
        'fna': 'fasta',
        'faa': 'fasta',
        'sto': 'stockholm',
        'stk': 'stockholm',
        'stockholm': 'stockholm',
        'aln': 'clustal',
        'clustal': 'clustal',
        'phy': 'phylip',
        'phylip': 'phylip',
    }

    detected = format_map.get(ext)
    if detected:
        return detected

    # Try content-based detection
    try:
        with open(filepath, 'r') as f:
            first_line = f.readline().strip()

            # Stockholm format
            if first_line.startswith('# STOCKHOLM'):
                return 'stockholm'

            # FASTA format
            if first_line.startswith('>'):
                return 'fasta'

            # Clustal format
            if first_line.startswith('CLUSTAL') or first_line.startswith('MUSCLE'):
                return 'clustal'

            # PHYLIP format (first line is typically: num_sequences num_positions)
            if first_line.split() and len(first_line.split()) == 2:
                try:
                    int(first_line.split()[0])
                    int(first_line.split()[1])
                    return 'phylip'
                except ValueError:
                    pass
    except Exception:
        pass

    # Default to FASTA
    return 'fasta'


def convert_to_fasta(input_file: str, input_format: Optional[str] = None, verbose: bool = True) -> Tuple[str, bool]:
    """
    Convert alignment to FASTA format if needed.

    Args:
        input_file: Path to input alignment
        input_format: Format hint ('fasta', 'stockholm', 'clustal', 'phylip')
                     If None, auto-detect from extension/content
        verbose: Print conversion messages

    Returns:
        Tuple of (fasta_path, is_temp_file)
        - fasta_path: Path to FASTA file (original or converted)
        - is_temp_file: True if temp file was created and should be cleaned up
    """
    from Bio import AlignIO
    from tqdm import tqdm

    # Detect format
    detected_format = detect_format(input_file, input_format)

    # Already FASTA - return as-is
    if detected_format == 'fasta':
        return input_file, False

    # Convert to FASTA
    if verbose:
        print(f"[GAPCLEAN] Converting {detected_format.upper()} to FASTA...")
        print(f"[GAPCLEAN] Reading alignment...")

    try:
        # Read alignment in detected format
        alignment = AlignIO.read(input_file, detected_format)

        # Create temporary FASTA file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.fa', prefix='gapclean_convert_')
        os.close(temp_fd)  # Close the file descriptor

        num_seqs = len(alignment)
        aln_len = alignment.get_alignment_length()

        # Write as FASTA with progress bar
        if verbose:
            print(f"[GAPCLEAN] Writing {num_seqs} sequences to FASTA format...")

        with open(temp_path, 'w') as f:
            if verbose:
                # Write with progress bar
                for record in tqdm(alignment, total=num_seqs, desc="[GAPCLEAN] Converting", unit="seqs"):
                    f.write(f">{record.id}\n{str(record.seq)}\n")
            else:
                # Write without progress
                AlignIO.write(alignment, f, 'fasta')

        if verbose:
            print(f"[GAPCLEAN] Converted {num_seqs} sequences of length {aln_len}")

        return temp_path, True

    except Exception as e:
        raise ValueError(
            f"Failed to convert {detected_format.upper()} to FASTA: {e}\n"
            f"Please ensure the file is a valid {detected_format.upper()} alignment."
        )


def convert_from_fasta(fasta_file: str, output_file: str, output_format: str, verbose: bool = True) -> None:
    """
    Convert FASTA alignment to desired output format.

    Args:
        fasta_file: Path to FASTA alignment
        output_file: Path to output file
        output_format: Desired format ('fasta', 'stockholm', 'clustal', 'phylip')
        verbose: Print conversion messages
    """
    from Bio import AlignIO
    from Bio.Align import MultipleSeqAlignment
    from tqdm import tqdm
    import shutil

    output_format = output_format.lower()

    # Already FASTA - just copy
    if output_format == 'fasta':
        shutil.copy(fasta_file, output_file)
        return

    if verbose:
        print(f"[GAPCLEAN] Converting output to {output_format.upper()}...")
        print(f"[GAPCLEAN] Note: {output_format.upper()} conversion may take several minutes for large alignments...")

    try:
        # Read FASTA alignment
        if verbose:
            print(f"[GAPCLEAN] Reading FASTA alignment...")

        alignment = AlignIO.read(fasta_file, 'fasta')
        num_seqs = len(alignment)

        if verbose:
            print(f"[GAPCLEAN] Writing {num_seqs} sequences to {output_format.upper()} format...")
            print(f"[GAPCLEAN] This may take a while - BioPython's {output_format.upper()} writer is slow for large datasets.")

        # Write with simulated progress (BioPython doesn't expose write progress)
        # We can't easily hook into BioPython's write process, but we can show activity
        with open(output_file, 'w') as f:
            if verbose and num_seqs > 10000:
                # For large files, show a warning and indeterminate progress
                print(f"[GAPCLEAN] Writing in progress... (this will take ~{num_seqs//1000} minutes for {num_seqs} sequences)")

            # BioPython's write is a black box - we can't show granular progress
            # But at least we've warned the user
            AlignIO.write(alignment, f, output_format)

        if verbose:
            print(f"[GAPCLEAN] Successfully wrote {output_format.upper()} format")

    except Exception as e:
        raise ValueError(
            f"Failed to convert to {output_format.upper()}: {e}"
        )
