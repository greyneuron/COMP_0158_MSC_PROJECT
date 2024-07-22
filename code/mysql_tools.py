import mysql.connector
import time


#
# Used on 22 July to create pre-cprpus
#
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
        

# queries unique pfam records
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


    
# this is just to test the conection
def connection_test():
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


#
# main
#
if __name__ == '__main__':

    '''
    # create pre-corpus file in chunks of 500k proteins
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
    '''
    
    #get unique pfam entries
    print('gettting unique pfam entries')
    get_unique_pfam()