import re
import time
from gensim import corpora
from gensim.models import Word2Vec
import os

debug = False


# ------ Background------ 
#
# This script is step 4 of 5 to create sentences to form a corpus for word2vec
#
# 5 steps:
# 1. extract_tokens_from_db.sh : Runs sql from the mysql command line and pipes it to an output file : sql_output_<startprotein>_<iteration>.txt
# 2. convert_db_tokens_dat.sh  : Converts each of the txt outputs from step 1 into a dat file of pipe separated tokens.
#    Each line consists of information about a token and its corresponding uniprot id
# 3. combine_db_tokens_dat.py : Converts each lines (one per token) into a single line per protein (each line with multiple tokens for that protein plus metadata)
# 4. create_corpus.py : Creates a sentence for each protein with GAP DISORDER and PFAM 'words', orders the tokens and removes overlaps
# 5. run_word2vec.py  : Calls word2vec with the corpus
#


# Finds overlapping regions - and removes them, assumes the tokens
# are in order  - thus the start of token 2 will always be after the start of token 1
def remove_overlaps(protein_id, protein_length, tokens):
    # List to store overlapping intervals
    result = []
    prev_start, prev_end = None, None
    
    protein_start = 1
    protein_end = protein_length
    
    #print('removing overlaps from :', protein_id, protein_start, protein_end, tokens)
    num_tokens = len(tokens)
    for token in tokens:
        start, end = token[2], token[3]
        
        # start with first token
        if prev_start is None:
            if int(protein_start) < start:
                start_tuple = (-1, "START_GAP")
                result.append(start_tuple)
            prev_start, prev_end = start, end
            result.append(token)
        # if there is overlap - don't add this item (for now)    
        else:
            if start <= prev_end:
                #print('--------------> overlap : ', start , end)
                # Overlapping interval found, skip adding this item
                continue
            else:
                # No overlap, add the item to the result list
                result.append(token)
                prev_start, prev_end = start, end
    if (end < int(protein_end)):
        result.append((1000, "STOP_GAP"))
            
    return result


