#!/bin/bash


# ------------------------- DEPRECATED ------------------------- 
# Note that the approach in this script has been been superceded by a much faster approach as described in extract_tokens_from_db.sh
# --------------------------------------------------------------

# 5 steps:
# 1. extract_tokens_from_db.sh : Runs sql from the mysql command line and pipes it to an output file : sql_output_<startprotein>_<iteration>.txt
# 2. convert_db_tokens_dat.sh  : Converts each of the txt outputs from step 1 into a dat file of pipe separated tokens.
#    Each line consists of information about a token and its corresponding uniprot id
# 3. combine_db_tokens_dat.py : Converts each lines (one per token) into a single line per protein (each line with multiple tokens for that protein plus metadata)
# 4. create_corpus.py : Creates a sentence for each protein with GAP DISORDER and PFAM 'words', orders the tokens and removes overlaps
# 5. run_word2vec.py  : Calls word2vec with the corpus
#
# ------ Instructions for this script ------ 
# Just set the directory where the sql ouput is
# UNcomment the last line when you want ot actuall run the script - without that it will just print out
# the files it is going to parse (useful as a test)
#

directory="/data/dev/ucl/data/precorpus/0M_10M"
extension="txt"

# Get the list of files in numerical order
file_list=$(ls "$directory"/*"$extension" | sort -n)

# Loop through each file in the list
for file in $file_list; do
    echo "Processing file: $file"

    base_name=$(basename ${file})
    name_without_extension="${file%.*}"

    # TODO: UNCOMMENT THIS TO RUN
    #cat ${file} | awk '{FS ="\t"} {if (!($1~/^UNIPROT/)) print $1 ":" $2 ":" $3 "|" $5 ":" $6 ":" $7 ":" $8}' >> $name_without_extension.dat
done
