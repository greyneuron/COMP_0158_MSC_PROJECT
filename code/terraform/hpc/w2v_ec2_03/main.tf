# Creates an ec2 instance in a public subnet with ssh access.

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

# --------------------------------------------
resource "aws_instance" "w2v-ec2-server-03" {
  ami                    = "ami-0b995c42184e99f98"
  instance_type          = var.instance_type
  vpc_security_group_ids = [aws_security_group.w2v_security_group_03.id]
  availability_zone      = var.availabilty_zone

  # key-pair for this ec2
  key_name = aws_key_pair.w2v_ssh_key.key_name

  # need this for ssh
  associate_public_ip_address = true

  # >>>>>>>>>>>> TODO - Add in public subnet id (from output of vpc)
  subnet_id = "subnet-09fcec0d09be09cc7"

  tags = {
    Name = var.instance_name
  }
}

# ---------- ebs attachment

# >>>>>>>>>>>> TODO - Add in after running 'terraform apply' from the w2v-ebs module

resource "aws_volume_attachment" "w2v_ebs_att" {
  device_name = "/dev/sdh"
  volume_id   = "vol-04e37eccf94c8679a"
  instance_id = aws_instance.w2v-ec2-server-03.id
}



# ---------- key pair

# For this to work, you need to first generate a key-pair locally and then use the 
# Terraform construct below to upload the public key you just generated onto the EC2 server
# Keep the private key safe
#
# 1. ssh-keygen -t rsa -b 4096
# 2. Give the name "w2v_rsa" or whatever you want
# 3. Give a passphrase - remember this 
# 4. 2 files will then be generated - you need to put the name
#    of the .pub one into the below e.g. w2v_rsa.pub
# 5. Note also the reference to the key pair in the ec2 declaration above
# 
# When Terraform has run, find the instance name from the terraform output and connect this way:
# % ssh -i "w2v_rsa" ec2-user@ec2-3-251-68-222.eu-west-1.compute.amazonaws.com

resource "aws_key_pair" "w2v_ssh_key" {
  key_name   = var.key_pair_name
  public_key = file("w2v_rsa_key_03.pub")
}










