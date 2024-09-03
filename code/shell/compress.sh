#!/bin/bash

# compress distance files on aws
source_directory="/word2vec/models"
extension="npy"

# Get the list of files in numerical order
# ls -r will list in reverse order (oldest file first)
# ls -t will list newest first
file_list=$(ls -t -r "$source_directory"/*"$extension")

# Loop through each file in the list
for file in $file_list; do
    echo "Processing file: $file"
    gzip $file
done
