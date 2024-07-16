output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.w2v-server.id
}

output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.w2v-server.public_ip
}

output "instance_public_dns" {
  description = "Public DNS of the EC2 instance"
  value       = aws_instance.w2v-server.public_dns
}


output "security_group_id" {
  description = "Security group id"
  value       = aws_security_group.w2v_security_group.id
}