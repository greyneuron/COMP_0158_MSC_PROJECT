#!/bin/bash

# Renames files to aid listing them in order when searching a directory
#
# Files whose name contains a single digit number 0 to 9 are
# renamed to have two digits - from 0 to 00, from 1 to 01 
# Example: sqloutput_M_0.txt becomes sqloutput_M_00.txt
#
# NOTE : UNCOMMENT THE LAST LINE TO ACTUALLY DO THE RENAMING

# Directory to search for files
SEARCH_DIR="/data/dev/ucl/data/precorpus"

# Find all files in a dir
find "$SEARCH_DIR" -type f | while read -r file; do
  # Get dir & filename from the file path
  dir=$(dirname "$file")
  filename=$(basename "$file")
  
  # Check if the filename contains any numbers
  if [[ "$filename" =~ _[0-9]\.txt ]]; then
    # Add an extra 0 before each number in the filename
    new_filename=$(echo "$filename" | sed 's/M_\([0-9]\)/M_0\1/g')
    
    echo "will rename: $filename -> $new_filename"

    # UNCOMMENT THIS TO ACTUALLY RENAME THE FILE
    #mv "$file" "$dir/$new_filename"
  fi
done
