import argparse
from tqdm import tqdm

def process_fasta(input_file_path, output_file_path, threshold=99):
    threshold = float(threshold) / 100
    
    print("Step 1: Reading the file and concatenating sequences")
    with open(input_file_path, 'r') as f:
        sequences = [line.strip() for line in f]

    num_seq = len(sequences)
    seq_len = len(sequences[0])  # Assuming all sequences are of same length
    print("")
    print("Number of sequences: " + str(num_seq) + "      Sequence Length: " + str(seq_len))
    print("")
    print("Step 2: Calculating percentage of gaps for each column and identify columns to remove :: " + str(threshold) + "% gap threshold provided.")
    remove_columns = []
    for i in tqdm(range(seq_len), desc="Calculating gap percentages"):
        column = [seq[i] for seq in sequences]
        gap_percentage = (column.count('-') + column.count('.')) / num_seq
        if gap_percentage > threshold:
            remove_columns.append(i)
    print("")
    print("Step 3: Creating a new file with filtered sequences")
    print("")
    BUFFER_SIZE = 100000
    output_buffer = []

    with open(output_file_path, 'w') as g:
        for sequence in tqdm(sequences, desc="Filtering sequences"):
            filtered_seq = ''.join([char for i, char in enumerate(sequence) if i not in remove_columns])
            output_buffer.append(filtered_seq)
            
            if len(output_buffer) >= BUFFER_SIZE:
                g.write('\n'.join(output_buffer))
                g.write('\n')
                output_buffer = []

        # Write any remaining sequences in the buffer
        if output_buffer:
            g.write('\n'.join(output_buffer))
            g.write('\n')

    print("Finished")

def main():
    parser = argparse.ArgumentParser(description='Process a sequence file and remove gaps in columns with a threshold.')
    parser.add_argument('-i', '--input', help='Input file path', required=True)
    parser.add_argument('-o', '--output', help='Output file path', required=True)
    parser.add_argument('-t', '--threshold', help='Threshold for gap removal (default is 99)', type=int, default=99)

    args = parser.parse_args()

    process_fasta(args.input, args.output, args.threshold)

if __name__ == "__main__":
    main()
