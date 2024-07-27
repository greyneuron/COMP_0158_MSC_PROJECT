#!/bin/bash

# renames files whose name contains number 0 to 9 to instead be
# 00 to 09. E.G sqloutput_M_0.txt becomes sqloutput_M_00.txt
# this keeps the order better 

# Directory to search for files
SEARCH_DIR="/data/dev/ucl/data/precorpus"

# Find all files containing numbers in their names
find "$SEARCH_DIR" -type f | while read -r file; do
  # Extract the directory and filename from the file path
  dir=$(dirname "$file")
  filename=$(basename "$file")
  
  # Check if the filename contains any numbers
  if [[ "$filename" =~ _[0-9]\.txt ]]; then
    # Add an extra 0 before each number in the filename
    new_filename=$(echo "$filename" | sed 's/M_\([0-9]\)/M_0\1/g')
    
    echo "will rename: $filename -> $new_filename"

    # Rename the file
    #mv "$file" "$dir/$new_filename"
    
  fi
done
