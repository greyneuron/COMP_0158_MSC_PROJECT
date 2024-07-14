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
  db_subnet_group_name = aws_db_subnet_group.w2v_db_subnet_group.name
  
  skip_final_snapshot = true
  
  tags = {
    Name = "Word2Vec_DB"
  }
}