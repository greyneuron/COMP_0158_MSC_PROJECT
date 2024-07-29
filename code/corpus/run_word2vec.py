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
# Locally (2020 Macbook) it took 6s to parse 10 corpus files (ie 10M proteins)
# and a further 61s to create the model
#
def create_w2v(corpus_dir, model_name, vector_size, window_size):
    FILE_LIMIT = 10
    
    current_date = datetime.now().strftime('%Y%m%d')
    model_name      = model_name + ".model"
    
    # find the files in the target directory
    print('Searching for corpi files in:', corpus_dir)
    file_list = glob.glob(os.path.join(corpus_dir, '*corpus_00M_*.txt'))
    
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
    
    # create model from sentences
    print(f"Creating model {model_name}.....")           
    w2v = Word2Vec(sentences, vector_size=vector_size, window=window_size, workers=4, epochs=10, min_count=5)
    
    # time check
    e2 = time.time()
    print(f"Model creation time {e2 - e}")
          
    # save model      
    w2v.save(model_name)
    print(f"Model saved to {model_name}")


corpus_dir      = "/Users/patrick/dev/ucl/comp0158_mscproject/code/corpus/corpus"
vector_size     = 10
window          = 5
current_date    = datetime.now().strftime('%Y%m%d')
model_dir       = "/Users/patrick/dev/ucl/comp0158_mscproject/code/corpus/model/"
model_name      = model_dir+"w2v_"+current_date + "_vs"+str(vector_size)+"_w"+str(window)+"_00M_2"
print(model_name)


create_w2v(corpus_dir, model_name, vector_size, window )




