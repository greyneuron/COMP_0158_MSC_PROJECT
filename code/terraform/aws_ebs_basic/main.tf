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

resource "aws_instance" "app_server" {
  ami           = "ami-08ca6be1dc85b0e84"
  instance_type = var.instance_type

  tags = {
    Name = var.instance_name
  }
}
