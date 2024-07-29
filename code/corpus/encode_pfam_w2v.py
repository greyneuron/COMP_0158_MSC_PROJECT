import time
from gensim.models import Word2Vec
import os
import glob
import numpy as np
import re

def encode_pfam_ids(model_name, pfam_file):

    

    print('loading model:', model_name + ".model")
    model = Word2Vec.load(model_name+ ".model")


    pfam_ids = ["PF00001", "PF00002", "PF00003", "PF00004", "PF00005","PF00006"]

    # ------ WORK OUT WHAT SIZE NP MATRIX IS NEEDED ---------

    # The vector size (columns) is encoded in the model file name
    vs_search   = re.search("_vs([0-9]+)_", model_name)
    vector_size = int(vs_search.group(1))

    # The num rows = number of pfam ids to encode
    matrix_rows = len(pfam_ids)

    print(f"Creating encoding matrix of size {matrix_rows} x {vector_size} .......")

    # create a numpy matrix to hold the encodings
    encoding_matrix = np.empty((matrix_rows,vector_size))

    # iterate through pfam entries and reate a matrix - one row per pfam
    # being the encoding for that word
    row = 0
    try:
        for pfam_id in pfam_ids:
            encoding = model.wv[pfam_id]
            #print(f"encoding for {pfam_id} : {encoding}")
            encoding_matrix[row, :] = encoding
            row += 1
        
        # print out the matrix
        print("\nENCODINGS TO SAVE:")
        print(encoding_matrix)
        
        # save the encoding
        np.save(model_name+"encoding", encoding_matrix)
        
        return model_name+"encoding.npy"
        # test reloading the encoding
        

    except Exception as e:
            print(f"An error occurred: {e}")
        


model_name = "/Users/patrick/dev/ucl/comp0158_mscproject/code/corpus/model/w2v_20240729_vs10_w5_00M_"
pfam_file = "/Users/patrick/dev/ucl/comp0158_mscproject/code/corpus/encoding/unique_pfam_20240722.dat"

# encode pfam ids
encoding_file = encode_pfam_ids(model_name, pfam_file)

# reload the encpdings just proudced

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
    
    