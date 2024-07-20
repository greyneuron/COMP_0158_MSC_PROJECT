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

# -------------- rds cidrs -----------

variable "rds_1_subnet_cidr_block" {
  description = "Public CIDR Block"
  type        = string
  default     = "10.0.5.0/24"
}

variable "rds_2_subnet_cidr_block" {
  description = "Public CIDR Block"
  type        = string
  default     = "10.0.6.0/24"
}

# -------- security group ---------

resource "aws_security_group" "w2v_rds_sg" {

  name   = "w2v_rds_sg"

  # ****** TODO : Put VPC ID HERE *******
  vpc_id = "vpc-01ede11f2f41296af"

  ingress {
    description = "Allow SQL - public to private"
    from_port   = "3306"
    to_port     = "3306"
    protocol    = "tcp"

    # ****** TODO : Put security group from ec2 here (w2v_ec2_security_group_id)
    security_groups = ["sg-0ff5b6d4352cfaa71"]
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ------------------------ sdb subnet group -------------------------

resource "aws_db_subnet_group" "w2v_db_subnet_group" {
  name = "w2v-db-subnet-group"
  subnet_ids = ["subnet-0fd63075992f3e124", "subnet-013fb8a61d8259bfd"]
  tags = {
    Name = "W2V DB Subnet Group"
  }
}


#https://aws.amazon.com/rds/mysql/pricing/

resource "aws_db_instance" "w2v-db" {
  allocated_storage = 100
  storage_type = "gp2"
  #engine = "postgres"
  #engine_version = "5.7"
  #instance_class = "db.r5.large"
  engine = "mysql"
  engine_version = "8.0.35"
  #instance_class = "db.t3.micro"
  instance_class = "db.t3.xlarge"
  identifier = "w2v-dev-db"
  username = "w2v"
  password = "w2v"

  vpc_security_group_ids = [aws_security_group.w2v_rds_sg.id]
  db_subnet_group_name = aws_db_subnet_group.w2v_db_subnet_group.id
  
  skip_final_snapshot = true
  
  tags = {
    Name = "Word2Vec_DB"
  }
}