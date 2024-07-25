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
start_pos=0
chunk_size=5
num_iterations=4


#echo "Querying database"
#for i in $(seq 0 5); 
#do
#    echo "iteration" $i "starting at" $start_pos
#    touch sql_output_${i}.txt

    # also works (hooray)
#    /usr/local/opt/mysql-client/bin/mysql -h $endpoint -P 3306 -u admin W2V -pw0rd2v3c -e "SELECT W2V_PROTEIN.*, W2V_TOKEN.* FROM ( SELECT UNIPROT_ID, START, END FROM W2V_PROTEIN W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT ${start_pos}, ${chunk_size}) AS W2V_PROTEIN INNER JOIN W2V_TOKEN AS W2V_TOKEN ON W2V_PROTEIN.UNIPROT_ID = W2V_TOKEN.UNIPROT_ID" >> sql_output_${i}.txt
    
    # cat the result and grep it
#    cat sql_output_${i}.txt | awk '{FS ="\t"} {print $1 ":" $2 ":" $3 "|" $5 ":" $6 ":" $7 ":" $8}' >> sql_output_${i}.dat
#
#    start_pos=$((start_pos + chunk_size))
#done


ignore_line="UNIPROT_ID"
echo "creating dat files"
for i in $(seq 0 1); 
do
  touch sql_output_${i}.dat
  # works but includes some lines that aren;t needed
  #cat sql_output_${i}.txt | awk '{FS ="\t"} {print $1 ":" $2 ":" $3 "|" $5 ":" $6 ":" $7 ":" $8}' >> sql_output_${i}.dat
  
  # works and ignores lines beginning with the word UNIPROT
  cat sql_output_${i}.txt | awk '{FS ="\t"} {if (!($1~/^UNIPROT/)) print $1 ":" $2 ":" $3 "|" $5 ":" $6 ":" $7 ":" $8}' >> sql_output_${i}.dat
done