from code.model.model_tasks import W2V_ModelTasks

def get_model_tasks(model_dir, vocab_dir):
    model_tasks = W2V_ModelTasks(model_dir, corpus_file)
    return model_tasks

def execute():
    model_dir="/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/models/"
    corpus_file="/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/corpus/uniref100_e_corpus_20240810.txt"
    
    # get an instance of model tools
    model_tasks = get_model_tasks(model_dir, corpus_file)
    
    # config to create a model
    vector_size = 10
    window_size = 5
    min_count   = 1
    model_tasks.create_w2v_model(vector_size, window_size, min_count)

    
    
    


if __name__ == '__main__':
    
    print('\n')
    print('---------------------------------------------------')
    print('       ** Word2Vec Model Task Manager **          ')
    print('---------------------------------------------------')
    
    execute()