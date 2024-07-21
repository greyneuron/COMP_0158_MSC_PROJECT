#!/bin/bash

# -------------- SSH --------------------

aws ec2 describe-instances | grep PublicDnsName
export dns="ec2-63-32-44-188.eu-west-1.compute.amazonaws.com"
ssh -i "w2v_rsa" ec2-user@$dns
Wel....ise


# -------------- Mount to existing EBS Volume --------------------
lsblk # get the name of the disk - you can tell it by its size
sudo mkdir /data
sudo mount /dev/nvme2n1 /data
cd /data/dev/ucl

# activate venv - this is really weird as it doesn;t always work - don't have to switch to bash
# this worked
source w2v-venv/bin/activate



# -------------- INstall MYSQL DIRECTLY ON THE EC2 INSTANCE --------------------

# https://muleif.medium.com/how-to-install-mysql-on-amazon-linux-2023-5d39afa5bf11
sudo wget https://dev.mysql.com/get/mysql80-community-release-el9-1.noarch.rpm
sudo rpm --import https://repo.mysql.com/RPM-GPG-KEY-mysql-2023
sudo dnf install mysql80-community-release-el9-1.noarch.rpm -y
sudo dnf install mysql-community-server -y
# start
sudo systemctl start mysqld

sudo vi /etc/my.cnf
# add this just after [mysqld] (Esc:wq! to save):
skip-grant-tables
secure-file-priv=''
#datadir=/var/lib/mysql
datadir=/data/dev/ucl/data/database

# connect
mysql

# create database
#CREATE DATABASE W2V_DB;
USE W2V_DB;

# create table
CREATE TABLE W2V_TOKEN (uniprot_id VARCHAR(16), type VARCHAR(16), token VARCHAR(64), start INT, end INT);

# Load PFAM test data
# 100 rows took 0.013s => 13s for 100,000 => 130s for 1M? => 40min for 18M => 2.8hrs for 296M?

LOAD DATA LOCAL INFILE '/data/dev/ucl/data/pfam/protein2ipr_pfam_20240715.dat' INTO TABLE W2V_TOKEN FIELDS TERMINATED BY '|';
# Query OK, 296017815 rows affected (2 hours 36 min 46.31 sec)

# DISORDER HAS 81M entries
LOAD DATA LOCAL INFILE '/data/dev/ucl/data/disorder/dat/disordered_tokens_20240719.dat' INTO TABLE W2V_TOKEN FIELDS TERMINATED BY '|';
#Query OK, 81257100 rows affected (7 min 48.900 sec)

# ------- anaconda - doesn;t work
sudo wget https://repo.continuum.io/archive/Anaconda2-4.1.1-Linux-x86_64.sh
install to /data/dev/usr/locl/bin/anaonda2



# -------------- SCP A FILE --------------------
# from directory with pem key (w2v-ec2)
# note I did a chmod 777 on the target directory

export dns="ec2-52-51-138-149.eu-west-1.compute.amazonaws.com"

# uploade protein dat files (4 mins)
scp -i "w2v_rsa" ~/dev/ucl/comp0158_mscproject/data/uniprot/uniprotkb-2759_78494531_1000.dat ec2-user@$dns:/data/dev/ucl/data/protein
scp -i "w2v_rsa" ~/dev/ucl/comp0158_mscproject/data/uniprot/proteins_ordered.dat ec2-user@$dns:/data/dev/ucl/data/protein

