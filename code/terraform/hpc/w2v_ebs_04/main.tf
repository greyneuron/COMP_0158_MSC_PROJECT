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
  region = "eu-west-1"
}

resource "aws_ebs_volume" "w2v-ebs-vol-04" {
  availability_zone = "eu-west-1a"
  size              = 125 # size in GB
  type              = "st1" # throughput optimised

  tags = {
    Name = "Word2Vec_EBS_04"
  }
}