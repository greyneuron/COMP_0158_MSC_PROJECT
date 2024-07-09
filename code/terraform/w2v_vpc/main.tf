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


# ----- vpc
resource "aws_vpc" "w2v-dev-vpc" {
  cidr_block           = var.vpc_cidr_block
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "w2v-dev-vpc"
  }
}

# ----- public subnet in vpc
resource "aws_subnet" "public_subnet" {
  cidr_block        = var.public_subnet_cidr_block
  vpc_id            = aws_vpc.w2v-dev-vpc.id
  availability_zone = var.availabilty_zone

  tags = {
    Name = "w2v-public-subnet"
  }
}

# ----- private subnet in vpc
resource "aws_subnet" "private_subnet" {
  cidr_block        = var.private_subnet_cidr_block
  vpc_id            = aws_vpc.w2v-dev-vpc.id
  availability_zone = var.availabilty_zone

  tags = {
    Name = "w2v-private-subnet"
  }
}


# gateway for vpc - needed for public access to vpc
resource "aws_internet_gateway" "w2v-igw" {
  vpc_id = aws_vpc.w2v-dev-vpc.id

  tags = {
    Name = "w2v-internet_gw"
  }

}

# ----- route table to actually make the subnet public
resource "aws_route_table" "w2v_rt" {
  vpc_id = aws_vpc.w2v-dev-vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.w2v-igw.id
  }

  tags = {
    Name = "w2v-route-table"
  }
}

# ----- route table to associate public subnet with internet gateway
resource "aws_route_table_association" "w2v_public_subnet_assoc" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.w2v_rt.id
}