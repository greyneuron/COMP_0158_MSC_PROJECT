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
from sklearn.metrics.pairwise import euclidean_distances
from scipy.spatial.distance import cosine

#
# creates cosine and euclidean distance matrices for the vocab in a model
# normalises them and outputs the raw, normalised and word vectors to a npy file
#
def create_distance_matrices(output_dir, model_file):
    # get model name from file
    name_search = re.search("(w2v.*)\.model", model_file)
    model_name = name_search.group(1)
    
    print(f"Loading model {model_name}.model")
    
    model       = Word2Vec.load(model_file)
    word_vectors    = model.wv
    
    # grab the vocab vector
    vocab           = model.wv.key_to_index
    vocab_vector    = []
    for i, word in enumerate(vocab):
        vocab_vector.append(word)

    print('word vectors shape:', word_vectors.vectors.shape)

    s = time.time()
    print('calculating cosine distances')
    cosine_distance_matrix = cosine_distances(word_vectors.vectors, word_vectors.vectors)

    # normalise
    non_diag_elements   = cosine_distance_matrix[np.triu_indices_from(cosine_distance_matrix, k=1)]
    max_value           = np.max(np.abs(non_diag_elements))
    print(f"normalising with max value: {max_value}")
    cosine_distance_matrix_norm = cosine_distance_matrix / max_value
    np.fill_diagonal(cosine_distance_matrix_norm, 0)
    
    
    print('calculating euclidean distances')
    euclidean_distance_matrix = euclidean_distances(word_vectors.vectors, word_vectors.vectors)
    # normalise
    non_diag_elements   = euclidean_distance_matrix[np.triu_indices_from(euclidean_distance_matrix, k=1)]
    max_value           = np.max(np.abs(non_diag_elements))
    print(f"normalising with max value: {max_value}")
    euclidean_distance_matrix_norm = euclidean_distance_matrix / max_value
    np.fill_diagonal(euclidean_distance_matrix_norm, 0)
    
    e = time.time()
    print(f"distance matrices computed for model: {model_name}. vocab size: {len(vocab)} euclidean shape: {euclidean_distance_matrix_norm.shape} cosine shape: {cosine_distance_matrix_norm.shape} time: {round(e-s,2)}s.")
    
    
    # normalized_dist_matrix = (distance_matrix - min_dist) / (max_dist - min_dist)
    
    # save distance matrix and pfam ids
    s = time.time()
    cos_output_name = output_dir+model_name+"_cos_dist.npy"
    with open(cos_output_name, "wb") as f:
        np.save(f, cosine_distance_matrix)
        np.save(f, cosine_distance_matrix_norm)
        np.save(f, vocab_vector)
    
    # save distance matrix and pfam ids
    euc_output_name = output_dir+model_name+"_euc_dist.npy"
    with open(euc_output_name, "wb") as f:
        np.save(f, euclidean_distance_matrix)
        np.save(f, euclidean_distance_matrix_norm)
        np.save(f, vocab_vector)

    e = time.time()
    print(f"distance matrices (normalised and raw) saved for model: {model_name}. time: {round(e-s,2)}s.")
    
    return vocab_vector, euclidean_distance_matrix, euclidean_distance_matrix_norm, cosine_distance_matrix, cosine_distance_matrix_norm

#
# test a matrix to see if its symmetric
#
def test_symmetric(matrix):
    print('testing matrix for symmmetry, shape is:', matrix.shape)
    print('testing matrix for symmmetry, max is:', matrix.max())
    assert np.array_equal(matrix, matrix.T), "matrix not symmetric"



#
# Test files load ok and are symmetric
#
def test_load_matrices(output_dir, model_file):
    # get model name from file
    name_search = re.search("(w2v.*)\.model", model_file)
    model_name = name_search.group(1)
    
    saved_cos_file  = output_dir+model_name+"_cos_dist.npy"
    saved_euc_file  = output_dir+model_name+"_euc_dist.npy"
    model           = Word2Vec.load(model_file)
    
    # load npy file
    print(f"loading {saved_cos_file}")
    npy_cosf                = open(saved_cos_file, 'rb')
    cos_dist_matrix         = np.load(npy_cosf) #loads first matrix
    cos_dist_matrix_norm    = np.load(npy_cosf) #loads second matrix
    
    print(f"loading {saved_euc_file}")
    npy_eucf                = open(saved_euc_file, 'rb')
    euc_dist_matrix         = np.load(npy_eucf) #loads first matrix
    euc_dist_matrix_norm    = np.load(npy_eucf) #loads second matrix

    test_symmetric(euc_dist_matrix)
    test_symmetric(euc_dist_matrix_norm)
    test_symmetric(cos_dist_matrix)
    test_symmetric(cos_dist_matrix_norm)


