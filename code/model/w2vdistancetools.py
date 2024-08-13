
import numpy as np
import time
from gensim.models import Word2Vec

# for mantel
from scipy.spatial.distance import pdist, squareform
from scipy.stats import pearsonr

class W2V_Distance_Tools:
    
    def __init__(self, model_dir, vocab_dir):
        print(f"W2V Distance Tools\nInitialised with model directory \n{model_dir}\nand vocab dir\n{vocab_dir}")
        self.model_dir = model_dir
        self.vocab_dir = vocab_dir

    #
    # gets the vocab for a model - returns a python list and a numpy array
    #
    def get_model_vocab(self, model_name):
        pfam_ids = []
        vocab_file = self.vocab_dir+model_name+'_vocab.txt'
        
        with open(vocab_file, 'r') as vf:
            for line in vf:
                line = line.rstrip()
                line =  line.lstrip()
                if line.startswith('PF'):
                    pfam_ids.append(line)
        vf.close()
        np_pfam_ids = np.array(pfam_ids)
        return pfam_ids, np_pfam_ids


    #
    # loads and returns a previously created distance matrix
    #
    def get_distance_matrix(self, model_name):
        distance_matrix_name = self.vocab_dir+model_name+'_dist.npy'
        print(f"Loading dist matrix {distance_matrix_name}")
        dist_matrix = np.load(distance_matrix_name)
        return dist_matrix



    # creates a distance matrix for a model
    # this assumes a certain naming convention for models and vocab files
    # For example
    #   If the model name is : w2v_20240811_v5_w5_mc3, the code will expect
    #   - a model called w2v_20240811_v5_w5_mc3.model
    #   - a vocab file  called w2v_20240811_v5_w5_mc3.txt
    #   And will output a distance matrix called:
    #   - w2v_20240811_v5_w5_mc3_dist.npy
    #   
    def create_distance_matrix(self, model_dir, model_name):
        #vocab_file = self.vocab_dir+model_name+'_vocab.txt'
        
        # get pfam ids from the vocab file corresponding to the model
        model       = Word2Vec.load(self.model_dir+'.model')
        pfam_ids    = self.get_model_vocab(self, model_name)

        # calculate matrix size and initialise
        num_entries     = len(pfam_ids)
        distance_matrix = np.zeros((num_entries, num_entries))
        
        # create empty distance matrix
        #print(f"Calculating distances for {num_entries} pfam ids under model {model_name}")
        error_count = 0
        success_count = 0
        s = time.time()
        for i in range(num_entries):
            for j in range(i+1, num_entries):
                pfam_1 = pfam_ids[i]
                pfam_2 = pfam_ids[j]
                try:
                    v1 = model.wv[pfam_1]
                    v2 = model.wv[pfam_2]
                    distance = np.linalg.norm(v1 - v2)
                    distance_matrix[i][j] = distance
                    success_count +=1
                except Exception as e: # a bit convoluted, but want to print out the missing pfam
                    #print(f"Exception calculating {pfam_1} to {pfam_2} : {e.args[0]}")
                    missing = re.search("Key '(.*)' not", e.args[0] )
                    print(missing.group(1))
                    #of.write(missing.group(1) + '\n')
                    error_count +=1
                    continue
        # close the output file
        #of.close()
        
        output_name = self.vocab_dir+model_name+"_dist"
        np.save(output_name, distance_matrix)
        e = time.time()
        print(f"distance matrix computed for model: {model_name}. num words: {num_entries}. time: {round(e-s,2)}s. success: {success_count} fail: {error_count} output: {output_name}.npy")
        
        return distance_matrix
    


    def mantel_test(self, matrix1, matrix2, permutations=10000):
        # Ensure that the matrices are square and of the same size
        assert matrix1.shape == matrix2.shape, "Matrices must have the same shape."
        assert matrix1.shape[0] == matrix1.shape[1], "Matrices must be square."

        # Flatten the upper triangular parts of the matrices
        triu_indices = np.triu_indices_from(matrix1, k=1)
        distances1 = matrix1[triu_indices]
        distances2 = matrix2[triu_indices]

        print("- calculating pearson correlation....")
        # Calculate the observed Pearson correlation
        observed_corr, _ = pearsonr(distances1, distances2)

        print("- running permutation test....")
        # Permutation test
        permuted_corrs = []
        for _ in range(permutations):
            np.random.shuffle(distances2)
            permuted_corr, _ = pearsonr(distances1, distances2)
            permuted_corrs.append(permuted_corr)

        # Calculate p-value
        print("- calculating p-value....")
        permuted_corrs = np.array(permuted_corrs)
        p_value = np.mean(permuted_corrs >= observed_corr)
        
        print("- test complete....")

        return observed_corr, p_value




    
    #
    # Compares distance matrices - assuems they have been created already
    # The target model is assume to be a superset of the source_model
    def perform_mantel_distance_comparison(self, source_model_name, target_model_name):

        # get the vocab list for both models we wish to compare
        source_vocab, np_source_vocab = self.get_model_vocab(source_model_name)
        target_vocab, np_target_vocab = self.get_model_vocab(target_model_name)

        print(f"Source model {source_model_name} vocab size: {len(source_vocab)}.")
        print(f"Target model {target_model_name} vocab size: {len(target_vocab)}.")

        # create a True/False mask with True where the item from the source array is in the target array
        mask = np.isin(np_target_vocab, np_source_vocab)
        print(f"Shared vocab between models: {mask.sum()}.")

        # load the target matrix (iw the one we want to reduce so it has the same entries as the source)
        target_matrix = self.get_distance_matrix(target_model_name)
        source_matrix = self.get_distance_matrix(source_model_name)

        # identify common rows/columns from the target matrix and create a new matrix with only those
        mask                = np.isin(np_target_vocab, np_source_vocab)
        target_matrix_subset  = target_matrix[np.ix_(mask, mask)]

        print(f"Target dist matrix reduced from {target_matrix.shape} to {target_matrix_subset.shape}")
        
        # can now compare distances using Mantel test
        print('Performing mantel test')
        observed_corr, p_value = self.mantel_test(source_matrix, target_matrix_subset)
        print(f"Mantel test results: {observed_corr} {p_value}")
        
        