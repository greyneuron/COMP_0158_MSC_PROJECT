
resource "aws_vpc" "test_env" {
  cidr_block           = var.cidr_block
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "test_env_vpc"
  }
}

resource "aws_subnet" "subnet" {
  cidr_block        = cidrsubnet(aws_vpc.test_env.cidr_block, 3, 1)
  vpc_id            = aws_vpc.test_env.id
  availability_zone = var.availabilty_zone
}

resource "aws_internet_gateway" "test_env_gw" {
    vpc_id = aws_vpc.test_env.id
}