#
# Optional method to test that the matrices are actually correct
#
def test_matrix_distances(output_dir, model_file, debug=False):
    # get model name from file
    name_search = re.search("(w2v.*)\.model", model_file)
    model_name = name_search.group(1)
    
    saved_cos_file  = output_dir+model_name+"_cos_dist.npy"
    saved_euc_file  = output_dir+model_name+"_euc_dist.npy"
    model           = Word2Vec.load(model_file)
    
    # load npy file
    print(f"loading {saved_cos_file}")
    npy_cosf                = open(saved_cos_file, 'rb')
    cos_dist_matrix         = np.load(npy_cosf) #loads first matrix
    cos_dist_matrix_norm    = np.load(npy_cosf) #loads second matrix
    cos_vocab   = np.load(npy_cosf)
    
    # load npy file
    print(f"loading {saved_euc_file}")
    npy_eucf        = open(saved_euc_file, 'rb')
    euc_dist_matrix         = np.load(npy_eucf) #loads first matrix
    euc_dist_matrix_norm    = np.load(npy_eucf) #loads second matrix
    euc_vocab       = np.load(npy_eucf)
    
    ignore_words = ['GAP','DISORDER','START_GAP','STOP_GAP']
    
    for i, word_1 in enumerate(cos_vocab):
        for j, word_2 in enumerate(cos_vocab):
            if(word_1 in ignore_words):
                continue
            if(word_1 in ignore_words):
                continue
            if(word_1 == word_2):
                continue
            
        # get vectors
        v1 = model.wv[word_1]
        v2 = model.wv[word_2]

        # get euc dist - cacluate from library and also retrive from matrix
        euc_dist    = np.linalg.norm(v1 - v2)
        euc_dist_1  = euc_dist_matrix[i,j]
        euc_dist_2  = euc_dist_matrix[j,i]
        
        # get cos dist - cacluate from library and also retrive from matrix
        cos_dist    = cosine(v1, v2)
        
        # get from matrix
        cos_dist_1       = cos_dist_matrix[i,j]
        cos_dist_2       = cos_dist_matrix[j,i]
        
        if(debug):
            print(f"EUC: {word_1} to {word_2} : \t| {euc_dist} \t| {euc_dist_1}  \t| {euc_dist_2}")
            print(f"COS: {word_1} to {word_2} : \t| {cos_dist} \t| {cos_dist_1}  \t| {cos_dist_2}")
        
        # check  - but need to round first
        euc_dist_rnd    = int(euc_dist * 100)
        euc_dist_1_rnd  = int(euc_dist_1 * 100)
        euc_dist_2_rnd  = int(euc_dist_1 * 100)
        
        # get cos dist - cacluate from library and also retrive from matrix
        cos_dist_rnd    = int(cos_dist * 100)
        
        # get from matrix
        cos_dist_1_rnd       = int(cos_dist_1 * 100)
        cos_dist_2_rnd       = int(cos_dist_2 * 100)

        assert euc_dist_rnd  == euc_dist_1_rnd, f"Euclidean distance not the same - {word_1} to {word_2} : {i},{j} : {euc_dist_rnd} v {euc_dist_1_rnd}"
        assert euc_dist_rnd  == euc_dist_2_rnd, f"Euclidean distance not the same - {word_1} to {word_2} : {i},{j} : {euc_dist_rnd} v {euc_dist_2_rnd}"
        assert cos_dist_rnd  == cos_dist_1_rnd, f"Cos distance not the same - {word_1} to {word_2} : {i},{j} : {cos_dist_rnd} v {cos_dist_1_rnd}."
        assert cos_dist_rnd  == cos_dist_2_rnd, f"Cos distance not the same - {word_1} to {word_2} : {i},{j} : {cos_dist_rnd} v {cos_dist_2_rnd}"
    return

#
# main method
#
if __name__ == '__main__':
    
    print('\n')
    print('---------------------------------------------------')
    print('       ** Word2Vec Distance Batch **          ')
    print('---------------------------------------------------')
    
    parser = argparse.ArgumentParser(prog='Word2Vec Distance Creation', description='Establishes correlation between two distances matrices')
    
    parser.add_argument("--model_file", help="full path to model", required=False)
    parser.add_argument("--output_dir", help="output directory for distance matrices", required=False)
    
    args            = parser.parse_args()
    model_file      = args.model_file
    output_dir      = args.output_dir

    #
    #--------------------------- create dist -----------------------
    #
    print(f"creating distance matrices for model {model_file}")
    
    s = time.time()
    vocab_vector, euclidean_distance_matrix, euclidean_distance_matrix_norm, cosine_distance_matrix, cosine_distance_matrix_norm = create_distance_matrices(output_dir, model_file)
    e = time.time()
    print(f"-------- > distance matrices created for {model_file}. time taken: {round(e-s,2)}")
    
    # testing used during dev
    #test_matrix_distances(output_dir, model_file, debug=False)
    #test_load_matrices(output_dir, model_file)
        
    
