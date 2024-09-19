from datetime import datetime
import time
import numpy as np
import re
import duckdb
import requests
from gensim.models import Word2Vec
from w2v_evo_utils import *

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





# --------------------------------------------------------------------------------------------------------------------------
#                               Interpro calls
# --------------------------------------------------------------------------------------------------------------------------


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
# Query interpro for clan id associated with a pfam id. returns 'undef' if there is no match
#
def get_interpro_clans(pfam_ids, output_file):
    print(f"gettting {len(pfam_ids)}")
    for i, pfam_id in enumerate (pfam_ids):
        pfam_id_clean = pfam_id.strip().strip('"')
        clan_id       = get_interpro_clan(pfam_id_clean)
        clan_id_clean = clan_id.strip().strip('"')
        print(f"{i} | {pfam_id_clean} | {clan_id_clean}")
        output_file.write(f"{i}|{pfam_id_clean}|{clan_id_clean}\n")
    


# --------------------------------------------------------------------------------------------------------------------------
#                               W2V Model Stuff
# --------------------------------------------------------------------------------------------------------------------------


#
# extracts the words used in a word2vec model by querying the model itself
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
    return pfam_vocab


#
# given a model, extracts its vocab, calls interpro and writes pfam ids and clan ids to a file
#
def get_interpro_clans_for_model(model_path, output_file):
    pfam_ids = get_pfam_vocab(model_path)
    
    get_interpro_clans(pfam_ids, output_file)
    




# --------------------------------------------------------------------------------------------------------------------------
#                               W2V Model Stuff
# --------------------------------------------------------------------------------------------------------------------------


#
# For a model, this method gets all the pfam words in the model and then finds the clan id in the database
# if the pfam entry is not in the database, it will return only pfams that are in clans that have more
# than min_clan_size entries
#
def get_pfam_clans_for_model(model_name, model_path, min_clan_size):
    print(f"get_pfam_clans_for_model() {model_name}, {model_path}")
    min_count_s = re.search("(mc[0-9]+)_", model_name)
    min_count = min_count_s.group(1)
    
    # call to various tility methods
    vocab = get_pfam_vocab(model_path)
    print(f"{min_count}: Found {len(vocab)}, pfam words in {model_name}. items[0-10] {vocab[0:10]}")
    
    # see if there is an entry
    con = duckdb.connect(database=db_string)
    
    filtered_clans = []
    filtered_pfams = []
    clan_dict = {}
    filtered_clan_dict = {}
    
    # loop through each pfam, find its clan and build up a dictinary of clans > pfam_ids
    for pfam_id in vocab:
        try:          
            results = con.execute(f"SELECT CLAN_ID FROM W2V_PFAM_CLAN_MC1 WHERE PFAM_ID='{pfam_id}'").fetchall()
            
            # if no result, get from interpro
            if(results is None or results ==[]):
                clan_id = get_interpro_clan(pfam_id)
                print(f"----------> No local clan entry for {pfam_id}, queried interpro w/ result:{pfam_id}:{clan_id}")
                #con.execute(f"INSERT INTO W2V_PFAM_CLAN (PFAM_ID, CLAN_ID) VALUES ('{pfam_id}', '{clan_id}')")
            else:
                clan_id = results[0][0]
                if (clan_id != 'undef'):
                    #add clan id to dictionary
                    if clan_id in clan_dict:
                        clan_dict[clan_id].append(pfam_id)  # Append to the list if the key exists
                    else:
                        clan_dict[clan_id] = [pfam_id]
        except Exception as e:
            print('get_pfam_clans_for_model() error', e, results)
            con.close()
            return
    con.close()
    
    # get dictionary with only clans with more than one pfam
    filtered_clan_dict = {key:value for key, value in clan_dict.items() if len(value) >= min_clan_size}
    filtered_clans = list(filtered_clan_dict.keys())
    filtered_pfams = list(set([item for sublist in filtered_clan_dict.values() for item in sublist]))
    
    return filtered_pfams, filtered_clans, filtered_clan_dict

