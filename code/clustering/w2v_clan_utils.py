from datetime import datetime
import time
import numpy as np
import re
import duckdb
import requests
from gensim.models import Word2Vec

#
# THis file contains a number of different functions to query clans and create a db table mapping
# pfam ids to clans
#


db_string = "/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/database/w2v_20240731_test.db"

model_dir="/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/models/best/"

#model_name="w2v_20240901_sg1_mc1_w44_v25"
#model_name="w2v_20240901_sg1_mc3_w44_v25"
#model_name="w2v_20240901_sg1_mc5_w44_v25"
model_name="w2v_20240903_sg1_mc8_w44_v25_best"

pfams_with_clans="/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/clusters/matched_pfam_clans.txt"

code_dir="/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/code/clustering"
output_dir='/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/clusters/'


#
# extracts the words used in a word2vec model by wuerying the model itself
# returns a list of words with any whitespace remoived as well as count of the umber of items
#       
def get_pfam_vocab(model_path):
    model = Word2Vec.load(model_path)
    
    vocab           = model.wv.key_to_index
    pfam_vocab    = []
    for i, word in enumerate(vocab):
        if (word == 'GAP' or word == 'START_GAP' or word == 'STOP_GAP' or word == 'DISORDER'):
            #print('ignoring', word)
            continue
        word = word.lstrip()
        word = word.rstrip()
        pfam_vocab.append(word)
    return pfam_vocab, len(pfam_vocab)

#
# Query interpro for clan id associated with a pfam id. returns 'undef' if there is no match
#
def get_interpro_clan(pfam_id):
    # Example URL
    url = "https://www.ebi.ac.uk/interpro/api/entry/pfam/"+pfam_id+"/"  # Replace with the actual URL

    response = requests.get(url)
    if response.status_code == 200:
        content = response.text

        # Search for the token in the content
        # set_info":{"accession":"CL0192","name":"GPCR_A"}
        #token_match = re.search("set_info\":\{\"(acc.*)on\"", content)
        token_match = re.search("set_info\":\{\"acc.*(CL[0-9]+)\"", content)

        if token_match:
            token = token_match.group(1)  # Extract the token
            #print(f"{pfam_id}:{token}:")
            return token
        else:
            return 'undef'
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return 'error'

    
#
# For a model, this method gets all the pfam words in the model and then finds the clan id in the database
# if the pfam entry is not in the database, it will query interpro and put the result into the db
#
def get_pfam_clans_for_model(model_name, model_path):
    min_count_s = re.search("(mc[0-9]+)_", model_name)
    min_count = min_count_s.group(1)
    # call to various tility methods
    vocab, vocab_count = get_pfam_vocab(model_path)
    
    print(f"{min_count}: Found {vocab_count}, pfam words in {model_name}. items[0-10] {vocab[0:10]}")
    
    # see if there is an entry
    con = duckdb.connect(database=db_string)
    for pfam_id in vocab:
        try:          
            results = con.execute(f"SELECT CLAN_ID, MC1, MC3, MC5, MC8 FROM W2V_PFAM_CLAN WHERE PFAM_ID='{pfam_id}'").fetchall()
            
            # if no result, get from interprot
            if(results ==[]):

                clan_id = get_interpro_clan(pfam_id)
                print(f"No local clan entry for {pfam_id}, queried interpro w/ result:{pfam_id}:{clan_id}")
                
                con.execute(f"INSERT INTO W2V_PFAM_CLAN (PFAM_ID, CLAN_ID) VALUES ('{pfam_id}', '{clan_id}')")
                
            #else:
            #    for res in results:
            #        print(res)
        except Exception as e:
            print('Error', e, results)
            con.close()
            return
    con.close()


# --------------------------------------------------------------------------------------------------------------------------

#
# one off method to clean up a previous list of clans - wasn;t sure if I'd removed all the whitespace etc
#
def clean_dat():
    dat_file = "/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/data/clusters/pfam_api_clan_results.txt"
    clean_dat_file = "/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/data/clusters/pfam_api_clan_results_clean.dat"
    
    of = open(clean_dat_file, "w")
    
    with open(dat_file, 'r') as file:
        for j, line in enumerate(file):
            #print(line.strip())  # Strip removes any extra newline characters
            tokens = line.split("|")
            for i, token in enumerate(tokens):
                if i>0:
                    of.write('|')
                word = token.strip().strip('"')
                #word = word.rstrip()
                #word = word.lstrip()
                if(word == "_with"):
                    word = "undef"
                #print(f"{j}:{i}:{word}:")
                of.write(word)
            of.write('\n')
    of.close()
    return(clean_dat_file)




