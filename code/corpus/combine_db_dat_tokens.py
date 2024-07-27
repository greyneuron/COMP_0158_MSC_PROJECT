
import re
import csv
import time
import os

# This script is step 3 of 4 to get a sentence to pass into word2vec
# It assumes there is a database with two tables :W2V_PROTEIN and W2V_TOKEN
#
# 4 steps:
# 1. Runs sql from the mysql command line and pipes it to an output file : sql_output_<startprotein>_<iteration>.txt
#    You need to change the start poisitoin and chunk size and number of iterations
#    I found that it would iterate through 500k proteins in about 3.5mins so I would set the chunk size to 500000 and iterate from 0..9 to get 10M
# 2. convert_db_tokens_dat.sh converts each of the sql txt outputs from step 1 into a dat file of pipe separated tokens - each line has a token and its corresponding uniprot id
# 3. ** THIS SCRIPT ** : Converts the lines from step 2 into a single line per protein - containing al token info
# 4. The final script then creates a sentence for each protein with GAP DISORDER and PFAM
'''
Combines token lines such as the below into a single line per protein id
A0A010PZP8:1:633|DISORDER:Polar:50:103
A0A010PZP8:1:633|DISORDER:Consensus Disorder Prediction:50:109
A0A010PZP8:1:633|DISORDER:Consensus Disorder Prediction:553:598
A0A010PZP8:1:633|PFAM:PF00172:16:53
A0A010PZP8:1:633|PFAM:PF04082:216:322
'''

def combine_tokens(input_dir, input_file_root, input_file_ext, output_dir):
    input_dat     = input_dir + input_file_root + input_file_ext
    
    output_name = re.sub("sql_output", "precorpus", input_file_root)
    output_dat    = output_dir + '/' + output_name + ".dat"
    
    print('processing input:', input_dat, 'output to:', output_dat)
    
    last_protein    = "start"
    current_protein = ""
    protein_buffer  = ""

    protein_disorder_count = 0
    protein_pfam_count = 0
    
    of      = open(output_dat, "w")
        
    with open(input_dat, 'r') as file:
        for line_number, line in enumerate(file):
            #print('line:',line.strip('\n'))
            cols = line.split('|')
            
            if(len(cols) > 1):
                # get key info from current line
                protein_info = cols[0].strip('\n')
                p_cols      = protein_info.split(':')
            
                token_info  = cols[1].strip('\n')
                t_cols      = token_info.split(':')

                current_protein = p_cols[0]
                protein_start   = p_cols[1]
                protein_end     = p_cols[2]

                token_type  = t_cols[0]
                token       = t_cols[1]
                token_start = t_cols[2]
                token_end   = t_cols[3]
                
                # debug
                # print(' -', current_protein, protein_start, protein_end, token, token_start, token_end)
                
                # if the curent result line is for a new protein (ie the protine id at the start of the output has changed)
                if (last_protein == "start" or current_protein != last_protein ):

                    # if we have a new protein thats not the start, output the buffer
                    if(last_protein != "start"):
                        combined_line = protein_start_buffer + ':' + str(protein_pfam_count) + ':' + str(protein_disorder_count) + protein_buffer
                        of.write(combined_line +'\n')
                        #of.write(protein_buffer + '\n')
                        #print('combined line :', combined_line, '\n')
                        protein_buffer  = ""
                        protein_pfam_count      = 0
                        protein_disorder_count  = 0
                    
                    # otherwise, add to current buffer
                    last_protein = current_protein
                    protein_start_buffer = ':'.join([current_protein, protein_start, protein_end])
                
                # for a disorder token
                if (token_type == "DISORDER"):
                    protein_buffer = protein_buffer + '|' + token_type + ':' + token_start + ':' + token_end
                    protein_disorder_count += 1
                
                # for a pfam token
                elif (token_type == "PFAM"):
                    protein_buffer = protein_buffer + '|' + token + ':' + token_start + ':' + token_end
                    protein_pfam_count += 1



input_file_root = "sql_output_00M_00"
input_file_ext = ".dat"
input_dir       = "/Users/patrick/dev/ucl/comp0158_mscproject/code/corpus/input/"
output_dir      = "/Users/patrick/dev/ucl/comp0158_mscproject/code/corpus/output"

combine_tokens(input_dir, input_file_root, input_file_ext, output_dir)
