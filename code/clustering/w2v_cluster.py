from datetime import datetime
import time
import numpy as np
import argparse

from gensim.models import Word2Vec
from scipy.cluster.vq import kmeans
from scipy.cluster.vq import whiten

from sklearn.cluster import KMeans

#
# loads a model and returns its vocab and vocab vectors
#
def get_model_elements(model_path):
    print(f"Loading model {model_path}")
    
    model           = Word2Vec.load(model_path)
    pfam_vectors    = model.wv.vectors
    
    # grab the vocab vector
    vocab           = model.wv.key_to_index
    pfam_vocab    = []
    for i, word in enumerate(vocab):
        #if (word == 'GAP' or word == 'START_GAP' or word == 'STOP_GAP' or word == 'DISORDER'):
        #    continue
        pfam_vocab.append(word)
    
    return pfam_vocab, pfam_vectors
    
#
# check matrix
#
def check_vectors(vector_matrix):
    nans = np.isnan(vector_matrix)
    print(nans)
    print(nans.sum())
    
    infs = np.isinf(vector_matrix)
    print(infs)
    print(infs.sum())
    

#
# runs kmeans clustering
#
def run_kmeans(vector_matrix, k, n):
    print(f"running kmeans...")
    
    centroids, distortion  = kmeans(vector_matrix, k, iter=n, check_finite=False)
    
    print(f"centroids shape {centroids.shape}")

#
# main method
#
if __name__ == '__main__':
    
    current_date    = datetime.now().strftime('%Y%m%d')
    s1 = time.time()
    
    print('\n')
    print('---------------------------------------------------')
    print('             ** Word2Vec Clustering **             ')
    print('---------------------------------------------------\n')
    
    
    # ------------------------------------- define arguments -------------------------------------
    parser = argparse.ArgumentParser(prog='Word2Vec Distance Creation', description='Establishes correlation between two distances matrices')
    parser.add_argument("--model_dir", help="folder where model is located", required=True)
    parser.add_argument("--model_name", help="name of model (without .model extension)", required=True)
    parser.add_argument("--k", help="number of clusters", required=True)
    parser.add_argument("--n", help="number of iterations", default=10)
    parser.add_argument("--output_dir", help="output directory for results", required=True)
    
    # ------------------------------------- extract arguments from shell script -------------------------------------
    args            = parser.parse_args()
    model_dir       = args.model_dir
    model_name      = args.model_name
    k               = args.k
    n               = args.n
    output_dir      = args.output_dir

    # -------------------------------------------------- extract files ---------------------------------------------
    s = time.time()
    print(f"Creating {k} clusters for model {model_name} over {n} iterations ....\n")
    
    model_file = model_name+'.model'
    model_path = model_dir+model_file
    
    pfam_vocab, pfam_vectors = get_model_elements(model_path)
    print(f"Model loaded vocab length: {len(pfam_vocab)} vector matrix shape: {pfam_vectors.shape} ....")
    
    '''
    # wrote this becuase kmeans was complainign about Nans and infs
    check_vectors(pfam_vectors)
    of = open(output_dir+'vectors.txt', 'a')
    np.savetxt(of, pfam_vectors)
    of.close
    
    check_vectors(pfam_vectors)
    '''
    '''
    print('whiten...')
    pfam_vectors_w = whiten(pfam_vectors)
    print('scipy kmeans...\n')
    run_kmeans(pfam_vectors_w, int(k), int(n))
    '''
    
    pfam_vectors_pfam_only  = np.delete(pfam_vectors, [0,1,2,3], axis=0)
    pfam_vocab_pfam_only    = np.delete(pfam_vocab, [0,1,2,3])
    
    #print(pfam_vectors_pfam_only)
    
    print('scikit kmeans...\n')
    
    kmeans_full     = KMeans(n_clusters=100, random_state=0, n_init="auto").fit(pfam_vectors)
    kmeans_full_cl  = KMeans(n_clusters=100, random_state=0, n_init="auto").fit(pfam_vectors_pfam_only)
    
    print(f"num labeled items in full: {len(kmeans_full.labels_)} num labeled items in clean: {len(kmeans_full_cl.labels_)}")
    
    log_file = output_dir+current_date+"_kmeans_assignments.txt"
    vocab_file = output_dir+current_date+"_model_vocab.txt"
    
    lf = open(log_file, "w")
    lf.write("word \t|\t label 1 \t|\t label 2 \n")
    vf = open(vocab_file, "w")

    
    for i in range(len(pfam_vocab)):
        item = pfam_vocab[i]
        if (item == 'GAP' or item == 'START_GAP' or item == 'STOP_GAP' or item == 'DISORDER'):
            #print(f"item {i} is {item} - only in first kmeans")      
            lf.write(str(pfam_vocab[i]) + '\t|\t' + str(kmeans_full.labels_[i]) + '\t|\t - \n')
            continue
        else:
            #print(f"item {i} is {item} - in both kmeans")
            vf.write(item+'\n')
            lf.write(str(pfam_vocab[i]) + '\t|\t' + str(kmeans_full.labels_[i]) + '\t|\t' + str(kmeans_full_cl.labels_[i-4]) + '\n')
    
    lf.close()
    vf.close()
        
    


