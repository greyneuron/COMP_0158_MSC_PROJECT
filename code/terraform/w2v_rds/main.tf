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

# ------------------------ rds cidrs -------------------------

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

# ------------------------ security group -------------------------


resource "aws_security_group" "w2v_rds_sg" {

  name   = "w2v_rds_sg"
  #vpc_id = aws_vpc.w2v-dev-vpc.id
  vpc_id = "vpc-011f0d152f4120d5b"

  ingress {
    description = "Allow SQL - public to private"
    from_port   = "3306"
    to_port     = "3306"
    protocol    = "tcp"
    security_groups = [""]
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ------------------------ sdb subnet group -------------------------

resource "aws_db_subnet_group" "w2v_db_subnet_group" {
  name = "w2v-db-subnet-group"
  subnet_ids = ["subnet-0781c9f1e82b15266", "subnet-097332a318820a881"]

  tags = {
    Name = "W2V DB Subnet Group"
  }
}

resource "aws_db_instance" "w2v-db" {
  allocated_storage = 10
  storage_type = "gp2"
  engine = "postgres"
  #engine_version = "5.7"
  instance_class = "db.r5.large"
  identifier = "w2v-dev-db"
  username = "w2v"
  password = "w0rd2v3c"

  vpc_security_group_ids = ["sg-025bc1d4418edcbdf"]
  db_subnet_group_name = aws_db_subnet_group.w2v_db_subnet_group.id
  
  skip_final_snapshot = true
  
  tags = {
    Name = "Word2Vec_DB"
  }
}