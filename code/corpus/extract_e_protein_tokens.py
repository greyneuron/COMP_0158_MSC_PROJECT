import duckdb
import time

db_string = "/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/database/w2v_20240731_test.db"

#
# SEPTEMBER 10th - SIMPLIFIED THE ORIGINAL QUERY AND RE_GENERATED THE CORPUS AS A SANITY CHECK
#
# The original code is in data_preparation duck_db_data_loader
#



#output_file = "/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/corpus_validation_sep/uniref100_e_tokens_inner_join_20240910.dat"

#
# Executes an inner join on W2V_TOKEN and W2V_PROTEIN_UREF100_E to extract only tokens for eukaryotic proteins.
# It outputs one line per token/protein pair - so these need to be combined (see combine_e_protein_tokens.py)
#
def extract_eukaryotic_tokens_inner_join(start, end):
    s = time.time()
    of  = open(output_file, "a")
    con = duckdb.connect(database=db_string)
    
    try:
        # join wuery
        results = con.execute(f"SELECT T2.COUNTER, T2.LENGTH, T1.UNIPROT_ID, T1.TOKEN, T1.TYPE, T1.START, T1.END FROM W2V_TOKEN T1 INNER JOIN W2V_PROTEIN_UREF100_E T2 ON T1.UNIPROT_ID = T2.UNIPROT_ID WHERE T2.COUNTER >= {start} and T2.COUNTER <{end} ORDER BY T2.COUNTER").fetchall()
        
        # output results
        for res in results:
            buffer = "|".join( [ str(res[0]), str(res[1]), str(res[2]), str(res[3]), str(res[4]), str(res[5]), str(res[6]) ] )
            #print(buffer)
            of.write(buffer +'\n')
            
    except Exception as e:
        print(f"---------------> Error {e} between {start} and {end} positions., closing file {output_file}")
        of.close()
        con.close()
        return       
    
    # time check
    e = time.time()
    print(f"inner join query for entries from {start} to {end}, time: {round(e-s, 2)}s")

    of.close()
    con.close()

# There are 95,272,305 eukaryotic proteins - note that the the last 2 proteins have no tokens, thus the last counter in the output
# will have a counter of 95,272,302 corresponding to the protein Z4YNP1
#end_pos = 95272305
end_pos = 95272350
chunk   = 1000000

#
# run
#
for i in range (0, end_pos, chunk):
    extract_eukaryotic_tokens_inner_join(i, i+chunk)