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


resource "aws_ebs_volume" "w2v_ebs_vol" {
  availability_zone = var.availabilty_zone
  size              = 10
}