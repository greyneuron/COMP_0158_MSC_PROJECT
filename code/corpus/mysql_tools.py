import mysql.connector
import time
import sys

#
# This set of scripts was used to extract all tokens and protein information from the 
# database. I used an AWS RDS instance for this and connected over EC2.
#
# For some reason this script was incredibly slow compared to executing the same SQL 
# directly through a SQL command line on EC2 connecting to the separate RDS instance.
# I also tried loading MySQL onto the same EC@ instance but that was even slower.
#
# After much trial and error I eventally switched to using shell scripts in the 'corpus' directory instead
# I also created an RDS instance from the AWS console instead of from Terraform - this seemed to 
# work better, probably due to some missing config that wasn;t included in Terraform



# get this info from the RDS DATABASE console in AWS
db_host     ="w2v-db-1.cligs4ak0dtg.eu-west-1.rds.amazonaws.com"
db_user     = "admin"
db_password = "w0rd2v3c"
db_database = "W2V"

#
# returns a connection
#
def test_connection():
    print('Database connection test......')
    try:
        con = mysql.connector.connect(user=db_user, password=db_password, host=db_host, database=db_database)
    except Exception as e:
        print('unable to get connection', e)
        return None
    print('Connection successful')
    con.close()
    return


def create_precorpus_from_sql():
    return

#
# WORKS - Used on 22 July and modified to include protein info
# for some reason the query to include protein info runs a lot slower
#
def create_precorpus(from_record, chunk_size, filename, iteration):
    s   = time.time()
    #of  = open(output_name, "w")
    
    size = int(chunk_size)
    fr = int(from_record)
    print('\tprecorpus from', from_record,'chunk', chunk_size, 'it:', iteration, 'filename:', filename)
    
    if iteration == 1:
        of = open(filename, "w")
    else:
        of = open(filename, "a")
    
    try:
        con = mysql.connector.connect(user='admin', password='w0rd2v3c', host=db_host, database='W2V')
        cursor = con.cursor()
        
        # Note that this query wil find 'size' proteins but only return rows in tokens that have a match - hence yo might get some with no matches
        query = f"SELECT W2V_PROTEIN.*, W2V_TOKEN.* FROM ( SELECT UNIPROT_ID, START, END FROM W2V_PROTEIN W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT {fr}, {size}) AS W2V_PROTEIN INNER JOIN W2V_TOKEN AS W2V_TOKEN ON W2V_PROTEIN.UNIPROT_ID = W2V_TOKEN.UNIPROT_ID"
        
        # SELECT W2V_PROTEIN.*, W2V_TOKEN.* FROM ( SELECT UNIPROT_ID, START, END FROM W2V_PROTEIN W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT 0, 20) AS W2V_PROTEIN INNER JOIN W2V_TOKEN AS W2V_TOKEN ON W2V_PROTEIN.UNIPROT_ID = W2V_TOKEN.UNIPROT_ID;
        #SELECT W2V_PROTEIN.*, W2V_TOKEN.* FROM ( SELECT UNIPROT_ID, START, END FROM W2V_PROTEIN W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT 10, 10) AS W2V_PROTEIN INNER JOIN W2V_TOKEN AS W2V_TOKEN ON W2V_PROTEIN.UNIPROT_ID = W2V_TOKEN.UNIPROT_ID;
        #SELECT W2V_PROTEIN.* FROM W2V_PROTEIN W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT 0, 20;
        # SELECT * FROM W2V_TOKEN WHERE UNIPROT_ID='A0A010PZJ8';returns 4 rows
        
        cursor.execute(query)
        e = time.time()
        
        results = cursor.fetchall()
        
        last_protein    = "start"
        current_protein = ""
        protein_buffer  = ""
        
        if(len(results) > 0):
            for res in results:
                #print(res)
                current_protein = res[0]
                # if the curent result line is for a new protein (ie the protine id at the start of the output has changed)
                if (last_protein == "start" or current_protein != last_protein ):
                    if(last_protein != "start"):
                        of.write(protein_buffer + '\n')
                    protein_start   = res[1]
                    protein_end     = res[2]
                    last_protein    = current_protein
                    protein_buffer = ':'.join([current_protein, str(protein_start), str(protein_end)])
                token_type = res[4]
                if (token_type == "DISORDER"):
                    protein_buffer = protein_buffer + '|' + token_type + ':' + str(res[6]) + ':' + str(res[7])
                    #print('Token:', token_type, res[5], res[6])
                elif (token_type == "PFAM"):
                    #print('Token:', res[4], res[5], res[6])
                    protein_buffer = protein_buffer + '|' + res[5] + ':' + str(res[6]) + ':' + str(res[7])
                #print(protein_buffer)
            # write last result
            of.write(protein_buffer + '\n')
        else:
            # just means this iteration had no results
            print('No results returned')
            of.close()
            con.close()
            return 1
        # end of results    
        e = time.time()
        #print('entire execution took', str(e-s), 'ms end to end')
        of.close()
        con.close()
        return 1
    # exception
    except Exception as e:
        print('error connecting', e)
        of.close()
        #con.close()
        return -1 



