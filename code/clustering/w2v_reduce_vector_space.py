from datetime import datetime
import time
import numpy as np
import random
import argparse

from gensim.models import Word2Vec

from sklearn.model_selection import train_test_split

#
# This loads a w2v model and then removes vectors that don;t have a pfam clan as well as vectors related to GAP words and DISORDER words
#

model_dir="/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/models/best/"
model_name="w2v_20240903_sg1_mc8_w44_v25_best"
pfams_with_clans="/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/clusters/matched_pfam_clans.txt"

code_dir="/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/code/clustering"
output_dir='/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/clusters/'


# Retrieves a subset of vectors from a w2v model dictionary - those being the vectors corresponding to pfam words
# in the dictionary that only have mappings to clans. This subset will be used to train model and see if it can
# accurately predict the labels of a test set
#
def reduce_model(model_path):
    
    model = Word2Vec.load(model_path)
    # I just happen to know that we will end up with 6,133 words, each with a vector of 25 dimensions
    
    X = np.empty((6133, 25))
    X_PFAM = []
    Y_CLAN = []
    
    # Open the file in read mode
    with open(pfams_with_clans, 'r') as file:
        i = 0
        for line in file:
            #print(line.strip())  # Strip removes any extra newline characters
            tokens = line.split("|")
            pfam_id = tokens[0].rstrip()
            pfam_id = pfam_id.lstrip()
            clan_id = tokens[1].rstrip()
            clan_id = clan_id.lstrip()
            #print(f"{pfam_id}:{clan_id}:")
            
            v = model.wv[pfam_id]
            
            X[i,:] = v
            X_PFAM.append(pfam_id)
            Y_CLAN.append(clan_id)
            i +=1
            
            print(f"{pfam_id} {clan_id}:\n{v}")
    file.close()
    
    return X, X_PFAM, Y_CLAN
        


#
# main method
#
if __name__ == '__main__':
    
    current_date    = datetime.now().strftime('%Y%m%d')
    s1 = time.time()
    
    print('\n')
    print('---------------------------------------------------')
    print('             ** Word2Vec - Model reduction **      ')
    print('---------------------------------------------------\n')
    
    model_path = model_dir+model_name+'.model'
    
    # get vectors from out model only for words that have clan entries
    print(f"getting matrix of pfam words with clans")
    X, X_PFAM, Y_CLAN = reduce_model(model_path)
    
    
    print(f"Matrix has shape {X.shape}")
    assert len(X_PFAM) == len(Y_CLAN), "vectors must be of same length"
    assert len(Y_CLAN) == len(X_PFAM), "matrix must have same number of rows s labels"
    
    
    print(f"splitting into train and test sets")
    num_entries = len(X_PFAM)
    train_split = 0.8

    # Create a list of indices for 100 items and randomly select 80% for training and 20% for testing
    indices = list(range(num_entries))
    selected_indices        = random.sample(indices, int(train_split * num_entries))
    non_selected_indices    = list(set(indices) - set(selected_indices))

    # use those indices to cut down my model
    X_PFAM_train = [X_PFAM[i] for i in selected_indices]
    X_PFAM_test  = [X_PFAM[i] for i in non_selected_indices]
    
    Y_CLAN_train = [Y_CLAN[i] for i in selected_indices]
    Y_CLAN_test  = [Y_CLAN[i] for i in non_selected_indices]
    
    X_train = X[selected_indices, :]
    X_test  = X[non_selected_indices, :]
    
    #print(f"training indices {selected_indices}\nX train:\n {X_train}")

    print(f"training a model")
    from sklearn.ensemble import RandomForestClassifier
    
    clf = RandomForestClassifier(max_depth=5, random_state=0)
    clf.fit(X_train, Y_CLAN_train)
    
    model = Word2Vec.load(model_path)
    
    success = 0
    fail = 0
    test_size = len(non_selected_indices)
    for i in range(test_size):
        test_idx = non_selected_indices[i]
        
        test_vec = X[test_idx,:]
        print(f"test vector has shape {test_vec.shape}")
        test_vec = test_vec.reshape(1,25)
        
        print(f"test vector has shape {test_vec.shape}\n")
        test_y_truth    = Y_CLAN[test_idx]
        test_pfam_truth = X_PFAM[test_idx]
        
        print(f"Testing {test_idx} {test_pfam_truth} {test_y_truth} with vector \n{test_vec}\nactual vector:\n {model.wv[test_pfam_truth]}....")
        
        y_pred = clf.predict(test_vec)
        print(f"Test id {test_idx}, test pfam {test_pfam_truth}, test clan (truth) {test_y_truth}..... predicted clan {y_pred}\n")
        if (test_y_truth == y_pred):
            success +=1
    print(f"success : {success}, percent success : {round (success/test_size)}")
    
    #X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

