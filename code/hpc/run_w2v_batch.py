# -*- coding: utf-8 -*-
from gensim.test.utils import datapath
from gensim.models.word2vec import LineSentence
import sys
import argparse
from gensim.test.utils import datapath
from gensim.models.word2vec import LineSentence
import time
from datetime import datetime
from gensim.models import Word2Vec
import pickle as pkl

def create_w2v_model(sentences, model_type, vector_size, window_size, min_count):
    w2v = Word2Vec(sentences, sg=model_type, vector_size=vector_size, window=window_size, workers=4, epochs=10, min_count=min_count)
    return w2v


#
# Parses a corpus file to load sentences into an array
# Follows the same approach as this tutorial https://rare-technologies.com/word2vec-tutorial/#app
#
def get_array_sentences(corpus_file, limit=-1):
    # initialise
    sentences = []
    counter = 0
    num_tokens = 0

    print(f"parsing sentence to array from: {corpus_file}")
    with open(corpus_file, 'r') as file:
        for line in file:
            if limit != -1 and counter >= limit:
                break
            line = line.strip('\n')
            tokens = line.split()
            
            print(f"{counter} : {tokens}")
            
            sentences.append(tokens)
            
            #print(f"{counter} : {sentences}")
            
            counter +=1
            num_tokens += len(tokens)
    return sentences

#
# Use gensim to read sentences from a file
#
def get_line_sentences(corpus_file):
    print(f"creating sentences using Line Sentence from: {corpus_file}")
    sentences = LineSentence(datapath(corpus_file))
    print(sentences)
    return sentences


#
# main method
#
if __name__ == '__main__':
    
    current_date    = datetime.now().strftime('%Y%m%d')
    CBOW            = 0
    SKIP_GRAM       = 1
    
    
    print('\n')
    print('---------------------------------------------------')
    print('       ** Word2Vec Model Batch **          ')
    print('---------------------------------------------------')
    
    parser = argparse.ArgumentParser(prog='Word2Vec Model Task Manager', description='Orchestrates the creation of word2vec models')
    
    parser.add_argument("--corpus_file", help="full path to corpus (pickle file from python array)", required=False)
    parser.add_argument("--output_dir", help="output directory for models", required=False)
    parser.add_argument("--model_type", choices=['cbow', 'skip'], help="output directory for models", required=False)
    parser.add_argument("--mc", help="min word count (integer)", required=True)

    #parser.add_argument("--vs", help="vector size (integer)", required=True)
    
    parser.add_argument("--ws", help="window size (integer)", required=True)
    #parser.add_argument("--mc", help="min word count (integer)", required=True)
    
    
    # extract arguments
    args            = parser.parse_args()
    sentences_file  = args.corpus_file
    output_dir      = args.output_dir
    model_type      = args.model_type
    pickle_file     = sentences_file
    
    window_size     = int(args.ws)
    min_count       = int(args.mc)
    
    
    '''
    vector_size     = args.vs
    window_size     = args.ws
    '''
    
    # sort out model type
    if 'bag' == model_type:
        model_type = CBOW
    elif 'skip' == model_type:
        model_type = SKIP_GRAM
    
    
    print(f"Running word2vec with model_type: {model_type} window_size: {window_size} min_count: {min_count} output_dir: {output_dir}, sentences: {sentences_file}.")
    
    #
    # create sentences and save to pickle - only need to do this once
    #
    '''
    s = time.time()
    #sentences = get_line_sentences(corpus_file)
    sentences = get_array_sentences(corpus_file)
    e = time.time()
    print(f"sentences created {e-s} seconds")
    with open(pickle_file, 'wb') as f:
        pkl.dump(sentences, f)
    '''

    #
    # load pre-prepared sentences
    #
    print('loading array from file:', sentences_file)
    s = time.time()
    with open(sentences_file, 'rb') as f:
        sentences = pkl.load(f)
    e = time.time()
    print(f"sentence array loaded in {round(e-s, 2)} seconds.")
    
    #
    # Change these params for each batch
    #
    #vector_sizes    = [5, 10, 25, 40, 65, 80, 100]
    vector_sizes    = [5, 10]
    
    #
    # create and save model
    #
    for vector_size in vector_sizes:
        s = time.time()
        print(f"creating model type: {model_type} vs: {vector_size} ws: {window_size} mc: {min_count}.")
        
        model_name  = output_dir+"w2v_"+current_date + "_sg"+str(model_type) + "_v"+str(vector_size)+"_w"+str(window_size)+"_mc"+str(min_count)+".model"   
        w2v_model   = create_w2v_model(sentences, int(model_type), vector_size, window_size, min_count)
        w2v_model.save(model_name)
        e = time.time()

        print(f"{model_name} | {model_type} | {vector_size} | {window_size} | {min_count} | {round(e-s,2)}s")
    
