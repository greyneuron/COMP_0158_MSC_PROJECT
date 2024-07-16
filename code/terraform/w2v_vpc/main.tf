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

# ------------------------ vpc -------------------------
resource "aws_vpc" "w2v-dev-vpc" {
  cidr_block           = var.vpc_cidr_block
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "w2v-dev-vpc"
  }
}

# ------------------------ subnets -------------------------

# ----- public subnet in vpc
resource "aws_subnet" "w2v-public-subnet" {
  cidr_block        = var.public_subnet_cidr_block
  vpc_id            = aws_vpc.w2v-dev-vpc.id
  availability_zone = var.availabilty_zone

  tags = {
    Name = "w2v-public-subnet"
  }
}

# ----- private subnet in vpc
resource "aws_subnet" "w2v-private-subnet" {
  cidr_block        = var.private_subnet_cidr_block
  vpc_id            = aws_vpc.w2v-dev-vpc.id
  availability_zone = var.availabilty_zone

  tags = {
    Name = "w2v-private-subnet"
  }
}

# ----- rds subnet in vpc
resource "aws_subnet" "w2v-rds-subnet-1" {
  cidr_block        = var.rds_1_subnet_cidr_block
  vpc_id            = aws_vpc.w2v-dev-vpc.id
  availability_zone = var.availabilty_zone

  tags = {
    Name = "w2v_rds_subnet_1"
  }
}

# ----- rds subnet in vpc
resource "aws_subnet" "w2v-rds-subnet-2" {
  cidr_block        = var.rds_2_subnet_cidr_block
  vpc_id            = aws_vpc.w2v-dev-vpc.id
  availability_zone = var.availabilty_zone_2

  tags = {
    Name = "w2v_rds_subnet_2"
  }
}

# ------------------------ igw -------------------------

# ----- internet gateway
resource "aws_internet_gateway" "w2v-igw" {
  vpc_id = aws_vpc.w2v-dev-vpc.id

  tags = {
    Name = "w2v-internet_gw"
  }
}

# ------------------------ route tables -------------------------

# ----- public route table
resource "aws_route_table" "w2v-public-rt" {
  vpc_id = aws_vpc.w2v-dev-vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.w2v-igw.id
  }
  tags = {
    Name = "w2v-route-table"
  }
}
resource "aws_route_table_association" "w2v_public_subnet_assoc" {
  route_table_id = aws_route_table.w2v-public-rt.id
  subnet_id = aws_subnet.w2v-public-subnet.id
}


# ----- private route table
resource "aws_route_table" "w2v-private-rt" {
  vpc_id = aws_vpc.w2v-dev-vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.w2v-igw.id
  }
  tags = {
    Name = "w2v-route-table"
  }
}
resource "aws_route_table_association" "w2v_private_subnet_assoc" {
  route_table_id = aws_route_table.w2v-private-rt.id
  subnet_id = aws_subnet.w2v-private-subnet.id
}
