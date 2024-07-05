from Bio import SeqIO
import re
import csv
import duckdb
import time

from collections import defaultdict

db_string = "/Users/patrick/dev/ucl/comp0158_mscproject/database/proteins.db"


def read_dat_file(path, dat):
    with open(path) as data:
        for line in data:
            entries = line.split(",")
            dat[entries[0]].append(line)
    return(dat)

#
# PARSE TREMBL FASTA AND LOOKUP PFAM ENTRIES - BASED UPON parse_tremble_fasta_old.py
#
def combine_tokens():
    fasta_dat   = "/Users/patrick/dev/ucl/comp0158_mscproject/data/uniprot/uniprotkb-2759_78494531_reduced.dat"
    pfam_dat    = "/Users/patrick/dev/ucl/comp0158_mscproject/data/pfam/pfam_entries_full.dat"
    output      = "/Users/patrick/dev/ucl/comp0158_mscproject/data/output_corpus.csv"
    
    #uniprot_re      = "tr\|([A-Z0-9]+)\|"
    
    PROCESS_LIMIT   = 10
    OUTPUT_LIMIT    = 10
    BUFFER_LIMIT    = 5000
    
    record_count    = 0
    buffer          = 0
    
    start_time = time.time()
    mid_time_start = time.time()
    
    # open a file for output
    output_file = open(output, "w")
    last_uniprot_id = ""
    
    #print('here 1')
    #accessions = defaultdict(list)
    #accessions = read_dat_file(fasta_dat, accessions)
    #print('here 2')
    
    chunk_size = 5
    counter = 0
    
    con = duckdb.connect(database=db_string) 
    
    with open(fasta_dat, 'r') as file:
        # iterate over each line in the file
        
        ids = []
        while counter < PROCESS_LIMIT:
            # Read a chunk of lines
            lines = [file.readline() for _ in range(chunk_size)]
            
            # Break if no more lines are read
            if not lines:
                break
        
            for line in lines:
                # Strip any leading/trailing whitespace (including newlines)
                line = line.strip()
            
                # Split the line into columns based on the '|' delimiter
                cols = line.split('|')
                ids.append(cols[0])
                print('looking up', cols[0])
                pfam_res = con.execute("SELECT * FROM PFAM_TOKEN WHERE column0 IN (?)", [cols[0]]).fetchall()
                print(cols[0], pfam_res)
                counter+=1
    
        #print('\nUniprot Ids (',len(ids), '):\n', ids)
    
        # look for pfam entries by id
        #db_start = time.time()
        #pfam_res = con.execute("SELECT * FROM PFAM_TOKEN WHERE column0 IN (?)", [['A0A010R6E0', 'A0A10RP22']]).fetchall()
        #db_end = time.time()
        #print('DB:', db_end - db_start)
    #output_line.joinuniprot_id
    
    
    '''
    # look for pfam entries by id
    db_start = time.time()
    pfam_res = con.execute("SELECT * FROM PFAM_TOKEN WHERE column0 = ?", [uniprot_id]).fetchall()
    db_end = time.time()
    print('DB:', db_end - db_start)
    #output_line.joinuniprot_id
    
    if pfam_res is not None:
        if len(pfam_res) >0:
            for item in pfam_res:
                #output_line = output_line + '|' + item[1]
                output_line.join([uniprot_id, '|', item[1]])
                #print(uniprot_id, item[1], item[2], item[3])
                #output_file.write(uniprot_id+','+item[1]+'\n')
            #output_line = output_line + '\n'
            output_line.join('\n')
    buffer +=1
        
        if buffer == BUFFER_LIMIT:
            #
            #print('flush....')          
            output_file.write(output_line)
            buffer = 0
            output_line = ""
        
        #con.execute("INSERT INTO PROTEIN (UNIPROT_ID, SHORT_DESCRIPTION, TAX_NAME, TAX_ID, DOM_TYPE, REP_ID, START_POS, END_POS) VALUES##(?,?,?,?,?,?,?,?)", (uniprot_id, short_desc, tax_name, tax_id, dom_type, rep_id, start, end))
        
        # -------- check for termination ------------
        if (record_count % OUTPUT_LIMIT == 0):
                mid_time_end = time.time()
                exec_time = mid_time_end - mid_time_start
                mid_time_start = mid_time_end
                print(record_count, 'lines processed in ', exec_time, 's')
        
        if(PROCESS_LIMIT != -1):
            if record_count >= PROCESS_LIMIT:
                print('Stopped at', PROCESS_LIMIT, 'last entry:', record.name)
                break
        # ------------------------------------
        
        record_count += 1
     
    con.close()
    output_file.close()
    
    end_time = time.time()
    exec_time = end_time - start_time
    print('Processed in ', exec_time, 's')

parse_trembl_fasta("LowComplexity")
#parse_trembl_fasta(file, "CoiledCoil")
'''

combine_tokens()