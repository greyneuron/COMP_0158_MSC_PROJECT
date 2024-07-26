#!/bin/bash

# This script is step 1 of 4 to get a sentence to pass into word2vec
# It assumes there is a database with two tables :W2V_PROTEIN and W2V_TOKEN
#
# 4 steps:
# 1. ** THIS SCRIPT ** : Runs sql from the mysql command line and pipes it to an output file : sql_output_<startprotein>_<iteration>.txt
#    You need to change the start poisitoin and chunk size and number of iterations
#    I found that it would iterate through 500k proteins in about 3.5mins so I would set the chunk size to 500000 and iterate from 0..9 to get 10M
# 2. convert_db_tokens_dat.sh converts each of the txt outputs from step 1 into a dat file of pipe separated tokens - each line has a token and its corresponding uniprot id
# 3. The next script then converts those lines into a single line per protein
# 4. The final script then creates a sentence for each protein with GAP DISORDER and PFAM

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
start_pos=30000000
chunk_size=500000
output_dir="output"

file_start=${start_pos}

#echo "Querying database"
for i in $(seq 0 19); 
do  
    SECONDS=0
    echo "iteration" $i ": starting at" $start_pos

    # create emty target files
    touch ${output_dir}/sql_output_${file_start}_${i}.txt

    # for local
    #/usr/local/opt/mysql-client/bin/mysql -h $endpoint -P 3306 -u admin W2V -pw0rd2v3c -e "SELECT W2V_PROTEIN.*, W2V_TOKEN.* FROM ( SELECT UNIPROT_ID, START, END FROM W2V_PROTEIN W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT ${start_pos}, ${chunk_size}) AS W2V_PROTEIN INNER JOIN W2V_TOKEN AS W2V_TOKEN ON W2V_PROTEIN.UNIPROT_ID = W2V_TOKEN.UNIPROT_ID" >> ${output_dir}/sql_output_${file_start}_${i}.txt
    
    
    # for aws ec2 and rds
    mysql -h $endpoint -P 3306 -u admin W2V -pw0rd2v3c -e "SELECT W2V_PROTEIN.*, W2V_TOKEN.* FROM ( SELECT UNIPROT_ID, START, END FROM W2V_PROTEIN W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT ${start_pos}, ${chunk_size}) AS W2V_PROTEIN INNER JOIN W2V_TOKEN AS W2V_TOKEN ON W2V_PROTEIN.UNIPROT_ID = W2V_TOKEN.UNIPROT_ID" >> ${output_dir}/sql_output_${file_start}_${i}.txt
    
    # cat the result and grep it
    #cat sql_output_${i}.txt | awk '{FS ="\t"} {print $1 ":" $2 ":" $3 "|" $5 ":" $6 ":" $7 ":" $8}' >> sql_output_${i}.dat
    duration=$SECONDS
    echo "iteration ${i} duration : $((duration / 60)) min $((duration % 60)) s."

    start_pos=$((start_pos + chunk_size))
done


#ignore_line="UNIPROT_ID"
#echo "creating dat files"
#for i in $(seq 0 1); 
#do
#  touch sql_output_${i}.dat
  # works but includes some lines that aren;t needed
  #cat sql_output_${i}.txt | awk '{FS ="\t"} {print $1 ":" $2 ":" $3 "|" $5 ":" $6 ":" $7 ":" $8}' >> sql_output_${i}.dat
  
  # works and ignores lines beginning with the word UNIPROT
#  cat sql_output_${i}.txt | awk '{FS ="\t"} {if (!($1~/^UNIPROT/)) print $1 ":" $2 ":" $3 "|" $5 ":" $6 ":" $7 ":" $8}' >> sql_output_${i}.dat
#done