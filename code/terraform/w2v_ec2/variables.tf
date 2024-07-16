variable "region" {
  default = "eu-west-1"
}


# t4g.medium = 2 vCPU 4GB, $0.0368
# t4g.large = 2 vCPU 8GB, $0.0736
# t4g.xlarge = 4 vCPU 16GB, $0.1472
variable "instance_type" {
  default = "d2.xlarge"
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

variable "web_server_port" {
  description = "Web Server port 80"
  type        = number
  default     = 80
}

variable "ssh_port" {
  description = "SSH Port"
  type        = number
  default     = 22
}

variable "https_port" {
  description = "HTTPS Port"
  type        = number
  default     = 443
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