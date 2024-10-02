from gensim.models import Word2Vec

#import w2v_clan_utils
from methods.w2v_random_forest import W2V_RandomForest
from methods.w2v_kmeans import W2V_KMeans
from methods.w2v_adaboost import W2V_AdaBoost
from methods.w2v_svm import W2V_SVM

#import w2v_evo_utils
#import w2v_clan_utils

from datetime import datetime
import re
import time
import numpy as np
import random
import argparse
import duckdb

from pathlib import Path

import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

#
# This loads a w2v model and then removes vectors that don;t have a pfam clan as well as vectors related to GAP words and DISORDER words
#
db_string = "/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/database/w2v_20240731_test.db"



# --------------------------------------------------------------------------------------------------------------------------
#                                               UTILITY METHODS
# --------------------------------------------------------------------------------------------------------------------------

#
# finds files in a directory - useful for iterating through a load of models in one directory
#
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
# extracts the words used in a word2vec model by loading and querying the model for its vocab
# returns a list of words in the vocab as count of the number of items. It only includes pfam words
#       
def get_pfam_vocab(model_path):
    model = Word2Vec.load(model_path)
    
    vocab           = model.wv.key_to_index
    pfam_vocab    = []
    for i, word in enumerate(vocab):
        if (word == 'GAP' or word == 'START_GAP' or word == 'STOP_GAP' or word == 'DISORDER'):
            #print('ignoring', word)
            continue
        word = word.lstrip()
        word = word.rstrip()
        pfam_vocab.append(word)
    return pfam_vocab



# For a model, this method gets all the pfam words in the model and then finds the clan id in the database
# if the pfam entry is not in the database. As it goes, it creates a dictionary keyed by clan id and whose 
# values are the pfam ids in that clan.
#
def get_pfam_clans_for_model(model_name, model_path, min_clan_size):

    min_count_s = re.search("(mc[0-9]+)_", model_name)
    min_count   = min_count_s.group(1)
    
    # initialise variables
    con = duckdb.connect(database=db_string)
    
    filtered_clans      = []
    filtered_pfams      = []
    clan_dict           = {}
    filtered_clan_dict  = {}
    
    # get model vocab excluding exclude GAP, DISORDER etc.
    vocab = get_pfam_vocab(model_path)
    
    # for each pfam id get the clan
    for pfam_id in vocab:
        try:          
            results = con.execute(f"SELECT CLAN_ID FROM W2V_PFAM_CLAN_MC1 WHERE PFAM_ID='{pfam_id}'").fetchall()       
            if(results is None or results ==[]):
                raise Exception(f"No clan entry for {pfam_id} - query interpro and add the entry to the DB table W2V_PFAM_CLAN_MC1" ) 
            
            else:
                clan_id = results[0][0]
                if (clan_id != 'undef'):
                    # add clan id to dictionary
                    if clan_id in clan_dict:
                        clan_dict[clan_id].append(pfam_id)  # Append to the list if the key exists
                    else:
                        clan_dict[clan_id] = [pfam_id]
        except Exception as e:
            print('get_pfam_clans_for_model() error', e, results)
            con.close()
            return
    con.close()
    
    # get dictionary with only clans with more than one pfam
    filtered_clan_dict  = {key:value for key, value in clan_dict.items() if len(value) >= min_clan_size}
    filtered_clans      = list(filtered_clan_dict.keys())
    filtered_pfams      = list(set([item for sublist in filtered_clan_dict.values() for item in sublist]))
    
    # return only the pfams that have clans, what those clans are, and the clan dictionary mapping the two
    return filtered_pfams, filtered_clans, filtered_clan_dict


