variable "region" {
  default = "eu-west-1"
}

variable "instance_type" {
  default = "t2.micro"
}

variable "availabilty_zone" {
  default = "eu-west-1a"
}

variable "instance_name" {
  description = "Name for EC2 instance"
  type        = string
  default     = "My Fist Terraform INstance"
}

variable "bucket_name" {
  description = "S3 BUcket"
  type        = string
  default     = "word2vec-s3"
}

variable "server_port" {
  description = "Server use this port for http requests"
  type        = number
  default     = 80
}

variable "ssh_port" {
  description = "Describes the ssh port"
  type        = number
  default     = 22
}