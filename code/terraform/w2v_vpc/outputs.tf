output "vpc_id" {
  description = "VPC Id"
  value       = aws_vpc.w2v-dev-vpc.id
}

output "w2v_public_subnet_id" {
  description = "W2V Public Subnet Id"
  value       = aws_subnet.public_subnet.id
}

output "w2v_private_subnet_id" {
  description = "W2V Private Subnet Id"
  value       = aws_subnet.private_subnet.id
}

output "w2v_rds_subnet_1" {
  description = "W2V RDS Subnet 1 Id"
  value       = aws_subnet.w2v_rds_subnet_1.id
}

output "w2v_rds_subnet_2" {
  description = "W2V RDS Subnet 2 Id"
  value       = aws_subnet.w2v_rds_subnet_2.id
}