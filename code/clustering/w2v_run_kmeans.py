from gensim.models import Word2Vec
from w2v_clustering_model import W2V_Clustering_Model
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
model_dir="/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/models/best/"
output_dir='/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/clusters/'


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



# Retrieves a subset of vectors from a w2v model dictionary - those being the vectors corresponding to pfam words
# in the dictionary that only have mappings to clans. This subset will be used to train model and see if it can
# accurately predict the labels of a test set
#
def get_model_vectors_clan_only(model_path, min_count, vector_size):
    
    model = Word2Vec.load(model_path)
    # I just happen to know that we will end up with 6,133 words, each with a vector of 25 dimensions
    
    if(min_count == 'mc1'):
        num_rows = 7508
    elif(min_count == 'mc3'):
        num_rows = 6745
    elif(min_count == 'mc5'):
        num_rows = 6419
    elif(min_count == 'mc8'):
        num_rows = 6133
    
    # create matrices and arrays for data
    X           = np.empty((num_rows, vector_size))
    X_pfam_ids  = []
    Y           = []
    
    #print(f"Created matrix X {X.shape}")
    
    full_vocab, num_items = get_pfam_vocab(model_path)
    con = duckdb.connect(database=db_string)
    count = 0
    for pfam_id in full_vocab:
        try:          
            result = con.execute(f"SELECT PFAM_ID, CLAN_ID FROM W2V_PFAM_CLAN WHERE PFAM_ID ='{pfam_id}'").fetchall()
            
            #if(result == []):
            #    print(f"No results for {pfam_id}")
            if(result != []):
                #print(result)
                pfam_result = result[0][0]
                clan_result = result[0][1]
                
                if clan_result != 'undef':
                    #print(f" ----------------- adding {clan_result} for {pfam_result}")
                    X_pfam_ids.append(pfam_result)
                    Y.append(clan_result)
                    X[count,:] = model.wv[pfam_result]
                    count +=1
                #else:
                #    print(f"ignoring {clan_result} for {pfam_result}")
        except Exception as e:
            print('Error', e, pfam_id)
            con.close()
            return
    #print(f"model with mc {min_count} has {count} pfam-clan pairs.")
    con.close()
    
    return X, Y, X_pfam_ids
    
    
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
    
    #model_names=['w2v_20240901_sg1_mc1_w44_v25', 'w2v_20240901_sg1_mc3_w44_v25', 'w2v_20240901_sg1_mc5_w44_v25', 'w2v_20240903_sg1_mc8_w44_v25_best', 'w2v_20240901_sg1_mc8_w13_v5_best_cosine', 'w2v_20240903_sg1_mc8_w44_v75', 'w2v_20240831_sg1_mc1_w8_v100', 'w2v_20240901_sg1_mc1_w44_v75', 'w2v_20240831_sg1_mc5_w3_v5']
    
    #model_names=['w2v_20240831_sg1_mc1_w3_v25_mac','w2v_20240831_sg1_mc5_w3_v50',  'w2v_20240831_sg1_mc5_w3_v75']
    
    model_names=['w2v_20240831_sg1_mc3_w3_v100']
    

    for model_name in model_names:
        
        # get details from model name
        model_path = model_dir+model_name+'.model'
        min_count_s = re.search("(mc[0-9]+)_", model_name)
        min_count = min_count_s.group(1)
        vector_s = re.search("v([0-9]+)", model_name)
        vector_size = vector_s.group(1)
        
        # get vocab for model
        vocab, vocab_count = get_pfam_vocab(model_path)

        
        # get training and test data - only use pfam ids that have known clan ids
        X, Y, X_pfam_ids = get_model_vectors_clan_only(model_path, min_count, int(vector_size))
        
        print(f"\nModel {model_name} with {min_count} original vocab size {vocab_count}: Found {len(Y)} mapped pfam words... X : {X.shape} Y : {len(Y)} pfams {len(X_pfam_ids)}")
        
        #
        # create classifier
        #
        k = 500
        iterations = 100
        depth      = 20
        depths = [10, 15, 20, 25, 30, 40,50]
        
        for depth in depths:
            classifier = W2V_Clustering_Model(X, Y, X_pfam_ids, k, depth, iterations, 'rf', model_name, output_dir)
        
            #
            # train and test classifier
            #
            classifier.run(True)
    
   
   

