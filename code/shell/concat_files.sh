#!/bin/bash

# set the directory and extension of files ton concatenate
source_directory="/Users/patrick/dev/ucl/comp0158_mscproject/data/corpus/tokens/"
extension="dat"
output_file="/Users/patrick/dev/ucl/comp0158_mscproject/data/corpus/tokens/uniref100_e_tokens_20240808_ALL.dat"

# Get the list of files in numerical order
# ls -r will list in reverse order (oldest file first)
# ls -t will list newest first
file_list=$(ls -t -r "$source_directory"/*"$extension")

# Loop through each file in the list
for file in $file_list; do
    #echo "Processing file: $file and appending to $output_file"
    echo "Processing file: $file"

    cat ${file} >> $output_file
done


# to get unique
#cat "/Users/patrick/dev/ucl/comp0158_mscproject/data/pfam/non_unique_eukaryotic_pfam.txt" | sort | uniq > "/Users/patrick/dev/ucl/comp0158_mscproject/data/pfam/unique_eukaryotic_pfam.txt"