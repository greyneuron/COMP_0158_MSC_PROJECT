from w2vdistancetools import W2V_Distance_Tools

def get_model_tools(model_dir, vocab_dir):
    distance_tools = W2V_Distance_Tools(model_dir, vocab_dir)
    return distance_tools

def execute():
    vocab_dir="/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/models/vocab/"
    model_dir="/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/models/"  
    
    # get an instance of model tools
    model_tools = get_model_tools(model_dir, vocab_dir)
    
    # speciify the models to work with - model 1 shold have the larget vocab
    model1 = 'w2v_20240811_v5_w5_mc5'
    model2 = 'w2v_20240811_v5_w5_mc3'
   
    
    # compare the model distances
    model_tools.perform_mantel_distance_comparison(model1, model2)




if __name__ == '__main__':
    
    print('\n')
    print('---------------------------------------------------')
    print('       ** Word2Vec Model Orchestration **          ')
    print('---------------------------------------------------')
    
    execute()