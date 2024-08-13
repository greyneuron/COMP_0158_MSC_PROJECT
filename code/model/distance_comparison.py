
class W2V_Distance_Tools:
    
    def __init__(self):
        print('W2V Distance Tools - constructor')

    # creates a distance matrix for a model
    # this assumes a certain naming convention for models and vocab files
    # For example
    #   If the model name is : w2v_20240811_v5_w5_mc3, the code will expect
    #   - a model called w2v_20240811_v5_w5_mc3.model
    #   - a vocab file  called w2v_20240811_v5_w5_mc3.txt
    #   And will output a distance matrix called:
    #   - 
    #   
    def create_distance_matrix(self, model_dir, model_name, vocab_dir):
        vocab_file = vocab_dir+model_name+'_vocab.txt'
        
        # get pfam ids from the models vocab
        #print(f"Encoding vocab file: {vocab_file}")
        model = Word2Vec.load(model_dir+model_name+'.model')
        pfam_ids = []
        with open(vocab_file, 'r') as vf:
            for line in vf:
                line = line.rstrip()
                line =  line.lstrip()
                if line.startswith('PF'):
                    pfam_ids.append(line)
                    #encoding = model.wv[line]
                    #print(f"Encoding :{line}: {encoding}")
        #print(pfam_ids)
        vf.close()
        
        # calculate matrix size and initialise
        num_entries = len(pfam_ids)
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
        
        output_name = vocab_dir+model_name+"_dist"
        np.save(output_name, distance_matrix)
        e = time.time()
        print(f"distance matrix computed for model: {model_name}. num words: {num_entries}. time: {round(e-s,2)}s. success: {success_count} fail: {error_count} output: {output_name}.npy")
    

def distance_comparison()