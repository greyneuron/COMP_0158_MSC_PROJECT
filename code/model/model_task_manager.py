from model_tasks import W2V_ModelTasks
import sys
import argparse



def execute(model_tasks, model_type, model_dir, corpus_file):
    
    # config to create a model
    vector_size = 10
    window_size = 5
    min_count   = 1
    model_tasks.create_w2v_model(model_type, vector_size, window_size, min_count)

    
    
    


if __name__ == '__main__':
    
    mac_model_dir="/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/models/"
    mac_corpus_file="/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/corpus/uniref100_e_corpus_20240810.txt"
    
    ux_model_dir="/home/plowry/word2vec/data/models/"
    ux_corpus_file="/home/plowry/word2vec/data/models/corpus/uniref100_e_corpus_20240810.txt"
    
    CBOW = 0
    SKIP_GRAM = 1
    
    
    print('\n')
    print('---------------------------------------------------')
    print('       ** Word2Vec Model Task Manager **          ')
    print('---------------------------------------------------')
    
    parser = argparse.ArgumentParser(prog='Word2Vec Model Task Manager', description='Orchestrates the creation of word2vec models')
    
    parser.add_argument("--system", choices=['ux', 'mac'], help="system type to specify cospus file and model directories 'ux' for unix 'mc' for mac.", required=True)
    parser.add_argument("--mtype", choices=['cbow', 'skip'], help="Whether to use bag of words or skipgram", required=True)
    
    args = parser.parse_args()
    
    system  = args.system
    mtype   = args.mtype
    
    # sort out directories
    if 'ux' == system:
        model_dir = ux_model_dir
        corpus_file = ux_corpus_file
    elif 'mac' == system:
        model_dir = mac_model_dir
        corpus_file = mac_corpus_file
        
    # sort out model type
    if 'bag' == mtype:
        model_type = CBOW
    elif 'skip' == mtype:
        model_type = SKIP_GRAM
    
    print(f"running word2vec with model type {model_type} dir: {model_dir} corpus: {corpus_file}")

    model_tasks = W2V_ModelTasks(model_type, model_dir, corpus_file)
    
    execute(model_tasks, model_type, model_dir, corpus_file)