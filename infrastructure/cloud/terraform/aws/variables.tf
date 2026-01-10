# Variable definitions for AWS Terraform configuration

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod"
  }
}

variable "multi_region" {
  description = "Enable multi-region deployment"
  type        = bool
  default     = true
}

variable "regions" {
  description = "List of AWS regions for multi-region deployment"
  type        = list(string)
  default     = ["us-east-1", "us-west-2", "eu-west-1"]
}

variable "db_username" {
  description = "Database master username"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
  validation {
    condition     = length(var.db_password) >= 16
    error_message = "Database password must be at least 16 characters long"
  }
}

variable "domain_name" {
  description = "Base domain name for the application"
  type        = string
  default     = "insurance-ai-bridge.com"
}

variable "certificate_arn" {
  description = "ARN of ACM certificate for HTTPS (optional, will create if not provided)"
  type        = string
  default     = ""
}

variable "enable_waf" {
  description = "Enable AWS WAF for ALB"
  type        = bool
  default     = true
}

variable "backup_retention_days" {
  description = "Number of days to retain database backups"
  type        = number
  default     = 7
}

variable "postgres_instance_class" {
  description = "RDS PostgreSQL instance class"
  type        = string
  default     = "db.r5.xlarge"
}

variable "postgres_replica_instance_class" {
  description = "RDS PostgreSQL read replica instance class"
  type        = string
  default     = "db.r5.large"
}

variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.r6g.xlarge"
}

variable "redis_num_nodes" {
  description = "Number of Redis cache nodes"
  type        = number
  default     = 3
}

variable "backend_instance_type" {
  description = "EC2 instance type for backend autoscaling group"
  type        = string
  default     = "t3.large"
}

variable "backend_min_size" {
  description = "Minimum number of backend instances"
  type        = number
  default     = 10
}

variable "backend_max_size" {
  description = "Maximum number of backend instances"
  type        = number
  default     = 100
}

variable "backend_desired_capacity" {
  description = "Desired number of backend instances"
  type        = number
  default     = 20
}

variable "frontend_min_size" {
  description = "Minimum number of frontend instances"
  type        = number
  default     = 5
}

variable "frontend_max_size" {
  description = "Maximum number of frontend instances"
  type        = number
  default     = 50
}

variable "frontend_desired_capacity" {
  description = "Desired number of frontend instances"
  type        = number
  default     = 10
}

variable "tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default     = {}
}

