variable "region" {
  default = "eu-west-1"
}

variable "availabilty_zone" {
  default = "eu-west-1a"
}

variable "availabilty_zone_2" {
  default = "eu-west-1b"
}

# ------------- for vpc ------------

variable "vpc_cidr_block" {
  description = "CIDR Block"
  type        = string
  default     = "10.0.0.0/16"
}

# ------------- for subnet ------------

variable "public_subnet_cidr_block" {
  description = "Public CIDR Block"
  type        = string
  default     = "10.0.1.0/24"
}


variable "private_subnet_cidr_block" {
  description = "Private CIDR Block"
  type        = string
  default     = "10.0.101.0/24"
}


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