# upload code
scp -i "w2v_rsa" ~/dev/ucl/comp0158_mscproject/code/*.py ec2-user@e$dns:/data/dev/ucl/code

# upload pfam dat files (1 hour 10 mins)
scp -i "w2v_rsa" ~/dev/ucl/comp0158_mscproject/data/pfam/protein2ipr_pfam_20240715.dat ec2-user@$instance_id:/data/dev/ucl/data/pfam


# -------- Copy from ebs to s3
ssh to ec2
aws configure
aws s3 cp disorder/dat/disordered_tokens_20240719.dat s3://w2v-bucket/disordered/disordered_tokens_20240719.dat


# -------------- FORMAT an EBS VOLUME --------------------
# IF YOU DESTROY A VOLUME YOU DELETE THE DATA!!! BUT YOU CAN DESTROY AN EC2 INSTANCE MANY
# TIMES AND CONNECT IT TO A PREVIOUS EBS INSTANCE WHEN YOU RESTART

https://docs.aws.amazon.com/ebs/latest/userguide/ebs-using-volumes.html


# -------------- CONNECT MYSQL TO TERRAFORM RDS INSTANCE --------------------

ssh to ec2 instance

sudo dnf update -y
sudo dnf install mariadb105

export endpoint="w2v-dev-db.cligs4ak0dtg.eu-west-1.rds.amazonaws.com"
mysql -h $endpoint -P 3306 -u w2v -p


# create database
CREATE DATABASE W2V;
USE W2V;

SELECT USER, HOST FROM MYSQL.USER

# create table
CREATE TABLE W2V_TOKEN (uniprot_id VARCHAR(16), type VARCHAR(16), token VARCHAR(64), start INT, end INT);

# load data - THIS WAS NOT WORKING SO TRIED 
#LOAD DATA LOCAL INFILE '/data/dev/ucl/data/pfam/pfam_test_data.dat' INTO TABLE W2V_TOKEN FIELDS TERMINATED BY '|';
LOAD DATA LOCAL INFILE '/data/dev/ucl/data/pfam/protein2ipr_pfam_20240715.dat' INTO TABLE W2V_TOKEN FIELDS TERMINATED BY '|';
LOAD DATA LOCAL INFILE '/data/dev/ucl/data/disorder/dat/disordered_tokens_20240719.dat' INTO TABLE W2V_TOKEN FIELDS TERMINATED BY '|';

# --------------------------------------------------------------------------------------------------
#
# -------------- CONNECT MYSQL TO CONSOLE CREATED RDS INSTANCE --------------------
# With MySQL on the same EC@ instance and installed manually, it took 3hours or something to load pfam data
# Then tried the RDS instance I had created with Terrafor - couldn't load file for some reason - but I suspect
# npw that it's because I forgot to include the LOCAL keywoes in the LOAD DATA INFILE comand.
# 
# IN any case, I creared a new RDS instance through the RDS console and called it w2v-db-2, created a database
# called W2V and managed to execute queries for 1M proteins to get all pfam and disorder tokens in 150s compared to
# almost 1 hour on my laptop using DuckDB and python (PFAM and DISPORDER tokens in separate tables as didn;t have
# enough memory to create an index over a combined table).
#
#
# Sun July 21st - close f play:
# - New rds instance created and db created caled W2V with user 'admin' and password 'w0rd2v3c' - details below
# - Created W2V_TOKEN table and uploaded all pfam and disorder tokens
# - Created an index on that table
# - Loaded all protein data into W2V_PROTEIN
#
# - created snapshot : w2v-db-2-2024-07-21-1800 
# 
# CHECK : 78,494,529 lines in uniprotkb-2759_78494531.dat but 79,595,529 rows in W2V_PROTEIN --> Looks like rows were appended not replaced
#
# SELECT UNIPROT_ID, COUNT(*) FROM W2V_PROTEIN GROUP BY UNIPROT_ID HAVING COUNT(*) >1;
# 1000000 rows in set (1 min 11.686 sec)

#--------------------------------------------------------------------------------------------------

w2v-db-2
# MySQl
# eu-west-1a
# admin/w0rd2v3c

# db.t4g.xlarge
# 4CPU 16GB
# 60GiB
# gp3
# 3000 IOPS
# 125 MiBps strage throughput
# multi-az : no

# vpc: .....96af - same as vpc that ec2 is in
# subnet group: w2v-dev-vpc
# subnets: 9bfd and 3e124
# vpc security groups: w2v_rds_sg, rds-ec2-3 (not sure where this second one came from)
# Connected compute: EC2 008c compute resource securoty group: ec2-rds-3




# also selected the vpc id, submet groups and security groups

mysql -h w2v-db-2.cligs4ak0dtg.eu-west-1.rds.amazonaws.com -P 3306 -u admin -p

CREATE DATABASE W2V;
USE W2V;

# ----- create tables
CREATE TABLE W2V_TOKEN (uniprot_id VARCHAR(16), type VARCHAR(16), token VARCHAR(64), start INT, end INT);
CREATE TABLE W2V_PROTEIN (uniprot_id VARCHAR(16), start INT, end INT);

# ----- load disorder tokens - disorder has 81M entries
LOAD DATA LOCAL INFILE '/data/dev/ucl/data/disorder/dat/disordered_tokens_20240719.dat' INTO TABLE W2V_TOKEN FIELDS TERMINATED BY '|';
#Query OK, 81257100 rows affected (7 min 48.900 sec)

# ----- load pfam tokens  - pfam has 296M entries
LOAD DATA LOCAL INFILE '/data/dev/ucl/data/pfam' INTO TABLE W2V_TOKEN FIELDS TERMINATED BY '|';
# Query OK, 296017815 rows affected (26 min 16.749 sec)


# ----- load proteins
LOAD DATA LOCAL INFILE '/data/dev/ucl/data/protein/uniprotkb-2759_78494531_1000.dat' INTO TABLE W2V_PROTEIN FIELDS TERMINATED BY '|';

# --- WITHOUT AN INDEX 
MySQL [W2V]> SELECT COUNT(*) FROM W2V_TOKEN;

377,275,015 377M RECORDS
+-----------+
| COUNT(*)  |
+-----------+
| 377275015 |
+-----------+
1 row in set (6 min 32.217 sec)


MySQL [W2V]> SELECT * FROM W2V_TOKEN WHERE UNIPROT_ID = 'A0A010PZU8';
+------------+----------+-------------------------------+-------+------+
| uniprot_id | type     | token                         | start | end  |
+------------+----------+-------------------------------+-------+------+
| A0A010PZU8 | DISORDER | Consensus Disorder Prediction |     1 |   30 |
| A0A010PZU8 | PFAM     | PF00400                       |   865 |  900 |
| A0A010PZU8 | PFAM     | PF00400                       |   928 |  955 |
| A0A010PZU8 | PFAM     | PF00400                       |   960 |  998 |
| A0A010PZU8 | PFAM     | PF00400                       |  1017 | 1040 |
| A0A010PZU8 | PFAM     | PF00400                       |  1078 | 1108 |
| A0A010PZU8 | PFAM     | PF00400                       |  1233 | 1260 |
| A0A010PZU8 | PFAM     | PF05729                       |   358 |  479 |
| A0A010PZU8 | PFAM     | PF17100                       |   152 |  254 |
+------------+----------+-------------------------------+-------+------+
9 rows in set (7 min 34.802 sec)


# -- APPLY INDEX
CREATE INDEX TKN_IDX oON W2V_TOKEN(UNIPROT_ID);

MySQL [W2V]> CREATE INDEX TKN_IDX ON W2V_TOKEN (UNIPROT_ID);
Query OK, 0 rows affected (39 min 33.756 sec)
Records: 0  Duplicates: 0  Warnings: 0

SELECT * FROM W2V_TOKEN WHERE UNIPROT_ID = 'A0A010PZU8';
+------------+----------+-------------------------------+-------+------+
| uniprot_id | type     | token                         | start | end  |
+------------+----------+-------------------------------+-------+------+
| A0A010PZU8 | DISORDER | Consensus Disorder Prediction |     1 |   30 |
| A0A010PZU8 | PFAM     | PF00400                       |   865 |  900 |
| A0A010PZU8 | PFAM     | PF00400                       |   928 |  955 |
| A0A010PZU8 | PFAM     | PF00400                       |   960 |  998 |
| A0A010PZU8 | PFAM     | PF00400                       |  1017 | 1040 |
| A0A010PZU8 | PFAM     | PF00400                       |  1078 | 1108 |
| A0A010PZU8 | PFAM     | PF00400                       |  1233 | 1260 |
| A0A010PZU8 | PFAM     | PF05729                       |   358 |  479 |
| A0A010PZU8 | PFAM     | PF17100                       |   152 |  254 |
+------------+----------+-------------------------------+-------+------+
9 rows in set (0.003 sec)


# GAME CHANGER - 1000 proteins selected in 0.707s
LOAD DATA LOCAL INFILE '/data/dev/ucl/data/protein/uniprotkb-2759_78494531_1000.dat' INTO TABLE W2V_PROTEIN FIELDS TERMINATED BY '|';
SELECT W2V_TOKEN.*, W2V_PROTEIN.* FROM W2V_TOKEN INNER JOIN W2V_PROTEIN ON W2V_TOKEN.UNIPROT_ID = W2V_PROTEIN.UNIPROT_ID;
#3726 rows in set (0.707 sec)

# 100,000 proteins
scp -i "w2v_rsa" ~/dev/ucl/comp0158_mscproject/data/protein/uniprotkb-2759_78494531_100000.dat ec2-user@$dns:/data/dev/ucl/data/protein
SELECT W2V_TOKEN.*, W2V_PROTEIN.* FROM W2V_TOKEN INNER JOIN W2V_PROTEIN ON W2V_TOKEN.UNIPROT_ID = W2V_PROTEIN.UNIPROT_ID;
#342978 rows in set (32.751 sec)    

# 1M proteins
scp -i "w2v_rsa" ~/dev/ucl/comp0158_mscproject/data/protein/uniprotkb-2759_78494531_1M.dat ec2-user@$dns:/data/dev/ucl/data/protein # took 8s on 1.8Mb/s
LOAD DATA LOCAL INFILE '/data/dev/ucl/data/protein/uniprotkb-2759_78494531_1M.dat' INTO TABLE W2V_PROTEIN FIELDS TERMINATED BY '|'; # took 4.27s
SELECT W2V_TOKEN.*, W2V_PROTEIN.* FROM W2V_TOKEN INNER JOIN W2V_PROTEIN ON W2V_TOKEN.UNIPROT_ID = W2V_PROTEIN.UNIPROT_ID;
# 2842983 rows in set (2 min 35.930 sec)


# Load all 78M proteins
scp -i "w2v_rsa" ~/dev/ucl/comp0158_mscproject/data/protein/uniprotkb-2759_78494531.dat ec2-user@$dns:/data/dev/ucl/data/protein # 9min 18s on 2.2MB/s
LOAD DATA LOCAL INFILE '/data/dev/ucl/data/protein/uniprotkb-2759_78494531.dat' INTO TABLE W2V_PROTEIN FIELDS TERMINATED BY '|'; # 5min 45s
CREATE INDEX PTN_IDX ON W2V_PROTEIN (UNIPROT_ID);

# Compared to putput I was getting on mac using python lookups across two tables


(conda_ucl_base) patrick@Patricks-MBP code % python3 create_pre_corpus.py                                    
50000 lines processed in  324.17928981781006 s total: 50000 # 50,000 proteins in 5 mins!
50000 lines processed in  262.34461522102356 s total: 100000
50000 lines processed in  278.6645698547363 s total: 150000
50000 lines processed in  309.6166718006134 s total: 200000
50000 lines processed in  276.44881224632263 s total: 250000
50000 lines processed in  244.02400612831116 s total: 300000
50000 lines processed in  250.38070559501648 s total: 350000
50000 lines processed in  254.11079502105713 s total: 400000
50000 lines processed in  287.52336621284485 s total: 450000
50000 lines processed in  292.42263984680176 s total: 500000
50000 lines processed in  299.4286630153656 s total: 550000
50000 lines processed in  292.56242203712463 s total: 600000
50000 lines processed in  296.67819905281067 s total: 650000
50000 lines processed in  298.4477791786194 s total: 700000
50000 lines processed in  290.6085560321808 s total: 750000
50000 lines processed in  292.14460492134094 s total: 800000
50000 lines processed in  289.8639919757843 s total: 850000
50000 lines processed in  295.91912388801575 s total: 900000
50000 lines processed in  313.83148097991943 s total: 950000
50000 lines processed in  304.5584602355957 s total: 1000000 # 1 MILLION IN ABOUT 1 HOUR
50000 lines processed in  296.82561779022217 s total: 1050000
50000 lines processed in  309.57226300239563 s total: 1100000
50000 lines processed in  306.297119140625 s total: 1150000
50000 lines processed in  304.2672519683838 s total: 1200000
50000 lines processed in  289.63942098617554 s total: 1250000
50000 lines processed in  300.55637979507446 s total: 1300000
50000 lines processed in  295.591126203537 s total: 1350000
50000 lines processed in  294.9627618789673 s total: 1400000
50000 lines processed in  305.4713032245636 s total: 1450000
50000 lines processed in  299.7742500305176 s total: 1500000
50000 lines processed in  312.0243089199066 s total: 1550000
50000 lines processed in  306.6465458869934 s total: 1600000
50000 lines processed in  289.1072518825531 s total: 1650000
50000 lines processed in  303.91899490356445 s total: 1700000
50000 lines processed in  308.80527925491333 s total: 1750000
50000 lines processed in  302.2244539260864 s total: 1800000
50000 lines processed in  297.5620291233063 s total: 1850000
50000 lines processed in  301.681587934494 s total: 1900000
50000 lines processed in  310.106351852417 s total: 1950000
50000 lines processed in  309.0112931728363 s total: 2000000
*/



