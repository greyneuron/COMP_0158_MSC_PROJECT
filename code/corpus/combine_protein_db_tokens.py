
import re
import csv
import time
import os

# ------ Background------ 
#
# This script is step 3 of 5 to create sentences to form a corpus for word2vec
#
# 5 steps:
# 1. extract_tokens_from_db.sh : Runs sql from the mysql command line and pipes it to an output file : sql_output_<startprotein>_<iteration>.txt
# 2. convert_db_tokens_dat.sh  : Converts each of the txt outputs from step 1 into a dat file of pipe separated tokens.
#    Each line consists of information about a token and its corresponding uniprot id
# 3. combine_db_tokens_dat.py : Converts each lines (one per token) into a single line per protein (each line with multiple tokens for that protein plus metadata)
# 4. create_corpus.py : Creates a sentence for each protein with GAP DISORDER and PFAM 'words', orders the tokens and removes overlaps
# 5. run_word2vec.py  : Calls word2vec with the corpus
#
# This script combines multiple protein token entries into a single line per protein.
# Example of input:
#  A0A010PZP8:1:633|DISORDER:Polar:50:103
#  A0A010PZP8:1:633|DISORDER:Consensus Disorder Prediction:50:109
#  A0A010PZP8:1:633|DISORDER:Consensus Disorder Prediction:553:598
#  A0A010PZP8:1:633|PFAM:PF00172:16:53
#  A0A010PZP8:1:633|PFAM:PF04082:216:322

# Example of output:
#  protein_id:start:end:num tokens:numpfam tokens : num disorder tokens | disorder or pfam entries with start and end point
#
#  A0A010PZP8:1:633:5:2:3|DISORDER:50:103|DISORDER:50:109|DISORDER:553:598|PF00172:16:53|PF04082:216:322

# does the heavy lifting of combining pfam and disorder tokens into a single line per protein
def combine_tokens(input_dir, input_file_root, input_file_ext, output_dir):
    
    input_dat     = input_dir + '/' + input_file_root + input_file_ext
    
    output_name = re.sub("sql_output", "precorpus", input_file_root)
    output_dat    = output_dir + '/' + output_name + ".dat"
    
    #print('processing input:', input_dat)
    #print('output to:', output_dat)
    
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
                        combined_line = protein_start_buffer + ':' + str(protein_pfam_count + protein_disorder_count) + ':' + str(protein_pfam_count) + ':' + str(protein_disorder_count) + protein_buffer
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



# intermediate method that simply loops through a directory of input files and, for each  file
# calls the combine_tokens() method to combine the elements
def combine_token_files(input_dir, output_dir):
    try:
        # Get a list of all files in the directory
        files = []
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                #files.append(os.path.join(root, filename))
                file_path = os.path.join(root, file)
                file_name, file_extension = os.path.splitext(file)
                
                
                if ("dat" in file_extension):
                    s = time.time()
                    #print(f"processing : {file_name}{file_extension}")
                    
                    combine_tokens(root, file_name, file_extension, output_dir)
                    e = time.time()
                    print(f"processed : {file_name}{file_extension} time taken {e - s}" )
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return


# TODO: CHANGE THESE VALUES input_dir and output_dir
#input_dir       = "/Users/patrick/dev/ucl/comp0158_mscproject/code/corpus/input/"
input_dir       = "/Volumes/My Passport/data/corpus/precorpus_token_dat"
output_dir      = "/Users/patrick/dev/ucl/comp0158_mscproject/code/corpus/output"

combine_token_files(input_dir, output_dir)
