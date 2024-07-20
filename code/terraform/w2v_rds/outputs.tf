output "rds_endpoint" {
  description = "rds endpoint"
  value       =  aws_db_instance.w2v-db.endpoint
}