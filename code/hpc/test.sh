#!/bin/bash

hostname
date

evo_file="/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/distances/evo/rand_rep_distance_matrix.npy"
source_directory="/Volumes/My Passport/data/distances"
code_dir="/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/code/hpc"
output_dir='/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/distances/'


# Use find to locate all files in the directory and loop through them
#find "$source_directory" -type f | while IFS= read -r file; do
find "$source_directory" -type f -name "*w3_v5_*npy" | while IFS= read -r file; do
    echo "Processing file: $file"

    filename=$(basename "$file" | cut -d. -f1)

    echo "Found model name : ${filename}"
    
    python3 "${code_dir}/w2v_dist_corr_batch.py" --w2v_file="${file}" --evo_file="${evo_file}" --output_dir="$output_dir" --base_name="${filename}"


done
