#!/bin/bash

# --------------------------------------------------------------------------
#    Wrapper shell script to run mantel test on distance matrices
# --------------------------------------------------------------------------

hostname
date

evo_file="/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/distances/evo/rand_rep_distance_matrix.npy"
source_directory="/Volumes/My Passport/data/distances"
code_dir="/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/code/hpc"
output_dir='/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/distances/'

# find all npy files - each contains a matrix and vector
#find "$source_directory" -type f -name "*npy" | while IFS= read -r file; do
# find one file
find "$source_directory" -type f -name "w2v_20240831_sg1_mc1_w3_v10*npy" | while IFS= read -r file; do
    filename=$(basename "$file" | cut -d. -f1)
    echo "Processing model: ${filename}"
    python3 "${code_dir}/w2v_dist_corr_batch.py" --w2v_file="${file}" --evo_file="${evo_file}" --output_dir="$output_dir" --base_name="${filename}"

done
