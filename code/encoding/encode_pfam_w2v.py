import time
from gensim.models import Word2Vec
import os
import glob
import numpy as np
import re

#
# ----------- MAY NOT BE NEEDED -----------------------
#

#
# Gets the encoding vector for a list of pfam entries given a model
# Outputs the encoding to a numpy matrix - not entirely sure of the value of this
# as the encoding is already in the model
#
def encode_pfam_ids_for_model(model_name, pfam_file, target_folder):
    
    PFAM_LIMIT      = -1    # max to parse (useful for testin) set to -1 for all entries
    MAX_PFAM        = 15578 # total pfam entries > NEED TO CHECK THIS

    # load the model
    print('loading model:', model_name)
    model = Word2Vec.load(model_name)

    vector_size_search  = re.search("_vs([0-9]+)_", model_name)
    num_cols            = int(vector_size_search.group(1))
    
    base_name_search  = re.search("\/(w2v_.*)\.model", model_name)
    base_name         = base_name_search.group(1)
    print('base name for encoding:', base_name)

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
                '''
                if(row %10000 ==0):
                    m2 = time.time()
                    print(f"100000 pfam items encoded in {m2-m1}s")
                    m1 = m2
                '''
                row += 1
                
                if(PFAM_LIMIT != -1):
                    if line_number == (PFAM_LIMIT -1):
                        print(f"Line limit reached on line {line_number} - stopping.")
                        break
                    
        # save the encodings
        e1 = time.time()
        print(f"Encodings created in {e1 - s}s. Saving to {target_folder}{base_name}_encoding.npy")           
        np.save(target_folder+base_name+"_encoding", encoding_matrix)
        
        e2 = time.time()
        print(f"Encodings saved. Total time {e2 - s}s." )
        # return
        return model_name+"_encoding.npy"
            
    except Exception as e:
            print(f"An error occurred: {e}")
            


#
# parses a directory to build up sentences to create a model
#
def encode_all_models(models_dir, pfam_file, target_folder):
    # find the files in the target directory
    #print('Searching for corpi files in:', corpus_dir)
    file_list = glob.glob(os.path.join(models_dir, '*.model'))
    
    # initialise
    s = time.time()

    # parse each corpus file to build up the sentences
    for file_path in file_list:
        with open(file_path, 'r') as file:
            print(f'encoding using model: {file_path}')
            encode_pfam_ids_for_model(file_path, pfam_file, target_folder)
            
    # time check
    e = time.time()
    print(f"Overall encoding time {e - s}" )



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
    print("[15577,:]:", encoding_matrix[15577,:])


#
# ---------------- MAIN METHOD ---------------- 
#

# folder locations
model_folder    = "/Users/patrick/dev/ucl/comp0158_mscproject/models/"
pfam_file       = "/Users/patrick/dev/ucl/comp0158_mscproject/data/pfam/unique_eukaryotic_pfam.txt"
target_folder   = "/Users/patrick/dev/ucl/comp0158_mscproject/encodings/"

# encode pfam ids
print('------------ ENCODING ---------------------')
encode_all_models(model_folder, pfam_file, target_folder)

#encoding_file = encode_pfam_ids(model_name, pfam_file)

# test
#print('--------------- TESTING ------------------')
#test_encoding(encoding_file)

# calcualte distances
#print('----------- DISTANCE CALC ----------------')
#calculate_distances(encoding_file)
