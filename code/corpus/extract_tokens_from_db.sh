#!/bin/bash

# ------ Background------ 
#
# This script is step 1 of 5 to create sentences to form a corpus for word2vec
#
# 5 steps:
# 1. extract_tokens_from_db.sh : Runs sql from the mysql command line and pipes it to an output file : sql_output_<startprotein>_<iteration>.txt
# 2. convert_db_tokens_dat.sh  : Converts each of the txt outputs from step 1 into a dat file of pipe separated tokens.
#    Each line consists of information about a token and its corresponding uniprot id
# 3. combine_db_tokens_dat.py : Converts each lines (one per token) into a single line per protein (each line with multiple tokens for that protein plus metadata)
# 4. create_corpus.py : Creates a sentence for each protein with GAP DISORDER and PFAM 'words', orders the tokens and removes overlaps
# 5. run_word2vec.py  : Calls word2vec with the corpus

# ------ Pre-requisites for this script ------ 
# Protein and token information is stored in a database in W2V_PROTEIN and W2V_TOKEN tables
# It assume there are 2 tables in the database: W2V_PROTEIN and W2V_TOKEN
# 
# W2V_TOKEN (uniprot_id VARCHAR(16), type VARCHAR(16), token VARCHAR(64), start INT, end INT);
# W2V_PROTEIN (uniprot_id VARCHAR(16), start INT, end INT);

# ------ Instructions for this script ------ 
# Assumed there is a database with data in it and that you can connect and query it from python
# You need to modify this script and change the start poisition, chunk size and number of iterations
#     - I executed this script on an EC2 instance connected to RDS
#     - INitially I created an RDS instance with Terraform, but it actually was a lot easier to do it
#       through the AWS console and make sure it is set to 'public'. I used a single AZ instance
#     - I found that an AWS RDS instance of tyoe db.t4g.2xlarge  would iterate through 500k proteins in about 3.5mins.
#     - Thus I would set the chunk size to 500000 and iterate from 0..19 to get 10M proteins in each invocation of his script
# The script produces one file per 'chunk' - I did it this way to avoid the files getting too large and slowing down
# the write time. It took a lot of trail and error to get this to work so I just went with this approach as it worked.

# Each file has one line per row returned from the database, the results are not tab delimeted becuase you cannot dictae the 
# SQL output in this way. You could do if you were executing the SQL directly on the database and could save a file loaclly on
# that database.


# -------------- TODO BEFORE EXECUTING : SET THESE VARIABLES ---------------

#  **** NB : 3 x CHANGES ToO THESE 3 ITEMS : endpoint, start_pos, chunk_size
#  **** NB : 1 x CHANGE THE ITERATION LOOP
#  **** NB : 2 x CHANGES TO OUTPUT FILE NAME
endpoint="w2v-db-1.cligs4ak0dtg.eu-west-1.rds.amazonaws.com" # database endpoint (can get this from the AWS RDS console)
start_pos=20000000 # which protein you would like to start from - I had to proccess 78,000,000 proteins
chunk_size=500000  # how many proteins to query each time (and how many will be put in a file)

output_dir="output"
file_start=${start_pos}

# **** NB : CHANGE THE ITERATION (I.E. END OF THE LOOP ON THIS NEXT LINE)
for i in $(seq 0 19); 
do  
    SECONDS=0
    echo "iteration" $i ": starting at" $start_pos

    # create emty target files
    #touch ${output_dir}/sql_output_${file_start}_${i}.txt

    touch output/sql_output_20M_${i}.txt

    # for local
    #/usr/local/opt/mysql-client/bin/mysql -h $endpoint -P 3306 -u admin W2V -pw0rd2v3c -e "SELECT W2V_PROTEIN.*, W2V_TOKEN.* FROM ( SELECT UNIPROT_ID, START, END FROM W2V_PROTEIN W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT ${start_pos}, ${chunk_size}) AS W2V_PROTEIN INNER JOIN W2V_TOKEN AS W2V_TOKEN ON W2V_PROTEIN.UNIPROT_ID = W2V_TOKEN.UNIPROT_ID" >> output/sqloutput_${i}.txt
    #/usr/local/opt/mysql-client/bin/mysql -h $endpoint -P 3306 -u admin W2V -pw0rd2v3c -e "SELECT W2V_PROTEIN.*, W2V_TOKEN.* FROM ( SELECT UNIPROT_ID, START, END FROM W2V_PROTEIN W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT ${start_pos}, ${chunk_size}) AS W2V_PROTEIN INNER JOIN W2V_TOKEN AS W2V_TOKEN ON W2V_PROTEIN.UNIPROT_ID = W2V_TOKEN.UNIPROT_ID"
    
    
    # for aws ec2 and rds
    mysql -h $endpoint -P 3306 -u admin W2V -pw0rd2v3c -e "SELECT W2V_PROTEIN.*, W2V_TOKEN.* FROM ( SELECT UNIPROT_ID, START, END FROM W2V_PROTEIN W2V_PROTEIN ORDER BY UNIPROT_ID LIMIT ${start_pos}, ${chunk_size}) AS W2V_PROTEIN INNER JOIN W2V_TOKEN AS W2V_TOKEN ON W2V_PROTEIN.UNIPROT_ID = W2V_TOKEN.UNIPROT_ID" >> output/sql_output_20M_${i}.txt
    
    # cat the result and grep it
    #cat sql_output_${i}.txt | awk '{FS ="\t"} {print $1 ":" $2 ":" $3 "|" $5 ":" $6 ":" $7 ":" $8}' >> sql_output_${i}.dat
    duration=$SECONDS
    echo "iteration ${i} duration : $((duration / 60))min $((duration % 60))s."

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