#
# 
# gets clans for a pfam entry but doesn't call INterpro if there are gaps
#
def get_pfam_clans_db(pfam_ids):
    con = duckdb.connect(database=db_string)
    
    clans = []
    
    # loop through each pfam, find its clan and build up a dictinary of clans > pfam_ids
    for i, pfam_id in enumerate(pfam_ids):
        try:          
            results = con.execute(f"SELECT CLAN_ID FROM W2V_PFAM_CLAN_EVO WHERE PFAM_ID='{pfam_id}'").fetchall()
            if(results is None or results ==[]):
                print(f"----------> No local clan entry for {pfam_id}")
            else:
                clan_id = results[0][0]
                if (clan_id != 'undef'):
                    clans.append(clan_id)
        except Exception as e:
            print('get_clans_for_pfams() error', e, results)
            con.close()
            return
    con.close()
    return clans
            
    

#
# Gets all the pfam words in an evolutionary vector that have a clan associated with them and then 
# finds the clan id in the database. Returns only pfams that are in clans that have more
# than min_clan_size entries
#
def get_pfam_clans_for_evo(pfam_ids, min_clan_size):
    # see if there is an entry
    con = duckdb.connect(database=db_string)
    
    filtered_clans = []
    filtered_pfams = []

    clan_dict = {}
    filtered_clan_dict = {}
    
    # loop through each pfam, find its clan and build up a dictinary of clans > pfam_ids
    for i, pfam_id in enumerate(pfam_ids):
        try:          
            results = con.execute(f"SELECT CLAN_ID FROM W2V_PFAM_CLAN_EVO WHERE PFAM_ID='{pfam_id}'").fetchall()
            
            # if no result, get from interpro
            if(results is None or results ==[]):
                clan_id = get_interpro_clan(pfam_id)
                print(f"----------> No local clan entry for {pfam_id}, queried interpro w/ result:{pfam_id}:{clan_id}")
                #clan_id = get_interpro_clan(pfam_id)
                #print(f"----------> Retreived :{clan_id}")
            else:
                clan_id = results[0][0]
                if (clan_id != 'undef'):
                    #add clan id to dictionary
                    if clan_id in clan_dict:
                        clan_dict[clan_id].append(pfam_id)  # Append to the list if the key exists
                    else:
                        clan_dict[clan_id] = [pfam_id]
                    # track the index of the pfam that meets the criteria
        except Exception as e:
            print('get_pfam_clans_for_evo() error', e, results)
            con.close()
            return
    con.close()
    
    # get dictionary with only clans with more than one pfam
    filtered_clan_dict = {key:value for key, value in clan_dict.items() if len(value) >= min_clan_size}
    # get list of clans
    filtered_clans = list(filtered_clan_dict.keys())
    # get list of pfams
    filtered_pfams = list(set([item for sublist in filtered_clan_dict.values() for item in sublist]))
    
    return filtered_pfams, filtered_clans, filtered_clan_dict





#
#
# Assumes clans are in the database
#
def get_clans_for_pfams(pfam_ids):
    con = duckdb.connect(database=db_string)
    clans = []
    
    # loop through each pfam, find its clan and build up a dictinary of clans > pfam_ids
    for pfam_id in pfam_ids:
        try:          
            results = con.execute(f"SELECT CLAN_ID FROM W2V_PFAM_CLAN_MC1 WHERE PFAM_ID='{pfam_id}'").fetchall()
            
            if(results is None or results ==[]):
                print(f"--------------------> No local clan entry for {pfam_id}, update needed.")
            else:
                clan_id = results[0][0]
                clans.append(clan_id)
        except Exception as e:
            print('get_clans_for_pfams() error', e, results)
            con.close()
            return
    con.close()
    return clans
    


# --------------------------------------------------------------------------------------------------------------------------
'''
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

'''


# --------------------------------------------------------------------------------------------------------------------------
#                               Database Creation Stuff
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
# creates and loads clan data into a table
#
def create_clan_table():
    con = duckdb.connect(database=db_string)
    try:          
        con.execute("CREATE TABLE W2V_PFAM_CLAN_MC1 AS SELECT * FROM read_csv('/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/data/clans/202409120909_w2v_mc1_pfam_clans.txt', delim='|', header='false', columns={'counter' : USMALLINT, 'pfam_id' :'VARCHAR', 'clan_id': 'VARCHAR'})")
        print('table created')
        con.execute("CREATE INDEX PF_CL_MC1_IDX ON W2V_PFAM_CLAN_MC1(PFAM_ID)")
        print('idx created')
        count = con.execute("SELECT COUNT(*) FROM W2V_PFAM_CLAN_MC1").fetchall()
        print(f"count items : {count}")
    except Exception as e:
        print('Error', e)
        con.close()
        return
    con.close()
    
