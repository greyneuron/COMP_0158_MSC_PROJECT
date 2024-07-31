from Bio import SeqIO
import re
import csv
import duckdb
import time

# version update: tested again on July 31
#
# Reads in a TrEMBL file and writes out the key tokens to a tab delimited file:
#
# uniprot id | start |end
#
# The TrEMBL file was downloaded from Uniport and contains only eukaryotic proteins
# 
# On a mac, this read the full file and created the output in 788s
# It then took only 12s to load the 78,494,529 records into a local duck db instance (see duckdb_dat_loader.ipynb)
#
# In order to test the file, set the PROCESS_LIMIT to 10 - and it will only process 10 entries
#
def reduce_trembl_fasta(dom_type):
    #input        = "/Users/patrick/dev/ucl/comp0158_mscproject/data/uniprot/uniprotkb_100_test.fasta"
    #output      = "/Users/patrick/dev/ucl/comp0158_mscproject/data/uniprot/uniprotkb_100_test.dat"
    input        = "/Volumes/My Passport/data/protein/uniprot_trembl.fasta"
    output      = "/Volumes/My Passport/data/protein/uniprotkb-2759_78494531_20240714_test.dat"
    
    #uniprot_re  = "UniRef100_([A-Z0-9]+)"  # works for UniRef100
    #uniprot_re  = "tr|([A-Z0-9]+)|"        # works for TrEMBL from UniRef
    rexp  = ">tr|([A-Z0-9]+)\|"             # Works for TrEMBL 

    PROCESS_LIMIT   = 100                   # number of lines to process, set to -1 to ignore
    OUTPUT_LIMIT    = 100000                # determines how often to print a progress message
    
    record_count = 0
    error_count = 0
    start_time = time.time()
    mid_time_start = time.time()
    line = ""

    # -----------------
    print('parsing fasta into .dat file:', input)
    # -----------------
    
    output_file = open(output, "w")

    for record in SeqIO.parse(input, "fasta"):
        # extract id
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
        
        # create output file
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


# --------------------------------------------

# *************  MAIN  *************

# --------------------------------------------

reduce_trembl_fasta("LowComplexity")

