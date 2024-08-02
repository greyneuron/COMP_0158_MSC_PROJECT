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
# According to the uniprot site, this will have 169,760,630 entries
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
    input        = "/Volumes/My Passport/data/protein/uniref100.fasta"
    output      = "uniref100_tax_20240801.dat"
    
    # define regular expressions for UniRef format
    uniprot_re      = "UniRef100_([A-Z0-9]+)"
    taxonomy_re     = "TaxID=([0-9]+)"

    PROCESS_LIMIT   = -1               # number of lines to process, set to -1 to ignore
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
        
        #print(record.name, record.description)
        
        # extract protein id and taxonomy id
        uniprot_res = re.search(uniprot_re, record.name)
        uniprot_id  = uniprot_res.group(1)
        
        taxonomy_res = re.search(taxonomy_re, record.description)
        tax_id = taxonomy_res.group(1)

        # -------- get length ------------
        start = 0
        end = 0
        for m in re.finditer(r'.{3,}', str(record.seq)):            # modified for UniRef100
            start = str(m.start()+1)
            end = str(m.end()+1)
        
        # create output file entry
        try:
            line = "|".join([uniprot_id, str(start), str(end), str(tax_id)])
            output_file.write(line +'\n')
            #print(line)
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

