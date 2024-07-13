#!/bin/bash
# % ssh -i "w2v_rsa" ec2-user@ec2-3-251-68-222.eu-west-1.compute.amazonaws.com
# Wel....ise

sudo yum install pip

#
# every time I start EC2
# attach volume (assuming its already been formatted)
#
lsblk
sudo mkdir /data
sudo mount /dev/xvdh /data

# make dev directory
mkdir /data/dev
cd /data/dev
cd /data/dev/ucl/python/




sudo touch parse_dis.py
sudo vim parse_dis.py


# grep -c "disorder_prediction\" dbname=\"MOBIDBLT\"" /data/my_extra.xml



# create venv
python3 -m venv w2v-env

# stay in dev
source w2v-venv/bin/activate

# ------------ CLI ------------
# This is already installed on Amazon Linux but
# you must first run aws-configure and provide keys
# % aws-configure

# aws s3api list-buckets


# ------------ GIT ------------ 
# sudo yum install git
# git config --global user.name greyneuron
# git config --global user.email pllowry@hotmail.com

mkdir ucl
cd ucl

# ------- GIT Access key
# % ssh-keygen -t ed25519 -C pllowry@hotmail.com
# give it a name
# copy to s3
# % aws s3 cp w2v-ec2-ssh-key.pub s3://w2v-bucket/w2v-ec2-ssh-key.pub
#
# download from s3 locally
git clone git@github.com:greyneuron/COMP_0158_MSC_PROJECT