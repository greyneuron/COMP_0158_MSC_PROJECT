from Bio import SeqIO
import re
import csv
import duckdb
import time

# version update: tested again on August 1st to extract taxonomy id
#
# Reads in a UniRef file and writes out the key tokens to a tab delimited file, unlike the TrEMBL
# file I used, the full UniRef100 file doesn't have only eukaryotic proteins.
#
# ---------------------------------------------------------------------------
# 
# Full Uniref100 file : /Volumes/My Passport/data/protein/uniref100.fasta
#
# This UniRef100 file has 408,368,587 entries (compared to 78,494,529 in TrEMBL)
#
# Output format: uniprot id | start | end | taxonomy id
# 
# 01/08/2024 : On a macbook, this took on average 11s to parse 1M lines
# 01/08/2024 : On a macbook, this took on average 11s to parse 1M lines
# 01/08/2024 : Final lines of output showing 408,368,587 entries in 4,387s
#
# 1000000 lines processed in  10.067269086837769 s 	total : 408000000
# >>> 408368587 records processed in 4387.462231874466 s error count: 0
#
# Instructions - 
# Set the directory and file name for input and output,
# To test the scropt, set the PROCESS_LIMIT to 10 - and it will only process 10 entries
# Otherwise set it to -1 to process eerything
#
# ---------------------------------------------------------------------------
#
# I subsequently found out that it is possible to download eukaryotic proteins only from uniprot
# The taxonomy id to filter upon is 2759. This file can then be downloaded 
# https://www.uniprot.org/uniref?query=%28taxonomy_id%3A2759%29
#
#
# According to the uniprot site, this will have 95,272,305 entries
# 95,272,305 records processed in 1404.2241990566254 s error count: 0
#
# output: 
# line = "|".join([source, uniprot_id, str(len), str(start), str(end), n_members, str(tax_id), str(tax_name)])
#
# ---------------------------------------------------------------------------
#

''' Sample UniRef100 Entry
>UniRef100_Q6GZX4 Putative transcription factor 001R n=4 Tax=Ranavirus TaxID=10492 RepID=001R_FRG3G
MAFSAEDVLKEYDRRRRMEALLLSLYYPNDRKLLDYKEWSPPRVQVECPKAPVEWNNPPS
EKGLIVGHFSGIKYKGEKAQASEVDVNKMCCWVSKFKDAMRRYQGIQTCKIPGKVLSDLD
AKIKAYNLTVEGVEGFVRYSRVTKQHVAAFLKELRHSKQYENVNLIHYILTDKRVDIQHL
EKDLVKDFKALVESAHRMRQGHMINVKYILYQLLKKHGHGPDGPDILTVKTGSKGVLYDD
SFRKIYTDLGWKFTPL
'''
def reduce_uniref_fasta(dom_type):
    input        = "/Users/patrick/dev/ucl/comp0158_mscproject/data/protein/uniref_100only_2759-95272305_0804.fasta" # note that this file has loads of 90% entries
    #input        = "/Volumes/My Passport/data/protein/uniref100.fasta"
    output      = "uniref100only_2759-95272305_20240804_2.dat"
    
    # define regular expressions for UniRef format
    source_re           = "^(UniRef[0-9]*)_"
    uniprot_re          = "UniRef[0-9]*_([A-Z0-9]+)"
    taxonomy_id_re      = "TaxID=([0-9]+)"
    taxonomy_name_re    = "Tax=(.*) TaxID="
    members_re          = "n=([0-9]+)"

    PROCESS_LIMIT   = -1             # number of lines to process, set to -1 to ignore
    OUTPUT_LIMIT    = 1000000                # determines how often to print a progress message
    
    record_count = 0
    error_count = 0
    start_time = time.time()
    mid_time_start = time.time()
    line = ""

    # -----------------
    print('parsing uniref fasta into .dat file:', input)
    # -----------------
    
    output_file = open(output, "w")

    for record in SeqIO.parse(input, "fasta"):
        
        #print(record)
        #print(record.description)
        
        
        # extract protein id and taxonomy id
        source_res  = re.search(source_re, record.name)
        source      = source_res.group(1)
        
        member_res = re.search(members_re, record.description)
        if member_res is not None:
            n_members = member_res.group(1)
        else:
            n_members = 999999999
        
        
        uniprot_res = re.search(uniprot_re, record.name)
        uniprot_id  = uniprot_res.group(1)
        
        taxonomy_id_res = re.search(taxonomy_id_re, record.description)
        if taxonomy_id_res is not None:
            tax_id = taxonomy_id_res.group(1)
        else:
            #print(f"No Taxonomy id {record.description}")
            tax_id = 999999999
        
        taxonomy_name_res = re.search(taxonomy_name_re, record.description)
        if taxonomy_name_res is not None:
            tax_name = taxonomy_name_res.group(1)
        else:
            tax_name = "undef"


        # -------- get length ------------
        start = 0
        end = 0
        for m in re.finditer(r'.{3,}', str(record.seq)):            # modified for UniRef100
            start   = str(m.start()+1)
            end     = str(m.end()+1)
            len     = m.end() - m.start()
            
        
        # create output file entry
        try:
            line = "|".join([source, uniprot_id, str(len), str(start), str(end), n_members, str(tax_id), str(tax_name)])
            output_file.write(line +'\n')
            #print(">",line)
            record_count += 1
        except Exception as e:
            print('error parsing line', line, e)
            error_count += 1
            continue
        
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

reduce_uniref_fasta("LowComplexity")

