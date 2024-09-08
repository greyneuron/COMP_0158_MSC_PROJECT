from datetime import datetime
from sklearn.cluster import KMeans

class W2V_KMeans:
    
    def __init__(self, X, Y, pfam_ids, k, model_name, output_dir):
        print(f"\n------------ W2V KMeans Classifier ------------")
        print(f" Model name         : {model_name}")
        print(f" k                  : {k}")
        
        assert len(Y) == len(pfam_ids), "must have same number of labels as pfam_ids"
        assert len(Y) == X.shape[0], "matrix must have same number of rows as there are labels"
        
        self.X = X
        self.Y = Y
        self.pfam_ids = pfam_ids
        self.k = k
        self.model_type = 'km'

        self.model_name = model_name
        self.output_dir = output_dir

    #
    # runs the model!
    #
    def run(self, debug=False):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
                
        if(debug):
            logfile_name = self.output_dir+timestamp+'_km_clustering_results.txt'
            log = open(logfile_name, "a")
        
        N, D = self.X.shape[0], self.X.shape[1]
        
        print(f"\nKMeans {timestamp} : Fitting {self.model_name} : {N} samples, each with {D} features......")
        

        # call KMeans to fit_predict - it will return a label for eaach sample
        classifier  = KMeans(n_clusters=self.k, random_state=0)
        labels      = classifier.fit_predict(self.X)

        # output results
        print('PFAM \t|\t Label \t|\t Clan')
        if(debug):
            log.write("PFAM \t|\t Label \t|\t Clan\n")
        for i in range(N):
            print(f"{self.pfam_ids[i]} \t|\t {self.Y[i]} \t|\t {labels[i]}")
            if(debug):
                log.write(f"{self.pfam_ids[i]} \t|\t {self.Y[i]} \t|\t {labels[i]}\n")
        if(debug):
            log.close()
