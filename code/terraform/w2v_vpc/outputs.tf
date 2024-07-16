output "vpc_id" {
  description = "vpc id"
  value       = aws_vpc.w2v-dev-vpc.id
}

output "w2v_public_subnet_id" {
  description = "w2v public subnet id"
  value       = aws_subnet.public_subnet.id
}

output "w2v_private_subnet_id" {
  description = "w2v private subnet id"
  value       = aws_subnet.private_subnet.id
}

output "w2v_rds_subnet_1" {
  description = "w2v rds 1 subnet id"
  value       = aws_subnet.w2v_rds_subnet_1.id
}

output "w2v_rds_subnet_2" {
  description = "w2v rds 2 subnet id"
  value       = aws_subnet.w2v_rds_subnet_2.id
}