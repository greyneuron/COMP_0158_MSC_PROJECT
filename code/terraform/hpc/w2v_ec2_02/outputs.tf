output "w2v_ec2_instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.w2v-ec2-server-02.id
}

output "w2v_ec2_instance_type" {
  description = "EC2 Instance Type"
  value       = aws_instance.w2v-ec2-server-02.instance_type
}

output "w2v_ec2_public_dns" {
  description = "Public DNS of the EC2 instance"
  value       = aws_instance.w2v-ec2-server-02.public_dns
}
