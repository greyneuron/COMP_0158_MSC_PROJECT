import mysql.connector

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
    connect()
