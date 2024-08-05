import time
from gensim.models import Word2Vec
import os
import glob
import numpy as np
import re

#
# Takes a file of pfam entries and encodes them
#
def encode_pfam_ids(model_name, pfam_file):
    
    PFAM_LIMIT      = -1  # max to parse (useful for testin) set to -1 for all entries
    MAX_PFAM        = 20725 # total pfam entries > NEED TO CHECK THIS

    # load the model
    full_model_name = model_name + ".model"
    print('loading model:', full_model_name)
    model = Word2Vec.load(full_model_name)

    # ROWS - One per pfam entry
    # How many rows are needded - one row per pfam entry
    #pfam_ids    = ["PF00001", "PF00002", "PF00003", "PF00004", "PF00005","PF00006"]
    #num_rows    = len(pfam_ids)
    
    # COLUMNS - One for each dimension in the vector used to generate the model
    # The vector size (columns) is encoded in the model file name
    vs_search   = re.search("_vs([0-9]+)_", model_name)
    num_cols    = int(vs_search.group(1))

    # create a numpy matrix to hold the encodings
    if(PFAM_LIMIT != -1):
        encoding_matrix = np.empty((PFAM_LIMIT, num_cols))
    else:
        encoding_matrix = np.empty((MAX_PFAM, num_cols))
    print(f"Encoding matrix of shape {encoding_matrix.shape} created.")
    
    # open pfam file and create encodings
    row = 0
    s = time.time()
    m1 = time.time()
    try:
        with open(pfam_file, 'r') as pf:
            for line_number, line in enumerate(pf):
                line = line.rstrip()
                line = line.lstrip()
                #print(f":{line}:")
                
                try:
                    encoding = model.wv[line]
                    #print(f"encoding for line number {line_number} {line} : {encoding}")
                
                    # add to the matrix
                    encoding_matrix[row, :] = encoding
                except Exception as e:
                    #print(f"An error occurred: {e}")
                    encoding_matrix[row, :] = None
                
                # output interim timings
                if(row %1000 ==0):
                    m2 = time.time()
                    print(f"10000 pfam items encoded in {m2-m1}s")
                    m1 = m2
            
                row += 1
                
                if(PFAM_LIMIT != -1):
                    if line_number == (PFAM_LIMIT -1):
                        print(f"Line limit reached on line {line_number} - stopping.")
                        break
                    
        # save the encodings
        e1 = time.time()
        print(f"Encodings created in {e1 - s}s. Saving to {model_name}_encoding.npy")           
        np.save(model_name+"_encoding", encoding_matrix)
        
        e2 = time.time()
        print(f"Encodings saved. Total time {e2 - s}s." )
        # return
        return model_name+"encoding.npy"
            
    except Exception as e:
            print(f"An error occurred: {e}")
            
    

#
# Given an encoding matrix, calculate the distances bewtween pairs of pfam tokens
#
def calculate_distances(encoding_file):
    encoding_matrix = np.load(encoding_file)
    
    num_entries = encoding_matrix.shape[0]
    # calcualte distances

    print(f"\ncalculating distances for {num_entries} pfam ids")
    for i in range(num_entries):
        for j in range(i+1, num_entries):
            #print(f"i {i} {encoding_matrix[i,:]}")
            #print(f"j {j} {encoding_matrix[j,:]}")
            #print(encoding_matrix[j,:])
            distance = np.linalg.norm(encoding_matrix[i,:] - encoding_matrix[j,:])
            print(f"distance i:{i} to j:{j} = {distance}")
            

#
# just checks the encoding file by printing out some values
#
def test_encoding(encoding_file):
    print('\nTesting encoding', encoding_file)
    encoding_matrix = np.load(encoding_file)

    print(f"Matrix shape: {encoding_matrix.shape}")
    print(encoding_matrix)
    print("[0,:]:", encoding_matrix[0,:])
    print("[1,:]:", encoding_matrix[1,:])
    print("[2,:]:", encoding_matrix[2,:])


#
# ---------------- MAIN METHOD ---------------- 
#
model_name = "/Users/patrick/dev/ucl/comp0158_mscproject/code/corpus/model/w2v_20240805_vs10_w5"
pfam_file = "/Users/patrick/dev/ucl/comp0158_mscproject/code/corpus/encoding/unique_pfam_20240722.dat"


# encode pfam ids
print('------------ ENCODING ---------------------')
encoding_file = encode_pfam_ids(model_name, pfam_file)

# test
print('--------------- TESTING ------------------')
test_encoding(encoding_file)

# calcualte distances
print('----- DISTANCE CALC -----------------------')
calculate_distances(encoding_file)



'''
# reload the encodings just proudced

print("\nRELOADED ENCODINGS")
encoding_matrix = np.load(encoding_file)

print(f"Matrix shape: {encoding_matrix.shape}")
print(encoding_matrix)
print("[0,:]:", encoding_matrix[0,:])

num_entries = encoding_matrix.shape[0]
# calcualte distances

print(f"\ncalculating distances for {num_entries} pfam ids")
for i in range(num_entries):
    for j in range(i+1, num_entries):
        #print(f"i {i} {encoding_matrix[i,:]}")
        #print(f"j {j} {encoding_matrix[j,:]}")
        #print(encoding_matrix[j,:])
        distance = np.linalg.norm(encoding_matrix[i,:] - encoding_matrix[j,:])
        print(f"distance i:{i} to j:{j} = {distance}")
    
'''