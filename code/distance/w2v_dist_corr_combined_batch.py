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
from skbio.stats.distance import mantel
from skbio.stats.distance import DistanceMatrix
from scipy.stats import pearsonr

#
# creates cosine and euclidean distance matrices for the vocab in a model
# normalises them and outputs the raw, normalised and word vectors to a npy file
#
def create_distance_matrices(output_dir, model_file):
    # get model name from file
    name_search = re.search("(w2v.*)\.model", model_file)
    model_name = name_search.group(1)
    
    print(f"- loading model {model_name}.model")
    
    model       = Word2Vec.load(model_file)
    word_vectors    = model.wv
    
    # grab the vocab vector
    vocab           = model.wv.key_to_index
    vocab_vector    = []
    for i, word in enumerate(vocab):
        vocab_vector.append(word)

    print('- w2v word vectors shape:', word_vectors.vectors.shape)

    s = time.time()
    print('- calculating cosine distances')
    cosine_distance_matrix = cosine_distances(word_vectors.vectors, word_vectors.vectors)

    # normalise
    non_diag_elements   = cosine_distance_matrix[np.triu_indices_from(cosine_distance_matrix, k=1)]
    max_value           = np.max(np.abs(non_diag_elements))
    #print(f"normalising with max value: {max_value}")
    cosine_distance_matrix_norm = cosine_distance_matrix / max_value
    np.fill_diagonal(cosine_distance_matrix_norm, 0)
    
    
    print('- calculating euclidean distances')
    euclidean_distance_matrix = euclidean_distances(word_vectors.vectors, word_vectors.vectors)
    # normalise
    non_diag_elements   = euclidean_distance_matrix[np.triu_indices_from(euclidean_distance_matrix, k=1)]
    max_value           = np.max(np.abs(non_diag_elements))
    #print(f"normalising with max value: {max_value}")
    euclidean_distance_matrix_norm = euclidean_distance_matrix / max_value
    np.fill_diagonal(euclidean_distance_matrix_norm, 0)
    
    e = time.time()
    print(f"- distance matrices computed for model: {model_name}. vocab size: {len(vocab)} euclidean shape: {euclidean_distance_matrix_norm.shape} cosine shape: {cosine_distance_matrix_norm.shape} time: {round(e-s,2)}s.")
    
    # normalized_dist_matrix = (distance_matrix - min_dist) / (max_dist - min_dist)

    return vocab_vector, euclidean_distance_matrix_norm, cosine_distance_matrix_norm



#
# extract vocab vector and matrix from npy file
#                
def extract_evo_matrix_vector_files(npy_file_name):
    print(f"- loading {npy_file_name}")
    npy_f               = open(npy_file_name, 'rb')
    dist_matrix_norm    = np.load(npy_f) #loads second matrix
    vocab_vector        = np.load(npy_f)
    
    return vocab_vector, dist_matrix_norm


# ------------------- GET PFAM IDS FROM EVO VECTOR ----------------------------

#
# vectors in evo matrix have format K1SVA3.1/50-86|PF02829
# need to extract these
#
def extract_evo_pfam_ids(evo_vector):
    pfam_ids = []
    for item in evo_vector:
        #print(f"searching in {item}")
        pfam_search  = re.search("\|(PF.*)", item)
        pfam_id       = pfam_search.group(1)
        #print(f"found {pfam_id}")
        pfam_ids.append(pfam_id)
    return pfam_ids


