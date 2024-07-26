
import re
import csv
import time



# ----------------------------------
# pfam entries  : 298,766,058
# proteins      : 78,494,529
# disorder      : 81,257,100
# ----------------------------------


'''
Combines token lines such as the below into a single line per protein id
A0A010PZP8:1:633|DISORDER:Polar:50:103
A0A010PZP8:1:633|DISORDER:Consensus Disorder Prediction:50:109
A0A010PZP8:1:633|DISORDER:Consensus Disorder Prediction:553:598
A0A010PZP8:1:633|PFAM:PF00172:16:53
A0A010PZP8:1:633|PFAM:PF04082:216:322
'''

def combine_tokens_new():
    input_dat     = "/Users/patrick/dev/ucl/comp0158_mscproject/code/corpus/output/sqloutput_0.dat"
    output_dat    = "/Users/patrick/dev/ucl/comp0158_mscproject/code/corpus/output/pre_corpus_0.dat"
    
    
    last_protein    = "start"
    current_protein = ""
    protein_buffer  = ""
    
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

                token_type = t_cols[0]
                token = t_cols[1]
                token_start = t_cols[2]
                token_end = t_cols[3]
                
                # debug
                # print(' -', current_protein, protein_start, protein_end, token, token_start, token_end)
                
                # if the curent result line is for a new protein (ie the protine id at the start of the output has changed)
                if (last_protein == "start" or current_protein != last_protein ):
                    # if we have a new protein thats not the start, output the buffer
                    if(last_protein != "start"):
                        print('combined line', protein_buffer, '\n')
                        of.write(protein_buffer + '\n')
                    # otherwise, add to current buffer
                    last_protein = current_protein
                    protein_buffer = ':'.join([current_protein, protein_start, protein_end])
                
                # for a disprder token
                if (token_type == "DISORDER"):
                    protein_buffer = protein_buffer + '|' + token_type + ':' + token_start + ':' + token_end
                    #print('Token:', token_type, res[5], res[6])
                
                # for a pfam token
                elif (token_type == "PFAM"):
                    #print('Token:', res[4], res[5], res[6])
                    protein_buffer = protein_buffer + '|' + token + ':' + token_start + ':' + token_end

combine_tokens_new()






def combine_tokens():
    input_dat     = "/Users/patrick/dev/ucl/comp0158_mscproject/code/corpus/output/sql_output_0_1.dat"
    output        = "/Users/patrick/dev/ucl/comp0158_mscproject/data/corpus/output/pre_corpus.dat"
    
    
    with open(input_dat, 'r') as file:
        for line_number, line in enumerate(file):    
            #print('\nline:',line.strip('\n'))
            cols            = line.split('|')
            
            protein_info = cols[0]
            token_info = cols[1]
            
            print('protein:', protein_info, 'token:', token_info)
            
            
            
            last_pfam_protein_id = ""
            #token_line       = ""
            token_line = ':'.join([protein_id, protein_start, protein_end]) +'|'
            #print('token_line start:', token_line)
            
            #
            # GET PFAM AND DISORDER TOKENS FROM DB
            #
            #pfam_tokens = con.execute("SELECT * FROM PFAM_TOKEN WHERE UNIPROT_ID = (?)", [protein_id]).fetchall()
            #disorder_tokens = con.execute("SELECT * FROM PROTEIN_FEATURE WHERE UNIPROT_ID = (?)", [protein_id]).fetchall()
            
            pfam_tokens = con.execute("SELECT * FROM W2V_PFAM_TOKEN WHERE UNIPROT_ID = (?)", [protein_id]).fetchall()
            disorder_tokens = con.execute("SELECT * FROM W2V_DISORDER_TOKEN WHERE UNIPROT_ID = (?)", [protein_id]).fetchall()
            tokens = con.execute("SELECT * FROM W2V_TOKEN WHERE UNIPROT_ID = (?)", [protein_id]).fetchall()
            
            #
            # PFAM TOKENS
            # 
            pfam = False
            if pfam_tokens is not None and len(pfam_tokens) >0:
                pfam = True
                for item in pfam_tokens:
                    pfam_protein_id = item[0]
                    
                    # if this is first time, remember what protein we have found
                    # and create first part of output line, 
                    if(last_pfam_protein_id == ""):
                        last_pfam_protein_id = pfam_protein_id
                        #token_line = pfam_protein_id + '|' + item[1] + ':' + str(item[2]) +  ':' + str(item[3])
                        token_line = token_line + item[1] + ':' + str(item[2]) +  ':' + str(item[3])
                        continue
                    
                    # if not first time through and we have already found this protein, append to line
                    if (pfam_protein_id == last_pfam_protein_id):
                        pfam_line_extra = '|' + item[1] + ':' + str(item[2]) + ':' + str(item[3])
                        token_line = token_line + pfam_line_extra
                    
                    # if not first time and we have a new protein, then print the current line and start a new one
                    else:
                        last_pfam_protein_id = pfam_protein_id
                        token_line = token_line + '|' + item[1] + ':' + str(item[2]) +  ':' + str(item[3])
                
            # A0A010PZP8 has pfam and disorder entries
            if disorder_tokens is not None and len(disorder_tokens) > 0:
                #print(protein_id, ' PF :', token_line)
                #print(protein_id, ' DIS:', disorder_tokens )
                
                if(len(token_line) == 0):
                    disorder_entries = protein_id + 'DISORDER'
                else:
                    if(pfam):
                        disorder_entries = '|DISORDER'
                    else:
                        disorder_entries = 'DISORDER'
                for disorder_item in disorder_tokens:
                    disorder_entries = disorder_entries + ':' + str(disorder_item[3]) + ':' + str(disorder_item[4])
                token_line = token_line + disorder_entries

            record_count += 1
            
            # write out current line
            if(len(token_line) > 0):
                #print('final output:', token_line)
                output_file.write(token_line +'\n')
            
                
            # -------- check for termination ------------
            if (record_count % OUTPUT_LIMIT == 0):
                mid_time_end = time.time()
                t = mid_time_end - mid_time_start
                mid_time_start = mid_time_end
                print(OUTPUT_LIMIT, 'lines processed in ', t, 's', 'total:', record_count)
                
            if(PROCESS_LIMIT != -1):
                if record_count >= PROCESS_LIMIT:
                    print('limit reached, returning')
                    break
                
    con.close()
    output_file.close()
    
    end_time = time.time()
    exec_time = end_time - start_time
    print(record_count, 'proteins processed in ', exec_time, 's')
    
#combine_tokens()