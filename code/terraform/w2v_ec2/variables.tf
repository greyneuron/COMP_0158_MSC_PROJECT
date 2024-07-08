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
  default     = "Word2Vec Server"
}


# ------------- ports ------------

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

# ------------- key pair ------------
variable "key_pair_name" {
  description = "key_pair_name"
  type        = string
  default     = "word2vec_key_pair"
}

variable "file_name" {
  description = "Name of the key pair file"
  type        = string
  default     = "word2vec_key_pair_file"
}

# ------------- for vpc ------------

variable "cidr_block" {
  description = "CIDR Block"
  type        = string
  default     = "10.0.0.0/16"
}