#
# Basically the same as the above but just takes a list of pfams
#
def get_clans_for_pfams(pfam_ids):
    con = duckdb.connect(database=db_string)
    clans = []
    
    # loop through each pfam, find its clan and build up a dictinary of clans > pfam_ids
    for pfam_id in pfam_ids:
        try:          
            results = con.execute(f"SELECT CLAN_ID FROM W2V_PFAM_CLAN_MC1 WHERE PFAM_ID='{pfam_id}'").fetchall()
            
            if(results is None or results ==[]):
                print(f"--------------------> No local clan entry for {pfam_id}, update needed.")
                raise Exception(f"No clan entry for {pfam_id} - add the entry to the DB table W2V_PFAM_CLAN_MC1" )
            else:
                clan_id = results[0][0]
                clans.append(clan_id)
        except Exception as e:
            print('get_clans_for_pfams() error', e)
            con.close()
            return
    con.close()
    return clans


# --------------------------------------------------------------------------------

#
# gets the jaccard similarity of betweeen two sets
#
def jaccard_similarity(set1, set2):
    # intersection of two sets
    intersection = len(set1.intersection(set2))
    # Unions of two sets
    union = len(set1.union(set2))
     
    return intersection / union

# as above but for lists
def jaccard_similarity_list(list1, list2):
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(set(list1)) + len(set(list2))) - intersection
    return float(intersection) / union

# --------------------------------------------------------------------------------

'''
# Retrieves a subset of vectors from a w2v model - those being the vectors corresponding to pfam words
# in the dictionary that also have mappings to clans. Along with the vectors, this also returns the 
# pfam words as whci
def get_model_vectors_clan_only(model_path, min_count, vector_size, min_clan_size):
    
    model = Word2Vec.load(model_path)
    # I just happen to know that we will end up with 6,133 words, each with a vector of 25 dimensions
    
    if(min_count == 'mc1'):
        num_rows = 6728
    elif(min_count == 'mc3'):
        num_rows = 6745
    elif(min_count == 'mc5'):
        num_rows = 6419
    elif(min_count == 'mc8'):
        num_rows = 6057
    
    # create matrices and arrays for data
    X           = np.empty((num_rows, vector_size))
    pfam_ids    = []
    Y           = []
    
    #print(f"Created matrix X {X.shape}")
    
    full_vocab, num_items = get_pfam_vocab(model_path)
    con = duckdb.connect(database=db_string)
    count = 0
    clan_dict = {}
    for pfam_id in full_vocab:
        try:          
            result = con.execute(f"SELECT PFAM_ID, CLAN_ID FROM W2V_PFAM_CLAN WHERE PFAM_ID ='{pfam_id}'").fetchall()
            
            if(result == []):
                print(f"-------------> No results for {pfam_id}. Has it been queried from interpro?")
                new_clan_id = get_interpro_clan(pfam_id)
                result=[new_clan_id]
                print(f"-------------> No results for {pfam_id}. Got {new_clan_id} from interpro.")
            if(result != []):
                #print(result)
                pfam_result = result[0][0]
                clan_result = result[0][1]
                
                if clan_result != 'undef':
                    # find out how many clans are in the current clan and only add the pfam if the clan is large enough                    
                    num_pfams = get_clan_count(clan_result)
                    
                    if (num_pfams >= min_clan_size):
                        # add to the vector and matrix
                        pfam_ids.append(pfam_result)
                        Y.append(clan_result)
                        X[count,:] = model.wv[pfam_result]
                        
                        # add the current pfam to the respective clan in the dictionary
                        if clan_result in clan_dict:
                            clan_dict[clan_result].append(pfam_result)  # Append to the list if the key exists
                            count +=1
                        else:
                            clan_dict[clan_result] = [pfam_result]
                    else:
                        print(f"ignoring {pfam_result} clan {clan_result} size < {min_clan_size}")
        except Exception as e:
            print('get_model_vectors_clan_only() - error', e, pfam_id)
            con.close()
            return
    print(f"model with mc {min_count} has {count} pfam-clan pairs. X:{X.shape} Y:{len(Y)}")
    con.close()
    
    return X, Y, pfam_ids, clan_dict
'''



