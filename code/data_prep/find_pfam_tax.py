import duckdb
import time

db_string = "/Users/patrick/dev/ucl/comp0158_mscproject/database/w2v_20240731_test.db"
con = duckdb.connect(database=db_string)      

#
# W2V_TOKEN is built from protein2ipr.dat whcih has more proteins listed than are in the eukaryotic proteins I used
# to create W2V_PROTEIN. Thus need to do the query from w2v_token 
#
'''
pfam_id = "PF00155"
results = con.execute("SELECT TOKEN, UNIPROT_ID FROM W2V_TOKEN WHERE TOKEN = (?) AND TYPE='PFAM'", [pfam_id]).fetchall()
for res in results:
    protein_id = res[1]
    print(f"protein {protein_id} res: {res}")
    # get tax id
    tax_ids = con.execute("SELECT TAX_ID FROM W2V_PROTEIN_UNIREF_100_ALL_TAX WHERE UNIPROT_ID = (?)", [protein_id]).fetchall()
    for tax_id in tax_ids:
        print('tax id:',tax_id[0])
        tax_names = con.execute("SELECT NAME, TAX_ID FROM W2V_TAX_NAME WHERE TAX_ID = (?)", ['tax_id']).fetchall()
        for tax_name in tax_names:
            print('>>>>>>>>>>>>tax name', tax_name)
con.close()
'''


# From DuckDB, select entries from W2V_TOKEN from a subset of proteins in W2V_PROTEIN
# LIMIT     = restrict amount of rows fetched
# OFFSET    = at which point to start reading results

# works
#results = con.execute("SELECT W2V_PROTEIN.*, W2V_TOKEN.* FROM ( SELECT UNIPROT_ID FROM W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT 10 OFFSET 0) AS W2V_PROTEIN INNER JOIN W2V_TOKEN AS W2V_TOKEN ON W2V_PROTEIN.UNIPROT_ID = W2V_TOKEN.UNIPROT_ID").fetchall()

# works to only return some rows from token
# results = con.execute("SELECT W2V_PROTEIN.*, W2V_TOKEN.TYPE, W2V_TOKEN.TOKEN FROM ( SELECT UNIPROT_ID FROM W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT 10 OFFSET 0) AS W2V_PROTEIN INNER JOIN W2V_TOKEN AS W2V_TOKEN ON W2V_PROTEIN.UNIPROT_ID = W2V_TOKEN.UNIPROT_ID").fetchall()

# this works and only returns pfam entries - 
#results = con.execute("SELECT W2V_PROTEIN.*, W2V_TOKEN.TYPE, W2V_TOKEN.TOKEN FROM ( SELECT UNIPROT_ID FROM W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT 10 OFFSET 0) AS W2V_PROTEIN INNER JOIN W2V_TOKEN AS W2V_TOKEN ON W2V_PROTEIN.UNIPROT_ID = W2V_TOKEN.UNIPROT_ID WHERE W2V_TOKEN.TYPE = 'PFAM' ").fetchall()


def find_tax_for_pfam():
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
    limit   = 10000    # how many rows to return

    # perform query
    s = time.time()
    results = con.execute(f"SELECT W2V_PROTEIN.*, W2V_TOKEN.TOKEN, W2V_TOKEN.START, W2V_TOKEN.END FROM ( SELECT UNIPROT_ID FROM W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT {limit} OFFSET {offset}) AS W2V_PROTEIN INNER JOIN W2V_TOKEN AS W2V_TOKEN ON W2V_PROTEIN.UNIPROT_ID = W2V_TOKEN.UNIPROT_ID WHERE W2V_TOKEN.TYPE = 'PFAM' ").fetchall()
    e1 = time.time()

    # print results
    for res in results:
        protein_id = res[0]
        pfam_id = res[1]
        #print(protein_id, pfam_id)
        
        # see if I can get the protein in UniRef
        tax_ids = con.execute("SELECT TAX_ID FROM W2V_PROTEIN_UNIREF_100_ALL_TAX WHERE UNIPROT_ID = (?)", [protein_id]).fetchall()
        for tax_id in tax_ids:
            #print(f"protein {protein_id} tax id: {tax_id[0]}")
            #tax_names = con.execute("SELECT NAME, TAX_ID FROM W2V_TAX_NAME WHERE TAX_ID = (?)", ['tax_id']).fetchall()
            # works
            # tax_names = con.execute("SELECT * FROM W2V_TAX_CAT WHERE ID = (?)", [tax_id[0]]).fetchall()
            # works
            tax_names = con.execute("SELECT * FROM W2V_TAX_NAME WHERE TAX_ID = (?)", [tax_id[0]]).fetchall()
            for tax_name in tax_names:
                print(f"Taxonomy name for pfam {pfam_id} associated with protein {protein_id} is {tax_name}")
        
    e2 = time.time()

    print(f"query {len(results)} took {e1-s}s, overall took {e2-s}s")

    con.close()
    
    




def find_tax_for_protein():
    print('find tax for protein')
    offset  = 0    # start point
    limit   = 5000000    # how many rows to return

    # perform query
    s = time.time()
    results = con.execute(f"SELECT W2V_PROTEIN.*, W2V_PROTEIN_UNIREF_100_ALL_TAX.TAX_ID FROM ( SELECT UNIPROT_ID FROM W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT {limit} OFFSET {offset}) AS W2V_PROTEIN INNER JOIN W2V_PROTEIN_UNIREF_100_ALL_TAX AS W2V_PROTEIN_UNIREF_100_ALL_TAX ON W2V_PROTEIN.UNIPROT_ID = W2V_PROTEIN_UNIREF_100_ALL_TAX.UNIPROT_ID ").fetchall()
    e1 = time.time()

    # print results
    for res in results:
        print(res)
        # get tax id for protein id
        
    e2 = time.time()

    print(f"query {len(results)} took {e1-s}s, overall took {e2-s}s")

    con.close()

    
    
    
    
    

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
find_tax_for_protein()
