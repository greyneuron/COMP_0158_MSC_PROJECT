import duckdb

class ProteinDB:
    def __init__(self):
        print('ProteinDB')
    
    
    def create_tables(self):
        # Connect in memory
        con = duckdb.connect(database=':memory:')

        # Create table
        duckdb.sql("\
            CREATE TABLE PROTEIN_SENTENCE (\
                UNIPROT_ID VARCHAR,\
                DESCRIPTION VARCHAR,\
                NAME VARCHAR,\
                TAX_ID VARCHAR,\
                TAX_DESCRIPTION VARCHAR\
            )")

        duckdb.sql("\
            CREATE TABLE PROTEIN_WORD (\
                UNIPROT_ID VARCHAR,\
                WORD_TYPE VARCHAR,\
                REF_ID VARCHAR,\
                REF_TXT VARCHAR,\
                START_POS USMALLINT,\
                END_POS USMALLINT\
            )")
        
        # Close the connection
        con.close()
        
    def describe_tables(self):
        result = duckdb.sql('DESCRIBE PROTEIN_SENTENCE')
        print(result)
        result = duckdb.sql('DESCRIBE PROTEIN_WORD')
        print(result)
        