import re
import time

# finds overlapping regions - but assumes each token is in order
# thus the start of token 2 will always be after the start of token 1
def find_overlaps(tokens):
    # List to store overlapping intervals
    overlaps = []
    
    # Iterate through the sorted list and check for overlaps
    for i in range(1, len(tokens)):
        i1, w1, s1, e1 = tokens[i - 1]
        i2, w2, s2, e2 = tokens[i]
        
        # scenario 1 : start of tokem 2 is before the end of token 1
        if s2 <= e1:
            overlaps.append((tokens[i - 1], tokens[i]))
        # scenario 2 : start 1 is before the end of token 1
        #if s2 <= e1:
        #    overlaps.append((tokens[i - 1], tokens[i]))
    return overlaps


# finds overlapping regions - and removes them, assumes the tokens
# are in order  - thus the start of token 2 will always be after the start of token 1
def remove_overlaps(tokens):
    # List to store overlapping intervals
    result = []
    prev_start, prev_end = None, None
    
    for token in tokens:
        start, end = token[2], token[3]
        
        # start with first token
        if prev_start is None:
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
    return result



def create_corpus():
    input_file      = "/Users/patrick/dev/ucl/comp0158_mscproject/data/corpus/pre_corpus_20240715_1130.dat"
    
    PARSE_LIMIT  = 100  # number of lines to parse
    DEBUG_LIMIT  = 10   # number of lines after which to print a debug message
    
    start_time      = time.time()
    mid_time_start  = time.time()
    
    with open(input_file, 'r') as input:
        for line_number, line in enumerate(input): # one line number per protein
            
            # protein details, pfam tokens and disordered tokens are separated by |
            # within that are the start and end poisitions
            # e.g. A0A010PZP8:1:633|PF00172:16:53|PF04082:216:322|DISORDER:50:103:50:109:553:598
            # 1 protein, 2 pfam tokens, 3 disordered regions
            
            cols  = line.split('|')
            token_idx = 0
            
            print('\nline >', line.strip('\n'), '<')
            #print(len(cols), '> entries')
            
            tokens = []

            # each col is a section - either being the uniptor part, pfam or disoreded reginos
            for col in cols:
                col = col.rstrip("\n\s\t")
                # just in case
                if col == None or col == "":
                    continue
                # process a PFAM token
                if col.startswith('PF'):
                    pf_cols = col.split(':')
                    pf_token = pf_cols[0]
                    for pf in range(1, len(pf_cols)-1,2):
                        #print('PFM:', token_idx, ':', pf_token, 'start:', pf_cols[pf],'end:', pf_cols[pf + 1])
                        tuple = (token_idx, pf_token, int(pf_cols[pf]), int(pf_cols[pf + 1]))
                        tokens.append(tuple)
                        token_idx += 1
                # process a 'disordered'token
                elif col.startswith('DIS'):
                    dis_cols = col.split(':')
                    for dis in range(1, len(dis_cols)-1,2):
                        #print('DIS:', token_idx, ': start:', dis_cols[dis],'end:', dis_cols[dis + 1])
                        tuple = (token_idx, 'DISORDER', int(dis_cols[dis]), int(dis_cols[dis+1]))
                        tokens.append(tuple)
                        token_idx += 1
                # just printing out the token if needed
                else:
                    protein_cols = col.split(':')
                    #print('PROT:', protein_cols[0], 'start:', protein_cols[1], 'end:', protein_cols[2])
            #print('tokens:', tokens)
            
            # sort the tokens by start point (second item)
            sorted_tokens = sorted(tokens, key=lambda x: x[2])
            sorted_tokens_no_overlap = remove_overlaps(sorted_tokens)
            
            #print('sorted:', sorted_tokens)
            print('no overlaps',sorted_tokens_no_overlap)

create_corpus()