# --------------------------------------------------------------------------------------------------------------------------

#
# check how duckdb would interpret a dat file
#
def sniff_tables():
    clean_dat_file = "/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/data/clusters/pfam_api_clan_results_clean.dat"
    con = duckdb.connect(database=db_string) 
    results = con.execute(f"SELECT Prompt FROM sniff_csv('{clean_dat_file}', delim='|')").fetchall()
    for res in results:
        print(res)


#
# add extra tables to the database - not really needed
#
def alter_clan_tables():
    con = duckdb.connect(database=db_string)
    try:          
        con.execute("ALTER TABLE W2V_PFAM_CLAN ADD COLUMN MC1 BOOLEAN default FALSE")
        con.execute("ALTER TABLE W2V_PFAM_CLAN ADD COLUMN MC3 BOOLEAN default FALSE")
        con.execute("ALTER TABLE W2V_PFAM_CLAN ADD COLUMN MC5 BOOLEAN default FALSE")
        con.execute("ALTER TABLE W2V_PFAM_CLAN ADD COLUMN MC8 BOOLEAN default FALSE")
        res = con.execute("DESCRIBE W2V_PFAM_CLAN").fetchall()
        print(res)
    except Exception as e:
        print('Error adding columns', e)
        con.close()
        return
    con.close()


#
# creates and loads clan data into a table
#
def create_clan_tables():
    con = duckdb.connect(database=db_string)
    try:          
        #con.execute("CREATE TABLE W2V_PFAM_CLAN AS SELECT * FROM read_csv('/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/data/clusters/pfam_api_clan_results_clean.dat', delim='|', header='false', columns={'pfam_id' :'VARCHAR', 'clan_id': 'VARCHAR'})")
        #print('table created')
        #con.execute("CREATE INDEX PF_CL_IDX ON W2V_PFAM_CLAN(PFAM_ID)")
        #print('idx created')
        count = con.execute("SELECT COUNT(*) FROM W2V_PFAM_CLAN").fetchall()
        print(f"count items : {count}")
    except Exception as e:
        print('Error', e)
        con.close()
        return
    con.close()
    
    
# --------------------------------------------------------------------------------------------------------------------------    

#
# runa general query
#
def query_clan_tables():
    con = duckdb.connect(database=db_string)
    try:          
        results = con.execute("SELECT COUNT(*) FROM W2V_PFAM_CLAN WHERE CLAN_ID !='undef'").fetchall()
        #results = con.execute("SELECT CLAN_ID, COUNT(*) AS item_count FROM W2V_PFAM_CLAN GROUP BY CLAN_ID").fetchall()
        print(results)
        #for res in results:
        #    print(f"{res[0]} | {res[1]}")
    except Exception as e:
        print('Error', e)
        con.close()
        return
    con.close()



# --------------------------------------------------------------------------------------------------------------------------


#
# main method
#
if __name__ == '__main__':
    
    model_dir="/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/models/best/"
    model_names=['w2v_20240901_sg1_mc1_w44_v25', 'w2v_20240901_sg1_mc3_w44_v25', 'w2v_20240901_sg1_mc5_w44_v25', 'w2v_20240903_sg1_mc8_w44_v25_best']
    output_dir='/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/clusters/'
    
    current_date    = datetime.now().strftime('%Y%m%d')
    s1 = time.time()
    
    print('\n')
    print('---------------------------------------------------')
    print('             ** Word2Vec - Cluster Tools   **      ')
    print('---------------------------------------------------\n')
    
    
    #clean_dat_file = clean_dat()
    #sniff_tables()
    #create_clan_tables()
    #alter_clan_tables()
    #model_path = model_dir+model_name+'.model'
    #get_pfam_clans_for_model(model_name, model_path)
    
    
    query_clan_tables()

    