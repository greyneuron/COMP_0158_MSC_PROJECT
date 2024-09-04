#!/bin/bash

hostname
date

platform=$1

if [[ "$platform" == "mac" ]]; then 
    echo "setting mac parameters"
    source_dir='/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/models/hpc/models'
    #output_dir='/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/models/hpc/distances/'
    output_dir='/Volumes/My Passport/data/distances/'
    code_dir="/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/code/hpc"

elif [[ "$platform" == "aws" ]]; then 
    echo "setting aws parameters"
    corpus_file='/word2vec/code/word2vec_sentences.pkl'
    output_dir='/word2vec/models/01'
    code_dir="/word2vec/code"
fi


# set the directory and extension of files ton concatenate
extension="model"

# Get the list of models
file_list=$(find "$source_dir" -name "*$extension")

# Loop through each file in the list
for file in $file_list; do

    dir=$(dirname "$file")
    filename=$(basename "$file" | cut -d. -f1)

    echo "Creating matrices for : $filename"
    
    python3 "${code_dir}/w2v_dist_batch.py" --model_file="${file}" --output_dir="$output_dir"

    #echo "zip up the cosine matrices.."
    #echo "zip up the euclidean matrices.."
    ##gzip ${output_dir}${filename}_cos_dist.npy
    #gzip ${output_dir}${filename}_euc_dist.npy
    #echo "$filename complete"
done


# call python
#python3 "${code_dir}/w2v_dist_batch.py" --model_file="${source_file}" --output_dir="$output_dir"

date