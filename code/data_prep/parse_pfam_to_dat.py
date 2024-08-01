from Bio import SeqIO
import re
import csv
import time
import duckdb



#
# Reads a full protein2ipr file and writes only lines with pfam entries into a new dat
# file. The outputs include the uniprot id, the word 'PFAM', the PFAM id and the 
# start and end point of the pfam entry on the protein. The word 'PFAM" is included
# to distinguish it from the other tokens that will be processed - these will be identified
# by the word 'DISPORDER'.
#
# SAMPLE INPUT Many entries against A0A001:
'''
A0A001	IPR003439	ABC transporter-like, ATP-binding domain	PS50893	344	573
A0A001	IPR003593	AAA+ ATPase domain	SM00382	369	550
A0A001	IPR011527	ABC transporter type 1, transmembrane domain	PF00664	17	276
A0A001	IPR011527	ABC transporter type 1, transmembrane domain	PS50929	17	289
A0A001	IPR017871	ABC transporter-like, conserved site	PS00211	478	492
A0A001	IPR027417	P-loop containing nucleoside triphosphate hydrolase	G3DSA:3.40.50.300	341	573
A0A001	IPR027417	P-loop containing nucleoside triphosphate hydrolase	SSF52540	342	565
A0A001	IPR036640	ABC transporter type 1, transmembrane domain superfamily	G3DSA:1.20.1560.10	1	301
A0A001	IPR036640	ABC transporter type 1, transmembrane domain superfamily	SSF90123	3	300
A0A001	IPR039421	Type 1 protein exporter	PTHR24221	17	563
'''

# SAMPLE OUTPUT: Only list the PFAM rows
''' 
A0A001|PFAM|PF00664|17|276
'''
#
# Performance: 20240715.dat : 1,355,591,115 records processed in 1,3042s
#
# In order to test the file, set the PROCESS_LIMIT to 10 - and it will only process 10 entries
#
def parse_protein2ipr_pfam():
    path        = "/Volumes/My Passport/data/pfam/protein2ipr.dat"
    output      = "/Volumes/My Passport/data/pfam/protein2ipr_pfam_20240715_test.dat"
    
    uniprot_id  = ""
    output_file = open(output, "w")
    
    PROCESS_LIMIT   = 10         # total lines to process (-1 to ignore)
    OUTPUT_LIMIT    = 1000000    # how often to print

    
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
                
                output_line = "|".join([uniprot_id, 'PFAM', pfam_word, start, end]) + '\n'
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

parse_protein2ipr_pfam()


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