# -------------- Setup python  --------------------
# install python etc (note: python 3 should already be there)
sudo yum install pip

# create venv
cd /data/dev/ucl
python3 -m venv w2v-env

# activate
bash # had to switch to bash
source w2v-venv/bin/activate






# ------------ CLI ------------
# This is already installed on Amazon Linux but
# you must first run aws-configure and provide keys
# % aws-configure

# aws s3api list-buckets


# ------------ GIT ------------ 
% sudo yum install git
% git config --global user.name greyneuron
% git config --global user.email pllowry@hotmail.com

mkdir ucl
cd ucl

# ------- GIT Access key
# https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account
# Do this from your ec2 command line

# % ssh-keygen -t ed25519 -C pllowry@hotmail.com

# copy to s3 - don't have to do this as can copy from clipboard
# % aws s3 cp w2v-ec2-ssh-key.pub s3://w2v-bucket/w2v-ec2-ssh-key.pub
# download from s3 locally
git clone git@github.com:greyneuron/COMP_0158_MSC_PROJECT

% ssh-keygen -t ed25519 -C pllowry@hotmail.com
% sudo cat /root/.ssh/id_rsa.pub

copy whole line to clipboard and save


go to git
go to profile picture > settings > SSH and GPG Keys > New SSH key
Copy in the clipboard

