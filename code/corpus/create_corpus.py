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
def remove_overlaps(protein_id, protein_start, protein_end, tokens):
    # List to store overlapping intervals
    result = []
    prev_start, prev_end = None, None
    
    #print('removing overlaps from :', protein_id, protein_start, protein_end, tokens)
    
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
        result.append((100000, "STOP_GAP"))
            
    return result


#
# This does most of the work - it returns a corpus from one file 
# It breaks each line into individual chunks (tuples) - each representing
# a token. These are then ordered according to their start and end poitiion and overlaps are 
# removed. The final sentence will contain the words 'GAP' 'DISORDER' or 'PF<id>
# EXAMPLE INPUT:
#   A0A010PZK3:1:513:1:4|DISORDER:414:512|DISORDER:417:433|DISORDER:445:462|DISORDER:491:505|PF00722:58:224
#
def create_corpus_for_file(input_dir, input_file_root, input_file_ext, output_dir):
    
    input_file    = input_dir + '/' + input_file_root + input_file_ext
    output_name   = re.sub("precorpus", "corpus", input_file_root)
    output_file    = output_dir + '/' + output_name + ".txt"
    
    print('outputting corpus to:', output_file)
    
    PARSE_LIMIT  = - 1  # number of lines to parse (useful for testing -1 means all)
    debug = False 

    corpus = [] # contains a list of tuples
    of     = open(output_file, "w")
    with open(input_file, 'r') as input:
        for line_number, line in enumerate(input): # one line number per protein
            
            # each section is split by a pipe '|' - the first sectoin contains protein metadata 
            cols    = line.split('|')
            
            num_cols        = len(cols)
            
            # get protein meta data
            protein_section = cols[0].rstrip("\n")
            protein_pieces  = protein_section.split(':')
            protein_id      = protein_pieces[0]
            protein_start   = protein_pieces[1]
            protein_end     = protein_pieces[2]
            num_tokens      = protein_pieces[3]
            num_pfam_tokens     = protein_pieces[5]
            num_disorder_tokens = protein_pieces[5]
            
            if debug:
                print('\nline:', line.rstrip('\n'), '>', num_cols -1, 'tokens')
            #print(protein_id, protein_start, protein_end, num_pfam_tokens, num_disorder_tokens)                                              
                                                 
            # tokens for the current line
            tokens = []

            # extract tuples from subsequent sections (if the exist)
            if(num_cols > 1):
                for i in range(1, num_cols):
                    token_elements  = cols[i].split(':')
                    token_item      = token_elements[0]
                    token_start     = int(token_elements[1])
                    token_end       = int(token_elements[2].rstrip('\n'))
                    
                    tuple = (i-1, token_item, token_start, token_end)
                    tokens.append(tuple)
                    #print(i-1, token_item, token_start, token_end)
                        
            #print('tokens:', tokens)
            
            # sort the tokens by start point (second item)
            sorted_tokens = sorted(tokens, key=lambda x: x[2])
            
            # remove overlapping tokens and add a START_GAP and END_GAP at the end
            sorted_tokens_no_overlap = remove_overlaps(protein_id, protein_start, protein_end, sorted_tokens)

            
            sentence = ""
            idx = 0
            num_tokens = len(sorted_tokens_no_overlap)
            for token in sorted_tokens_no_overlap:
                sentence = sentence + token[1] + " "
                # add gaps in between tokens
                if (idx > 0 and idx < num_tokens -2):
                    sentence = sentence + "GAP "
                idx += 1
            if(debug): print('final sentence:', sentence)
            of.write(sentence +'\n')
                    
            if(PARSE_LIMIT != -1):            
                if(line_number == PARSE_LIMIT):
                    print('\n------', PARSE_LIMIT, 'lines processed, terminating.')
                    of.close()
                    return
    of.close()
    return


#
# Loops through precorpus files 
#
def create_corpus_files(input_dir, output_dir):
    corpus = []
    try:
        # Get a list of all files in the directory
        files = []
        for root, dirs, files in os.walk(input_dir):
            for file in files:

                file_path = os.path.join(root, file)
                file_name, file_extension = os.path.splitext(file)
                
                
                if ("dat" in file_extension):
                    s = time.time()
                    #print(f"processing : {root} {file_name} {file_extension}")
                    
                    corpus.append(create_corpus_for_file(root, file_name, file_extension, output_dir))
                    
                    e = time.time()
                    print(f"processed : {root}/{file_name}{file_extension} time taken {e - s}" )
        return 
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


#input_dir       = "/Users/patrick/dev/ucl/comp0158_mscproject/code/corpus/input/"
input_dir       = "/Users/patrick/dev/ucl/comp0158_mscproject/code/corpus/output"
output_dir      = "/Users/patrick/dev/ucl/comp0158_mscproject/code/corpus/corpus"

create_corpus_files(input_dir, output_dir)







