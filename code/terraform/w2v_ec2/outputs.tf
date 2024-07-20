output "w2v_ec2_instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.w2v-server.id
}

output "w2v_ec2_public_dns" {
  description = "Public DNS of the EC2 instance"
  value       = aws_instance.w2v-server.public_dns
}


output "w2v_ec2_security_group_id" {
  description = "Security group id"
  value       = aws_security_group.w2v_security_group.id
}