#
# WORKS - Used on 22 July and modified to include protein info
# for some reason the query to include orotein info runs a lot slower
#
def create_pre_corpus_v2(from_record, chunk_size, iteration):
    
    output_name     = "precorpus/20240725/precorpus_20240725_v2_" + str(iteration) + '.dat'
    
    print('pre-corpus creation, iteration', iteration, 'from protein', from_record,'output file:', output_name)
    
    s       = time.time()
    of      = open(output_name, "w")
    size    = int(chunk_size)
    fr      = int(from_record)
    
    try:
        con = mysql.connector.connect(user='admin', password='w0rd2v3c', host=db_host, database='W2V')
        cursor = con.cursor()
        
        query = f"SELECT W2V_PROTEIN.*, W2V_TOKEN.* FROM ( SELECT UNIPROT_ID, START, END FROM W2V_PROTEIN W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT {fr}, {size}) AS W2V_PROTEIN INNER JOIN W2V_TOKEN AS W2V_TOKEN ON W2V_PROTEIN.UNIPROT_ID = W2V_TOKEN.UNIPROT_ID"
        
        cursor.execute(query)
        e = time.time()
        
        results = cursor.fetchall()
        
        last_protein    = "start"
        current_protein = ""
        protein_buffer  = ""
        
        if(len(results) > 0):
            for res in results:
                #print(res)
                current_protein = res[0]
                
                # if the curent result line is for a new protein (ie the protine id at the start of the output has changed)
                if (last_protein == "start" or current_protein != last_protein ):
                    if(last_protein != "start"):
                        of.write(protein_buffer + '\n')
                    protein_start   = res[1]
                    protein_end     = res[2]
                    last_protein    = current_protein
                    protein_buffer = ':'.join([current_protein, str(protein_start), str(protein_end)])
                token_type = res[4]
                
                # for a disprder token
                if (token_type == "DISORDER"):
                    protein_buffer = protein_buffer + '|' + token_type + ':' + str(res[6]) + ':' + str(res[7])
                    #print('Token:', token_type, res[5], res[6])
                
                # for a pfam token
                elif (token_type == "PFAM"):
                    #print('Token:', res[4], res[5], res[6])
                    protein_buffer = protein_buffer + '|' + res[5] + ':' + str(res[6]) + ':' + str(res[7])
        else:
            print('No results returned')
            of.close()
            con.close()
            return 1
        # end of results    
        e = time.time()
        print('entire execution took', str(e-s), 'ms end to end')
        of.close()
        con.close()
        return 1
    # exception
    except Exception as e:
        print('error connecting', e)
        of.close()
        con.close()
        return -1




