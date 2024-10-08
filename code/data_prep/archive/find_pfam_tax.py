import duckdb
import time

db_string = "/Users/patrick/dev/ucl/comp0158_mscproject/database/w2v_20240731_test.db"
con = duckdb.connect(database=db_string)      


# From DuckDB, select entries from W2V_TOKEN from a subset of proteins in W2V_PROTEIN
# LIMIT     = restrict amount of rows fetched
# OFFSET    = at which point to start reading results

# works
#results = con.execute("SELECT W2V_PROTEIN.*, W2V_TOKEN.* FROM ( SELECT UNIPROT_ID FROM W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT 10 OFFSET 0) AS W2V_PROTEIN INNER JOIN W2V_TOKEN AS W2V_TOKEN ON W2V_PROTEIN.UNIPROT_ID = W2V_TOKEN.UNIPROT_ID").fetchall()

# works to only return some rows from token
# results = con.execute("SELECT W2V_PROTEIN.*, W2V_TOKEN.TYPE, W2V_TOKEN.TOKEN FROM ( SELECT UNIPROT_ID FROM W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT 10 OFFSET 0) AS W2V_PROTEIN INNER JOIN W2V_TOKEN AS W2V_TOKEN ON W2V_PROTEIN.UNIPROT_ID = W2V_TOKEN.UNIPROT_ID").fetchall()

# this works and only returns pfam entries - 
#results = con.execute("SELECT W2V_PROTEIN.*, W2V_TOKEN.TYPE, W2V_TOKEN.TOKEN FROM ( SELECT UNIPROT_ID FROM W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT 10 OFFSET 0) AS W2V_PROTEIN INNER JOIN W2V_TOKEN AS W2V_TOKEN ON W2V_PROTEIN.UNIPROT_ID = W2V_TOKEN.UNIPROT_ID WHERE W2V_TOKEN.TYPE = 'PFAM' ").fetchall()




# The table W2V_PROTEIN whcih was used to create the corpus was created from a TrEMBL extract of eukaryotic proteins. This format does not contain taxonomy informatoin
# The UniRef extract taken on August 3rd and 4th does and has been loaded into the  W2V_PROTEIN_UREF100_E table. This query creates a join across those tables 
# offset0 and limit of 500,000 took 54s for the query and  88s overall
#
# Really what is needed is to get the eukaryotic proteins and the pfam entries that correspond to those. Note that W2V_TOKEN is created from protein2ipr so that will have pfam entries

#
def find_tax_for_trembl_protein():
    print('find tax for protein')
    offset  = 0    # start point
    limit   = 5000000    # how many rows to return

    # perform query
    s = time.time()
    results = con.execute(f"SELECT W2V_PROTEIN.*, W2V_PROTEIN_UREF100_E.TAX_ID FROM ( SELECT UNIPROT_ID FROM W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT {limit} OFFSET {offset}) AS W2V_PROTEIN INNER JOIN W2V_PROTEIN_UREF100_E AS W2V_PROTEIN_UREF100_E ON W2V_PROTEIN.UNIPROT_ID = W2V_PROTEIN_UREF100_E.UNIPROT_ID ").fetchall()
    e1 = time.time()

    # print results
    for res in results:
        print(res)
        # get tax id for protein id
        
    e2 = time.time()

    print(f"query {len(results)} took {e1-s}s, overall took {e2-s}s")

    con.close()

    
    
    
    
    
#
# THis was just to test out various query formats for the join and get timings
#
def baseline_query():
    # THIS IS THE BEST QUERY
    # - TIMES ON MACBOOK
    # offset 0, limit 10 - took 4s
    # offset 0, limit 10,000 took 5s !
    # offset 0, limit 100,000 took 6s - overall took 7s to print out results
    # offset 0, limit 500,000 took 8.7s - overall took 12.5s

    # offset 100000, limit 10,000 took 5.45s and 5.25s
    # offset 100000, limit 100,000 took 7.8s and 8.65s
    # offset 100000, limit 500,000 took 10s and 14s

    offset  = 0    # start point
    limit   = 10    # how many rows to return

    s = time.time()
    results = con.execute(f"SELECT W2V_PROTEIN.*, W2V_TOKEN.TOKEN, W2V_TOKEN.START, W2V_TOKEN.END FROM ( SELECT UNIPROT_ID FROM W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT {limit} OFFSET {offset}) AS W2V_PROTEIN INNER JOIN W2V_TOKEN AS W2V_TOKEN ON W2V_PROTEIN.UNIPROT_ID = W2V_TOKEN.UNIPROT_ID WHERE W2V_TOKEN.TYPE = 'PFAM' ").fetchall()
    e1 = time.time()

    for res in results:
        print(res)
        # get tax id for protein id
        
    e2 = time.time()

    print(f"query {len(results)} took {e1-s}s, overall took {e2-s}s")

    con.close()
    
    
    

#baseline_query()
#find_tax_for_pfam()
find_tax_for_trembl_protein()
