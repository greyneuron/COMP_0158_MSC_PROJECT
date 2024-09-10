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

#
# create a model with given config
#
def create_w2v_model(sentences, model_type, vector_size, window_size, min_count):
    w2v = Word2Vec(sentences, sg=model_type, vector_size=vector_size, window=window_size, workers=4, epochs=10, min_count=min_count)
    return w2v


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
            
            print(f"{counter} : {tokens}")
            
            sentences.append(tokens)
            
            #print(f"{counter} : {sentences}")
            
            counter +=1
            num_tokens += len(tokens)
    return sentences

#
# Use gensim to read sentences from a file - not used
#
'''
def get_line_sentences(corpus_file):
    print(f"creating sentences using Line Sentence from: {corpus_file}")
    sentences = LineSentence(datapath(corpus_file))
    print(sentences)
    return sentences
'''

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
def create_distance_matrix(model_base_name, model_name):
    print(f"Creating distance matrix for model {model_base_name}.")
    # get pfam ids from the vocab file corresponding to the model
    model       = Word2Vec.load(model_name)
    
    #print('model_vocab:', model.wv.key_to_index)
    pfam_ids = []
    vocab = model.wv.key_to_index
    
    print(f"Model {model_base_name} has a vocab of {len(vocab)}")
    for word in vocab:
        pfam_ids.append(word)

    # calculate matrix size and initialise
    num_entries     = len(pfam_ids)
    distance_matrix = np.zeros((num_entries, num_entries))
    
    error_count = 0
    success_count = 0
    s = time.time()
    
    # loop through each entry and calulate its distance
    for i in range(num_entries):
        for j in range(i+1, num_entries):
            pfam_1 = pfam_ids[i]
            pfam_2 = pfam_ids[j]
            try:
                v1 = model.wv[pfam_1]
                v2 = model.wv[pfam_2]
                
                # distance calc
                
                distance = np.linalg.norm(v1 - v2)
                #print(f"distance {pfam_1} to {pfam_2} : {distance}")
                
                distance_matrix[i][j] = distance
                success_count +=1
            except Exception as e: # a bit convoluted, but want to print out the missing pfam
                missing = re.search("Key '(.*)' not", e.args[0] )
                print(missing.group(1))
                error_count +=1
                continue
    
    # normalise and flip - same way as db did so comparison is on equal basis
    max_dist = np.max(distance_matrix)
    min_dist = np.min(distance_matrix)
    print(f"min dist: {min_dist}. max dist: {max_dist}")
    
    #np.fill_diagonal(distance_matrix, (np.max(distance_matrix)*1.2))
    
    normalized_dist_matrix = (distance_matrix - min_dist) / (max_dist - min_dist)
    
    #flipped_norm_dist_matrix = 1.0 - normalized_dist_matrix
    
    # save distance matrix and pfam ids
    output_name = model_name+"_dist_normalised.npy"
    with open(output_name, "wb") as f:
        np.save(f, normalized_dist_matrix)
        np.save(f, pfam_ids)

    e = time.time()
    print(f"distance matrix computed for model: {model_base_name}. num words: {num_entries}. time: {round(e-s,2)}s. success: {success_count} fail: {error_count} output: {output_name}")
    
    return


#
# main method
#
if __name__ == '__main__':
    
    current_date    = datetime.now().strftime('%Y%m%d')
    CBOW            = 0
    SKIP_GRAM       = 1
    
    
    print('\n')
    print('---------------------------------------------------')
    print('       ** Word2Vec Model Batch **          ')
    print('---------------------------------------------------')
    
    parser = argparse.ArgumentParser(prog='Word2Vec Model Task Manager', description='Orchestrates the creation of word2vec models')
    
    parser.add_argument("--corpus_file", help="full path to corpus (pickle file from python array)", required=False)
    parser.add_argument("--output_dir", help="output directory for models", required=False)
    parser.add_argument("--model_type", choices=['cbow', 'skip'], help="output directory for models", required=False)
    parser.add_argument("--mc", help="min word count (integer)", required=True)
    parser.add_argument("--ws", help="window size (integer)", required=True)
    #parser.add_argument("--vs", help="vector size (integer)", required=True)
    
    
    # extract arguments
    args            = parser.parse_args()
    sentences_file  = args.corpus_file
    output_dir      = args.output_dir
    model_type      = args.model_type
    window_size     = int(args.ws)
    min_count       = int(args.mc)
    #vector_size     = args.vs
    
    pickle_file     = sentences_file
    
    # sort out model type
    if 'bag' == model_type:
        model_type = CBOW
    elif 'skip' == model_type:
        model_type = SKIP_GRAM
    
    
    #print(f"Running word2vec with model_type: {model_type} window_size: {window_size} min_count: {min_count} output_dir: {output_dir}, sentences: {sentences_file}.")
    
    log_file = output_dir+'/'+current_date+"_model_log.txt"
    lf = open(log_file, "w")
    
    #
    # -------------------------- load sentences -----------------------
    #
    
    print('loading sentences from pickle file:', sentences_file)
    s = time.time()
    with open(sentences_file, 'rb') as f:
        sentences = pkl.load(f)
    e = time.time()
    print(f"sentences loaded in {round(e-s, 2)} seconds.")
    
    
    # -----------------------------------------------------------------
    #
    # Change these params for each batch
    #
    # -----------------------------------------------------------------
    #vector_sizes    = [75, 100]
    vector_sizes    = [250, 500, 750, 1000]

    
    #
    # create and save model
    #
    for vector_size in vector_sizes:
        
        model_base_name = "w2v_"+current_date + "_sg"+str(model_type) + "_mc"+str(min_count) +"_w"+str(window_size) + "_v"+str(vector_size)+".model"
        model_name      = output_dir+"w2v_"+current_date + "_sg"+str(model_type) + "_mc"+str(min_count) +"_w"+str(window_size) + "_v"+str(vector_size)+".model"
        print(f"creating model {model_name}.")
        
        s = time.time()
        #
        #--------------------------- create model -----------------------
        # create model here
        
        w2v_model   = create_w2v_model(sentences, int(model_type), vector_size, window_size, min_count)
        w2v_model.save(model_name)
        
        e = time.time()
        time_taken=str(round(e-s, 2))
        
        print(f"w2v_model_create_{current_date} | {model_type} | {min_count} | {window_size} | {vector_size} | {time_taken}")
        
        #
        #--------------------------- create dist -----------------------
        #
        '''
        print("creating distance matrix")
        create_distance_matrix(model_base_name, model_name)
        
        e2 = time.time()
        matrix_time_taken=str(round(e2-e, 2))
        
        print(f"w2v_model_create_{current_date} | {model_type} | {min_count} | {window_size} | {vector_size} | {time_taken} | {matrix_time_taken}")
        lf.write(f"w2v_model_create_{current_date} | {model_type} | {min_count} | {window_size} | {vector_size} | {time_taken} | {matrix_time_taken}\n")
        '''
    
