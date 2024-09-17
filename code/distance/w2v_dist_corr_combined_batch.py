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

from scipy.spatial.distance import correlation
from skbio.stats.distance import mantel

from scipy.stats import pearsonr
from scipy.stats import spearmanr

#
# Gets pairwise distance matrices for a model using both euclidean and cosine distances
# 
#
def get_distances(model_path):
    model           = Word2Vec.load(model_path)
    word_vectors    = model.wv
    
    print('- w2v word vectors shape:', word_vectors.vectors.shape)
    
    # grab the pfam words
    pfams = []
    vocab           = model.wv.key_to_index
    for i, word in enumerate(vocab):
        pfams.append(word)

    # get cosine and normalise
    print('- calculating cosine distances')
    cosine_distance_matrix = cosine_distances(word_vectors.vectors, word_vectors.vectors)
    non_diag_elements       = cosine_distance_matrix[np.triu_indices_from(cosine_distance_matrix, k=1)]
    max_value               = np.max(np.abs(non_diag_elements))
    cosine_distance_matrix_norm = cosine_distance_matrix / max_value
    np.fill_diagonal(cosine_distance_matrix_norm, 0)
    
    # get euclidean and normalise
    print('- calculating euclidean distances')
    euclidean_distance_matrix   = euclidean_distances(word_vectors.vectors, word_vectors.vectors)
    non_diag_elements           = euclidean_distance_matrix[np.triu_indices_from(euclidean_distance_matrix, k=1)]
    max_value                   = np.max(np.abs(non_diag_elements))
    euclidean_distance_matrix_norm = euclidean_distance_matrix / max_value
    np.fill_diagonal(euclidean_distance_matrix_norm, 0)
    
    return pfams, euclidean_distance_matrix, cosine_distance_matrix, euclidean_distance_matrix_norm, cosine_distance_matrix_norm



# ------------------- EVOLUTIONARY MATRIX -------------------------------------

#
# extract vocab vector and matrix from npy file
#                
def extract_evo_matrix_vector_files(npy_file_name):
    print(f"- loading {npy_file_name}")
    npy_f               = open(npy_file_name, 'rb')
    dist_matrix_norm    = np.load(npy_f) #loads second matrix
    vocab_vector        = np.load(npy_f)
    
    return vocab_vector, dist_matrix_norm

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

# -------------------------------------------------------------------



def find_files(directory):
    files_info = []
    # Traverse the directory recursively
    for file_path in Path(directory).rglob(f'*model'):
        if file_path.is_file():  # Check if it's a file
            filename = file_path.stem  # Get the filename without extension
            file_extension = file_path.suffix  # Get the file extension
            files_info.append((str(file_path), filename, file_extension))
    
    return files_info




