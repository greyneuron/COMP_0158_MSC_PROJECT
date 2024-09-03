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
import numpy as np
import re
from sklearn.metrics.pairwise import cosine_distances

#
# gets the vocab for a model - returns a python list and a numpy array
#
def get_model_vocab(model_dir, model_name):
    pfam_ids = []

    model = Word2Vec.load(model_dir+model_name+'.model')
    vocab = model.wv.key_to_index
    
    print(f"Model {model_name} has a vocab of {len(vocab)}")
    for word in vocab:
        pfam_ids.append(word)
    return pfam_ids

# creates a distance matrix for a model
# this assumes a certain naming convention for models and vocab files
# For example
#   If the model name is : w2v_20240811_v5_w5_mc3, the code will expect
#   - a model called w2v_20240811_v5_w5_mc3.model
#   - a vocab file  called w2v_20240811_v5_w5_mc3.txt
#   And will output a distance matrix called:
#   - w2v_20240811_v5_w5_mc3_dist.npy
#   
def create_cosine_distance_matrix(model_base_name, model_name):
    print(f"Creating distance matrix for model {model_base_name}")
    print(f"Loading model {model_name}")
    # get pfam ids from the vocab file corresponding to the model
    model       = Word2Vec.load(model_name)
    
    #print('model_vocab:', model.wv.key_to_index)
    pfam_ids = []
    vocab = model.wv.key_to_index
    
    print(f"Model {model_base_name} has a vocab of {len(vocab)}")
    
    word_vectors    = model.wv
    print(word_vectors[0])
    
    
    for word in vocab:
        pfam_ids.append(word)
    num_entries     = len(pfam_ids)
    
    error_count = 0
    success_count = 0
    s = time.time()
    vectors = np.empty(num_entries)
    
    # loop through each entry and calulate its distance
    for i in range(num_entries):
        pfam_1 = pfam_ids[i]
        try:
            v1 = model.wv[pfam_1]
            vectors[i] = v1
            success_count +=1
        except Exception as e: # a bit convoluted, but want to print out the missing pfam
            print('Exception', e)
            continue
        
    cosine_distance_matrix = cosine_distances(vectors, vectors)
    
    #normalized_dist_matrix = (distance_matrix - min_dist) / (max_dist - min_dist)
    

    # save distance matrix and pfam ids
    #output_name = model_name+"_cosine_dist_normalised.npy"
    #with open(output_name, "wb") as f:
    #    np.save(f, cosine_distance_matrix)
    #    np.save(f, pfam_ids)

    e = time.time()
    print(f"cosine distance matrix computed for model: {model_base_name}. num words: {num_entries}. time: {round(e-s,2)}s. success: {success_count} fail: {error_count} output: {output_name}")
    
    return cosine_distance_matrix


#
# main method
#
if __name__ == '__main__':
    
    
    print('\n')
    print('---------------------------------------------------')
    print('       ** Word2Vec Cosine Distance Batch **          ')
    print('---------------------------------------------------')
    
    output_dir = '/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/data/models/hpc/mac/'
    model_base_name = 'w2v_20240831_sg1_mc1_w3_v5_mac.model'
    model_name      = output_dir+model_base_name
    
    print(f"loading model {model_name}.")
        

        
    #
    #--------------------------- create dist -----------------------
    #
    print("creating distance matrix")
    cosine_dist = create_cosine_distance_matrix(model_base_name, model_name)
    
    e2 = time.time()
    matrix_time_taken=str(round(e2-e, 2))
    
    #print(f"w2v_model_create_{current_date} | {model_type} | {min_count} | {window_size} | {vector_size} | {time_taken} | {matrix_time_taken}")
    #lf.write(f"w2v_model_create_{current_date} | {model_type} | {min_count} | {window_size} | {vector_size} | {time_taken} | {matrix_time_taken}\n")
        
    
