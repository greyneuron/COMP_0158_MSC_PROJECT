from Bio import SeqIO
import re
import csv
import duckdb
import time

# internal representation
from protein_db import ProteinDB

pdb = ProteinDB()

#
# PARSE TREMBL FASTA AND LOOKUP PFAM ENTRIES
#
# 0.8s per 1000 lines - 82s for 100k
# 10k lines ~= 7 to 8s
# 100k lines ~= 70s
# 1M took ~= 669s

# thus 78M ~= 780 min = 10hrs

def parse_trembl_fasta(dom_type):
    path            = "/Users/patrick/dev/ucl/comp0158_mscproject/data/uniprot/uniprot_trembl_10M.fasta"
    output          = "/Users/patrick/dev/ucl/comp0158_mscproject/data/small_output_corpus.csv"
    uniprot_re      = "tr\|([A-Z0-9]+)\|"
    
    PROCESS_LIMIT   = 1000000
    OUTPUT_LIMIT    = 100000
    BUFFER_LIMIT    = 5000
    
    con = duckdb.connect(database=ProteinDB.db_string) 
    
    record_count    = 0
    buffer          = 0
    
    start_time = time.time()
    mid_time_start = time.time()
    
    # loop through the fasta file
    output_file = open(output, "w")
    last_uniprot_id = ""
    output_line = "Word2vec" + str(start_time)
    
    for record in SeqIO.parse(path, "fasta"):
        
        result      = re.search(uniprot_re, record.name)
        uniprot_id  = result.group(1)
        
        # look for pfam entries by id
        #db_start = time.time()
        pfam_res = con.execute("SELECT * FROM PFAM_TOKEN WHERE column0 = ?", [uniprot_id]).fetchall()
        #db_end = time.time()
        #print('DB:', db_end - db_start)
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