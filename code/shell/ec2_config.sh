#!/bin/bash

# -------------- SSH --------------------

aws ec2 describe-instances | grep PublicDnsName

export instance_id="ec2-63-32-44-188.eu-west-1.compute.amazonaws.com"

ssh -i "w2v_rsa" ec2-user@$instance_id

Wel....ise


# -------------- Mount to existing EBS Volume --------------------
lsblk # get the name of the disk - you can tell it by its size
sudo mkdir /data
sudo mount /dev/nvme2n1 /data
cd /data/dev/ucl

# activate venv - this is really weird as it doesn;t always work
bash # had to switch to bash
source w2v-venv/bin/activate


# -------------- SCP A FILE --------------------
# from directory with pem key (w2v-ec2)
# note I did a chmod 777 on the target directory

export instance_id="ec2-52-51-138-149.eu-west-1.compute.amazonaws.com"

# uploade protein dat files (4 mins)
scp -i "w2v_rsa" ~/dev/ucl/comp0158_mscproject/data/uniprot/proteins_ordered.dat ec2-user@$instance_id:/data/dev/ucl/data/protein

# upload code
scp -i "w2v_rsa" ~/dev/ucl/comp0158_mscproject/code/*.py ec2-user@e$instance_id:/data/dev/ucl/code

# upload pfam dat files (1 hour 10 mins)
scp -i "w2v_rsa" ~/dev/ucl/comp0158_mscproject/data/pfam/protein2ipr_pfam_20240715.dat ec2-user@$instance_id:/data/dev/ucl/data/pfam



# -------------- FORMAT an EBS VOLUME --------------------
# IF YOU DESTROY A VOLUME YOU DELETE THE DATA!!! BUT YOU CAN DESTROY AN EC2 INSTANCE MANY
# TIMES AND CONNECT IT TO A PREVIOUS EBS INSTANCE WHEN YOU RESTART

https://docs.aws.amazon.com/ebs/latest/userguide/ebs-using-volumes.html


# -------------- MYSQL RDS --------------------

ssh to ec2 instance

sudo dnf update -y
sudo dnf install mariadb105

Get the RDS endpoint - I got it from the console. 
For example: 

w2v-dev-db.cligs4ak0dtg.eu-west-1.rds.amazonaws.com

Now connect from an ec2 console:
mysql -h w2v-dev-db.cligs4ak0dtg.eu-west-1.rds.amazonaws.com -P 3306 -u w2v -p


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