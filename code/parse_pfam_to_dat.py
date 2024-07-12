from Bio import SeqIO
import re
import csv
import time
import duckdb

PROCESS_LIMIT   = -1   # total lines to process (-1 to ignore)
OUTPUT_LIMIT    = 100000    # how often to print


#
# Reads a full protein2ipr file and outputs only lines with pfam entries
#
# Writes about 100k lines every 1.2s
# Took 16454s to process 1,355,591,115 records
#
def parse_protein2ipr_pfam():
    path        = "/Users/patrick/dev/ucl/comp0158_mscproject/data/pfam/protein2ipr.dat"
    output      = "/Users/patrick/dev/ucl/comp0158_mscproject/data/pfam/protein2ipr_pfam.dat"
    
    uniprot_id  = ""
    output_file = open(output, "w")
    
    record_count    = 0
    start_time      = time.time()
    mid_time_start  = time.time()
    
    with open(path, 'r') as input_file:
        for line_number, line in enumerate(input_file):
            
            output_line = ""
            match = re.search("([A0A0-9]*[a-zA-Z0-9]+)\\tIPR[0-9]+\\t.*\\t(PF[0-9]+)\\t([0-9]+)\\t([0-9]+)", line)

            if match is not None:
                uniprot_id  = match.group(1)
                pfam_word   = match.group(2)
                start       = match.group(3)
                end         = match.group(4)
                
                output_line = "|".join([uniprot_id, pfam_word, start, end]) + '\n'
                output_file.write(output_line)
                
            #print('input:', line)
            #print('output:', output_line)
            
            record_count += 1
            
            # -------- check for termination -----
            if (record_count % OUTPUT_LIMIT == 0):
                mid_time_end = time.time()
                exec_time = mid_time_end - mid_time_start
                mid_time_start = mid_time_end
                print(OUTPUT_LIMIT, 'lines processed in ', exec_time, 's', '\ttotal :', record_count)
            if(PROCESS_LIMIT != -1):
                if record_count == PROCESS_LIMIT:
                    break
            # ------------------------------------  
            
    output_file.close()
    end_time = time.time()
    exec_time = end_time - start_time
    print('>>>', record_count, 'records processed in', exec_time, 's')    

#parse_protein2ipr_pfam()


# --------------------------------------------

# *************  DATABASE STUFF  *************

# --------------------------------------------

# load data
def load_pfam_dat_db():
    db_string = "/Users/patrick/dev/ucl/comp0158_mscproject/database/test.db"
    
    con = duckdb.connect(database=db_string)           
    con.execute("CREATE TABLE PFAM_TOKEN AS SELECT * FROM read_csv_auto('/Users/patrick/dev/ucl/comp0158_mscproject/data/pfam/protein2ipr_pfam.dat', columns={'uniprot_id' :'VARCHAR', 'token' : 'VARCHAR', 'start': 'USMALLINT', 'end': 'USMALLINT'})")
    description = con.execute("DESCRIBE MY_UNIPROT_DATA").fetchall()
    print(description)
    con.close()
#load_pfam_dat_db()

# check its there
def db_test():
    db_string = "/Users/patrick/dev/ucl/comp0158_mscproject/database/test.db"
    
    con = duckdb.connect(database=db_string)           
    count = con.execute("SELECT COUNT(*) FROM PFAM_TOKEN").fetchall()
    print(count)
    con.close()
#db_test()

# apply index
def db_index():
    db_string = "/Users/patrick/dev/ucl/comp0158_mscproject/database/test.db"
    
    con = duckdb.connect(database=db_string)
    s   = time.time()           
    res = con.execute("CREATE INDEX PF_TKN_IDX ON PFAM_TOKEN(UNIPROT_ID)")
    
    print(res)
    print('time:', time.time() - s,'s')
    con.close()
#db_index()


def db_query():
    db_string = "/Users/patrick/dev/ucl/comp0158_mscproject/database/test.db"
    
    con = duckdb.connect(database=db_string)
    s   = time.time()           
    res = con.execute("SELECT * FROM PFAM_TOKEN WHERE UNIPROT_ID=(?)", ['X8JK18']).fetchall()
    
    print(res)
    print('time:', time.time() - s,'s')
    con.close()
#db_query()
