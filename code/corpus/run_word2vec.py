import re
import time
from gensim import corpora
from gensim.models import Word2Vec
import os

# ------ Background------ 
#
# This script is step 5 of 5 to create sentences to form a corpus for word2vec
#
# 5 steps:
# 1. extract_tokens_from_db.sh : Runs sql from the mysql command line and pipes it to an output file : sql_output_<startprotein>_<iteration>.txt
# 2. convert_db_tokens_dat.sh  : Converts each of the txt outputs from step 1 into a dat file of pipe separated tokens.
#    Each line consists of information about a token and its corresponding uniprot id
# 3. combine_db_tokens_dat.py : Converts each lines (one per token) into a single line per protein (each line with multiple tokens for that protein plus metadata)
# 4. create_corpus.py : Creates a sentence for each protein with GAP DISORDER and PFAM 'words', orders the tokens and removes overlaps
# 5. run_word2vec.py  : Calls word2vec with the corpus
#



#print("\n***** CORPUS *****:\n",corpus,'\n')

# documentation
# https://github.com/piskvorky/gensim#documentation
#
# also



# https://www.geeksforgeeks.org/nlp-gensim-tutorial-complete-guide-for-beginners/

#w2v = Word2Vec(corpus, size=100, window=5, workers=4, iter=10, min_count=5)

corpus_file     = "/Users/patrick/dev/ucl/comp0158_mscproject/code/corpus/corpus/corpus_00M_00.txt"
output_file     = "/Users/patrick/dev/ucl/comp0158_mscproject/code/corpus/w2v_vectors/vectors_00M_00.txt"

w2v = Word2Vec(sentences = corpus_file, vector_size=100, window=5, workers=4, epochs=10, min_count=5)
model = w2v.load("word2vec.model")
model.train(corpus_file)
w2v.save("word2vec.model")


'''
print('Creating dictionary')
dictionary = corpora.Dictionary(corpus)
dictionary.save('/Users/patrick/dev/ucl/comp0158_mscproject/data/corpus/corpus.dict')  # store the dictionary, for future reference
print(dictionary)

print('Creating encoding')
protein_doc = "DISORDER GAP PF00250 GAP"
print('BoW for', protein_doc,':')
protein_vec = dictionary.doc2bow(protein_doc.split())
print(protein_vec)
'''