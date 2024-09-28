from datetime import datetime
from sklearn.cluster import KMeans

class W2V_KMeans:
    
    def __init__(self, X, Y, pfam_ids, model_name, output_dir):
        #print(f"\n------------ W2V KMeans Classifier ------------")
        #print(f" Model name         : {model_name}")
        
        assert len(Y) == len(pfam_ids), "must have same number of labels as pfam_ids"
        assert len(Y) == X.shape[0], "matrix must have same number of rows as there are labels"
        
        self.X = X
        self.Y = Y
        self.pfam_ids = pfam_ids
        self.model_type = 'km'

        self.model_name = model_name
        self.output_dir = output_dir

    #
    # runs the model and returns a dictionary of cluster ids mapped to the pfams they contain
    #
    def run(self, k, debug=False):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        
        cluster_dict = {}
                
        #if(debug):
        #    logfile_name = self.output_dir+timestamp+'_kmeans_k'+str(k)+'_results.txt'
        #    log = open(logfile_name, "a")
        
        N, D = self.X.shape[0], self.X.shape[1]
        
        print(f"\nKMeans {timestamp} : Fitting {self.model_name} : {N} samples, each with {D} features. K={k}.")
        

        # call KMeans to fit_predict - it will return a label for eaach sample
        classifier  = KMeans(n_clusters=int(k), random_state=0)
        labels      = classifier.fit_predict(self.X)
        
        #print(classifier.labels_)

        # output results
        #print('Model \t|\t PFAM Id \t|\t True Label \t|\t Cluster Number')
        for i in range(N):
            cluster_id = labels[i]
            pfam_id    = self.pfam_ids[i]
            # add the current pfam to its clan
            if cluster_id in cluster_dict:
                cluster_dict[cluster_id].append(pfam_id)  # Append to the list if the key exists
            else:
                cluster_dict[cluster_id] = [pfam_id]
            
            #print(f"{self.model_name} \t|\t {self.pfam_ids[i]} \t|\t {self.Y[i]} \t|\t {labels[i]}")
            #if(debug):
            #    log.write(f"{self.model_name} \t|\t kmeans \t|\t {k} \t|\t {self.pfam_ids[i]} \t|\t {self.Y[i]} \t|\t {labels[i]}\n")
        #if(debug):
        #   log.close()
        return cluster_dict
