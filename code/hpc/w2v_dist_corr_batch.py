# -*- coding: utf-8 -*-
import re
import time
from datetime import datetime
import os
import numpy as np
import argparse
from skbio.stats.distance import mantel
from skbio.stats.distance import DistanceMatrix
from scipy.stats import pearsonr
#
# determines closeness of fit between distance matrices
#
# much of this code ws first developed in run_word2vec.ipynb and pasted in here for further refinement
#

# ------------------- MAKE SYMMETRICAL  ----------------------------
#
# make a matrix symmetrical - my word2vec matrices are not
#
'''
def make_symmetrical(matrix):
    matrix_sym = matrix + matrix.T - np.diag(matrix.diagonal())
    return matrix_sym
''' 


# ------------------- GET MATRICES AND VECTORS FROM NPY FILE ----------------------------


#
# extract vocab vector and matrix from npy file
#                
def extract_matrix_vector_files(npy_file_name):
    print(f"loading {npy_file_name}")
    npy_f               = open(npy_file_name, 'rb')
    dist_matrix         = np.load(npy_f) #loads first matrix
    dist_matrix_norm    = np.load(npy_f) #loads second matrix
    vocab_vector        = np.load(npy_f)
    
    return vocab_vector, dist_matrix, dist_matrix_norm



#
# extract vocab vector and matrix from npy file
#                
def extract_evo_matrix_vector_files(npy_file_name):
    print(f"loading {npy_file_name}")
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

    

# ------------- REDUCE A MATRIX BASED UPON COMMON ENTRIES IN A VECTOR ----------

# Reduces the target matrix to only have entries that are common to 
# 2 vectors list the entries in 2 matrices. This routine identified the 
# common elements between these vectors and removes them from the target matrix
# It also reorders the target matrix so that the entries are in the same order

# source_vector : list of items in the source matrix
# target_vector : list of items in the target matrix
# target_matrix : the matrix to be reduced and reordered

def reduce_matrix(source_vector, target_vector, target_matrix):

    reorder_indices = []
    missing_items   = []
    found_items     = []
    # get index of each source vector in the target vector and add that index to a list
    # thus this list is now in the same order as the source vector
    for item in source_vector:
        if (item == 'GAP' or item == 'START_GAP' or item == 'STOP_GAP' or item == 'DISORDER'):
            continue
        else:
            try:
                find_index = np.where(target_vector == item)[0]
                if len(find_index) > 0 :
                    reorder_indices.append(find_index[0])
                    found_items.append(item)
                    #print('found item at', find_index[0])
                else:
                    #print(item, 'not found in target vector')
                    missing_items.append(item)
            except Exception as e:
                print(f"error looping through vector at {item}, {e}")
    
    reordered_vector = target_vector[reorder_indices]

    #print('target indices for items only in the source vector:', reorder_indices, '(should only have these rows and columns left).\n')
    #print('target entries for items only in the source vector:', target_vector[reorder_indices], '\n')

    # take ony the rows from the target - but this will still have all columns
    reordered_matrix = target_matrix[reorder_indices, :]
    # now take only the columns
    reordered_matrix = reordered_matrix[:, reorder_indices]

    return found_items, missing_items, reordered_vector, reordered_matrix




# ------------------------------------------------------------------------

#
# performs mantel test on 2 matrices - in this case two matrices from word2vec
# used this at first but got same results as with skbio
#
#
# performs mantel test on 2 matrices - in this case two matrices from word2vec
#
def custom_mantel_test(source_matrix, target_matrix, permutations=10):
    
    s = time.time()
    
    # Ensure that the matrices are square and of the same size
    assert source_matrix.shape == target_matrix.shape, "Matrices must have the same shape."
    assert source_matrix.shape[0] == source_matrix.shape[1], "Matrices must be square."
    assert target_matrix.shape[0] == target_matrix.shape[1], "Matrices must be square."

    # Flatten the upper triangular parts of the matrices
    print("flattening matrices......")
    triu_indices = np.triu_indices_from(source_matrix, k=1)
    distances1 = source_matrix[triu_indices]
    distances2 = target_matrix[triu_indices]

    print("calculating pearson correlation....")
    # Calculate the observed Pearson correlation
    observed_corr, _ = pearsonr(distances1, distances2)

    print("running permutation tests....")
    # Permutation test
    permuted_corrs = []
    i = 0
    for _ in range(permutations):
        np.random.shuffle(distances2)
        permuted_corr, _ = pearsonr(distances1, distances2)
        permuted_corrs.append(permuted_corr)
        #print(f" - permutation {i} complete")
        i+=1

    # Calculate p-value
    print("- calculating p-value....")
    permuted_corrs = np.array(permuted_corrs)
    p_value = np.mean(permuted_corrs >= observed_corr)
    
    e = time.time()
    
    #print(f"- test complete in {round(e-s,2)}s. correlation: {observed_corr}. p-value: {p_value}")

    return observed_corr, p_value    
    



