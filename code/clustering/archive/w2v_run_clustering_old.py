from gensim.models import Word2Vec

from code.clustering.w2v_clan_helper import *
from code.clustering.methods.w2v_random_forest import W2V_RandomForest
from code.clustering.methods.w2v_kmeans import W2V_KMeans
from w2v_adaboost import W2V_AdaBoost
from code.clustering.methods.w2v_svm import W2V_SVM

from datetime import datetime
import re
import time
import numpy as np
import random
import argparse
import duckdb


#
# This loads a w2v model and then removes vectors that don;t have a pfam clan as well as vectors related to GAP words and DISORDER words
#
db_string = "/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/database/w2v_20240731_test.db"



# --------------------------------------------------------------------------------------------------------------------------
#                                               UTILITY METHODS
# --------------------------------------------------------------------------------------------------------------------------

#
# extracts the words used in a word2vec model by wuerying the model itself
# returns a list of words with any whitespace remoived as well as count of the umber of items
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
    return pfam_vocab, len(pfam_vocab)




def jaccard_similarity(set1, set2):
    # intersection of two sets
    intersection = len(set1.intersection(set2))
    # Unions of two sets
    union = len(set1.union(set2))
     
    return intersection / union

def jaccard_similarity_list(list1, list2):
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(set(list1)) + len(set(list2))) - intersection
    return float(intersection) / union


# Retrieves a subset of vectors from a w2v model dictionary - those being the vectors corresponding to pfam words
# in the dictionary that only have mappings to clans. This subset will be used to train model and see if it can
# accurately predict the labels of a test set
#
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
def run_svm(X, Y, pfam_ids, kernel, model_name, output_dir):
    depth           = 8
    classifier  = W2V_SVM(X, Y, pfam_ids, kernel, model_name, output_dir,)
    classifier.run(True)

#
# creates and runs random forest generators with varying depths
#
def run_kmeans(X, Y, pfam_ids, model_name, output_dir):
    
    classifier  = W2V_KMeans(X, Y, pfam_ids, model_name, output_dir,)
    ks = [500]
    threshold = 0.5 # just a threshold for jaccard
        
    for k in ks:
        cluster_dict = classifier.run(k, True)
        
        max_similarity = 0
        max_key_1 = ""
        max_key_2 = ""
        similarity_count = 0
        
        for key_1, set_1 in cluster_dict.items():
            for key_2, set_2 in clan_dict.items():
                similarity = jaccard_similarity_list(set_1, set_2)
                
                if similarity >= threshold:
                    similarity_count += 1
                    print(f"\nSimilarity : {key_1} to {key_2} : {similarity} - KMeans Cluster {key_1}: \n{cluster_dict[key_1]}\nClan {key_2}: \n{clan_dict[key_2]}")
        
                if similarity > 0:
                    if similarity > max_similarity:
                        max_similarity = similarity
                        max_key_1 = key_1
                        max_key_2 = key_2
                    #print(f"Jaccard Similarity cluster {key_1} to clan {key_2} : {similarity}")
        print(f"\n{similarity_count} items of {len(cluster_dict)} above similarity threshold {threshold}")
        print(f"\nMax similarity : {max_key_1} to {max_key_2} : {max_similarity} - KMeans Cluster {max_key_1}: \n{cluster_dict[max_key_1]}\nClan {max_key_2}: \n{clan_dict[max_key_2]}")
    
    cluster_dict = classifier.run(True)
    return cluster_dict


#
# main method
#
if __name__ == '__main__':
    
    current_date    = datetime.now().strftime('%Y%m%d')
    s1 = time.time()
    
    print('\n')
    print('---------------------------------------------------')
    print('            ** Word2Vec - Clustering  **           ')
    print('---------------------------------------------------\n')
    
    
    output_dir='/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/logs/clustering/'

    #model_dir="/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/models/best/"
    #model_names=['w2v_20240831_sg1_mc1_w8_v100']
    #model_names=['w2v_20240901_sg1_mc1_w44_v25', 'w2v_20240901_sg1_mc3_w44_v25', 'w2v_20240901_sg1_mc5_w44_v25', 'w2v_20240903_sg1_mc8_w44_v25_best', 'w2v_20240901_sg1_mc8_w13_v5_best_cosine', 'w2v_20240903_sg1_mc8_w44_v75', 'w2v_20240831_sg1_mc1_w8_v100', 'w2v_20240901_sg1_mc1_w44_v75', 'w2v_20240831_sg1_mc5_w3_v5', 'w2v_20240831_sg1_mc1_w3_v25_mac','w2v_20240831_sg1_mc5_w3_v50',  'w2v_20240831_sg1_mc5_w3_v75', 'w2v_20240831_sg1_mc3_w3_v100']
    
    model_dir   ="/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/data/models_validation_sep/"
    model_names = ['w2v_20240911_sg1_mc1_w3_v25']

    timestamp = datetime.now().strftime('%Y%m%d_%H%M')

    for model_name in model_names:
        
        # get details from model name
        model_path = model_dir+model_name+'.model'
        min_count_s = re.search("(mc[0-9]+)_", model_name)
        min_count = min_count_s.group(1)
        vector_s = re.search("v([0-9]+)", model_name)
        vector_size = vector_s.group(1)
        
        # -------------------------------------- get pfams and clans for model - only if clans have >=2 clans
        pfams, clans, clan_dict = get_pfam_clans_for_model(model_name, model_path, 2)

        print(f"\nModel {model_name} has {len(pfams)} with entries in {len(clans)} clans.")

        X = get_model_vectors(model_path, pfams, int(vector_size))
        Y = get_clans_for_pfams(pfams)
        
        
        # ------------------------------------------------------------------- 
        #  run whichever clustering we want
        # -------------------------------------------------------------------- 
        
        #run_kmeans(X, Y, pfams, model_name, output_dir)
        
        run_forest(X, Y, pfams, model_name, output_dir)
        #run_adaboost(X, Y, pfams, model_name, output_dir)
        #run_svm(X, Y, pfams, 'rbf', model_name, output_dir)
