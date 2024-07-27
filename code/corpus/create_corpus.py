import re
import time
from gensim import corpora
from gensim.models import Word2Vec

debug = False

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
    input_file = "/Users/patrick/dev/ucl/comp0158_mscproject/code/corpus/output/precorpus_00M_00.dat"
    corpus = []
    debug = True
    
    PARSE_LIMIT  = 10  # number of lines to parse
    
    # EXAMPLE INPUT:
    # A0A010PZK3:1:513:1:4|DISORDER:414:512|DISORDER:417:433|DISORDER:445:462|DISORDER:491:505|PF00722:58:224
    with open(input_file, 'r') as input:
        for line_number, line in enumerate(input): # one line number per protein
            
            cols    = line.split('|')
            
            num_cols = len(cols)
            protein_section = cols[0].rstrip("\n")
            protein_pieces = protein_section.split(':')
            
            protein_id      = protein_pieces[0]
            protein_start   = protein_pieces[1]
            protein_end     = protein_pieces[2]
            num_pfam_tokens = protein_pieces[3]
            num_disorder_tokens = protein_pieces[4]
            
            print('\nline:', line.rstrip('\n'), '>', num_cols -1, 'tokens')
            #print(protein_id, protein_start, protein_end, num_pfam_tokens, num_disorder_tokens)                                              
                                                 
            # tokens for the current line
            tokens = []

            if(num_cols > 1):
                for i in range(1, num_cols):
                    #print(cols[i])
                    
                    token_elements  = cols[i].split(':')
                    token_item      = token_elements[0]
                    token_start     = token_elements[1]
                    token_end       = token_elements[2].rstrip('\n')
                    
                    #print(i-1, token_item, token_start, token_end)
                    
                    if token_item.startswith('PF'):
                        tuple = (i-1, token_item, int(token_start), int(token_end))
                        tokens.append(tuple)

                    elif token_item.startswith('DIS'):
                        tuple = (i-1, token_item, int(token_start), int(token_end))
                        tokens.append(tuple)
                        
            print('tokens:', tokens)
            # sort the tokens by start point (second item)
            sorted_tokens = sorted(tokens, key=lambda x: x[2])
            sorted_tokens_no_overlap = remove_overlaps(sorted_tokens)
            
            if(debug): 
                print('unsorted', tokens)
                print('sorted:', sorted_tokens)
                print('no overlaps',sorted_tokens_no_overlap)
            
            sentence = []
            for token in sorted_tokens_no_overlap:
                sentence.append(token[1])
                sentence.append('GAP')
            if(debug): print('final sentence:', sentence)
            
            
                    
            if(PARSE_LIMIT != -1):            
                if(line_number == PARSE_LIMIT):
                    print('\n------', PARSE_LIMIT, 'lines processed, terminating.')
                    return corpus

            '''
            # each col is a section - either being the uniptor part, pfam or disoreded reginos
            for col in cols:
                col = col.rstrip("\n\t")
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
                # process a 'disordered' token
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
            
            if(debug): 
                print('unsorted', tokens)
                print('sorted:', sorted_tokens)
                print('no overlaps',sorted_tokens_no_overlap)
            
            sentence = []
            for token in sorted_tokens_no_overlap:
                sentence.append(token[1])
                sentence.append('GAP')
            if(debug): print('final sentence:', sentence)
            
            # add to corpus
            if(len(sentence) != 0):
                corpus.append(sentence)
            
            # this just prints a progress message
            if (line_number % DEBUG_LIMIT == 0):
                mid_time_end = time.time()
                exec_time = mid_time_end - mid_time_start
                mid_time_start = mid_time_end
                print(line_number, 'lines processed in', round(mid_time_end - start_time,2))
            
            # drops out if we only want to process a number of files
            if(PARSE_LIMIT != -1):            
                if(line_number == PARSE_LIMIT):
                    end_time = time.time()
                    tot_time = end_time - start_time
                    print(PARSE_LIMIT, 'lines processed, terminating....')
                    return corpus
            '''
    return corpus


# this returns a list of lists
corpus = create_corpus()


#print("\n***** CORPUS *****:\n",corpus,'\n')

#w2v = Word2Vec(corpus, size=100, window=5, workers=4, iter=10, min_count=5)


'''
print('Creating dictionary')
dictionary = corpora.Dictionary(corpus)
dictionary.save('/Users/patrick/dev/ucl/comp0158_mscproject/data/corpus/corpus.dict')  # store the dictionary, for future reference
print(dictionary)

print('Creating encoding')
protein_doc = "DISORDER GAP PF00250 GAP"
print('BoW for', protein_doc,':')
protein_vec = dictionary.doc2bow(protein_doc.split())
print(protein_vec)
'''