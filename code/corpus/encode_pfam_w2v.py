import time
from gensim.models import Word2Vec
import os
import glob

def encode_pfam(model, pfam_id):
    return 
    
model_file = "/Users/patrick/dev/ucl/comp0158_mscproject/code/corpus/my_w2v_model.model"
pfam_file = "/Users/patrick/dev/ucl/comp0158_mscproject/code/corpus/encoding/unique_pfam_20240722.dat"


print('loading model:', model_file)
model = Word2Vec.load(model_file)

try:
    print('PF00001', model.wv["PF00001"])
    print('PF00002', model.wv["PF00002"])
    print('Hello', model.wv["Hello"])
except Exception as e:
        print(f"An error occurred: {e}")
    