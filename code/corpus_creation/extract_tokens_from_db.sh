#!/bin/bash

# This script queries mysql directly to find all tokens for a set of proteins
# It takes about 3min to find ll tokens for 1M proteins and outputs to a file
# the file has one line per row returned- i e multiple proteins duplicated
# the file is tab delimeted but you cnnot change the delimeter

# It assume there are 2 tables in the database: W2V_PROTEIN and W2V_TOKEN
# 
# W2V_TOKEN (uniprot_id VARCHAR(16), type VARCHAR(16), token VARCHAR(64), start INT, end INT);
# W2V_PROTEIN (uniprot_id VARCHAR(16), start INT, end INT);
#
#

# TODO: SET THESE VARIABLES
endpoint="w2v-db-1.cligs4ak0dtg.eu-west-1.rds.amazonaws.com"
start=0
chunk=10
id="A0A074Y5L9"

'''
# works - loop from 0 to 10
for i in {0..1}
do
  # Create a file with the counter as its name
    #echo "connection $i"
    start=$((i*10))
    grep "${i}0" test.txt
    #export file_name=("sql_output" + $1 + "test.txt")
    
done
'''



# this works
#/usr/local/opt/mysql-client/bin/mysql -h $endpoint -P 3306 -u admin W2V -pw0rd2v3c -e "DESC W2V_TOKEN"

# this also works
#/usr/local/opt/mysql-client/bin/mysql -h $endpoint -P 3306 -u admin W2V -pw0rd2v3c -e "SELECT * FROM W2V_TOKEN WHERE UNIPROT_ID='${id}'"

# also works
#/usr/local/opt/mysql-client/bin/mysql -h $endpoint -P 3306 -u admin W2V -pw0rd2v3c -e "SELECT * FROM W2V_PROTEIN LIMIT ${start}, ${chunk}"

'''
# this works
new_start=0
new_chunk=2
for i in {0..5}
do
  # Create a file with the counter as its name
    #echo "connection $i"
    echo "starting at" $start
    #/usr/local/opt/mysql-client/bin/mysql -h $endpoint -P 3306 -u admin W2V -pw0rd2v3c -e "SELECT * FROM W2V_PROTEIN LIMIT ${start}, ${chunk}"
    /usr/local/opt/mysql-client/bin/mysql -h $endpoint -P 3306 -u admin W2V -pw0rd2v3c -e "SELECT * FROM W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT ${start}, ${chunk}"
    start=$((start + chunk))
done
'''


start_pos=0
chunk_size=2

for i in {0..5}
do
    echo "starting at" $start_pos
    # works
    #/usr/local/opt/mysql-client/bin/mysql -h $endpoint -P 3306 -u admin W2V -pw0rd2v3c -e "SELECT * FROM W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT ${start_pos}, ${chunk_size}"

    # also works (hooray)
    /usr/local/opt/mysql-client/bin/mysql -h $endpoint -P 3306 -u admin W2V -pw0rd2v3c -e "SELECT W2V_PROTEIN.*, W2V_TOKEN.* FROM ( SELECT UNIPROT_ID, START, END FROM W2V_PROTEIN W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT ${start_pos}, ${chunk_size}) AS W2V_PROTEIN INNER JOIN W2V_TOKEN AS W2V_TOKEN ON W2V_PROTEIN.UNIPROT_ID = W2V_TOKEN.UNIPROT_ID"

    start_pos=$((start_pos + chunk_size))
done