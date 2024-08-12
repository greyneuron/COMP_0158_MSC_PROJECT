import re
import time
from gensim import corpora
from gensim.models import Word2Vec
import os

debug = False


# ------ Background------ 
#
# This is an improved version following improvements to my means of extracting tokens
# 
# ------ OLD NOTES --------
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
# ------ REVISED NOTES --------
# This script is step 4 of 5 to create sentences to form a corpus for word2vec
#
# 5 steps:
# 1. Use the method extract_eukaryotic_tokens() in duckdb_dat_loader to extract all tokens for eukaryotic proteins - this produces multuple files each line containing a toek for a proteion
# 2. Use a shell script such as shell/concat_files.sh to concatenate all the files together
# 3. Use script combine_e_protein_tokens.py to consolidate all the lines of tokens into single lines of tokens - one for each eukaryotic protein
# 2. Use THIS script, create_corpus.py, to parse the previous output to create a corpus of sentences- one for each protein with GAP DISORDER and PFAM 'words', orders the tokens and removes overlaps
# 5. run_word2vec.py  : Calls word2vec with the corpus


#
# This method processes an ordered list of tokens (order by their start position) and removes overlaps.
#
# Rules:
# - First token always added
# - If there is an overlap and the current token is pfam and previous was disorder, the previous disorder is removed and the current pfam added
# - If there is an overlap and the current token is pfam and previous was pfam as well, the current pfam token is ignored
# - If there is an overlap and the current token is disorder and previous was disorder as well, the current disorder token is ignored
#
def reorder_tokens(tokens, debug=False):
    reordered_tokens        = []
    prev_start, prev_end    = None, None
    last_token_added        = None

    for token in tokens:
        #print(f"processing {token}")
        token_start = token[2]
        token_end   = token[3]
        if token[1].startswith('PF'):
            token_type = "pfam"
        elif token[1].startswith('DISORDER'):
            token_type = "disorder"
        
        # start with first token
        if prev_start is None:
            prev_start, prev_end = token_start, token_end
            reordered_tokens.append(token)
            if(debug): print(f"adding {token[1]} at {token[2]}.")
            last_token_added = token
        
        # if there is overlap - don't add the current item unless its pfam and the previos was disorder    
        else:
            if token_start <= prev_end:
                if token_type == "pfam":
                    if(debug): print(f"overlapping pfam token {token_start} with last added {last_token_added}")
                    # replace previous if it was a disorder token
                    if last_token_added[1].startswith('DISORDER'):
                        if(debug): print(f"removing {last_token_added[1]} at {last_token_added[2]}.")
                        if(debug): print(f"adding {token[1]} at {token[2]}.")
                        reordered_tokens[len(reordered_tokens) -1] = token
                        prev_start, prev_end = token_start, token_end
                        last_token_added = token
                else:
                    if(debug): print(f"overlapping token {token[1]} at pos {token_start} with last added {last_token_added}, not adding.")
            else:
                # No overlap, add the item to the result list
                if(debug): print(f"adding {token[1]} at {token[2]}.")
                reordered_tokens.append(token)
                last_token_added = token
                prev_start, prev_end = token_start, token_end
    return reordered_tokens
    
    
    
    
    
    




# Finds overlapping regions - and removes them, assumes the tokens
# are in order  - thus the start of token 2 will always be after the start of token 1
def add_bookends(protein_id, protein_length, tokens, debug=False):
    # List to store overlapping intervals
    result = []
    prev_start, prev_end = None, None
    
    protein_start = 1
    protein_end = protein_length

    num_tokens = len(tokens)
    for token in tokens:
        start, end = token[2], token[3]
        
        # start with first token
        if prev_start is None:
            if int(protein_start-1) < start:
                start_tuple = (-1, "START_GAP ")
                result.append(start_tuple)
            prev_start, prev_end = start, end
            result.append(token)
        # if there is overlap - don't add this item (for now)    
        else:
            if start <= prev_end:
                if token[1].startswith('PF'):
                    continue
            else:
                # No overlap, add the item to the result list
                result.append(token)
                prev_start, prev_end = start, end
    if (end < int(protein_end)):
        result.append((1000, " STOP_GAP"))
            
    return result


