#
# This creates Terraform module creates an ec2 instance in a public subnet with ssh access.check 
#
# Prior to running this:
# 1. Have an aws acount setup and generated access keys
# 2. Install AWS CLI
# 3. Install Terraform (I followed the Terraform tutorial which has about 6 parts
#    and results in you creating an ec2 instance - useful for making sure everything is installed)
#
# 4. Run w2v_vpc to create a network, take the vpc id and paste it into security_group.tf 
# 5. Run w2v_ebs to create an ebs and then paste its id into the 'ebs-attachment' entry below
#

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.18.1"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region = var.region
}

resource "aws_instance" "w2v-server" {
  #ami                    = "ami-08ca6be1dc85b0e84"
  ami                    = "ami-0b995c42184e99f98"
  instance_type          = var.instance_type
  vpc_security_group_ids = [aws_security_group.instance.id]
  availability_zone      = var.availabilty_zone

  # key-pair for this ec2
  key_name = aws_key_pair.w2v_ssh_key.key_name


  # need this for ssh
  associate_public_ip_address = true

  #subnet_id = aws_subnet.subnet.id
  subnet_id = "subnet-0b5a447ba95b50112"

  # ----- install some software
  user_data = <<-EOL
    #!/bin/bash -xe

    sudo yum install python3 pip3
    sudo pip3 install virtualenv
    sudo virtualenv word2vec
    EOL

  tags = {
    Name = var.instance_name
  }
}

#
# Attach EBS volume (ie disk) - get the volume_id AFTE
# running terraform apply from the ebs folder
#
resource "aws_volume_attachment" "w2v_ebs_att" {
  device_name = "/dev/sdh"
  volume_id   = "vol-0bf7b73594de17579"
  instance_id = aws_instance.w2v-server.id
}



# ---------- key pair

# For this to work, you need to generate a key-pair locally and then use the 
# following Terraform construct to upload the public key you generated 
# to the ec2 server. Keep the provate key safe
# 1. ssh-keygen -t rsa -b 4096
# 2. Give the name "w2v_rsa" or whatever you want
# 3. Give a passphrase - remember this 
# 4. 2 files will then be generated - you need to put the name
#    of the .pub one into the below e.g. w2v_rsa.pub
# 5. Note also the reference to the key pair in the ec2 declaration above
# 
# When Terraform has run, find the instance name from the console and connect this way:
# % ssh -i "w2v_rsa" ec2-user@ec2-3-251-68-222.eu-west-1.compute.amazonaws.com
#

# pubilc key will stay on server
resource "aws_key_pair" "w2v_ssh_key" {
  key_name   = var.key_pair_name
  public_key = file("w2v_rsa.pub")
}

/*
# RSA key of size 4096 bits
resource "tls_private_key" "rsa" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

# private key wil remain local (e.g. on your laptop)
resource "local_file" "tf_key" {
  content  = tls_private_key.rsa.private_key_pem
  filename = var.file_name
}
*/









