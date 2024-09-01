1. Create VPC - only needed once
    - % cd terraform/w2v_vpc
    - % terraform apply

    - Take the outputs, for example
    
    vpc_id = "vpc-01ede11f2f41296af"
        > Use in w2v_ec2/security_group.tf
    
    w2v_public_subnet_id = "subnet-0858c958d9bbbdae9"
        > Use in w2v_ec2/main.tf



2. Create EBS instance
    - % cd terraform/w2v_ebs
    - % terraform apply

    - Take the outputs, e.g:

        - For the EC2 instance you need the volume id:

        > id=vol-05f27d34631d31dd8

    - For RDS you need the subnet groups and securoty groups )not sure if this actually works)
        > Paste 2 subnet ids into RDS
        > paste securoty group into RDS (public sec grp)

3. EC2



--- Connect to EC2 ---
Take the dns name from the output: ec2-3-248-193-3.eu-west-1.compute.amazonaws.com

export dns="ec2-3-248-193-3.eu-west-1.compute.amazonaws.com"

ssh -i "w2v_rsa_key_03" ec2-user@$dns

WelcometoParadise

--- Format disk : ONLY DO once
lsblk -f
sudo mkfs -t xfs /dev/nvme1n1

sudo mkdir /word2vec
sudo mount /dev/nvme1n1 /word2vec


----------- Create venv
sudo yum install pip

cd /word2vec
sudo mkdir code
sudo mkdir models
sudo chmod 777 -R models
sudo chmod 777 -R code
sudo python3 -m venv w2v-env

sudo chmod 777 -R w2v-env

. w2v-env/bin/activate
sudo pip install gensim
sudo pip install numpy


exit ssh

-- copy code across

scp -i "w2v_rsa_key_04" ../../../hpc/w2v_batch.py ec2-user@$dns:/word2vec/code
scp -i "w2v_rsa_key_04" ../../../hpc/run_w2v_02.sh ec2-user@$dns:/word2vec/code
scp -i "w2v_rsa_key_04" ../../../hpc/word2vec_sentences.pkl ec2-user@$dns:/word2vec/code


-- ssh back in
ssh -i "w2v_rsa_key_04" ec2-user@$dns


cd /word2vec
. w2v-env/bin/activate
sudo chmod 777 -R code
sudo chmod 777 -R models

cd code
sudo ./run_w2v_04.sh aws



clear





------------------------------------------------
-- Subsequent EC2
------------------------------------------------

1. Change EC2 name in variables.tf
2. terraform apply

export dns="ec2-3-248-193-3.eu-west-1.compute.amazonaws.com"
ssh -i "w2v_rsa" ec2-user@$dns

cd /word2vec
. w2v-env/bin/activate

cd code
sudo ./run_w2v_03.sh aws







--- Timings
t3.2xlarge.....
                mac     t3.2xlarge ($0.36 ph)   
load pickle     246s    175.54s

mac:    w2v_model_create_20240831 | 1 | 5 | 3 | 1 | 1238.38
mac:    w2v_model_create_20240831 | 1 | 10 | 3 | 1 | 1319.78
mac:    w2v_model_create_20240831 | 1 | 25 | 3 | 1 | 1283.5
mac:    w2v_model_create_20240831 | 1 | 50 | 3 | 1 | 1257.68

mac     w2v_model_create_20240831 | 1 | 1 | 3 | 10 | 1902.61 | 698.72


aws 02  w2v_model_create_20240831 | 1 | 5 | 5 | 1 | 1604.3



4. RDS


SSH to EC@ instance
    % ssh -i "w2v_rsa" ec2-user@<take from ouput of starting ec2>


Now execute the following:
sudo dnf update -y
sudo dnf install mariadb105

Get the RDS endpoint. For example: w2v-dev-db.cligs4ak0dtg.eu-west-1.rds.amazonaws.com

NOTE: I HASD TO MAKE THE CONNECTION MYSELF

mysql -h w2v-dev-db.cligs4ak0dtg.eu-west-1.rds.amazonaws.com -P 3306 -u admin -p

mysql -h w2v-dev-db.cligs4ak0dtg.eu-west-1.rds.amazonaws.com -P 3306 -u w2v -p

S3 Lambda
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html