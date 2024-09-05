#!/bin/bash

# --------------------------------------------------------------------------
#    Wrapper shell script to run mantel test on distance matrices
# --------------------------------------------------------------------------

hostname
date

model_dir="/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/models/best/"
model_name="w2v_20240903_sg1_mc8_w44_v25_best"

code_dir="/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/code/clustering"
output_dir='/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/clusters/'


python3 "${code_dir}/w2v_cluster.py" --k=10 --model_dir="${model_dir}" --model_name="${model_name}" --output_dir="$output_dir"