#
# main method
#
if __name__ == '__main__':
    
    print('\n')
    print('---------------------------------------------------------------------------')
    print(' **              Word2Vec Distance & Correlation Batch                   **') 
    print('      takes a model, calculates its distance and compares it to randrep    ')
    print('---------------------------------------------------------------------------')


    from pathlib import Path
    
    # ------------------------ setup
    #
    
    evo_npy         = "/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/data/distances/evo/rand_rep_distance_matrix.npy"
    output_dir      = "/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/logs/"
    
    current_date    = datetime.now().strftime('%Y%m%d_%H%M')
    log_file        = output_dir+current_date+"_dist_matrix_comparison_pearsonr.txt"
    lf              = open(log_file, "a")
    
    print(f"Log file : {log_file}")
    
    # --------------------- get rand_rep matrix and vocab
    #
    evo_vocab_vector, evo_dist_matrix = extract_evo_matrix_vector_files(evo_npy)
    evo_vocab                         = extract_evo_pfam_ids(evo_vocab_vector)
    print(f"- rand_rep extracted. number of pfams : {len(evo_vocab)} matrix shape: {evo_dist_matrix.shape}\n")
    

    # --------------------- get models
    #
    #model_dir       = "/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/data/models/cbow/"
    #model_names     = ['w2v_20240911_cbow_mc1_w3_v5', 'w2v_20240911_cbow_mc1_w3_v10', 'w2v_20240911_cbow_mc1_w3_v25', 'w2v_20240911_cbow_mc1_w3_v50']
    #model_names     = ['w2v_20240911_cbow_mc1_w3_v10', 'w2v_20240911_cbow_mc1_w3_v25']
    
    model_dir       = "/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/data/models/"
    models_info     = find_files(model_dir)
    
    s = time.time()
    for model_info in models_info:
        #print(f"Model Path: {model_info[0]}, \tModel name: {model_info[1]}, Extension: {model_info[2]}")

        # get details from model name
        #model_path = model_dir+model_name+'.model'
        model_path = model_info[0]
        model_name = model_info[1]
        
        min_count_s = re.search("(mc[0-9]+)_", model_name)
        vector_s    = re.search("v([0-9]+)", model_name)
        vector_size = vector_s.group(1)
    
        #
        #--------------------------- create distance matrices -----------------------
        #
        print(f"Creating distance matrices for model {model_name} located at {model_path}")
        
        s2 = time.time()
        w2v_vocab, w2v_euc_dist_matrix, w2v_cos_dist_matrix, w2v_euc_dist_matrix_n, w2v_cos_dist_matrix_n = get_distances(model_path)
        e2 = time.time()
        print(f"- distance matrices created for {model_name}. time taken: {round(e2-s2,2)}")
        
        # make sure to use normalised!
        w2v_matrices = {'euc': w2v_euc_dist_matrix_n, 'cos' :w2v_cos_dist_matrix_n}
        
        # loop through each type of distance matrix
        for dist_type, w2v_distance_matrix in w2v_matrices.items():
            s1 = time.time()
            print(f"\n** {model_name} - {dist_type} correlation...")
            print(' - converting to Distance Matrix ahead of correlation and distance calculations...')
            w2v_dist_matrix_fl   = w2v_distance_matrix.astype(np.float64)

            w2v_vocab_np         = np.array(w2v_vocab)
            evo_vocab_np         = np.array(evo_vocab)
                        
            # Convert existing matrices to DistanceMatrix
            w2v_dist_matrix_new = DistanceMatrix(w2v_dist_matrix_fl, ids=w2v_vocab_np)
            evo_dist_matrix_new = DistanceMatrix(evo_dist_matrix, ids=evo_vocab_np)
            
            
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
            # --------------------------- reduce to same sizes based upon shared vocab -----------------------
            # ------- Note that this has been tested extensively in distance_helper.ipynb
            #

            print(f" - current matrix shapes. \t w2v: {w2v_distance_matrix_fl.shape} evo : {evo_dist_matrix.shape}")
            try:
                # create a new evo matrix to only have the pfams that it shares with the w2v matric
                new_evo         = evo_dist_matrix_new.filter(w2v_vocab_np, False)
                new_evo_ids     = new_evo.ids
                # create a new w2v matrix to only have the pfams that it shares with the new evo one!
                new_w2v         = w2v_dist_matrix_new.filter(new_evo_ids, False)
                new_w2v_ids     = new_w2v.ids
            except Exception as e:
                print('Error', e)
            print(f" - New matrix shapes. \t w2v: {new_w2v.shape} evo : {new_evo.shape}")

            #
            #--------------------------- can now do some corelation! -----------------------
            #
            
            
            # extract in condesed form - basically a 1D array buit only of upper triangle of matrix and exclude diagonals
            print(f" - running scipy correlation on {model_name} - {dist_type} distance.")
            new_w2v_condensed = new_w2v.condensed_form()
            new_evo_condensed = new_evo.condensed_form()
            
            '''
            #print(len(new_w2v_condensed), len(new_evo_condensed))
            my_correlation = correlation(new_w2v_condensed, new_evo_condensed)
            print(' - scipy correlation:', my_correlation)

            print(f" - running mantel test on {model_name} - {dist_type} distance.")
            n=50
            corr_coeff, p_value, num = mantel(new_w2v, new_evo, permutations=n, strict=False)
            print(f" - mantel test corr : {round(corr_coeff,4)} p_val : {round(p_value,4)} num: {num}.\n")
            
            e1 = time.time()
            
            print(f"Correlation tests on {model_name} dist type {dist_type}. corr-coeff: {round(my_correlation,4)} mantel corr : {round(corr_coeff,4)} mantel p_val : {round(p_value,4)}. time : {round(e1 - s1, 2)}s\n")
            lf.write(f"{current_date} | {model_name} \t| {dist_type} \t| {round(my_correlation, 4)} \t|  {round(corr_coeff,4)} | {round(p_value,4)} | {round(e1 - s1, 2)}s \n")
            lf.flush()
            '''
            
            # ---- pearsonr
            print(f" - running pearsonr test on {model_name} - {dist_type} distance.")
            pearson_result = pearsonr(new_w2v_condensed, new_evo_condensed)
            e1 = time.time()
            
            print(f"Pearsonr test on {model_name} dist type {dist_type}. pearsonr stat: {round(pearson_result.statistic, 4)} pval: {round(pearson_result.pvalue, 4)}  time : {round(e1 - s1, 2)}s\n")
            lf.write(f"{current_date} | {model_name} \t| {dist_type} \t| pearsonr | {round(pearson_result.statistic,4)} | {round(pearson_result.pvalue, 4)} | {round(e1 - s1, 2)}s \n")
            
            # ---- spearmanr
            print(f" - running spearmanr test on {model_name} - {dist_type} distance.")
            spearmanr_result = spearmanr(new_w2v_condensed, new_evo_condensed)
            e2 = time.time()
            
            print(f"Spearmanr test on {model_name} dist type {dist_type}. spearmanr stat: {round(spearmanr_result.statistic, 4)} pval: {round(spearmanr_result.pvalue, 4)}  time : {round(e1 - s1, 2)}s\n")
            lf.write(f"{current_date} | {model_name} \t| {dist_type} \t| spearmanr | {round(spearmanr_result.statistic,4)} | {round(spearmanr_result.pvalue, 4)} | {round(e2 - e1, 2)}s \n")
            
            
            lf.flush()
                      
    e = time.time()
    print(f"{current_date} distance comparisons complete in time:  {round(e - s, 2)}")
    lf.close()
    
    
