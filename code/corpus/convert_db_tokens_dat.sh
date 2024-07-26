#!/bin/bash

# This script is step 2 of 4 to get a sentence to pass into word2vec
# It assumes there is a database with two tables :W2V_PROTEIN and W2V_TOKEN
#
# 4 steps:
# 1. Runs sql from the mysql command line and pipes it to an output file : sql_output_<startprotein>_<iteration>.txt
#    You need to change the start poisitoin and chunk size and number of iterations
#    I found that it would iterate through 500k proteins in about 3.5mins so I would set the chunk size to 500000 and iterate from 0..9 to get 10M
# 2. ** THIS SCRIPT ** : convert_db_tokens_dat.sh converts each of the txt outputs from step 1 into a dat file of pipe separated tokens - each line has a token and its corresponding uniprot id
# 3. The next script then converts those lines into a single line per protein
# 4. The final script then creates a sentence for each protein with GAP DISORDER and PFAM

directory="/Users/patrick/dev/ucl/comp0158_mscproject/code/corpus/output"
extension="txt"

# single quotes '...' doesn't further interpret whats between the quotes
# double quotes "..." interprets $, `" \ !
#name=patrick
#echo '$name' # -> prints out $name
#echo "$name" # -> prints out patrick

# Get the list of files in numerical order
file_list=$(ls "$directory"/*"$extension" | sort -n)

# Loop through each file in the list
for file in $file_list; do
    echo "Processing file: $file"

    base_name=$(basename ${file})
    name_without_extension="${file%.*}"
    #echo "base:" $name_without_extension

    # convert
    cat ${file} | awk '{FS ="\t"} {if (!($1~/^UNIPROT/)) print $1 ":" $2 ":" $3 "|" $5 ":" $6 ":" $7 ":" $8}' >> $name_without_extension.dat

done
