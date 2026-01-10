# Output definitions for AWS Terraform configuration

output "vpc_ids" {
  description = "VPC IDs for each region"
  value       = aws_vpc.main[*].id
}

output "vpc_cidr_blocks" {
  description = "CIDR blocks for each VPC"
  value       = aws_vpc.main[*].cidr_block
}

output "alb_dns_names" {
  description = "DNS names of Application Load Balancers"
  value       = aws_lb.main[*].dns_name
}

output "alb_arns" {
  description = "ARNs of Application Load Balancers"
  value       = aws_lb.main[*].arn
}

output "database_endpoints" {
  description = "RDS PostgreSQL primary endpoints"
  value       = aws_db_instance.postgres_primary[*].endpoint
}

output "database_replica_endpoints" {
  description = "RDS PostgreSQL read replica endpoints"
  value       = aws_db_instance.postgres_replica[*].endpoint
}

output "redis_endpoints" {
  description = "ElastiCache Redis configuration endpoints"
  value       = aws_elasticache_replication_group.redis[*].configuration_endpoint_address
}

output "redis_primary_endpoints" {
  description = "ElastiCache Redis primary endpoints"
  value       = aws_elasticache_replication_group.redis[*].primary_endpoint_address
}

output "redis_reader_endpoints" {
  description = "ElastiCache Redis reader endpoints"
  value       = aws_elasticache_replication_group.redis[*].reader_endpoint_address
}

output "cloudfront_domains" {
  description = "CloudFront distribution domain names"
  value       = aws_cloudfront_distribution.frontend[*].domain_name
}

output "cloudfront_distribution_ids" {
  description = "CloudFront distribution IDs"
  value       = aws_cloudfront_distribution.frontend[*].id
}

output "global_accelerator_dns" {
  description = "Global Accelerator DNS name"
  value       = aws_globalaccelerator_accelerator.main.dns_name
}

output "global_accelerator_ips" {
  description = "Global Accelerator IP addresses"
  value       = aws_globalaccelerator_accelerator.main.ip_sets[0].ip_addresses
}

output "s3_frontend_buckets" {
  description = "S3 bucket names for frontend assets"
  value       = aws_s3_bucket.frontend[*].id
}

output "acm_certificate_arns" {
  description = "ACM certificate ARNs"
  value       = aws_acm_certificate.main[*].arn
}

output "security_group_ids" {
  description = "Security group IDs"
  value = {
    api      = aws_security_group.api[*].id
    database = aws_security_group.database[*].id
    redis    = aws_security_group.redis[*].id
  }
}

output "subnet_ids" {
  description = "Subnet IDs organized by region and type"
  value = {
    public  = aws_subnet.public[*].id
    private = aws_subnet.private[*].id
  }
}

output "autoscaling_group_names" {
  description = "Autoscaling group names"
  value       = aws_autoscaling_group.backend[*].name
}

