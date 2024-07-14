import duckdb
import re
import csv
import xml.etree.ElementTree as ElementTree
import time
import os

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
import re
import xml.etree.ElementTree as ElementTree
import time

# grep -c "disorder_prediction\" dbname=\"MOBIDBLT\"" /Volumes/My\ Passport/downloads/extra.xml
# 57,013,227

#wc -l extra.xml
#4,007,237,378

def parse_extra_file():
    file        = "/Volumes/My Passport/downloads/extra.xml"
    output      = "/Users/patrick/dev/ucl/comp0158_mscproject/data/disordered/disordered_tokens_test.dat"
    
    file        = "/data/my_extra.xml"
    output      = "/data/disordered_tokens.dat"

    iteration_count = 0
    start_time      = time.time()
    mid_time_start  = time.time()
    first_line      = True
    
    output_file = open(output, "w")
    
    # get an iterable
    context = ElementTree.iterparse(file, events=("start", "end"))
    # turn it into an iterator
    context = iter(context)
    # get the root element
    event, root = next(context)
    #con = duckdb.connect(database=ProteinDB.db_string)


    ELEMENT_LIMIT   = -1  # elements in xml to parse
    OUTPUT_LIMIT    = 2000000   # number of elements how often to print a progress message
    BUFFER_SIZE     = 500       # number of dat entries before flushing
    
    protein_count       = 0
    element_count       = 0
    dat_record_count    = 0
    total_record_count  = 0
    output_buffer       = ""
    
    for event, protein in context:
        element_count +=1
        if event == "end" and protein.tag == "protein":
            protein_count += 1
            
            # look within the protein tag
            for match in protein:
                if 'MOBIDBLT' in match.attrib['dbname']:
                    for coords in match:
                        # get the entries for a single dat line
                        uniprot_id  = protein.attrib['id']
                        start       = coords.attrib['start']
                        end         = coords.attrib['end']
                        
                        dat_line = "|".join([uniprot_id, start, end])
                        output_buffer += dat_line + '\n'
                        
                        dat_record_count   += 1
                        total_record_count += 1
                        
                        if(dat_record_count % BUFFER_SIZE == 0):
                            output_file.write(output_buffer)
                            output_buffer = ""
                            dat_record_count = 0
        
        if (element_count % OUTPUT_LIMIT == 0):
            mid_time_end = time.time()
            exec_time = mid_time_end - mid_time_start
            mid_time_start = mid_time_end
            print(element_count,'elements processed', total_record_count, 'total entries found\t',total_record_count, 'time taken last batch:\t', round(exec_time,2), '\ttime to date:\t', round(mid_time_end - start_time,2))
                            
        if(ELEMENT_LIMIT != -1):
            if element_count >= ELEMENT_LIMIT:
                print(element_count, 'elements processed.', protein_count, 'proteins found. Total dat entries:', total_record_count, 'Current dat record count to flush:', dat_record_count)
                if(dat_record_count >0 ):
                    output_file.write(output_buffer)
                output_file.close()
                #con.close()
                print('*')
                root.clear()
                return
    output_file.close()
    #con.close()
    print('*')
    root.clear()
    
    
    
    
 
# --------------------------------------------
    
def parse_extra_files():
    root_folder = "/Volumes/My Passport/downloads/"
    
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file.startswith("extras_part_"):
                print(os.path.join(root, file))

#parse_extra_files()









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