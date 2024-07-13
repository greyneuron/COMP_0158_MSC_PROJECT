from Bio import SeqIO
import re
import csv
import duckdb
import time

from collections import defaultdict 


# ----------------------------------
# pfam entries  : 298,766,058
# proteins      : 78,494,529
# ----------------------------------


#
# PARSES FASTA DAT FILE AND LOOKS UP PFAM TOKENS FROM DATABASE
#
# 100,000 lines took 73s - 77s
# 500,000 lines took 376s (6min 16s) and resulted in 331,278 entries
# 1M lines  ~= 750s = 12.5 min
# 10M lines ~= 125mins = 2hr 5min
# 78M lines ~= 16hr
def combine_tokens():
    protein_dat   = "/Users/patrick/dev/ucl/comp0158_mscproject/data/uniprot/proteins_ordered.dat"
    pfam_dat    = "/Users/patrick/dev/ucl/comp0158_mscproject/data/pfam/protein2ipr_pfam.dat"
    db_string   = "/Users/patrick/dev/ucl/comp0158_mscproject/database/test.db"
    
    output      = "/Users/patrick/dev/ucl/comp0158_mscproject/data/corpus/protein_pfam_corpus.dat"
    
    PROCESS_LIMIT   = 100
    OUTPUT_LIMIT    = 10
    
    record_count    = 0
    buffer          = 0
    start_time      = time.time()
    mid_time_start  = time.time()
    
    # open a file for output
    output_file = open(output, "w")

    record_count = 0
    
    con = duckdb.connect(database=db_string) 
    
    with open(protein_dat, 'r') as file:
        for line_number, line in enumerate(file):    
            cols            = line.split('|')
            protein_id      = cols[0]
            last_pfam_protein_id = ""
            pfam_line       = ""
            
            # get pfam tokens from db
            pfam_tokens = con.execute("SELECT * FROM PFAM_TOKEN WHERE UNIPROT_ID = (?)", [protein_id]).fetchall()
                
            if pfam_tokens is not None and len(pfam_tokens) >0:
                for item in pfam_tokens:
                    pfam_protein_id = item[0]
                    
                    # if this is first time, remember what protein we have found
                    # and create first part of output line, 
                    if(last_pfam_protein_id == ""):
                        last_pfam_protein_id = pfam_protein_id
                        pfam_line = pfam_protein_id + '|' + item[1] + ':' + str(item[2]) +  ':' + str(item[3])
                        continue
                    
                    # if not first time through and we have already found this protein, append to line
                    if (pfam_protein_id == last_pfam_protein_id):
                        pfam_line_extra = '|' + item[1] + ':' + str(item[2]) + ':' + str(item[3])
                        pfam_line = pfam_line + pfam_line_extra
                    
                    # if not first time and we have a new protein, then print the current line and start a new one
                    else:
                        last_pfam_protein_id = pfam_protein_id
                        pfam_line = pfam_protein_id + '|' + item[1] + ':' + str(item[2]) +  ':' + str(item[3])
                # write out current line
                #print(pfam_line)
                output_file.write(pfam_line +'\n')
            record_count += 1
                
            # -------- check for termination ------------
            if (record_count % OUTPUT_LIMIT == 0):
                mid_time_end = time.time()
                t = mid_time_end - mid_time_start
                mid_time_start = mid_time_end
                print(OUTPUT_LIMIT, 'lines processed in ', t, 's', 'total:', record_count)
                
            if(PROCESS_LIMIT != -1):
                if record_count >= PROCESS_LIMIT:
                    print('limit reached, returning')
                    break
                
    con.close()
    output_file.close()
    
    end_time = time.time()
    exec_time = end_time - start_time
    print(record_count, 'proteins processed in ', exec_time, 's')

combine_tokens()













# ----------------------------------


#
# LOOKUP IN DATABASE
#
def combine_tokens_db():
    print('combine via db')
    output      = "/Users/patrick/dev/ucl/comp0158_mscproject/data/output_db_.dat"
    db_string   = "/Users/patrick/dev/ucl/comp0158_mscproject/database/test.db"
    
    PROCESS_LIMIT   = 1000
    OUTPUT_LIMIT    = 100
    
    record_count    = 0
    start_time      = time.time()
    mid_time_start  = time.time()
    
    # open a file for output
    output_file = open(output, "w")
    last_uniprot_id = ""
    record_count = 0
    
    # get proteins - this takes 106s with an ORDER BY clause (100s without)
    # 10 pfam lookups finished in 112s (106s without)
    con = duckdb.connect(database=db_string)
    s = time.time()
    #proteins = con.execute("SELECT * FROM MY_UNIPROT_DATA ORDER BY ID ASC").fetchall()
    proteins = con.execute("SELECT * FROM MY_UNIPROT_DATA").fetchall()
    e = time.time()
    print('protein search complete in (s):', e-s)
    
    for i in range(10):
        uniprot_id = proteins[i][0]
        print(proteins[i])
        pfam_res = con.execute("SELECT * FROM PFAM_TOKEN WHERE UNIPROT_ID = (?)", [uniprot_id]).fetchall()
        print(pfam_res)
        record_count +=1
        
    con.close()
    end_time = time.time()
    exec_time = end_time - start_time
    print(record_count, 'records processed in ', exec_time, 's')   

