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


# -------------- S3 ---------------

# Create a S3 bucket
resource "aws_s3_bucket" "w2v_s3_bucket" {
  bucket = "w2v-bucket"

  lifecycle {
    prevent_destroy = true
  }
}
