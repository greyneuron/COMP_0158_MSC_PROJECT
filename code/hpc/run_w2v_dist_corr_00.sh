#!/bin/bash

hostname
date

platform=$1

if [[ "$platform" == "mac" ]]; then 
    echo "setting mac parameters"
    source_file='/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/data/models/hpc/eucdist_mc1/w2v_20240902_sg1_mc1_w3_v100.model_dist_normalised_mac.npy'
    target_file='/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/models/evo/rand_rep_distance_matrix.npy'

    output_dir='/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/code/hpc/models/'
    code_dir="/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/code/hpc"

elif [[ "$platform" == "aws" ]]; then 
    echo "setting aws parameters"
    corpus_file='/word2vec/code/word2vec_sentences.pkl'
    output_dir='/word2vec/models/01'
    code_dir="/word2vec/code"
fi

# call python
python3 "${code_dir}/w2v_dist_corr_batch.py" --source_file="${source_file}" --target_file="${target_file}" --output_dir="$output_dir"

date