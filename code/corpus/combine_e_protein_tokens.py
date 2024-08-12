
import re
import csv
import time
import os

# ------ Background------ 
#
# This script was step 3 of 5 to create sentences to form a corpus for word2vec (as described in db_approach/extract_tokens_from_db.sh) but has since been modified
# but it still does broadly the same thing - it combines multiple protein token entries across mutiple lines into a single line per protein. The precursor to this
# step can be found in code/data_prep/duckdb_dat_loader.ipynb in method extract_eukaryotic_tokens()
#
# Example of input - multiple lines per protein

'''
UNIPROT LENGTH TYPE TOKEN TOKEN START TOKEN END
A0A010PZP8|632|DISORDER|Polar|50|103
A0A010PZP8|632|DISORDER|Consensus Disorder Prediction|50|109
A0A010PZP8|632|DISORDER|Consensus Disorder Prediction|553|598
A0A010PZP8|632|PFAM|PF00172|16|53
A0A010PZP8|632|PFAM|PF04082|216|322

A0A010PZK3|512|DISORDER|Consensus Disorder Prediction|414|512
A0A010PZK3|512|DISORDER|Polar|417|433
A0A010PZK3|512|DISORDER|Polar|445|462
A0A010PZK3|512|DISORDER|Polar|491|505
A0A010PZK3|512|PFAM|PF00722|58|224
A0A010PZK7|664|PFAM|PF14033|123|575
'''

# Example of output - one line per protein including metadata at the start:
'''
protein_id:start:end:num tokens:numpfam tokens : num disorder tokens | disorder or pfam entries with start and end point
A0A010PZP8:1:633:5:2:3|DISORDER:50:103|DISORDER:50:109|DISORDER:553:598|PF00172:16:53|PF04082:216:322
'''



# does the heavy lifting of combining pfam and disorder tokens into a single line per protein
def combine_tokens(input_file, output_file):
    
    s = time.time()
    
    print(f"Combining tokens in {input_file}, output to {output_file}")
    
    line_limit = -1 # set to non negative number to limit output
    
    last_protein    = "start"
    current_protein = ""
    protein_buffer  = ""

    protein_disorder_count = 0
    protein_pfam_count = 0
    
    of      = open(output_file, "w")
    
    lines_processed = 0
    output_lines    = 0
    with open(input_file, 'r') as file:
        for line_number, line in enumerate(file):
            lines_processed += 1
            
            if(line_limit != -1 and line_number > line_limit):
                print(f"Hit line limit of {line_limit}, returning")
                return
            
            #print('line:',line.strip('\n'))
            
            cols = line.split('|')
            #print(cols)
            if(len(cols) > 1):

                current_protein = cols[0].strip('\n')
                protein_len     = cols[1].strip('\n')

                token_type  = cols[2].strip('\n')
                token       = cols[3].strip('\n')
                token_start = cols[4].strip('\n')
                token_end   = cols[5].strip('\n')
                
                # if the curent result line is for a new protein (ie the protine id at the start of the output has changed)
                if (last_protein == "start" or current_protein != last_protein ):

                    # if we have a new protein thats not the start, output the buffer
                    if(last_protein != "start"):
                        combined_line = protein_start_buffer + ':' + str(protein_pfam_count + protein_disorder_count) + ':' + str(protein_pfam_count) + ':' + str(protein_disorder_count) + protein_buffer
                        of.write(combined_line +'\n')
                        output_lines += 1
                        
                        #print('combined line :', combined_line.strip('\n'), '\n')
                        
                        protein_buffer  = ""
                        protein_pfam_count      = 0
                        protein_disorder_count  = 0
                    
                    # otherwise, add to current buffer
                    last_protein = current_protein
                    protein_start_buffer = ':'.join([current_protein, protein_len])
                
                # for a disorder token
                if (token_type == "DISORDER"):
                    protein_buffer = protein_buffer + '|' + token_type + ':' + token_start + ':' + token_end
                    protein_disorder_count += 1
                
                # for a pfam token
                elif (token_type == "PFAM"):
                    protein_buffer = protein_buffer + '|' + token + ':' + token_start + ':' + token_end
                    protein_pfam_count += 1
    e = time.time()
    print(f"{lines_processed} lines processed in {round(e-s,2)}s. {output_lines} lines written to {output_file}")


# TODO: CHANGE THESE VALUES input_dir and output_dir
input_file       = "/Users/patrick/dev/ucl/comp0158_mscproject/data/corpus/tokens/uniref100_e_tokens_20240808_ALL.dat"
output_file      = "/Users/patrick/dev/ucl/comp0158_mscproject/data/corpus/tokens_combined/uniref100_e_tokens_20240808_ALL_COMBINED.dat"

combine_tokens(input_file, output_file)