# Retrieves a subset of vectors from a w2v model dictionary - those being the vectors corresponding to pfam words
# in the dictionary that only have mappings to clans. This subset will be used to train model and see if it can
# accurately predict the labels of a test set
#
def get_model_vectors(model_path, pfams, vector_size):
    model = Word2Vec.load(model_path)

    # create matrices and arrays for data
    X = np.empty((len(pfams), vector_size))
    for i, pfam_id in enumerate(pfams):
        vector = model.wv.get_vector(pfam_id)
        X[i] = vector
    return X


'''
def reduce_matrix(source_list, target_list, target_matrix):
    reorder_indices = []
    missing_items   = []
    found_items     = []
    source_vector = np.array(source_list)
    target_vector = np.array(target_list)
    
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

    return reordered_vector.tolist(), reordered_matrix

'''



# ----------------------------------------------------------------------------------------

#
# creates and runs random forest generators with varying depths
#
def run_forest(X, Y, pfam_ids, model_name, output_dir):
    #depths = [10, 15, 20, 25, 30, 40, 50]
    depths  = [10]
    for depth in depths:
        classifier = W2V_RandomForest(X, Y, pfam_ids, depth, model_name, output_dir,)
        classifier.run(True)
        
#
# creates and runs adaboost
#
def run_adaboost(X, Y, pfam_ids, model_name, output_dir):
    depth           = 6
    classifier  = W2V_AdaBoost(X, Y, pfam_ids, depth, model_name, output_dir,)
    classifier.run(True)

#
# creates and runs svm with a kernel
#
def run_svm(X, Y, pfam_ids, kernel, model_name, output_dir, lf):
    depth           = 8
    classifier  = W2V_SVM(X, Y, pfam_ids, kernel, model_name, output_dir,)
    classifier.run(True)

#
# creates and runs random forest generators with varying depths
#
def run_kmeans(X, Y, min_clan_size, k, pfam_ids, clan_dict, model_name, output_dir, lf):
    
    #detail_dir = output_dir + 'detail/'
    classifier  = W2V_KMeans(X, Y, pfam_ids, model_name, output_dir,)
    
    #detail_log_file   = detail_dir+model_name+'_kmeans_k'+str(k)+'_cluster_results.txt'
    #detail_file       = open(detail_log_file, "a")
    
    # get KMeans guess as to what the clusters are
    # KMeans returns a dictionary of 'k' clusters and the pfams within each 
    cluster_dict = classifier.run(k, False)
    
    max_similarity  = 0
    max_key_1       = ""
    max_key_2       = ""
    max_i = 0
    max_j = 0
    
    similarity_count    = 0
    similarity_total    = 0
    threshold           = 0.4 # just a threshold for jaccard    
    similarity_thresh_count = 0

    score_matrix = np.zeros((len(cluster_dict), len(clan_dict)))
    i = 0
    # loop through each cluster that has been found by KMeans
    # and compare it to the actual clans in clan_dict
    
    k_keys      = list(cluster_dict.keys())
    clan_keys   = list(clan_dict.keys())
    
    for key_1, set_1 in cluster_dict.items():
        #print(f" assessing {key_1} of {len(cluster_dict)}")
        j = 0
        for key_2, set_2 in clan_dict.items():
            similarity          = jaccard_similarity_list(set_1, set_2)
            similarity_total    += similarity
            similarity_count    += 1
            
            #k_keys.append(key_1)
            #clan_keys.append(key_2)
            
            score_matrix[i,j] = similarity
            
            # separate tracker to see how often we actually see similar clusters 
            if similarity >= threshold:
                #print(f"K{key_1} to {key_2} similarity : {round(similarity, 2)} {len(set_1)} : {len(set_2)}")
                similarity_thresh_count += 1
            #else:
                #print(f"K{key_1} to {key_2} similarity : {round(similarity, 2)}") 
            # keep track of maximum
            if similarity > 0:
                if similarity > max_similarity:
                    max_similarity = similarity
                    max_key_1 = key_1
                    max_key_2 = key_2
                    max_i = i
                    max_j = j
            #detail_file.write(f"{model_name} | {min_clan_size} | {k} | sim[{i},{j}] | {round(similarity, 4)} | {key_1} | {key_2} \n")
            j+=1
        i+=1 

    print(f" - {similarity_count} items of {len(cluster_dict)} above similarity threshold of {threshold}.")
    print(f" - Max similarity kmeans cluster : [{max_i}, {max_j}] kcluster: {max_key_1} clan: {max_key_2} : {max_similarity}")
    #detail_file.close()
    return score_matrix, k_keys, clan_keys, max_key_1, max_key_2, max_similarity

