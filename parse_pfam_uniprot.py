from Bio import SeqIO
import re
import csv
import duckdb

# internal representation
from protein_db import ProteinDB

limit       = True # if True, onLy parses Max_lines lines 
MAX_COUNT   = -1
OUTPUT_LIMIT = 10000000

def parse_parse_protein_2ipr_pfam():
    path        = "/Users/patrick/dev/ucl/comp0158_mscproject/data/protein2ipr_pfam.dat"
    output      = "/Users/patrick/dev/ucl/comp0158_mscproject/data/pfam_entries_full.dat"
    
    uniprot_id = ""
    output_file = open(output, "w")
    count = 0
    
    with open(path, 'r') as input_file:
        for line_number, line in enumerate(input_file):
            
            # -------- check for termination ------------
            #
            if ((line_number // OUTPUT_LIMIT > 0) and (line_number % OUTPUT_LIMIT) == 0):
                count += 1
                print(count * OUTPUT_LIMIT, 'lines processed.....')
            if(MAX_COUNT != -1):
                if line_number >= MAX_COUNT:
                    print('Processing limit reached %s stopping. Last entry was %s' % (MAX_COUNT, uniprot_id))
                    break
            # ------------------------------------  
            
            match = re.search("([A0A0-9]*[a-zA-Z0-9]+)\\tIPR[0-9]+\\t.*\\t(PF[0-9]+)\\t([0-9]+)\\t([0-9]+)", line)

            if match is not None:
                uniprot_id  = match.group(1)
                pfam_word   = match.group(2)
                start       = match.group(3)
                end         = match.group(4)
                item_type   = "PFAM"
            
            #print(uniprot_id, pfam_word, start, end)
            output_file.write(uniprot_id+"\t"+pfam_word+"\t"+start+"\t"+end+'\n')
            
    output_file.close()      

#parse_parse_protein_2ipr_pfam()