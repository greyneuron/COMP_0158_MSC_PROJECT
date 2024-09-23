#!/bin/bash



#   This is the most basic QSUB file needed for this cluster.
#   Further examples can be found under /share/apps/examples
#   Most software is NOT in your PATH but under /share/apps
#
#   For further info please read http://hpc.cs.ucl.ac.uk
#   For cluster help email cluster-support@cs.ucl.ac.uk
#
#   NOTE hash dollar is a scheduler directive not a comment.


# These are flags you must include - Two memory and one runtime.
# Runtime is either seconds or hours:min:sec

#$ -l tmem=3G
#$ -l h_vmem=3G
#$ -l h_rt=7200 

#These are optional flags but you probably want them in all jobs

#$ -S /bin/bash
#$ -j y
#$ -N word2vec_01

#$ -o /home/plowry/word2vec/logs
#$ -e /home/plowry/word2vec/logs

#The code you want to run now goes here.

hostname
date

platform=$1

if [[ "$platform" == "mac" ]]; then 
    echo "Setting mac parameters"
    #corpus_file='/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/data/corpus/uniref100_e_corpus_gap_50_20240920_1643.txt'
    corpus_file='/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/data/corpus/0922/uniref100_e_corpus_gap_100_20240922_1421.txt'
    output_dir='/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/data/models/0922_g100/'
    code_dir="/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/code/model"

elif [[ "$platform" == "aws" ]]; then 
    echo "setting aws parameters"
    corpus_file='/word2vec/code/uniref100_e_corpus.dat'
    output_dir='/word2vec/models/'
    code_dir="/word2vec/code"
else
    echo "setting hpc parameters"
    corpus_file='/home/plowry/word2vec/models/word2vec_sentences.pkl'
    output_dir='/home/plowry/word2vec/models/'
    code_dir="/home/plowry/word2vec"

    source /share/apps/source_files/python/python-3.11.9.source
    . /home/plowry/w2v-env/bin/activate
fi

# call python

date
echo "running models...."
python3 "${code_dir}/w2v_model_batch.py" --mt skip --mc -1 --ws -1 --vs -1 --corpus_file="${corpus_file}" --output_dir="$output_dir"
date



