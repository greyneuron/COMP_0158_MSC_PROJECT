# -*- coding: utf-8 -*-
from gensim.test.utils import datapath
from gensim.models.word2vec import LineSentence
import sys
import argparse
from gensim.test.utils import datapath
from gensim.models.word2vec import LineSentence
import time
from datetime import datetime
from gensim.models import Word2Vec
import pickle as pkl


#
# Parses a corpus file to load sentences into an array
# Follows the same approach as this tutorial https://rare-technologies.com/word2vec-tutorial/#app
#
def get_array_sentences(corpus_file, limit=-1):
    # initialise
    sentences = []
    counter = 0
    num_tokens = 0

    print(f"parsing sentence to array from: {corpus_file}")
    with open(corpus_file, 'r') as file:
        for line in file:
            if limit != -1 and counter >= limit:
                break
            line = line.strip('\n')
            tokens = line.split()
            
            #print(f"{counter} : {tokens}")
            
            sentences.append(tokens)
            
            #print(f"{counter} : {sentences}")
            
            counter +=1
            num_tokens += len(tokens)
    return sentences



#
# main method
#
if __name__ == '__main__':
    
    pickle_file='/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/code/hpc/word2vec_sentences.pkl'
    corpus_file='/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/code/hpc/uniref100_e_corpus_20240810.txt'
    
    #
    # create sentences and save to pickle - only need to do this once
    #

    s = time.time()
    sentences = get_array_sentences(corpus_file)
    e = time.time()
    print(f"sentences created {e-s} seconds")
    with open(pickle_file, 'wb') as f:
        pkl.dump(sentences, f)
    print(f"pickle file created")
    
    #
    # load pre-prepared sentences
    #
    '''
    print('loading array from file:', sentences_file)
    s = time.time()
    with open(sentences_file, 'rb') as f:
        sentences = pkl.load(f)
    e = time.time()
    print(f"sentence array loaded in {round(e-s, 2)} seconds.")
    '''
    
