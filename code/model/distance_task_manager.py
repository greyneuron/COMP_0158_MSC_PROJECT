from distance_tasks import W2V_DistanceTasks


def execute():
    model_dir="/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/models/"  
    
    # get an instance of model tools
    distance_tasks = get_distance_tasks(model_dir)
    
    '''
    # speciify the models to work with - model 1 shold have the larget vocab
    model1 = 'w2v_20240811_v5_w5_mc5'
    model2 = 'w2v_20240811_v5_w5_mc3'
    
   
    # create distance matrix
    models = [model1, model2]
    for model in models:
        print ('creating distance matrix for model', model)
        model_tools.create_distance_matrix(model)
    '''
    
    
    #distance_tasks.create_distance_matrix('w2v_20240814_v5_w5_mc1')
    
    # get npy files for db
    db_file = '/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/evolutionary/rand_rep_distance_matrix.npy'
    distance_tasks.extract_npy_files(db_file)
    
    # compare the model distances
    #model_tools.mantel_test(model1, model2)


if __name__ == '__main__':
    # confgiguration - change here for your system
    model_dir="/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/models/"
    distances_dir="/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/models/distances/"
    
    print('\n')
    print('---------------------------------------------------')
    print('     ** Word2Vec Distance Task Manager **          ')
    print('---------------------------------------------------')
    
    # create instance of DistanceTools
    distance_tasks = W2V_DistanceTasks(model_dir, distances_dir)
    
    # unpack a evolutionary distaance binary
    #db_file = '/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/evolutionary/rand_rep_distance_matrix.npy'
    #distance_tasks.extract_npy_files(db_file)
    
    w2v_model_name          = 'w2v_20240814_v5_w5_mc1'
    evo_dist_matrix_name    = 'rand_rep_distance_matrix.npy'
    evo_vector_name         = 'rand_rep_distance_vector.npy'
    
    #distance_tasks.create_distance_matrix(w2v_model_name)
    #distance_tasks.w2v_evo_mantel_test(w2v_model_name, evo_dist_matrix_name, evo_vector_name)
    
    #distance_tasks.test_reorder_2()
    
    distance_tasks.w2v_evo_mantel_test(w2v_model_name, evo_dist_matrix_name, evo_vector_name)
    
    
    
    