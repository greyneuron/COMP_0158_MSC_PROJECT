import mysql.connector

# make sure to create db first
# connect to mysql from ssh
# mysql -h w2v-dev-db.cligs4ak0dtg.eu-west-1.rds.amazonaws.com -P 3306 -u w2v -p
# CREATE DATABASE w2v_db;

# Database connection
conn = mysql.connector.connect(
    host="w2v-dev-db.cligs4ak0dtg.eu-west-1.rds.amazonaws.com",
    user="w2v",
    password="w0rd2v3c",
    database="w2v_db"
)
cursor = conn.cursor()

# Create table (if not exists)
cursor.execute("""
    CREATE TABLE PFAM_TOKEN (uniprot_id VARCHAR(16), token VARCHAR(16), start INT, end INT)
""")

# Load data
load_data_query = """
    LOAD DATA LOCAL INFILE '/data/dev/ucl/data/pfam/protein2ipr_pfam_20240715.dat' INTO TABLE PFAM_TOKEN FIELDS TERMINATED BY '|';
    
    LOAD DATA LOCAL INFILE '/data/dev/ucl/data/pfam/pfam_test_data.dat' INTO TABLE PFAM_TOKEN FIELDS TERMINATED BY '|';
    
    
"""
cursor.execute(load_data_query)

# Commit and close
conn.commit()
cursor.close()
conn.close()