#
# This does most of the work - it returns a corpus from one file 
# It breaks each line into individual chunks (tuples) - each representing
# a token. These are then ordered according to their start and end poitiion and overlaps are 
# removed. The final sentence will contain the words 'GAP' 'DISORDER' or 'PF<id>
# EXAMPLE INPUT:
#       A0A010PZJ8:493:4:1:3|DISORDER:1:30|DISORDER:1:32|DISORDER:468:493|PF01399:335:416
# EXAMPLE OUTPUT:
#       START_GAP DISORDER GAP PF01399 GAP DISORDER
#
def create_corpus(input_file, output_file, ignore_file, debug=False):
    
    print('outputting corpus to:', output_file)
    
    PARSE_LIMIT  = -1  # number of lines to parse (useful for testing -1 means all)
    debug = False
    
    # init
    num_tokens      = 0
    num_pfam_tokens = 0
    num_disorder_tokens = 0

    #corpus  = [] # contains a list of tuples
    of      = open(output_file, "w")
    ignoref = open(ignore_file, "w")
    
    # parse input file
    with open(input_file, 'r') as input:
        for line_number, line in enumerate(input): # one line number per protein
            
            #print(f"\nline: {line.strip('\n')}")
            
            # each section is split by a pipe '|' - the first sectoin contains protein metadata
            line = line.strip('\n')
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
                #print(f"Ignoring {line.strip('\n')} - it has no tokens or no pfam tokens..")
                ignoref.write(protein_id + '|' + " SKIP_NO_PFAM |" + line + '\n')
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
            
            # sort tokens and remove overlaps - i imagine there is a smarter way to do this
            sorted_tokens               = sorted(tokens, key=lambda x: x[2]) # order by start position
            reordered_tokens            = reorder_tokens(sorted_tokens)      # reorder by replacing overlaps
            
            bookended_tokens    = add_bookends(protein_id, protein_length, reordered_tokens)
            
            # debug
            if(debug): print(f"sorted tokens    : {sorted_tokens}")
            if(debug): print(f"combined tokens  : {reordered_tokens}")
            if(debug): print(f"with bookends    : {bookended_tokens}")
            
            # double check that we have enough tokens for a sentence!
            num_sorted_tokens  = len(bookended_tokens)
            if(num_sorted_tokens <= 1):
                print(f"NOT ENOUGH TOKENS FOR THIS PROTEIN: {protein_id}. line: {line}")
                ignoref.write(protein_id + '|' + " SKIP_TOO_SMALL |" + line + '\n')
                continue
            
            # create sentences - add gaps where appropriate - basically in between any words
            # as long as the first word or last word isn;t also a gap (which is possible) ad
            # thenwe'd have two GAP tokens. NOte that I have differentiated between gaps that appear
            # as the first token or last token - not sure it will make any difference
            sentence = ""
            for i in range(num_sorted_tokens):
                sentence += bookended_tokens[i][1]
                # Check if we should add "GAP"
                if i < len(bookended_tokens) - 1:  # Check if not the last word
                    if bookended_tokens[i][1] != "START_GAP " and bookended_tokens[i+1][1] != " STOP_GAP":
                        if(bookended_tokens[i+1][2] > bookended_tokens[i][3] + 1):
                            sentence += " GAP "
                        elif(bookended_tokens[i+1][2] == bookended_tokens[i][3] + 1):
                            sentence += " "
            # DEBUG
            #print(f"sentence for {protein_id}: {sentence}")
            of.write(sentence +'\n')
            
            if(PARSE_LIMIT != -1):            
                if(line_number == PARSE_LIMIT):
                    print('\n------', PARSE_LIMIT, 'lines processed, terminating.')
                    of.close()
                    return
    of.close()
    ignoref.close()
    return

# ------------------------------------------------------------------------------------------------------
#
#                               SETUP & RUN
#
# ------------------------------------------------------------------------------------------------------
input_file      = "/Users/patrick/dev/ucl/comp0158_mscproject/data/corpus/tokens_combined/uniref100_e_tokens_20240808_ALL_COMBINED.dat"
output_file     = "/Users/patrick/dev/ucl/comp0158_mscproject/data/corpus/uniref100_e_corpus_20240810.txt"
ignore_file     = "/Users/patrick/dev/ucl/comp0158_mscproject/data/corpus/uniref100_e_corpus_20240810_ignored.txt"

s = time.time()
create_corpus(input_file, output_file, ignore_file)
e = time.time()

print(f"Corpus created in {round(e-s,2)}s; ouput to {output_file}")




'''
EXAMPLES FOR TESTING

TEST1:664:1:1:0|PFAM1234:123:575
TEST2:214:1:1:0|PF14273:31:213
TEST3:214:1:1:0|PF14273:31:214
TEST4:100:4:2:2|PF14273:30:40|DISORDER:50:60|PF2345:65:70|DISORDER:80:100
TEST5:100:4:2:2|PF14273:0:40|DISORDER:50:60|PF2345:61:70|DISORDER:80:100
TEST6:100:4:2:2|PF14273:1:40|DISORDER:50:60|PF2345:62:70|DISORDER:80:98
TEST7:100:4:0:4|DISORDER:0:40|DISORDER:50:60|DISORDER:51:60|DISORDER:80:100
TEST8:106:4:1:3|DISORDER:38:106|DISORDER:55:72|PF00424:60:70|PF00424:42:91
TEST9:106:4:1:3|DISORDER:38:106|DISORDER:55:72|PF00424:60:70|PF00425:61:91
TEST10:106:4:1:3|DISORDER:38:106|DISORDER:55:72|PF00424:60:70|PF00425:71:91
A0A2A9PFF7:106:4:1:3|DISORDER:38:106|DISORDER:55:72|DISORDER:83:106|PF00424:42:91
A0A0A2VYH2:310:1:1:0|PF01278:29:310
D5J701:86:1:1:0|PF01766:3:84



'''