Go back to EC@ consoloe
%ssh git@github.com
This will show that you authernitcated

git clone git@github.com:greyneuron/COMP_0158_MSC_PROJECT

*** STILL WOULD NOT WORK ***

THen tried this:
sudo ssh-add ~/.ssh/id_ed25519

ALSO COULDN:T FIND EGENT


# -------------- Develop  Splitting files --------------------


# -------------- Download data
# download data
mkdir /data/dev/ucl/data/disorder
cd /data/dev/ucl/data/disorder

# this download took about 50mins
sudo curl --location https://ftp.ebi.ac.uk:443/pub/databases/interpro/releases/100.0/extra.xml.gz --output my_extra.xml.gz
sudo gzip -d my_extra.xml.dz



sudo touch split_file.py
sudo chmod split_file.py
sudo chmod /data/dev/ucl/data/disorder

sudo vim split_file.py
 - copy in code
 - ESC :wq!

python3 split_file.py


sudo touch parse_dis.py
sudo vim parse_dis.py

# create venv
python3 -m venv w2v-env

# stay in dev
source w2v-venv/bin/activate



# -------- Glue

1. Put data in s3 buckets
2. Create a folder in s3 for the Glue Datastore (w2v-bucket/datastore)
3. Create glue datastores
        - w2v-bucket/w2v_datastore
4. Create a crawler
        - Specify s3 of dat files s3://w2v-bucket/pfam DO NOT GIVE THE FILE NAME
        - Specify datastore s3://w2v-bucket/datastore
        - Give table name/prefix e.g. w2v_pfam_tokens
4. Create tables and specify source
        - tables to go into w2v_datastore
        - w2v_pfam_tokens , then select the s3 bucket that holds the data and specify it is a pipe delimted csv
        - w2v_datastore_tokens and do the same
        - also ad columns for each table and make sure to specify the type


You can also add tables using a crawler

Go to Athena and create query result bucket in s3