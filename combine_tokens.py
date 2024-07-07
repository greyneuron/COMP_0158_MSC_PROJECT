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
# PARSES FASTA DAT FILE AND LOOKUP PFAM TOKENS FROM DATABASE
#
# 100,000 lines in 92s - roughly 1.5 mins
# 1M lines `~= 15mins
# 10M lines ~= 150 mins = 2hr 30min
# 78M lines ~= 
def combine_tokens():
    fasta_dat   = "/Users/patrick/dev/ucl/comp0158_mscproject/data/uniprot/uniprotkb-2759_78494531_reduced.dat"
    pfam_dat    = "/Users/patrick/dev/ucl/comp0158_mscproject/data/pfam/protein2ipr_pfam.dat"
    db_string   = "/Users/patrick/dev/ucl/comp0158_mscproject/database/test.db"
    
    output      = "/Users/patrick/dev/ucl/comp0158_mscproject/data/corpus.dat"
    
    PROCESS_LIMIT   = 1000000
    OUTPUT_LIMIT    = 10000
    BUFFER_LIMIT    = 5000
    
    record_count    = 0
    buffer          = 0
    start_time      = time.time()
    mid_time_start  = time.time()
    
    # open a file for output
    output_file = open(output, "w")

    record_count = 0
    
    con = duckdb.connect(database=db_string) 
    
    with open(fasta_dat, 'r') as file:
        for line_number, line in enumerate(file):    
            cols        = line.split('|')
            #uniprot_id  = cols[0]
            
            output_line = cols[0] #uniprot_id
                
            #ids.append(cols[0])
            #print('looking up', uniprot_id)
            #pfam_res = con.execute("SELECT * FROM PFAM_TOKEN WHERE column0 IN (?)", [cols[0]]).fetchall()
            pfam_res = con.execute("SELECT * FROM PFAM_TOKEN WHERE UNIPROT_ID = (?)", [cols[0]]).fetchall()
                
            if pfam_res is not None:
                if len(pfam_res) >0:
                    for item in pfam_res:
                        output_line.join([cols[0], '|', item[1], '|',str(item[2]), '|', str(item[3])])
                        #print(uniprot_id, item[1], item[2], item[3])
                        #output_file.write(uniprot_id+','+item[1]+'\n')
                    #print(output_line)            
            output_file.write(output_line+'\n')
            #print(output_line)
            
            record_count += 1
                
            # -------- check for termination ------------
            if (record_count % OUTPUT_LIMIT == 0):
                mid_time_end = time.time()
                t = mid_time_end - mid_time_start
                mid_time_start = mid_time_end
                print(OUTPUT_LIMIT, 'lines processed in ', t, 's', 'total:', record_count)
                
            if(PROCESS_LIMIT != -1):
                if record_count == PROCESS_LIMIT:
                    break
                
    con.close()
    output_file.close()
    
    end_time = time.time()
    exec_time = end_time - start_time
    print(record_count, 'records processed in ', exec_time, 's')

#combine_tokens()


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

combine_tokens_db()



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
    fasta_dat   = "/Users/patrick/dev/ucl/comp0158_mscproject/data/uniprot/uniprotkb-2759_78494531_reduced.dat"
    pfam_dat    = "/Users/patrick/dev/ucl/comp0158_mscproject/data/pfam/protein2ipr_pfam.dat"
    
    output      = "/Users/patrick/dev/ucl/comp0158_mscproject/data/new_attempt.csv"
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
    
    with open(fasta_dat, 'r') as file:
        for line_number, line in enumerate(file):
            
            # using split
            cols        = line.split('|')
            uniprot_id  = cols[0]
            #print('searching for', uniprot_id)
                
            with open(pfam_dat, 'r') as pfam_file:
                for pf_line_number, pf_line in enumerate(pfam_file):
                    pf_cols = pf_line.split('\t')
                
                    #print(pf_cols[0])
                
                    if(pf_cols[0] == uniprot_id):
                        print(uniprot_id, ':', pf_line, '@', pf_line_number)
                        line = ":".join([uniprot_id, pf_line, '\n'])
                        output_file.write(line)
                        break
                
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

#combine_tokens_db()

#combine_tokens_db_2()
