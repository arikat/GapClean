import argparse
from tqdm import tqdm

def process_fasta(input_file_path, output_file_path, threshold=None, seed_index=None):
    with open(input_file_path, 'r') as f:
        sequences = [line.strip() for line in f if not line.startswith(">")]

    num_seq = len(sequences)
    seq_len = len(sequences[0])  # Assuming all sequences are of the same length
    print(f"\nNumber of sequences: {num_seq}      Sequence Length: {seq_len}\n")
    
    remove_columns = []

    if threshold is not None:
        print(f"Removing columns with more than {threshold}% gaps.")
        threshold = float(threshold) / 100
        for i in range(seq_len):
            column = [seq[i] for seq in sequences]
            gap_percentage = (column.count('-') + column.count('.')) / num_seq
            if gap_percentage > threshold:
                remove_columns.append(i)

    elif seed_index is not None:
        print(f"Removing columns based on gaps in the seed sequence at index {seed_index}.")
        seed_sequence = sequences[seed_index]
        remove_columns = [i for i, char in enumerate(seed_sequence) if char == '-' or char == '.']

    print("\nCreating a new file with filtered sequences\n")
    with open(output_file_path, 'w') as g:
        for sequence in sequences:
            filtered_seq = ''.join([char for i, char in enumerate(sequence) if i not in remove_columns])
            g.write(filtered_seq + '\n')

    print("Finished")


def main():
    parser = argparse.ArgumentParser(description='Process a sequence file to either remove gaps in columns exceeding a threshold across all sequences or based on gaps in a specified seed sequence.')
    
    parser.add_argument('-i', '--input', help='Input file path', required=True)
    parser.add_argument('-o', '--output', help='Output file path', required=True)
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-t', '--threshold', help='Threshold for gap removal across all sequences (percentage, without the % sign)', type=int)
    group.add_argument('-s', '--seed', help='Index of the seed sequence (0-based) for gap removal based on this sequence only', type=int)

    args = parser.parse_args()

    # Call the processing function with either threshold or seed, depending on what was provided
    process_fasta(args.input, args.output, threshold=args.threshold, seed_index=args.seed)


if __name__ == "__main__":
    main()
