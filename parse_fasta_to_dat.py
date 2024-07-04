from Bio import SeqIO
import re
import csv
import duckdb
import time

#
# Reads in a TrEMBL file and writes out only the important bits
# to a separate file that can be parsed again - but quicker
# Read the full file and created the output in 788s
# It then took only 12s to load the 78,494,529 records into the db 
#
def reduce_trembl_fasta(dom_type):
    #input        = "/Users/patrick/dev/ucl/comp0158_mscproject/data/uniprot/uniprotkb_100_test.fasta"
    #output      = "/Users/patrick/dev/ucl/comp0158_mscproject/data/uniprot/uniprotkb_100_test.dat"
    input        = "/Users/patrick/dev/ucl/comp0158_mscproject/data/uniprot/uniprotkb-2759_78494531.fasta"
    output      = "/Users/patrick/dev/ucl/comp0158_mscproject/data/uniprot/uniprotkb-2759_78494531_reduced.dat"
    
    #uniprot_re  = "UniRef100_([A-Z0-9]+)" # works for UniRef100
    #uniprot_re  = "tr|([A-Z0-9]+)|" # works for TrEMBL from UniRef
    rexp  = ">tr|([A-Z0-9]+)\|" # Works for TrEMBL 

    PROCESS_LIMIT   = -1 # number of lines to process, set to -1 to ignore
    OUTPUT_LIMIT    = 100000  # determines how often to print a progress message
    
    record_count = 0
    error_count = 0
    start_time = time.time()
    mid_time_start = time.time()
    line = ""
    
    output_file = open(output, "w")
    
    for record in SeqIO.parse(input, "fasta"):
        # extracts the id from the name
        #print(record.name)
        uniprot_res = re.search(rexp, record.name)
        uniprot_id  = uniprot_res.group(1)
        #print(uniprot_id)

        # -------- get length ------------
        start = 0
        end = 0
        for m in re.finditer(r'.{3,}', str(record.seq)):            # modified for UniRef100
            start = str(m.start()+1)
            end = str(m.end()+1)
        
        #print(uniprot_id, start, end)
        try:
            line = "|".join([uniprot_id, start, end]) +'\n'
            output_file.write(line)
            record_count += 1
        except:
            print('error parsing line', line)
            error_count += 1
            continue
        
        #print(line)
        #print('id %s start %s end %s ' % (uniprot_id, start, end))
        record_count += 1
        
       # -------- check for termination ------------
        if (record_count % OUTPUT_LIMIT == 0):
                mid_time_end = time.time()
                exec_time = mid_time_end - mid_time_start
                mid_time_start = mid_time_end
                print(OUTPUT_LIMIT, 'lines processed in ', exec_time, 's', '\ttotal :', record_count)
        
        if(PROCESS_LIMIT != -1):
            if record_count == PROCESS_LIMIT:
                break
        # ------------------------------------

    end_time = time.time()
    exec_time = end_time - start_time
    print('>>>', record_count, 'records processed in', exec_time, 's', 'error count:', error_count)


def load_fasta_dat_db():
    db_string = "/Users/patrick/dev/ucl/comp0158_mscproject/database/test.db"
    con = duckdb.connect(database=db_string)           
    con.execute("CREATE TABLE MY_UNIPROT_DATA AS SELECT * FROM read_csv_auto('/Users/patrick/dev/ucl/comp0158_mscproject/data/uniprot/uniprotkb-2759_78494531_reduced.dat', columns={'id' :'VARCHAR', 'start': 'USMALLINT', 'end': 'USMALLINT'})")
    description = con.execute("DESCRIBE MY_UNIPROT_DATA").fetchall()
    print(description)
    con.close()

def create_idx():
    
    
def count():
    db_string = "/Users/patrick/dev/ucl/comp0158_mscproject/database/test.db"
    con = duckdb.connect(database=db_string)        
    count = con.execute("SELECT COUNT(*) FROM MY_UNIPROT_DATA").fetchall()
    print(count)
    con.close()
 


#reduce_trembl_fasta("LowComplexity")
#parse_trembl_fasta(file, "CoiledCoil")
count()  
