
resource "aws_vpc" "w2v-dev-vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "w2v-dev-vpc"
  }
}

resource "aws_subnet" "w2v-dev-subnet" {
  cidr_block        = cidrsubnet(aws_vpc.w2v-dev-vpc.cidr_block, 3, 1)
  vpc_id            = aws_vpc.w2v-dev-vpc.id
  availability_zone = var.availabilty_zone
}


# not sure I really want an internet gateway - would rather keep this closed off
# need it to be able to ssh
resource "aws_internet_gateway" "w2v-igw" {
    vpc_id = aws_vpc.w2v-dev-vpc.id
}
