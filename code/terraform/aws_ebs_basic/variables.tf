variable "region" {
  default = "eu-west-1"
}

variable "instance_type" {
  default = "t2.micro"
}

variable "instance_name" {
  description = "Name for EC2 instance"
  type        = string
  default     = "My Fist Terraform INstance"
}