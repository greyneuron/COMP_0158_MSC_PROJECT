# https://www.geeksforgeeks.org/how-to-create-an-aws-ec2-instance-and-attach-ebs-to-ec2-with-terraform/

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
  ami                    = "ami-08ca6be1dc85b0e84"
  instance_type          = var.instance_type
  vpc_security_group_ids = [aws_security_group.instance.id]
  availability_zone      = var.availabilty_zone

  subnet_id = aws_subnet.subnet.id

  tags = {
    Name = var.instance_name
  }
}


# ---------- key pair

# RSA key of size 4096 bits
resource "tls_private_key" "rsa-4096-example" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "local_file" "tf_key" {
  content  = tls_private_key.rsa-4096-example.private_key_pem
  filename = var.file_name
}

resource "aws_key_pair" "tf_key" {
  key_name   = var.key_pair_name
  public_key = tls_private_key.rsa-4096-example.public_key_openssh
}