'''
#
# creates and loads clan data into a table
#
def create_clan_count_tables():
    con = duckdb.connect(database=db_string)
    try:          
        #con.execute("CREATE TABLE W2V_CLAN_PFAM_COUNT AS SELECT * FROM read_csv('/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/data/clusters/pfam_counts_per_w2v_clan.txt', delim='|', header='false', columns={'clan_id' :'VARCHAR', 'count': 'USMALLINT'})")
        print('table W2V_CLAN_PFAM_COUNT created')
        con.execute("CREATE INDEX CL_CNT_IDX ON W2V_CLAN_PFAM_COUNT(CLAN_ID)")
        #print('idx created')
        count = con.execute("SELECT COUNT(*) FROM W2V_CLAN_PFAM_COUNT").fetchall()
        print(f"count items : {count}")
    except Exception as e:
        print('Error', e)
        con.close()
        return
    con.close()
    
    
#
# creates and loads clan data into a table
#
def get_clan_count(clan_id):
    con = duckdb.connect(database=db_string)
    try:          
        result = con.execute(f"SELECT COUNT FROM W2V_CLAN_PFAM_COUNT WHERE CLAN_ID ='{clan_id}'").fetchall()
        con.close()
        if result is None or result == []:
            return 0
        else:
            return result[0][0]
            
    except Exception as e:
        print('get_clan_count - error', e)
        con.close()
        return
    con.close()
'''

# --------------------------------------------------------------------------------------------------------------------------    

#
# run a general query
#
def execute_db_query():
    con = duckdb.connect(database=db_string)
    try:          
        #con.execute("DROP TABLE W2V_PFAM_CLAN")
        #con.execute("DROP INDEX PF_CL_IDX")
        results = con.execute("SELECT COUNT(*) FROM W2V_PFAM_CLAN WHERE CLAN_ID !='undef'").fetchall()
        #results = con.execute("SELECT CLAN_ID, COUNT(*) AS item_count FROM W2V_PFAM_CLAN GROUP BY CLAN_ID").fetchall()
        #print(results)
        #for res in results:
        #    print(f"{res[0]} | {res[1]}")
    except Exception as e:
        print('Error executing query :', e)
        con.close()
        return
    con.close()
    print('query executed')



# --------------------------------------------------------------------------------------------------------------------------


#
# main method
#
if __name__ == '__main__':
    
    model_dir   ="/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/data/models_validation_sep/"
    clan_dir    ="/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/data/clans/"
    evo_file    ="/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/data/distances/evo/rand_rep_distance_matrix.npy"
    
    #model_names=['w2v_20240910_sg1_mc1_w3_v5', 'w2v_20240910_sg1_mc3_w3_v5', 'w2v_20240910_sg1_mc8_w44_v5']
    #output_dir='/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/clusters/'
    

    print('\n---------------------------------------------------')
    print('             ** Word2Vec - Clan Utils      **      ')
    print('---------------------------------------------------\n')
    
    
    current_date    = datetime.now().strftime('%Y%m%d%H%m')
    s1 = time.time()
    
    # ---------------------------------------------------------------- get clans for evo matrices
    '''
    # get pfams that are in the evolutinary matrix/vector file
    clan_file = clan_dir+current_date+'_evo_pfam_clans.txt'
    evo_pfams = get_evo_pfams_from_npy(evo_file)
    cf = open(clan_file, 'w')
    get_interpro_clans(evo_pfams, cf)
    cf.close()
    '''
    
    # ---------------------------------------------------------------- get clans for w2v model
    '''
    model_file = model_dir+'w2v_20240911_sg1_mc1_w3_v5.model'
    w2v_clan_file = clan_dir+current_date+'_w2v_mc1_pfam_clans.txt'
    wcf = open(w2v_clan_file, 'w')
    get_interpro_clans_for_model(model_file, wcf )
    wcf.close()
    '''
    

    # ---------------------------------------------------------------- load clans into db
    '''
    # create tables holding clan ids for each pfam : W2V_PFAM_CLAN_MC1 and W2V_PFAM_CLAN_EVO
    # change the method to import the appropiate file
    create_clan_table()
    '''
    
    
 #execute_db_query()
    
    
    
    #clean_dat_file = clean_dat()
    #sniff_tables()
    #create_clan_tables()
    #create_clan_count_tables()
    
    #print(get_clan_count('CL0167'))
    
    #alter_clan_tables()
    #model_path = model_dir+model_name+'.model'
    #get_pfam_clans_for_model(model_name, model_path)
    #query_clan_tables()

    