#
# main method
#
if __name__ == '__main__':
    
    current_date = datetime.now().strftime('%Y%m%d%H%M')
    s            = time.time()
    
    print('\n')
    print('---------------------------------------------------')
    print('            ** Word2Vec - Clustering  **           ')
    print('---------------------------------------------------')
    
    # ----------------------------------------------------------------------------------------------------------------------------
    
    
    # 1. Create a suitable test name below
    # 2. Make sure the models to test are in a folder with that name
    # 3. Also make sure there is a similarly named log file folder
    
    
    test_name       = '0910_g1'
    save_matrices   = True     # set to true to putput the similarity matrices
    max_count       = 100       # this is just for debuging purposes - set max_count to 1 to just run 1 model
    
    model_dir       = '/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/models/'+test_name+'/graph/'
    output_dir      = '/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/logs/clustering/'+test_name+'/'
    
    output_matrices = '/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/clusters/sim_matrices/'
    
    summary_filename = output_dir+current_date+'_'+test_name+'_km_results.txt'
    summary_file     = open(summary_filename, "a")
    #evo_file='/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/data/distances/evo/rand_rep_distance_matrix.npy'
    
    
    # ----------------------------------------------------------------------------------------------------------------------------
    
    print('---------------------------------------------------------------------------')
    print('                         ** Word2Vec - Clustering  **                      ')
    print(f"                             Test : {test_name}                           ")
    print('---------------------------------------------------------------------------')
    
    # ----------------------------------------------------------------------------------------------------------------------------
    # get all the models to test
    models_info     = find_files(model_dir)
    #min_clan_sizes  = [2, 10, 25, 50, 100, 150, 200, 250]
    min_clan_sizes  = [100]
    
    # loop through all the models in the 'best' folder
    count       = 0
    for model_info in models_info:
        if count < max_count:
            
            model_path = model_info[0]
            model_name = model_info[1]
            
            # get info from filename for logging purposes
            type_s      = re.search("_([a-zA-Z0-9]+)_mc", model_name)
            type        = type_s.group(1)
            gap_s       = re.search("_g([0-9]+)", model_name)
            gap_size    = gap_s.group(1)
            vector_s    = re.search("v([0-9]+)", model_name)
            vector_size = vector_s.group(1)
            min_count_s = re.search("mc([0-9]+)_", model_name)
            min_count   = min_count_s.group(1)
            vector_s    = re.search("_v([0-9]+)", model_name)
            vector_size = vector_s.group(1)
            window_s    = re.search("_w([0-9]+)_", model_name)
            window_size = window_s.group(1)
            
            print('\n----------- Clustering W2V Vectors ----------- ')
            print(f" Model      : {model_name}")
            print(f" Type       : {type}")
            print(f" Gap        : {gap_size}")
            print(f" Min count  : {min_count}")
            print(f" Vector     : {vector_size}")
            print(f" Window     : {window_size}")
            print('--------------------------------------------------- ')

            for min_clan_size in min_clan_sizes:
                # ----------------------------------------------------------------------------------------------------------
                # Get pfams and clans for model - if clans have >= min_clan_size clans 
                # This has been checked multiple times
                # ----------------------------------------------------------------------------------------------------------
                pfams, clans, clan_dict = get_pfam_clans_for_model(model_name, model_path, min_clan_size)

                # Get the corresponding vectors for those pfams (X) and their actual clans (Y)
                X = get_model_vectors(model_path, pfams, int(vector_size))
                Y = get_clans_for_pfams(pfams) # get correct clans (belt and braces to make sure order is same)
                
                # useful to check pfams being used
                '''    
                for clan, clan_pfams in clan_dict.items():
                    print(f"{clan} : {len(clan_pfams)} pfam entries:\n {clan_pfams}")
                '''    
                print(f"MIN CLAN SIZE: {min_clan_size} : NUM CLANS : {len(clans)} : NUM PFAMS : {len(pfams)} ({model_name}) X (vectors): {X.shape} Y (labels - clans): {len(Y)}")
                
                # number of clusters == nuumber of clans
                k_multipliers = [1.0, 0.75, 0.5, 0.25]
                for k_multiplier in k_multipliers:
                    k = int(k_multiplier * len(clans))
                    print(f" - USING K MULTIPLIER OF : {str(k_multiplier)}")
                    # ----------------------------------------------------------------------------------------------------------
                    #                               Run KMeans
                    # ----------------------------------------------------------------------------------------------------------
                    score_matrix, k_keys, clan_keys, max_kcluster, max_clan, max_sim  = run_kmeans(X, Y, min_clan_size, k, pfams, clan_dict, model_name, output_dir, summary_file)
                    
                    print(f"\n - {model_name} | mcs: {min_clan_size} | k: {k} | mean: {round(score_matrix.mean(), 4)} | max: {round(score_matrix.max(),4)} | min: {round(score_matrix.min(), 4)} | > | k:{max_kcluster} c:{max_clan} = {round(max_sim, 5)}")
                    
                    summary_file.write(f"{model_name} | 'kmeans' | {min_clan_size} | {k} | {round(score_matrix.mean(), 4)}  | {round(score_matrix.max(), 5)} {round(score_matrix.min(),4)} | > | {max_kcluster} : {max_clan} : {round(max_sim, 5)}\n")
                    summary_file.flush()
                    
                    if (save_matrices):
                        # save the score matrix to a file
                        jaccard_matrix_name=test_name+'_'+model_name+'_mcs'+str(min_clan_size)+'_kmeans_jaccard_'+str(k_multiplier)+'.npy'
                        jaccard_file_name = output_matrices+jaccard_matrix_name
                        with open(jaccard_file_name, "wb") as f:
                            np.save(f, score_matrix)
                            np.save(f, k_keys)
                            np.save(f, clan_keys)
                            f.close()
                    count +=1
    summary_file.close()
        
    
    '''    
    # -------------------------------------- get pfams and clans for model - only if clans have >=2 clans
    print('\n\n------------------------ > Clustering Evo Vectors')
    
    full_evo_pfams, full_evo_matrix     = w2v_evo_utils.get_evo_pfams_from_npy(evo_file)
    
    # get only pfam ids and clans that meet criteria
    evo_pfams, evo_clans, evo_clan_dict = w2v_clan_utils.get_pfam_clans_for_evo(full_evo_pfams, 2)
    
    print(f"Evo distance matrix with {len(full_evo_pfams)} pfams has {len(evo_pfams)} with entries in {len(evo_clans)} clans.\n")
    
    # use this smaller pfam list to modify the original matrix
    reordered_pfams, X = reduce_matrix(evo_pfams, full_evo_pfams, full_evo_matrix)
    
    # now get the correct clans for this new list (bit of a safety net)
    Y = w2v_clan_utils.get_pfam_clans_db(reordered_pfams)
    
    run_kmeans(X, Y, reordered_pfams, evo_clan_dict, 'evo', output_dir)
    
    # need to remove non-matching items from the distance matrix
        
    # ------------------------------------------------------------------- 
    #  run whichever clustering we want
    # -------------------------------------------------------------------- 
    
    #run_kmeans(X, Y, pfams, model_name, output_dir)

    #run_forest(X, Y, pfams, model_name, output_dir)
    #run_adaboost(X, Y, pfams, model_name, output_dir)
    #run_svm(X, Y, pfams, 'rbf', model_name, output_dir)
    '''