#
# main
#
if __name__ == '__main__':
        
    # 10,000 and 50 - dies on iteration 22
    # 1000 and 100 ok
    # 1000 and 1000 - each iteration takes about 0.25s => 1M to take 250s but stopped on 221
    # Iteration 23 220000 10000 query time: 127.24671959877014 ms Results found: 14327 ITERATION 23  Iteration time: 127.3628249168396 ms

    # this is what I used on Tuesday
    print("Precorpus creation - using Tuesday approach of 250k chunks")
    chunk_size      = 250000
    num_iterations  = 320
    iteration       = 1
    result          = 0
    start           = 0

    s = time.time()
    print('START. Processing', num_iterations * chunk_size, 'proteins in chunks of', chunk_size)

    while(result != -1 and iteration <= num_iterations):
        #result = test_chunk(start, chunk_size, iteration)
        
        result = create_pre_corpus_v2(start, chunk_size, iteration)
        
        iteration +=1
        start += chunk_size
    e = time.time()

    print('COMPLETE. Total time for:', num_iterations * chunk_size, 'proteins', str(e-s), 'ms')
    
    # end of Tuesday
    
    
    '''
    
    # start of Thursday
    print("Precorpus creation - using Thursday approach")
    print('arguments:', sys.argv)
    
    print('start position:', sys.argv[1])
    #print('file id:', sys.argv[2])
    #test_connection()
    
    
    #proteins_per_file = 5000000 #15M
    #chunk_size        = 200000  # how many proteins to search for in DB one go - these are joined against the W2V_TOKEN table
    
    proteins_per_file = 500000 #15M
    chunk_size        = 1000  # how many proteins to search for in DB one go - these are joined against the W2V_TOKEN table
    
    # get command line arg
    start_pos           = int(sys.argv[1])
    
    if (proteins_per_file % chunk_size) != 0:
        print("error, chunk size must divide into proteins per file evenly")
        
        
    num_iterations  = proteins_per_file / chunk_size     # number of chunks in this exeution (all will go in one file gives 15M)
    
    # initialise
    iteration       = 1     # tracks
    result          = 0
    file_name     = "precorpus/20240725/precorpus_x2_" + str(start_pos) + '.dat'

    print('START. Processing', proteins_per_file, 'proteins in', num_iterations, 'iterations with chunks of', chunk_size, '. Output:', file_name)

    s   = time.time()
    s1   = time.time()
    
    while(result != -1 and iteration <= num_iterations):

        s1   = time.time()
        result = create_precorpus(start_pos, chunk_size, file_name, iteration)
        e = time.time()
        print(' - iteration', iteration, 'time taken:', str(e-s1), 's')
        
        iteration +=1
        start_pos += chunk_size
        
    e = time.time()
    print('COMPLETE. Total time for:', num_iterations * chunk_size, 'proteins', str(e-s), 's output:', file_name)
    

    '''







