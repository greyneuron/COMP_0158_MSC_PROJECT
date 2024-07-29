import time
from gensim.models import Word2Vec
import os
import glob
import numpy as np

def encode_pfam(model, pfam_id):
    return 
    
model_file = "/Users/patrick/dev/ucl/comp0158_mscproject/code/corpus/my_w2v_model.model"
pfam_file = "/Users/patrick/dev/ucl/comp0158_mscproject/code/corpus/encoding/unique_pfam_20240722.dat"

print('loading model:', model_file)
model = Word2Vec.load(model_file)

try:
    for pfam_id in ["PF00001", "PF00002"] :
        encoding = model.wv[pfam_id]
        #print(pfam_id, len(encoding),  '\n',encoding)
        
        np_vector = np.array(encoding)
        print(pfam_id, 'numpy array:\n', np_vector)

except Exception as e:
        print(f"An error occurred: {e}")
    