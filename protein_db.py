import duckdb

class ProteinDB:
    db_string = "/Users/patrick/dev/ucl/comp0158_mscproject/database/proteins.db"
    
    def __init__(self):
        print('ProteinDB created at ', ProteinDB.db_string)
    
    
    def create_protein_table(self):
        #con = duckdb.connect(database=':memory:')
        con = duckdb.connect(database=ProteinDB.db_string)
        
        # protein sentence - comes from uniref100
        con.execute("\
            CREATE TABLE PROTEIN (\
                UNIPROT_ID VARCHAR,\
                SHORT_DESCRIPTION VARCHAR,\
                TAX_NAME VARCHAR,\
                TAX_ID VARCHAR,\
                DOM_TYPE VARCHAR,\
                REP_ID VARCHAR,\
                START_POS USMALLINT,\
                END_POS USMALLINT\
            )")
        
        result = con.execute("DESCRIBE PROTEIN")
        print(result)

        con.close()
    
    
    def create_protein_indices(self):
        con = duckdb.connect(database=ProteinDB.db_string)
        con.execute("CREATE INDEX PROT_ID_X ON PROTEIN(UNIPROT_ID)")
        con.close()
    
    def create_pfam_indices(self):
        con = duckdb.connect(database=ProteinDB.db_string)
        con.execute("CREATE INDEX WORD_PROT_ID_X ON PROTEIN_WORD(UNIPROT_ID)")
        con.close()
    
    
    # holds pfam and disordered regions
    def create_word_table(self):
        con = duckdb.connect(database=ProteinDB.db_string)
        # pfam and disordered entries
        con.execute("\
            CREATE TABLE PROTEIN_WORD (\
                UNIPROT_ID VARCHAR,\
                WORD_TYPE VARCHAR,\
                REF_ID VARCHAR,\
                REF_TXT VARCHAR,\
                START_POS USMALLINT,\
                END_POS USMALLINT\
            )")
        con.close()        