'''   
#
# alternative way to get results
# took 3s to do 1000 - but lots of that might be connection time; 10000 took 4.3s
#
def test_chunk(fr, size, iteration):
    s = time.time()
    print('\nIteration', iteration, fr, size)
    output_name     = "precorpus/pre_corpus_20240723_new_" + str(iteration) + '.dat'
    try:
        of  = open(output_name, "w")
        
        con     = mysql.connector.connect(user=db_user, password=db_password, host=db_host, database='W2V')
        cursor  = con.cursor()
        
        # this takes ages
        # query = f"SELECT W2V_PROTEIN.*, W2V_TOKEN.TYPE, W2V_TOKEN.TOKEN, W2V_TOKEN.START, W2V_TOKEN.END FROM (SELECT UNIPROT_ID, START, END FROM W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT {fr}, {size}) AS W2V_PROTEIN INNER JOIN W2V_TOKEN AS W2V_TOKEN ON W2V_PROTEIN.UNIPROT_ID = W2V_TOKEN.UNIPROT_ID"
        
        # this is also slow
        #query = f"SELECT T1.UNIPROT_ID, T1.START, T1.END, T2.TYPE, T2.TOKEN, T2.START, T2.END FROM W2V_PROTEIN AS T1 INNER JOIN W2V_TOKEN AS T2 ON T1.UNIPROT_ID = T2.UNIPROT_ID LIMIT {fr}, {size}"
        
        # this worked fine on Monday and is till pretty fast - 100k queried in 1.8s and written in 17.6 seconds 
        #query = f"SELECT W2V_PROTEIN.UNIPROT_ID, W2V_TOKEN.* FROM (SELECT UNIPROT_ID FROM W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT {fr}, {size}) AS W2V_PROTEIN INNER JOIN W2V_TOKEN AS W2V_TOKEN ON W2V_PROTEIN.UNIPROT_ID = W2V_TOKEN.UNIPROT_ID"
        
        # THIS WORKS FASTER - NOT SURE WHY : DID 1M PROTEINS in 19s using 10 x 100k chunks (BUT DIDN:T GET PROTEIN START AND END)
        #query = f"SELECT W2V_PROTEIN.*, W2V_TOKEN.* FROM (SELECT UNIPROT_ID FROM W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT {fr}, {size}) AS W2V_PROTEIN INNER JOIN W2V_TOKEN AS W2V_TOKEN ON W2V_PROTEIN.UNIPROT_ID = W2V_TOKEN.UNIPROT_ID"
        
        
        
        # GETS ALL INFO NEEDED - BUT STRUGGLES WITH CHUNK OF 100k - db.t3.xlarge
        #query = f"SELECT W2V_PROTEIN.*, W2V_TOKEN.* FROM (SELECT UNIPROT_ID, START, END FROM W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT {fr}, {size}) AS W2V_PROTEIN INNER JOIN W2V_TOKEN AS W2V_TOKEN ON W2V_PROTEIN.UNIPROT_ID = W2V_TOKEN.UNIPROT_ID"
        
        # this query is fast from the sql command line - took 15s with 2,000,000, 100,000
        query = f"SELECT T1.UNIPROT_ID, T1.START, T1.END, T2.TYPE, T2.TOKEN, T2.START, T2.END FROM W2V_PROTEIN T1 INNER JOIN W2V_TOKEN T2 ON T1.UNIPROT_ID = T2.UNIPROT_ID LIMIT {fr}, {size}"
        
        cursor.execute(query)
        
        e = time.time()
        print('query time:', str(e-s), 'ms')
        
        results = cursor.fetchall()
        print('Results found:', len(results))
        
        i = 0
        last_protein    = "start"
        current_protein = ""
        protein_buffer  = ""
        
        if(len(results) > 0):
            for res in results:
                print('res', i, ':', res)
                
                current_protein = res[0]
                # if the curent result line is for a new protein (ie the protine id at the start of the output has changed)
                if (last_protein == "start" or current_protein != last_protein ):
                    protein_start   = res[1]
                    protein_end     = res[2]
                    last_protein    = current_protein
                    protein_buffer = ':'.join([current_protein, str(protein_start), str(protein_end)])
                    #print('New protein:', protein_buffer)
                # if the curent result line is for a protein we're already processing (ie the protine id at the start of the output has changed)
                #else:
                #    print('Existing protein', last_protein, current_protein)
                token_type = res[4]
                if (token_type == "DISORDER"):
                    protein_buffer = protein_buffer + '|' + token_type + ':' + str(res[6]) + ':' + str(res[7])
                    #print('Token:', token_type, res[5], res[6])
                elif (token_type == "PFAM"):
                    #print('Token:', res[4], res[5], res[6])
                    protein_buffer = protein_buffer + '|' + res[5] + ':' + str(res[6]) + ':' + str(res[7])
                
                #print(protein_buffer)
                of.write(protein_buffer + '\n')
                i+=1
            #output_line = "|".join([res[0], res[2], res[3], str(res[4]), str(res[5])])
    except Exception as e:
        print('error connecting', e)
        con.close()
        of.close()
        return -1
    #print('closing connection')
    con.close()
    of.close()
    e = time.time()
    print('ITERATION', iteration, ' Iteration time:', str(e-s), 'ms')
    return 0

'''












