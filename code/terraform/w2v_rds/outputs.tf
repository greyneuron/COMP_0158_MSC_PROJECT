output "rds_endpoint" {
  description = "rds endpoint"
  value       =  aws_db_instance.w2v-db.endpoint
}

output "rds_db_name" {
  description = "rds endpoint"
  value       =  aws_db_instance.w2v-db.db_name
}

output "rds_db_username" {
  description = "db username"
  value       =  aws_db_instance.w2v-db.username
}

output "rds_db_password" {
  description = "db password"
  value       =  aws_db_instance.w2v-db.password
  sensitive = true
}