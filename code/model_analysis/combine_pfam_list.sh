#!/bin/bash

# ------ Background------ 
#
# Use this script to combine multiple pfam ids into one - pfam ids have been found by 
# joining agsainst the protein table that contains only eukaryotic proteins 
#

directory="/Users/patrick/dev/ucl/comp0158_mscproject/data/pfam/tmp/"
extension="txt"

# Get the list of files in numerical order
file_list=$(ls "$directory"/*"$extension" | sort -n)

# Loop through each file in the list
for file in $file_list; do
    echo "Processing file: $file"

    cat ${file} >> "/Users/patrick/dev/ucl/comp0158_mscproject/data/pfam/non_unique_eukaryotic_pfam.txt"
done


# to get unique
cat "/Users/patrick/dev/ucl/comp0158_mscproject/data/pfam/non_unique_eukaryotic_pfam.txt" | sort | uniq > "/Users/patrick/dev/ucl/comp0158_mscproject/data/pfam/unique_eukaryotic_pfam.txt"
