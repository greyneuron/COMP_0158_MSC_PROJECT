import re
import time
from gensim import corpora
from gensim.models import Word2Vec
from datetime import datetime
import os
import glob

# for mantel
from scipy.spatial.distance import pdist, squareform
from scipy.stats import pearsonr

class W2V_ModleTasks:
    
    def __init__(self, model_dir, vocab_dir, corpus_file):
        print(f"W2V_ModleTasks\nInitialised with model directory \n{model_dir}\nand vocab dir\n{vocab_dir}")
        self.model_dir = model_dir
        self.vocab_dir = vocab_dir
        self.corpus_file = corpus_file
        self.sentences = None
        
    #
    # parses a dicorpus file to build up sentences to create a model
    #
    def get_corpus_sentences(self):
        # initialise
        s = time.time()
        if(self.sentences is None):
            print(f'No sentences set, parsing file for sentences: {self.corpus_file}')
            sentences = []
            counter = 0
            num_tokens = 0
            print(f'Parsing file for sentences: {self.corpus_file}')
            with open(self.corpus_file, 'r') as file:
                for line in file:
                    line = line.strip('\n')
                    tokens = line.split()
                    sentences.append(tokens)
                    counter +=1
                    num_tokens += len(tokens)
            # time check
            e = time.time()
            print(f"{counter} sentences processed, {num_tokens} added in {e - s}s" )
            self.sentences = sentences
        return self.sentences
    
    #
    # Create W2V model
    #
    def create_w2v_model(self, vector_size, window_size, min_count):
        current_date    = datetime.now().strftime('%Y%m%d')
        
        model_base_name = "w2v_"+current_date + "_v"+str(vector_size)+"_w"+str(window_size)
        model_name      = self.model_dir+model_base_name + ".model"
        
        s = time.time()
        
        if(self.sentences is None):
            self.get_corpus_sentences()
        
        # create model from sentences       
        w2v = Word2Vec(self.sentences, vector_size=vector_size, window=window_size, workers=4, epochs=10, min_count=min_count)
        
        # save model      
        w2v.save(model_name)
        
        
        e = time.time()
        print(f"created {model_base_name}, v:{vector_size}, w:{window_size}, ms:{mc}, time:{round(e-s,2)}s, output:{model_name}")
            
