import re
import time
from gensim import corpora
from gensim.models import Word2Vec
from datetime import datetime
import os
import glob

# ------ Background------ 
#
# This script is step 5 of 5 to create sentences to form a corpus for word2vec
#
# 5 steps:
# 1. extract_tokens_from_db.sh : Runs sql from the mysql command line and pipes it to an output file : sql_output_<startprotein>_<iteration>.txt
# 2. convert_db_tokens_dat.sh  : Converts each of the txt outputs from step 1 into a dat file of pipe separated tokens.
#    Each line consists of information about a token and its corresponding uniprot id
# 3. combine_db_tokens_dat.py : Converts each lines (one per token) into a single line per protein (each line with multiple tokens for that protein plus metadata)
# 4. create_corpus.py : Creates a sentence for each protein with GAP DISORDER and PFAM 'words', orders the tokens and removes overlaps
# 5. run_word2vec.py  : Calls word2vec with the corpus
#


# documentation : https://github.com/piskvorky/gensim#documentation


# Creates a word2vec model
# opens a folder with corpus files, for each file it tokenises the words in each 
# and adds ech token to the sentecnes required for word2vec. It then creates and saves 
# the model.
#
'''
On Macbook - V10 W5
Sentence parse time taken 800.3100779056549
Creating model /Users/patrick/dev/ucl/comp0158_mscproject/code/corpus/model/w2v_20240805_vs10_w5.model.....
Model creation time 1976.5878400802612
Model saved to /Users/patrick/dev/ucl/comp0158_mscproject/code/corpus/model/w2v_20240805_vs10_w5.model

On Macbook - V10 W10
Sentence parse time taken 881.1151170730591
Creating model /Users/patrick/dev/ucl/comp0158_mscproject/models/w2v_20240805_vs10_w10.model.....
Model creation time 2052.9426929950714
Model saved to /Users/patrick/dev/ucl/comp0158_mscproject/models/w2v_20240805_vs10_w10.model
'''
#
# parses a directory to build up sentences to create a model
#
def get_corpus_sentences(corpus_dir):
    # find the files in the target directory
    #print('Searching for corpi files in:', corpus_dir)
    file_list = glob.glob(os.path.join(corpus_dir, '*corpus*.txt'))
    
    # initialise
    s = time.time()
    sentences = []
    
    # parse each corpus file to build up the sentences
    for file_path in file_list:
        with open(file_path, 'r') as file:
            print(f'Parsing file: {file_path}')
            for line in file:
                tokens = line.split()
                sentences.append(tokens)       
    # time check
    e = time.time()
    print(f"Sentence parse time taken {e - s}" )
    return sentences

#
# Create W2V model
#
def create_w2v(sentences, model_name, vector_size, window_size):
    current_date    = datetime.now().strftime('%Y%m%d')
    model_name      = model_name + ".model"
    
    s = time.time()
    
    print(f"Creating model {model_name} from corpus files in {corpus_dir}......")
    
    # create model from sentences
    print(f"Creating model {model_name}.....")           
    w2v = Word2Vec(sentences, vector_size=vector_size, window=window_size, workers=4, epochs=10, min_count=5)
    
    # time check
    e = time.time()
    print(f"Model creation time {e - s}s")
          
    # save model      
    w2v.save(model_name)
    print(f"Model saved to {model_name}")


# ---------------------------------------------------
#
# CHANGE MODEL PARAMETERS HERE
#
# ---------------------------------------------------

# create sentences
corpus_dir      = "/Users/patrick/dev/ucl/comp0158_mscproject/data/corpus/20240727/corpus/files"
sentences = get_corpus_sentences(corpus_dir)

vector_size = 10

# ---------------------- window 15
window          = 15
current_date    = datetime.now().strftime('%Y%m%d')
model_dir       = "/Users/patrick/dev/ucl/comp0158_mscproject/models/"
model_name      = model_dir+"w2v_"+current_date + "_vs"+str(vector_size)+"_w"+str(window)
create_w2v(sentences, model_name, vector_size, window )

# ---------------------- window 20
window          = 20
current_date    = datetime.now().strftime('%Y%m%d')
model_dir       = "/Users/patrick/dev/ucl/comp0158_mscproject/models/"
model_name      = model_dir+"w2v_"+current_date + "_vs"+str(vector_size)+"_w"+str(window)
create_w2v(sentences, model_name, vector_size, window )

# ---------------------- window 25
window          = 25
current_date    = datetime.now().strftime('%Y%m%d')
model_dir       = "/Users/patrick/dev/ucl/comp0158_mscproject/models/"
model_name      = model_dir+"w2v_"+current_date + "_vs"+str(vector_size)+"_w"+str(window)
create_w2v(sentences, model_name, vector_size, window )




