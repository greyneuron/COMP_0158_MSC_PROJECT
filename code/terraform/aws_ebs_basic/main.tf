terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  #region = "eu-west-1"
  region = var.region
}

resource "aws_instance" "w2v-server" {
  ami                    = "ami-08ca6be1dc85b0e84"
  instance_type          = var.instance_type
  vpc_security_group_ids = [aws_security_group.instance.id]
  availability_zone      = var.availabilty_zone

  tags = {
    Name = var.instance_name
  }
}


# -------------- S3 ---------------

# Create a S3 bucket
resource "aws_s3_bucket" "w2v_s3_bucket" {
  bucket = var.bucket_name


  lifecycle {
    prevent_destroy = false
  }
}
