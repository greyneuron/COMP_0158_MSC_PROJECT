import numpy as np
import time
from datetime import datetime
import random
from gensim.models import Word2Vec
import re
from sklearn.ensemble import RandomForestClassifier

class W2V_Clustering_Model:
    
    def __init__(self, X, Y, pfam_ids, k, depth, iterations, clustering_type, model_name, output_dir):
        print(f"\n------------ W2V KMeans model ------------")
        print(f" Model name         : {model_name}")
        print(f" Clustering type    : {clustering_type}")
        print(f" k                  : {k}")
        print(f" depth              : {depth}")
        print(f" num iterations     : {iterations}")
        
        assert len(Y) == len(pfam_ids), "must have same number of labels as pfam_ids"
        assert len(Y) == X.shape[0], "matrix must have same number of rows as there are labels"
        
        self.X = X
        self.Y = Y
        self.pfam_ids = pfam_ids
        self.k = k
        self.depth = depth
        self.iterations = iterations
        self.clustering_type = clustering_type
        self.model_name = model_name
        self.output_dir = output_dir

    #
    # runs a model!
    #
    def run(self, debug=False):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        
        model_dir="/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/models/best/"
        
        print(f"\nTraining......")
        
        print(f" - splitting data into train and test sets")
        
        # break into training and test sets
        num_entries          = self.X.shape[0]
        train_split          = 0.8
        indices              = list(range(num_entries))
        train_indices        = random.sample(indices, int(train_split * num_entries))
        test_indices         = list(set(indices) - set(train_indices))
        
        X_train = self.X[train_indices, :]
        Y_train = [self.Y[i] for i in train_indices]
        pfam_train = [self.pfam_ids[i] for i in train_indices]
        
        X_test = self.X[test_indices, :]
        Y_test = [self.Y[i] for i in test_indices]
        pfam_test = [self.pfam_ids[i] for i in test_indices]

        if(debug):
            log_file = self.output_dir+'logs/'+timestamp+'_'+self.clustering_type+'_k'+str(self.k)+'_d'+str(self.depth)+'_'+self.model_name+'.log'
            log = open(log_file, "w")
            
            log.write(f"------------ W2V KMeans model ------------\n")
            log.write(f" Model name         : {self.model_name}\n")
            log.write(f" Clustering type    : {self.clustering_type}\n")
            log.write(f" k                  : {self.k}\n")
            log.write(f" depth              : {self.depth}\n")
            log.write(f" num iterations     : {self.iterations}\n")

        #print(f"training indices {selected_indices}\nX train:\n {X_train}")
        print(f" - training")
        random_forest = RandomForestClassifier(max_depth=self.depth, random_state=0)
        random_forest.fit(X_train, Y_train)

        # just getting the model for testing
        model_path = model_dir+self.model_name+'.model'
        model = Word2Vec.load(model_path)
        
        print(f"\nTesting......")
        success = 0
        fail = 0
        for i in range(len(test_indices)):
            test_idx = test_indices[i]
            
            # get vector
            test_vec = self.X[test_idx,:]


            dims = len(test_vec)
            test_vec = test_vec.reshape(1,dims)
            
            test_y_truth    = self.Y[test_idx]
            test_pfam_truth = self.pfam_ids[test_idx]
        
            # get the prediction
            y_pred = random_forest.predict(test_vec)[0]
            
            #if(debug):
                #log.write(f" testing {test_idx} {test_pfam_truth} {test_y_truth} with vector \n{test_vec}\nactual vector:\n {model.wv[test_pfam_truth]}\n")
            #    log.write(f" truth: {test_y_truth} pred: {y_pred}\n")
                
            if (test_y_truth == y_pred):
                if(debug):
                    log.write(f"SUCCESS for {test_pfam_truth} true clan: {test_y_truth} pred clan: {y_pred}\n")
                success +=1
            else:
                if(debug):
                    log.write(f"FAIL for {test_pfam_truth} true clan: {test_y_truth} pred clan: {y_pred}\n")
                fail +=1
                
        print(f"result: {self.model_name} | {self.clustering_type} | {self.k} | {self.depth} | {self.iterations} | {len(test_indices)} | {success} | {fail} | {round (success/len(train_indices), 5)}")
        if(debug):
            log.write(f"result: {self.model_name} | {self.clustering_type} | {self.k} | {self.depth} | {self.iterations} | {len(test_indices)} | {success} | {fail} | {round (success/len(train_indices), 5)}\n")
            log.close()