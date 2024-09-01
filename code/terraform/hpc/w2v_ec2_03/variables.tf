variable "region" {
  default = "eu-west-1"
}


# d2.xlarge = x86_64, 4 cpu, 30.5GB, Moderate N/W, HDD 6144GB,  $0.735 ph
# d2.2xlarge = x86_64, 8 cpu, 61GB, Moderate N/W, HDD 12288GB,  $1.47 ph -> used this to process extras initially - fast but ran out of mem

# t3.large    = x86_64, 2 cpu, 8GB, ^5Gb,  $0.09 ph   --> fine for testing stuff
# t3.xlarge   = x86_64, 4 cpu, 16GB, ^5Gb,  $0.18 ph --> used when uploding extras and parsing extras, not great, alos on Mon 25/7 as most of grunt needed in rds
# t3.2xlarge  = x86_64, 8 cpu, 32GB, ^5Gb,  $0.36 ph
# r5d.2xlarge = x86_64, 8 cpu, 64GB, ^12.5Gb,  $0.564 ph

# Compare instance types
# From the console - go to EC2 and select Launch instance, on the next page to the 
# right of the instancy type dropdown there's a link to 'compare'. You might need 
# to add the price to the column

# explanation
# https://docs.aws.amazon.com/ec2/latest/instancetypes/instance-type-names.html

variable "instance_type" {
  default = "t3.2xlarge"
}

variable "availabilty_zone" {
  default = "eu-west-1a"
}

variable "instance_name" {
  description = "EC2 W2V03"
  type        = string
  default     = "Word2Vec EC2 Server 03"
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

variable "db_port" {
  description = "Database Port"
  type        = number
  default     = 3306
}

# ------------- key pair ------------
variable "key_pair_name" {
  description = "key_pair_name"
  type        = string
  default     = "word2vec_key_pair_03"
}

variable "file_name" {
  description = "Name of the key pair file"
  type        = string
  default     = "word2vec_key_pair_file"
}

# ------------- for vpc ------------


# variable "cidr_block" {
#  description = "CIDR Block"
#  type        = string
#  default     = "10.0.0.0/16"
# }