#
# This does most of the work - it returns a corpus from one file 
# It breaks each line into individual chunks (tuples) - each representing
# a token. These are then ordered according to their start and end poitiion and overlaps are 
# removed. The final sentence will contain the words 'GAP' 'DISORDER' or 'PF<id>
# EXAMPLE INPUT:
#
#   A0A010PZJ8:493:4:1:3|DISORDER:1:30|DISORDER:1:32|DISORDER:468:493|PF01399:335:416
#
def create_corpus(input_file, output_file):
    
    print('outputting corpus to:', output_file)
    
    PARSE_LIMIT  = 1000  # number of lines to parse (useful for testing -1 means all)
    debug = False
    
    # init
    num_tokens      = 0
    num_pfam_tokens = 0
    num_disorder_tokens = 0

    corpus = [] # contains a list of tuples
    of     = open(output_file, "w")
    
    # parse input file
    with open(input_file, 'r') as input:
        for line_number, line in enumerate(input): # one line number per protein
            
            #print(f"\nline: {line.strip('\n')}")
            
            # each section is split by a pipe '|' - the first sectoin contains protein metadata 
            cols        = line.split('|')
            num_cols    = len(cols)
            
            # get protein meta data - this is the first token
            protein_section = cols[0].rstrip("\n")
            protein_pieces  = protein_section.split(':')
            protein_id      = protein_pieces[0]
            protein_length  = int(protein_pieces[1])
            num_tokens      = int(protein_pieces[2])
            num_pfam_tokens     = int(protein_pieces[3])
            num_disorder_tokens = int(protein_pieces[4])
            
            # leave out lines with no pfam tokens
            if( (num_pfam_tokens == 0) or (num_tokens == 0)):
                print(f"{line} has no tokens or no pfam tokens, skipping..")
                continue
                                                                                      
            # tokens for the current line
            tokens = []

            # extract tokens from subsequent sections (if they exist)
            if(num_cols > 1):
                for i in range(1, num_cols):
                    token_elements  = cols[i].split(':')
                    token_item      = token_elements[0]
                    token_start     = int(token_elements[1])
                    token_end       = int(token_elements[2].rstrip('\n'))
                    
                    tuple = (i-1, token_item, token_start, token_end)
                    tokens.append(tuple)
                        
            #print(f"tokens for {protein_id}: {tokens}")
            
            # sort the tokens by start point (second item)
            sorted_tokens = sorted(tokens, key=lambda x: x[2])
            
            # remove overlapping tokens and add a START_GAP and END_GAP at the end
            sorted_tokens_no_overlap = remove_overlaps(protein_id, protein_length, sorted_tokens)
            
            #print(f"sorted no overlap for {protein_id}: {sorted_tokens_no_overlap}")
            
            # create sentences
            sentence = ""
            pos = 0
            num_sorted_tokens  = len(sorted_tokens_no_overlap)
            last_token  = sorted_tokens_no_overlap[num_tokens - 1][1]
            first_token = sorted_tokens_no_overlap[0][1]
            
            if(num_sorted_tokens <= 1):
                print('NOT ENOUGH TOKENS IN THIS LINE')
                continue
            
            print(sorted_tokens_no_overlap)
            result = []
            for i in range(len(sorted_tokens_no_overlap)):
                result.append(sorted_tokens_no_overlap[i][1])
                # Check if we should add "GAP"
                if i < len(sorted_tokens_no_overlap) - 1:  # Check if not the last word
                    if sorted_tokens_no_overlap[i][1] != "START_GAP" and sorted_tokens_no_overlap[i+1][1] != "STOP_GAP":
                        if(sorted_tokens_no_overlap[i+1][2] > sorted_tokens_no_overlap[i][3] + 1):
                            result.append("GAP")
            print(f"sentence for {protein_id}: {result} \n")
        
            '''
            # have at least 2 tokens
            for token in sorted_tokens_no_overlap:
                # first token - add in the token whatever
                if(pos == 0):
                    sentence = sentence + token[1] + " "
                    # add in a gap if there are more tokens left 
                    if (num_sorted_tokens == 2):
                        if((first_token != "START_GAP") and (last_token != "STOP_GAP")):
                            sentence = sentence + "GAP "
                    else:
                        if(first_token != "START_GAP"):
                            sentence = sentence + "GAP "
                    pos +=1
                    continue
                if(pos == 1):
                    sentence = sentence + token[1] + " "
                    if (num_sorted_tokens == 2):
                        pos +=1
                        continue
                    
                            
                        
                        
                # second token - add the token and add a gap only if the first_token wasn't START_GAP
                elif(idx == 1):
                    sentence = sentence + token[1] + " "
                    if ((first_token != "START_GAP") and (idx < num_sorted_tokens -1)):
                        sentence = sentence + "GAP "
                    idx +=1
                    continue
                
                # if second last token
                elif(idx == num_sorted_tokens -2):
                    if (last_token == "STOP_GAP"):
                        idx+=1
                        continue
                    else:
                        if(num_tokens > 1):
                            sentence = sentence + "GAP "
                            idx+=1
                            continue
                # if neither first nor second last
                elif(idx > 0 and idx < num_sorted_tokens -1 and num_tokens > 1):
                    sentence = sentence + "GAP "
                    idx += 1
                else:
                    idx +=1
                
                
                
            print(f"sentence for {protein_id}: {sentence}")
            of.write(sentence +'\n')
            '''
            
            if(PARSE_LIMIT != -1):            
                if(line_number == PARSE_LIMIT):
                    print('\n------', PARSE_LIMIT, 'lines processed, terminating.')
                    of.close()
                    return
    of.close()
    return


input_file      = "/Users/patrick/dev/ucl/comp0158_mscproject/data/corpus/tokens_combined/uniref100_e_tokens_20240808_ALL_COMBINED_TEST.dat"
output_file     = "/Users/patrick/dev/ucl/comp0158_mscproject/data/corpus/uniref100_e_corpus_20240808.dat"

create_corpus(input_file, output_file)


'''
TEST1:664:1:1:0|PFAM1234:123:575    > gap from start to pfam and gap to end         : START_GAP PFAMXX STOP_GAP : pass
TEST2:214:1:1:0|PF14273:31:213      > gap from start to pfam and tiny gap to end    : START_GAP PFAMXX STOP_GAP : pass
TEST3:214:1:1:0|PF14273:31:214      > gap from start to pfam and no gap at end      : START_GAP PFAMXX : pass

TEST4:100:4:2:2|PF14273:30:40|DISORDER:50:60|PF2345:65:70|DISORDER:80:100           : START_GAP PFAMXX GAP DISORDER GAP PFXXX DISORDER  : pass
TEST5:100:4:2:2|PF14273:0:40|DISORDER:50:60|PF2345:61:70|DISORDER:80:100            : PF14273 GAP DISORDER PF2345 DISORDER : fail




TEST1:664:1:1:0|PFAM1234:123:575
TEST2:214:1:1:0|PF14273:31:213
TEST3:214:1:1:0|PF14273:31:214
TEST4:100:4:2:2|PF14273:30:40|DISORDER:50:60|PF2345:65:70|DISORDER:80:100
TEST5:100:4:2:2|PF14273:0:40|DISORDER:50:60|PF2345:61:70|DISORDER:80:100

'''




