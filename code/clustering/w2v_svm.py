from datetime import datetime
from sklearn.svm import SVC
import random

class W2V_SVM:
    
    def __init__(self, X, Y, pfam_ids, kernel, model_name, output_dir):
        print(f"\n------------ W2V SVM Classifier ------------")
        print(f" Model name     : {model_name}")
        print(f" Kernel         : {kernel}")
        
        assert len(Y) == len(pfam_ids), "must have same number of labels as pfam_ids"
        assert len(Y) == X.shape[0], "matrix must have same number of rows as there are labels"
        
        self.X = X
        self.Y = Y
        self.pfam_ids = pfam_ids
        self.kernel     = kernel
        self.model_type = 'svm_'+self.kernel

        self.model_name = model_name
        self.output_dir = output_dir

    #
    # runs the model!
    #
    def run(self, debug=False):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
                
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
            logfile_name = self.output_dir+timestamp+'_smv_'+self.kernel+'_clustering_results.txt'
            log = open(logfile_name, "a")
            
        #
        # Train
        #
        N, D = self.X.shape[0], self.X.shape[1]
        print(f"\nSVM {self.kernel} {timestamp} : Fitting {self.model_name} : {N} samples, each with {D} features......")

        print(f" - svm classifier - training")
        classifier  = SVC(kernel=self.kernel)
        classifier.fit(X_train, Y_train)
        
        #
        # Test
        #
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
            y_pred = classifier.predict(test_vec)[0]
            
            #if(debug):
                #log.write(f" testing {test_idx} {test_pfam_truth} {test_y_truth} with vector \n{test_vec}\nactual vector:\n {model.wv[test_pfam_truth]}\n")
            #    log.write(f" truth: {test_y_truth} pred: {y_pred}\n")
                
            if (test_y_truth == y_pred):
                #if(debug):
                #    log.write(f"SUCCESS for {test_pfam_truth} true clan: {test_y_truth} pred clan: {y_pred}\n")
                success +=1
            else:
                #if(debug):
                #    log.write(f"FAIL for {test_pfam_truth} true clan: {test_y_truth} pred clan: {y_pred}\n")
                fail +=1
                
        print(f"result: {self.model_name} | {self.model_type} | {len(test_indices)} | {success} | {fail} | {round (success/len(train_indices), 5)}")
        if(debug):
            log.write(f"result: {self.model_name} | {self.model_type} | {len(test_indices)} | {success} | {fail} | {round (success/len(train_indices), 5)}\n")
        log.close()
