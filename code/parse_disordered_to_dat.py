import duckdb
import re
import csv
import xml.etree.ElementTree as ElementTree
import time

#
# THIS WILL ERROR IF YOU ONLY USE A PARTIAL FILE
#

# This works directly on the uncompressed .gz file
# No space on laptop for fully extracted extra.xml
#

# Used this command to extract first 10000 lines into a separate file:
#
# zgrep . -m 10000 data/disordered/extra.xml.gz > data/disordered/extra.10000.xml
#



def create_table():
    db_string   = "/Users/patrick/dev/ucl/comp0158_mscproject/database/proteins.db"
    con = duckdb.connect(database=db_string) 
    con.execute("\
    CREATE TABLE DISORDER_TOKEN(\
        UNIPROT_ID VARCHAR,\
        START USMALLINT,\
        END USMALLINT")
    con.close()


#
#
#
def parse_extra_file():
    file        = "/Volumes/My Passport/downloads/extra.xml"
    output      = "/Users/patrick/dev/ucl/comp0158_mscproject/data/disordered/disordered_tokens.dat"

    PROCESS_LIMIT   = -1 # number of lines to process, set to -1 to ignore
    OUTPUT_LIMIT    = 1000000  # determines how often to print a progress message
    
    record_count    = 0
    entry_count     = 0
    start_time      = time.time()
    mid_time_start  = time.time()
    
    output_file = open(output, "w")
    
    # get an iterable
    context = ElementTree.iterparse(file, events=("start", "end"))
    # turn it into an iterator
    context = iter(context)
    # get the root element
    event, root = next(context)
    #con = duckdb.connect(database=ProteinDB.db_string)

    for event, protein in context:
        if event == "end" and protein.tag == "protein":
            # print(elem.attrib['id'])
            for match in protein:
                if 'MOBIDBLT' in match.attrib['dbname']:
                    for coords in match:
                        uniprot_id = protein.attrib['id']
                        word_type="DISORDER"
                        start = coords.attrib['start']
                        end = coords.attrib['end']
                        
                        output_line = "|".join([uniprot_id, start, end])
                        #print(output_line)
                        output_file.write(output_line +'\n')
                        record_count +=1
                        
                        '''
                        print(protein.attrib['id']+"\tIPRXXXXXX\t" +
                                match.attrib['name']+"\t"+match.attrib['id']+"\t" +
                                coords.attrib['start']+"\t"+coords.attrib['end'])
                        '''
                        #con.execute("INSERT INTO PROTEIN_WORD (UNIPROT_ID, WORD_TYPE, START_POS, END_POS) VALUES(?,?,?,?)", (uniprot_id, word_type, start_pos, end_pos))
        entry_count += 1
        if (entry_count % OUTPUT_LIMIT == 0):
            mid_time_end = time.time()
            exec_time = mid_time_end - mid_time_start
            mid_time_start = mid_time_end
            print(OUTPUT_LIMIT, 'lines processed total entries found :', record_count, 'time taken:', exec_time)
                    
    # exit()
    root.clear()
        #con.close()
        
#parse_extra_file()



# --------------------------------------------

# *************  DATABASE STUFF  *************

# --------------------------------------------

db_string = "/Users/patrick/dev/ucl/comp0158_mscproject/database/test.db"

# load csv (or pipe delimited file)
def load_disorder_dat_db():
    con = duckdb.connect(database=db_string)           
    con.execute("CREATE TABLE DISORDER_TOKEN AS SELECT * FROM read_csv_auto('/Users/patrick/dev/ucl/comp0158_mscproject/data/disordered/disordered_tokens.dat', columns={'uniprot_id' :'VARCHAR', 'start': 'USMALLINT', 'end': 'USMALLINT'})")
    description = con.execute("DESCRIBE DISORDER_TOKEN").fetchall()
    print(description)
    con.close()
#load_disorder_dat_db()

# check its there
def db_test():
    con = duckdb.connect(database=db_string)           
    count = con.execute("SELECT COUNT(*) FROM DISORDER_TOKEN").fetchall()
    print(count)
    con.close()
#db_test()

# apply index
def db_index():
    con = duckdb.connect(database=db_string)          
    res = con.execute("CREATE INDEX DS_TKN_IDX ON DISORDER_TOKEN(UNIPROT_ID)")
    print(res)
    con.close()
#db_index()

# run a query
def db_query():
    con = duckdb.connect(database=db_string)          
    res = con.execute("SELECT * FROM DISORDER_TOKEN WHERE UNIPROT_ID=(?)", ['A0A0T6ANQ5']).fetchall()
    print(res)
    con.close()
db_query()