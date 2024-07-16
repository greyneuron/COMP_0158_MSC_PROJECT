resource "aws_security_group" "w2v_security_group" {

  name   = "w2v-security_group"
  #vpc_id = aws_vpc.w2v-dev-vpc.id
  vpc_id = "vpc-011f0d152f4120d5b"

  ingress {
    description = "Allow HTTP Traffic"
    from_port   = var.web_server_port
    to_port     = var.web_server_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    description = "Allow SSH"
    from_port   = var.ssh_port
    to_port     = var.ssh_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    #cidr_blocks = ["${var.my_ip}/32"]
  }
  ingress {
    description = "Allow HTTPS Traffic"
    from_port   = var.https_port
    to_port     = var.https_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    description = "Allow outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}