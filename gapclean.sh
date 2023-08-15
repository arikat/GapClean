#!/bin/bash

# Function to display help
display_help() {
    echo
    echo
    echo "  ====================================================  "
    echo
    echo "                      GapClean (v0.4)                   "
    echo
    echo "                  Written by Aarya Venkat               "
    echo
    echo "  ====================================================  "
    echo
    echo "Description: GapClean takes a gappy multiple sequence alignment"
    echo "and removes columns with gaps at a specified threshold value to"
    echo "produce a \"cleaner\" and easier to visualize sequence alignment."
    echo
    echo "Usage: $0 [options]"
    echo
    echo "   -i   Input file       Required."
    echo "   -o   Output file      Required."
    echo "   -t   Threshold value  Optional. Default is 99."
    echo "   -h   Display this help message."
    echo
    echo
    echo "  Example: gapclean -i input.fa -o output.fa -t 95  "
    echo
    exit 1
}

# Initialize variables
INPUT=""
OUTPUT=""
THRESHOLD=99  # Default value

# Parse command line arguments
while getopts "i:o:t:h" opt; do
  case $opt in
    i) INPUT="$OPTARG"
    ;;
    o) OUTPUT="$OPTARG"
    ;;
    t) THRESHOLD="$OPTARG"
    ;;
    h) display_help
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
    ;;
  esac
done

# Check if required arguments are provided
if [ -z "$INPUT" ] || [ -z "$OUTPUT" ]; then
    echo
    echo "Invalid options. -i (input) and -o (output) are required."
    echo
    display_help
    echo
    exit 1
fi

echo

# Dynamic naming based on the input name
HEADERS_TMP="${INPUT}.headers.txt"
SEQUENCES_TMP="${INPUT}.sequences.txt"
PROCESSED_SEQUENCES_TMP="${INPUT}.sequences.processed.txt"

echo "splitting $INPUT into sequences and headers"

grep -v ">" $INPUT > $SEQUENCES_TMP
grep ">" $INPUT > $HEADERS_TMP

echo

# Call the python script with the parsed arguments
python gapclean.py -i $SEQUENCES_TMP -o $PROCESSED_SEQUENCES_TMP -t "$THRESHOLD"

# Combine headers and processed sequences into the output file
paste -d'\n' $HEADERS_TMP $PROCESSED_SEQUENCES_TMP > $OUTPUT

# Remove temporary files
rm $HEADERS_TMP $SEQUENCES_TMP $PROCESSED_SEQUENCES_TMP