#
# main method
#
if __name__ == '__main__':
    
    print('\n')
    print('---------------------------------------------------------------------------')
    print(' **              Word2Vec Distance & Correlation Batch                   **') 
    print('      takes a model, calculates its distance and compares it to randrep    ')
    print('---------------------------------------------------------------------------')
    
    s1 = time.time()
    
    '''
    parser = argparse.ArgumentParser(prog='Word2Vec Distance Creation', description='Establishes correlation between two distances matrices')
    
    parser.add_argument("--model_file", help="full path to model", required=False)
    parser.add_argument("--output_dir", help="output directory for distance matrices", required=False)
    
    args            = parser.parse_args()
    model_file      = args.model_file
    output_dir      = args.output_dir
    '''
    
    model_dir       = "/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/data/models/cbow/"
    #model_names     = ['w2v_20240911_cbow_mc1_w3_v5', 'w2v_20240911_cbow_mc1_w3_v10', 'w2v_20240911_cbow_mc1_w3_v25', 'w2v_20240911_cbow_mc1_w3_v50']
    model_names     = ['w2v_20240911_cbow_mc1_w3_v10', 'w2v_20240911_cbow_mc1_w3_v25']
    
    evo_npy         = "/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/data/distances/evo/rand_rep_distance_matrix.npy"
    output_dir      = "/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/logs/"
    
    current_date    = datetime.now().strftime('%Y%m%d_%H%m')
    log_file        = output_dir+current_date+"_dist_matrix_comparison.csv"
    lf              = open(log_file, "a")
    
    # get rand_rep matrix and vocab
    evo_vocab_vector, evo_dist_matrix = extract_evo_matrix_vector_files(evo_npy)
    evo_vocab   = extract_evo_pfam_ids(evo_vocab_vector)
    print(f"- rand_rep extracted. number of pfams : {len(evo_vocab)} matrix shape: {evo_dist_matrix.shape}")
    
    # loop through models
    for model_name in model_names:
        
        # get details from model name
        model_path = model_dir+model_name+'.model'
        
        min_count_s = re.search("(mc[0-9]+)_", model_name)
        vector_s = re.search("v([0-9]+)", model_name)
        vector_size = vector_s.group(1)
    
        #
        #--------------------------- create distance matrices -----------------------
        #
        print(f"- creating distance matrices for model {model_path}")
        
        s = time.time()
        w2v_vocab, w2v_distance_matrix_euc, w2v_distance_matrix_cos = create_distance_matrices(output_dir, model_path)
        e = time.time()
        print(f"- distance matrices created for {model_path}. time taken: {round(e-s,2)}")
        
        w2v_matrices = {'euc': w2v_distance_matrix_euc, 'cos' :w2v_distance_matrix_cos}
        for dist_type, w2v_distance_matrix in w2v_matrices.items():
        
            #
            #--------------------------- create distance matrices -----------------------
            #
            # need to convert w2v matrices to float - mantel fails if they are doubles!
            w2v_distance_matrix_fl = w2v_distance_matrix.astype(np.float64)
            # also need to convert lists back into numpy
            w2v_vocab_np = np.array(w2v_vocab)
            evo_vocab_np = np.array(evo_vocab)
            
            # now create DistanceMatrices - this allows us to use the distance measures in skbio.stats.distance
            w2v_dist_matrix = DistanceMatrix(w2v_distance_matrix_fl, ids=w2v_vocab_np)
            evo_dist_matrix = DistanceMatrix(evo_dist_matrix, ids=evo_vocab_np)
            
            
            #
            #--------------------------- run mantel -----------------------
            #
            print(f"- running mantel test on {model_name} - {dist_type} distance.")
            num_permutations = [50]
            for n in num_permutations:
                s= time.time()
                corr_coeff, p_value, num = mantel(w2v_dist_matrix, evo_dist_matrix, permutations=n, strict=False)
                e = time.time()
                print(f"- mantel test on {model_name} dist type {dist_type} and {n} permutations complete in {round(e-s,2)}s. ** results corr : {round(corr_coeff,4)} p_val : {round(p_value,4)} num: {num}.\n")
                lf.write(f"{current_date} | mantel | {model_name} \t| {dist_type} \t| {round(e - s, 2)}s | {n} | {round(corr_coeff,4)} | {round(p_value,4)} | {num}\n")
    e1 = time.time()
    print(f"{current_date} distance comparisons complete for {model_name} time:  {round(e1 - s1, 2)}")
    lf.close()
    
    
