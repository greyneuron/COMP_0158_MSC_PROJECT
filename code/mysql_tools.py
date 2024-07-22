import mysql.connector
import time



def create_pre_corpus(from_record, chunk_size, iteration):
    
    output_name     = "precorpus/pre_corpus_20240722_" + str(iteration) + '.dat'
    
    print('pre-corpus creation, iteration', iteration, 'from protein', from_record,'output file:', output_name)
    
    s   = time.time()
    of  = open(output_name, "w")
    
    size = int(chunk_size)
    fr = int(from_record)
    
    try:
        con = mysql.connector.connect(user='admin', password='w0rd2v3c', host='w2v-rds-db.cligs4ak0dtg.eu-west-1.rds.amazonaws.com', database='W2V')
        #print('...connected')
        cursor = con.cursor()
        
        query = f"SELECT W2V_PROTEIN.UNIPROT_ID, W2V_TOKEN.* FROM (SELECT UNIPROT_ID FROM W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT {fr}, {size}) AS W2V_PROTEIN INNER JOIN W2V_TOKEN AS W2V_TOKEN ON W2V_PROTEIN.UNIPROT_ID = W2V_TOKEN.UNIPROT_ID"
        cursor.execute(query)
        e = time.time()
        
        #print('query took', str(e-s), 'ms')
        
        results = cursor.fetchall()
        #print(len(results), 'results')
        
        if(len(results) >0):
            for res in results:
                output_line = "|".join([res[0], res[2], res[3], str(res[4]), str(res[5])])
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
        return 
        
    

#
# This took 6.47 seconds to query 1M records from W2V_TOKEN
#
def output_query():
    print('output query - trying to connect...')
    
    try:
        s = time.time()
        con = mysql.connector.connect(user='admin', password='w0rd2v3c', host='w2v-rds-db.cligs4ak0dtg.eu-west-1.rds.amazonaws.com', database='W2V')
        #print('connected')
        
        cursor = con.cursor()
        
        #query = ("SELECT * FROM W2V_TOKEN WHERE UNIPROT_ID = 'A0A010PZU8'")
        #query = "SELECT * FROM W2V_TOKEN ORDER BY UNIPROT_ID LIMIT 1000000" # query first 1M items
        #query = "SELECT * FROM W2V_TOKEN ORDER BY UNIPROT_ID LIMIT 5000000, 10" # query first 10 items after 5M items - taking ages
        
        # these work
        # select first n proteins and query all tokens - 100k took 4.29s, 1M took 23s
        #query = "SELECT W2V_PROTEIN.UNIPROT_ID, W2V_TOKEN.* FROM (SELECT UNIPROT_ID FROM W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT 1000000) AS W2V_PROTEIN INNER JOIN W2V_TOKEN AS W2V_TOKEN ON W2V_PROTEIN.UNIPROT_ID = W2V_TOKEN.UNIPROT_ID"
        
        # Select 1M proteins after the first 2M. Took 32s compared to 23s for first 1M
        # Select 1M proteins after the first 10M. Query took 5s, overall took 48s
        query = f"SELECT W2V_PROTEIN.UNIPROT_ID, W2V_TOKEN.* FROM (SELECT UNIPROT_ID FROM W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT 10000000, 1000000 AS W2V_PROTEIN INNER JOIN W2V_TOKEN AS W2V_TOKEN ON W2V_PROTEIN.UNIPROT_ID = W2V_TOKEN.UNIPROT_ID"
        
        query_2 = f"SELECT * FROM W2V_TOKEN WHERE UNIPROT_ID = '{uniprot_id}'"

        print('executing query....')
        cursor.execute(query)
        e = time.time()
        print('query took', str(e-s), 'ms')
        
        for res in cursor:
            print(res[0], '|', res[2], '|', res[3], '|', res[4], '|', res[5])
        
        e = time.time()
        print('entire execution took', str(e-s), 'ms end to end')
    except:
        print('error connecting')
    
   
def connect():
    """ Connect to MySQL database """
    print('trying to connect...')
    
    try:
        con = mysql.connector.connect(user='admin', password='w0rd2v3c', host='w2v-rds-db.cligs4ak0dtg.eu-west-1.rds.amazonaws.com', database='W2V')
        print('connected')
        
        cursor = con.cursor()
        uniprot_id = "A0A010PZU8"

        # ---- test with hardcoded string : this works
        print('hardcoded test')
        query = ("SELECT * FROM W2V_TOKEN WHERE UNIPROT_ID = 'A0A010PZU8'")
        cursor.execute(query)
        
        for res in cursor:
            print(res)
        print('hardcoded test - success')
         
        # ---- test with parameterised string : also works
        print('parameterised test')
        query_2 = f"SELECT * FROM W2V_TOKEN WHERE UNIPROT_ID = '{uniprot_id}'"
        cursor.execute(query_2)
        
        for res in cursor:
            print(res)
        print('hardcoded test - success')

        # close connection
        cursor.close()
        con.close()
        
    except:
        print('error connecting')



if __name__ == '__main__':
    #connect()
    #output_query()
    
    start       = 0
    chunk_size  = 500000
    iteration   = 1
    result = 0
    
    print('processing in chunks of', chunk_size)
    while(result != -1):
        result = create_pre_corpus(start, chunk_size, iteration)
        iteration +=1
        start += chunk_size
        
    print('...end')