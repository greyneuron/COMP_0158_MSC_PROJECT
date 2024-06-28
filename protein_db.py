import duckdb

class ProteinDB:
    db_string = "/Users/patrick/dev/ucl/comp0158_mscproject/database/proteins.db"
    
    def __init__(self):
        print('ProteinDB')
    
    
    def create_tables(self):
        # Connect in memory
        
        #con = duckdb.connect(database=':memory:')
        con = duckdb.connect(database=ProteinDB.db_string)
        
        
        # protein sentence
        con.execute("\
            CREATE TABLE PROTEIN_SENTENCE (\
                UNIPROT_ID VARCHAR,\
                IPR VARCHAR,\
                DESCRIPTION VARCHAR,\
                TAX_NAME VARCHAR,\
                TAX_ID VARCHAR,\
                DOM_TYPE VARCHAR,\
                START_POS USMALLINT,\
                END_POS USMALLINT\
            )")

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

        # close the connection
        con.close()        
    
    def create_indexes(self):
        con = duckdb.connect(database=ProteinDB.db_string)
        con.execute("CREATE INDEX w_protid_idx ON PROTEIN_WORD(UNIPROT_ID)")
        con.execute("CREATE INDEX w_refid_idx ON PROTEIN_WORD(REF_ID)")
        con.execute("CREATE INDEX p_protid_idx ON PROTEIN_SENTENCE(UNIPROT_ID)")
        con.close()
        
    def describe_tables(self):
        con = duckdb.connect(database=ProteinDB.db_string)
        result = con.execute("DESCRIBE PROTEIN_SENTENCE")
        print(result)
        result = con.execute("DESCRIBE PROTEIN_WORD")
        print(result)
        con.close()