#combine_tokens_db()



# ------------------------------------------------------------------------------------


def read_dat_file(path, dat):
    with open(path) as data:
        for line in data:
            entries = line.split("\t")
            dat[entries[0]].append(line)
    return(dat)

def combine_tokens_dat_2_dat():
    fasta_dat   = "/Users/patrick/dev/ucl/comp0158_mscproject/data/uniprot/uniprotkb-2759_78494531_reduced.dat"
    pfam_dat    = "/Users/patrick/dev/ucl/comp0158_mscproject/data/pfam/pfam_entries_full.dat"
    output      = "/Users/patrick/dev/ucl/comp0158_mscproject/data/output_corpus.csv"

    accessions = defaultdict(list)
    
    print('combination dat2dat search')
    s = time.time()
    accessions = read_dat_file(fasta_dat, accessions)
    print('have proteins in', time.time() - s, 's')

#combine_tokens_dat_2_dat()



# ----------------------------------



#
# NOT FINISHED - IF FILES WERE ORDERED I COULD START AT LAST FIND POSITION
#
def search_ordered():
    fasta_dat   = "/Users/patrick/dev/ucl/comp0158_mscproject/data/uniprot/proteins_ordered.dat"
    pfam_dat    = "/Users/patrick/dev/ucl/comp0158_mscproject/data/pfam/protein2ipr_pfam.dat"
    
    output      = "/Users/patrick/dev/ucl/comp0158_mscproject/data/combined_ordered_search.csv"
    db_string   = "/Users/patrick/dev/ucl/comp0158_mscproject/database/proteins.db"
    
    PROCESS_LIMIT   = 10000
    OUTPUT_LIMIT    = 100
    
    record_count    = 0
    start_time      = time.time()
    mid_time_start  = time.time()
    
    # open a file for output
    output_file = open(output, "w")
    last_uniprot_id = ""
    record_count = 0
    
    last_pfam_match = 0
    last_protein_match = ""
    match = False
    
    with open(fasta_dat, 'r') as file:
        for line_number, line in enumerate(file):
            
            # using split
            cols        = line.split('|')
            uniprot_id  = cols[0]
                
            with open(pfam_dat, 'r') as pfam_file:
                for pf_line_number, pf_line in enumerate(pfam_file):
                    
                    pf_cols = pf_line.split('|')
                    current_id = pf_cols[0]
                    
                    if(current_id == uniprot_id):    
                        match = True
                        if not (current_id == last_protein_match): # if this is a new match
                            print('found new match for:', uniprot_id, ':', 'protein line # :', line_number, 'pfam line #:', pf_line_number, 'pfam line:', pf_line)
                            last_protein_match = current_id
                            break
                        else:
                            print('found + match  for:', uniprot_id, ':', 'protein line # :', line_number, 'pfam line #:', pf_line_number, 'pfam line:', pf_line)
                            break
                            
                        
                        #last_protein_match = pf_cols[0]
                        #last_match_line = pf_line_number
                        
                        #print('found:', uniprot_id, ':', 'protein line # :', line_number, 'pfam line #:', pf_line_number, 'pfam line:', pf_line)
                        
                        
                        #line = ":".join([uniprot_id, pf_line, '\n'])
                        #output_file.write(line)
                        break
                    else:
                        match = False
                
            record_count += 1
            # -------- check for termination ------------
            if (record_count % OUTPUT_LIMIT == 0):
                    mid_time_end = time.time()
                    t = mid_time_end - mid_time_start
                    mid_time_start = mid_time_end
                    print(OUTPUT_LIMIT, 'lines processed in ', t, 's', 'total:', record_count)
            if(PROCESS_LIMIT != -1):
                if record_count >= PROCESS_LIMIT:
                    print('Stopped at', PROCESS_LIMIT)
                    break
#search_ordered()

