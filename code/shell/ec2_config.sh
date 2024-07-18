#!/bin/bash

# -------------- SSH --------------------
# % ssh -i "w2v_rsa" ec2-user@ec2-3-251-70-140.eu-west-1.compute.amazonaws.com
# Wel....ise

# -------------- Format and mount a volume --------------------
#
# Format needed when EBS first creates - see instructions in link
# Attach needed every time an EC2 is created
#
https://docs.aws.amazon.com/ebs/latest/userguide/ebs-using-volumes.html

lsblk
sudo mkdir /data
sudo mount /dev/xvdh /data

# make dev directory
mkdir /data/dev
mkdir /data/dev/ucl



# -------------- Setup python  --------------------
# install python etc (note: python 3 should already be there)
sudo yum install pip

# create venv
cd /data/dev/ucl
python3 -m venv w2v-env

# activate
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