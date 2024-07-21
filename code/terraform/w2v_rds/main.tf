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
    security_groups = ["sg-036c5a755f46b12c5"]
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
# https://docs.aws.amazon.com/AmazonRDS/latest/APIReference/API_CreateDBInstance.html

resource "aws_db_instance" "w2v-db" {
  allocated_storage = 60 # in GB
  storage_type = "gp3" # gp = general purpose

  engine = "mysql"
  engine_version = "8.0.35"
  instance_class = "db.t4g.2xlarge"
  identifier = "w2v-dev-db"
  username = "w2v"
  password = "w0rd2v3c"

  vpc_security_group_ids = [aws_security_group.w2v_rds_sg.id]
  db_subnet_group_name = aws_db_subnet_group.w2v_db_subnet_group.id
  publicly_accessible = true
  
  skip_final_snapshot = true
  
  tags = {
    Name = "Word2Vec_DB"
  }
}