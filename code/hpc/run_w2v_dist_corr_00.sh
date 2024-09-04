#!/bin/bash

hostname
date

platform=$1

if [[ "$platform" == "mac" ]]; then 
    echo "setting mac parameters"

    source_directory="/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/distances"
    evo_file="/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/distances/evo/rand_rep_distance_matrix.npy"

    output_dir='/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/distances/'
    code_dir="/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/code/hpc"

elif [[ "$platform" == "aws" ]]; then 
    echo "setting aws parameters"
    source_directory='/word2vec/distances/'
    output_dir='/word2vec/models/'
    code_dir="/word2vec/code/"
fi


# ---------------------------------------------------------
# Get the list of models
# ---------------------------------------------------------
extension="npy"
#file_list=$(find "$source_directory" -name "*$extension")
#file_list=$(find "$source_directory" -name "*w3_v5_mac_euc*$extension")
file_list=$(find "$source_directory" -name "*w3_v5_mac_cos*$extension")

# Loop through each file in the list
for file in $file_list; do

    dir=$(dirname "$file")
    filename=$(basename "$file" | cut -d. -f1)

    echo "Found model name : ${filename}"

    #echo "Unzipping ${dir}/${filename}.npy.gz"
    #gzip -v -d "${dir}/${filename}.npy.gz"
    
    python3 "${code_dir}/w2v_dist_corr_batch.py" --w2v_file="${file}" --evo_file="${evo_file}" --output_dir="$output_dir" --base_name="${filename}"

    echo "$file complete"
done

date