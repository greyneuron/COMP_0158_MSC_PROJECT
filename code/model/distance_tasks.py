
import numpy as np
import time
from gensim.models import Word2Vec
import re

# for mantel
from scipy.spatial.distance import pdist, squareform
from scipy.stats import pearsonr

class W2V_DistanceTasks:
    
    def __init__(self, model_dir, distances_dir):
        print(f"W2V DistanceTasks\nInitialised with model directory \n{model_dir} and distances directory \n{distances_dir}.")
        self.model_dir = model_dir
        self.distances_dir = distances_dir

    #
    # gets the vocab for a model - returns a python list and a numpy array
    #
    def get_model_vocab(self, model_name):
        pfam_ids = []

        model = Word2Vec.load(self.model_dir+model_name+'.model')
        vocab = model.wv.key_to_index
        
        print(f"Model {model_name} has a vocab of {len(vocab)}")
        for word in vocab:
            pfam_ids.append(word)
        return pfam_ids

    #
    # Extracts a matrix and vector frpm a supplied npy file
    #
    def extract_npy_files(self, filename):
        
        output_matrix_name = self.distances_dir+'rand_rep_distance_matrix.npy'
        output_vector_name = self.distances_dir+'rand_rep_distance_vector.npy'
        
        print('opening', filename)
        f = open(filename, 'rb')
        matrix_1  = np.load(f) #loads first array
        vector_1  = np.load(f)
        
        matrix_len = matrix_1.shape[0]
        
        pfam_ids  = []
        print(f"matrix 1 shape: {matrix_1.shape} vocab: {len(vector_1)}")
        print(f"first 5 items")
        for i in range(matrix_len):
            entry   = vector_1[i]
            pfam_s  = re.search("\|(PF[0-9]*)", entry)
            pfam_id = pfam_s.group(1)
            #print(f"{i} :{pfam_id}: \tdistance entry:{matrix_1[i,0:5]}")
            pfam_ids.append(pfam_id)
        
        pfam_ids_np = np.array(pfam_ids)
        
        with open(output_matrix_name, "wb") as mf:
            np.save(mf, matrix_1)
        
        with open(output_vector_name, "wb") as vf:
            np.save(vf, pfam_ids_np)
    
    #
    # loads and returns a previously created distance matrix
    #
    def get_distance_matrix(self, model_name):
        distance_matrix_name = self.vocab_dir+model_name+'_dist.npy'
        print(f"Loading dist matrix {distance_matrix_name}")
        dist_matrix = np.load(distance_matrix_name)
        return dist_matrix

    
    #
    # reduces and reorders a target matrix so that it only has the items in source_v
    # source_v : list of items we want to have and in the order we need them
    # target_v : items that are currently in a target_matrix and the order they are in (assume same ordering rows and columns)
    # target_matrix : the matrix we want to remove ros/columns from and reorder to the same order as source_v
    # returns a new matrix which is the original target matrix but modified as decribed
    #
    def reorder_matrix(self, source_v, target_v, target_matrix):
        reorder_indices = []
        for item in source_v:
            
            if(item.startswith("PF")):
                
                #index = np.where(target_v == item)[0]
                #reorder_indices.append(index[0])
                index = np.where(target_v == item)[0]
                print(f"item: {item} index: {index}")
                if index.size != 0:
                    reorder_indices.append(index[0])
            else:
                continue
        print(f"{len(reorder_indices)} indices needed in target matrix and :{reorder_indices}")

        reordered_matrix = target_matrix[reorder_indices, :]
        reordered_matrix = reordered_matrix[:, reorder_indices]

        # Print the result
        #print('\n', reordered_matrix)
        return reordered_matrix
        
        


    # creates a distance matrix for a model
    # this assumes a certain naming convention for models and vocab files
    # For example
    #   If the model name is : w2v_20240811_v5_w5_mc3, the code will expect
    #   - a model called w2v_20240811_v5_w5_mc3.model
    #   - a vocab file  called w2v_20240811_v5_w5_mc3.txt
    #   And will output a distance matrix called:
    #   - w2v_20240811_v5_w5_mc3_dist.npy
    #   
    def create_distance_matrix(self, model_name):
        print(f"Creating distance matrix for model {model_name}.")
        # get pfam ids from the vocab file corresponding to the model
        model       = Word2Vec.load(self.model_dir+model_name+'.model')
        
        #print('model_vocab:', model.wv.key_to_index)
        pfam_ids = self.get_model_vocab(model_name)

        # calculate matrix size and initialise
        num_entries     = len(pfam_ids)
        distance_matrix = np.zeros((num_entries, num_entries))
        
        error_count = 0
        success_count = 0
        s = time.time()
        
        # loop through each entry and calulate its distance
        for i in range(num_entries):
            for j in range(i+1, num_entries):
                pfam_1 = pfam_ids[i]
                pfam_2 = pfam_ids[j]
                try:
                    v1 = model.wv[pfam_1]
                    v2 = model.wv[pfam_2]
                    
                    # distance calc
                    
                    distance = np.linalg.norm(v1 - v2)
                    #print(f"distance {pfam_1} to {pfam_2} : {distance}")
                    
                    distance_matrix[i][j] = distance
                    success_count +=1
                except Exception as e: # a bit convoluted, but want to print out the missing pfam
                    missing = re.search("Key '(.*)' not", e.args[0] )
                    print(missing.group(1))
                    error_count +=1
                    continue
        
        # normalise and flip - same way as db did so comparison is on equal basis
        max_dist = np.max(distance_matrix)
        min_dist = np.min(distance_matrix)
        print(f"min dist: {min_dist}. max dist: {max_dist}")
        np.fill_diagonal(distance_matrix, (np.max(distance_matrix)*1.2))
        
        normalized_dist_matrix = (distance_matrix - min_dist) / (max_dist - min_dist)
        
        flipped_norm_dist_matrix = 1.0 - normalized_dist_matrix
        
        # save distance matrix and pfam ids
        output_name = self.distances_dir+model_name+"_dist_normalised.npy"
        with open(output_name, "wb") as f:
            np.save(f, flipped_norm_dist_matrix)
            np.save(f, pfam_ids)

        e = time.time()
        print(f"distance matrix computed for model: {model_name}. num words: {num_entries}. time: {round(e-s,2)}s. success: {success_count} fail: {error_count} output: {output_name}")
        
        return
    
    
    #
    # performs mantel test on 2 matrices - in this case two matrices from word2vec
    #
    def w2v_evo_mantel_test(self, w2v_model_name, evo_dist_matrix_name, evo_vector_name, permutations=10):
        
        s = time.time()
        
        # get w2v distance matrix and vocab
        w2v_dist_file   = self.distances_dir+w2v_model_name+'_dist_normalised.npy'
        w2v_df          = open(w2v_dist_file, 'rb')
        w2v_dist_matrix = np.load(w2v_df) #loads first array
        w2v_vocab       = self.get_model_vocab(w2v_model_name)
        w2v_vocab_np    = np.array(w2v_vocab)
        
        # load evo matrix and vector
        evo_distance_file   = self.distances_dir+evo_dist_matrix_name
        evo_df              = open(evo_distance_file, 'rb')
        evo_dist_matrix     = np.load(evo_df)
        evo_vf              = open(self.distances_dir+evo_vector_name, 'rb')
        evo_vector          = np.load(evo_vf)
        
        print(f"w2v_dist_matrix shape: {w2v_dist_matrix.shape} vocab: {len(w2v_vocab)}")
        print(f"evo_dist_matrix shape: {evo_dist_matrix.shape} vocab: {len(evo_vector)}")
        
        matrix_2_common = self.reorder_matrix(w2v_vocab_np, evo_vector, evo_dist_matrix)
        print(f"reordered matrix 2 shape: {matrix_2_common.shape}.")
        
        
        # Ensure that the matrices are square and of the same size
        assert w2v_dist_matrix.shape == matrix_2_common.shape, "Matrices must have the same shape."
        assert w2v_dist_matrix.shape[0] == w2v_dist_matrix.shape[1], "Matrices must be square."
        assert matrix_2_common.shape[0] == matrix_2_common.shape[1], "Matrices must be square."

        # Flatten the upper triangular parts of the matrices
        triu_indices = np.triu_indices_from(w2v_dist_matrix, k=1)
        distances1 = w2v_dist_matrix[triu_indices]
        distances2 = matrix_2_common[triu_indices]

        print("- calculating pearson correlation....")
        # Calculate the observed Pearson correlation
        observed_corr, _ = pearsonr(distances1, distances2)

        print("- running permutation test....")
        # Permutation test
        permuted_corrs = []
        i = 0
        for _ in range(permutations):
            np.random.shuffle(distances2)
            permuted_corr, _ = pearsonr(distances1, distances2)
            permuted_corrs.append(permuted_corr)
            print(f"permutation {i} complete")
            i+=1

        # Calculate p-value
        print("- calculating p-value....")
        permuted_corrs = np.array(permuted_corrs)
        p_value = np.mean(permuted_corrs >= observed_corr)
        
        e = time.time()
        
        print(f"- test complete in {round(e-s,2)}s. correlation: {observed_corr}. p-value: {p_value}")

        return observed_corr, p_value
    
    
    
    

    #
    # performs mantel test on 2 matrices - in this case two matrices from word2vec
    #
    def w2v_mantel_test(self, model1, model2, permutations=10):
        
        s = time.time()
        
        file_1 = self.vocab_dir+model1+'_dist_normalised.npy'
        file_2 = self.vocab_dir+model2+'_dist_normalised.npy'
        
        f = open(file_1, 'rb')
        matrix_1 = np.load(f) #loads first array
        vector_1 = np.load(f)
        
        f = open(file_2, 'rb')
        matrix_2 = np.load(f) #loads first array
        vector_2 = np.load(f)
        
        print(f"matrix 1 shape: {matrix_1.shape} vocab: {len(vector_1)}")
        print(f"matrix 2 shape: {matrix_2.shape} vocab: {len(vector_2)}")
        
        matrix_2_common = self.reorder_matrix(vector_1, vector_2, matrix_2)
        print(f"reordered matrix 2 shape: {matrix_2_common.shape}.")
        
    
        # Ensure that the matrices are square and of the same size
        assert matrix_1.shape == matrix_2_common.shape, "Matrices must have the same shape."
        assert matrix_1.shape[0] == matrix_1.shape[1], "Matrices must be square."
        assert matrix_2_common.shape[0] == matrix_2_common.shape[1], "Matrices must be square."

        # Flatten the upper triangular parts of the matrices
        triu_indices = np.triu_indices_from(matrix_1, k=1)
        distances1 = matrix_1[triu_indices]
        distances2 = matrix_2_common[triu_indices]

        print("- calculating pearson correlation....")
        # Calculate the observed Pearson correlation
        observed_corr, _ = pearsonr(distances1, distances2)

        print("- running permutation test....")
        # Permutation test
        permuted_corrs = []
        i = 0
        for _ in range(permutations):
            np.random.shuffle(distances2)
            permuted_corr, _ = pearsonr(distances1, distances2)
            permuted_corrs.append(permuted_corr)
            print(f"permutation {i} complete")
            i+=1

        # Calculate p-value
        print("- calculating p-value....")
        permuted_corrs = np.array(permuted_corrs)
        p_value = np.mean(permuted_corrs >= observed_corr)
        
        e = time.time()
        
        print(f"- test complete in {round(e-s,2)}s. correlation: {observed_corr}. p-value: {p_value}")

        return observed_corr, p_value