#
# main method
#
if __name__ == '__main__':
    
    current_date    = datetime.now().strftime('%Y%m%d')
    s1 = time.time()
    
    print('\n')
    print('---------------------------------------------------')
    print('    ** Word2Vec Distance Correlations Batch **     ')
    print('---------------------------------------------------\n')
    
    
    # ------------------------------------- define arguments -------------------------------------
    parser = argparse.ArgumentParser(prog='Word2Vec Distance Creation', description='Establishes correlation between two distances matrices')
    parser.add_argument("--w2v_file", help="full path to w2v npy file (must have 2 matrices and a vector)", required=True)
    parser.add_argument("--base_name", help="base name of distance file - for logging", required=True)
    parser.add_argument("--evo_file", help="full path to evo npy file (must have 2 matrices and a vector)", required=True)
    parser.add_argument("--output_dir", help="output directory for distance matrices", required=True)
    
    # ------------------------------------- extract arguments from shell script -------------------------------------
    args         = parser.parse_args()
    w2v_file     = args.w2v_file
    evo_file     = args.evo_file
    output_dir   = args.output_dir
    base_name    = args.base_name
    
    # -------------------------------------------------- extract files ---------------------------------------------
    s = time.time()
    print(f"\nProcessing distances for model :{base_name}............\n")
    print(f"Extracting matrices and vectors from .npy files:\n - {w2v_file}\n - {evo_file}")
    w2v_vector, w2v_matrix, w2v_matrix_norm = extract_matrix_vector_files(w2v_file)
    evo_vector_raw, evo_matrix_norm = extract_evo_matrix_vector_files(evo_file)
    
    # need to extract pfam ids from evo vector as they are in this format : K1SVA3.1/50-86|PF02829
    evo_vector = extract_evo_pfam_ids(evo_vector_raw)
    
    # need to convert vocab vector to numpy for mantel test
    w2v_vector_np = np.array(w2v_vector)
    evo_vector_np = np.array(evo_vector)
    e = time.time()
    #print(f"Matrices extracted and converted. time taken: {round(e-s,2)}s\n")
    
    # NOTE THAT THE PREVIOUS CODE WAS REMOVED ON 4 SEPT AT ABOUT 1700 AS I DETERMINED I COULD COMPARE MUCH
    # QUICKER USING skbio LIBRARIES - THE OLD CODE WAS DEVELOPED IN run_word2vec.ipynb AND IS STILL THERE
    # -- COMPARISON
    # skbio mantel test with 50 permutations complete in 42.88s corr : 0.027683471717661834 p_val : 0.0196078431372549 num: 15030.
    # skbio mantel test with DistanceMatrices and 50 permutations complete in 26.14s corr : 0.027683471717661834 p_val : 0.0196078431372549 num: 15030.
    # skbio mantel test with unordered DistanceMatrices and 50 permutations complete in 34.17s corr : 0.027683471717661834 p_val : 0.0196078431372549 num: 15030.
    # custom mantel test with 50 permutations complete in 565.19s corr : 0.027683471717690037 p_val : 0.0 num: 15030.

    #num_permutations = [25,50,100]
    num_permutations = [50]
    log_file = output_dir+current_date+"_dist_matrix_mantel.txt"
    lf = open(log_file, "a")
    
    #
    # -------------- run mantel but convert to DistMatrix first without having removed non-common entries
    #
    
    # need to convert w2v matrices to float - mantel fails if they are doubles!
    w2v_matrix_norm_fl = w2v_matrix_norm.astype(np.float64)
    #evo_matrix_norm_fl = evo_matrix_norm.astype(np.float64)

    w2v_dist_matrix = DistanceMatrix(w2v_matrix_norm_fl, ids=w2v_vector_np)
    evo_dist_matrix = DistanceMatrix(evo_matrix_norm, ids=evo_vector_np)
    

    for n in num_permutations:
        #print(f"Starting skbio mantel test with unordered DistanceMatrices and {n} permutations")
        s= time.time()
        corr_coeff, p_value, num = mantel(w2v_dist_matrix, evo_dist_matrix, permutations=n, strict=False)
        e = time.time()
        #print(f"Mantel test with unordered DistanceMatrices and {n} permutations complete in {round(e-s,2)}s corr : {corr_coeff} p_val : {p_value} num: {num}.\n")
    
    e1 = time.time()
    
    print(f"{current_date} | mantel | {base_name} | {round(e1 - s1, 2)} | {n} | {corr_coeff} | {p_value} | {num}")
    lf.write(f"{current_date} | mantel | {base_name} \t| {round(e1 - s1, 2)}s | {n} | {corr_coeff} | {p_value} | {num}\n")