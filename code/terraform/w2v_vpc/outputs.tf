output "vpc_id" {
  description = "w2v vpc id"
  value       = aws_vpc.w2v-dev-vpc.id
}

output "w2v_public_subnet_id" {
  description = "w2v public subnet id"
  value       = aws_subnet.w2v-public-subnet.id
}

output "w2v_private_subnet_id" {
  description = "w2v private subnet id"
  value       = aws_subnet.w2v-private-subnet.id
}

output "w2v_rds_subnet_1" {
  description = "w2v rds subnet-1 id"
  value       = aws_subnet.w2v-rds-subnet-1.id
}

output "w2v_rds_subnet_2" {
  description = "w2v rds subnet-2 id"
  value       = aws_subnet.w2v-rds-subnet-2.id
}