'''
# THIS WORKS _ JUST COMMENTED OUT TO AVOID CONFUSION
#
# WORKS - Used on 22 July and modified to include protein info
# for some reason the query to include orotein info runs a lot slower
#
def create_pre_corpus(from_record, chunk_size, iteration):
    
    output_name     = "precorpus/pre_corpus_20240724a_" + str(iteration) + '.dat'
    
    print('pre-corpus creation, iteration', iteration, 'from protein', from_record,'output file:', output_name)
    
    s   = time.time()
    of  = open(output_name, "w")
    
    size = int(chunk_size)
    fr = int(from_record)
    
    try:
        con = mysql.connector.connect(user='admin', password='w0rd2v3c', host=db_host, database='W2V')
        #print('...connected')
        cursor = con.cursor()
        
        # CHANGED THIS
        #query = f"SELECT W2V_PROTEIN.UNIPROT_ID, W2V_TOKEN.* FROM (SELECT UNIPROT_ID FROM W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT {fr}, {size}) AS W2V_PROTEIN INNER JOIN W2V_TOKEN AS W2V_TOKEN ON W2V_PROTEIN.UNIPROT_ID = W2V_TOKEN.UNIPROT_ID"
        
        query = f"SELECT W2V_PROTEIN.*, W2V_TOKEN.* FROM ( SELECT UNIPROT_ID, START, END FROM W2V_PROTEIN W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT {fr}, {size}) AS W2V_PROTEIN INNER JOIN W2V_TOKEN AS W2V_TOKEN ON W2V_PROTEIN.UNIPROT_ID = W2V_TOKEN.UNIPROT_ID"
        
        cursor.execute(query)
        e = time.time()
        
        #print('query took', str(e-s), 'ms')
        
        results = cursor.fetchall()
        #print(len(results), 'results')
        
        if(len(results) >0):
            
            for res in results:
                #print ('result :', res)
                #output_line = "|".join([res[0], res[2], res[3], str(res[4]), str(res[5])]) # yesterday
                token_type = res[3]
                if token_type == "PFAM":
                    output_line = "|".join([res[0], str(res[1]), str(res[2]), res[4], res[5], str(res[6]), str(res[7])])
                else:
                    output_line = "|".join([res[0], str(res[1]), str(res[2]), res[4], str(res[6]), str(res[7])])
                #of.write(res[0], '|', res[2], '|', res[3], '|', res[4], '|', res[5])
                of.write(output_line + '\n')
                #print(res[0], '|', res[2], '|', res[3], '|', res[4], '|', res[5])
        else:
            print('No results returned')
            of.close()
            con.close()
            return -1
            
        e = time.time()
        print('entire execution took', str(e-s), 'ms end to end')
        of.close()
        con.close()
        return 1
        
    except Exception as e:
        print('error connecting', e)
        of.close()
        con.close()
        return -1 
'''


# ------------------------------------------------------------------------------------------------------------
#
#
# ------------------------------------------------------------------------------------------------------------






# ------------------------------------------------------------------------------------------------------------
#
#                                   IGNORE BELOW HERE
#
# ------------------------------------------------------------------------------------------------------------





#
# just use this to tes various quick queries
#
def test_query():
    print('Test query')
    try:
        con = get_connection()
        if (con != None):
            cursor = con.cursor()
            query = ("DESCRIBE W2V_PROTEIN")

            cursor.execute(query)
            result = cursor.fetchall()
            print('Test result\n', result)
        else:
            print('No connection')
    except Exception as e:
        print('error connecting', e)
        con.close()
        return
#test_query()





#
# queries unique pfam records
#
def get_unique_pfam():
    output_name     = "unique_corpus_pfam_20240722.dat"
    of  = open(output_name, "w")
    
    try:
        con = mysql.connector.connect(user='admin', password='w0rd2v3c', host='w2v-rds-db.cligs4ak0dtg.eu-west-1.rds.amazonaws.com', database='W2V')
        #print('...connected')
        cursor = con.cursor()
        
        query = "SELECT DISTINCT TOKEN FROM W2V_TOKEN WHERE TYPE='PFAM' ORDER BY TOKEN"
        cursor.execute(query)

        results = cursor.fetchall()

        if(len(results) >0):
            print(len(results), 'results returned')
            for res in results:
                of.write(res[0] + '\n')
        else:
            print('No results returned')  
        of.close()
        con.close()
        return
    except Exception as e:
        print('Error connecting', e)
        of.close()
        con.close()
        return 

