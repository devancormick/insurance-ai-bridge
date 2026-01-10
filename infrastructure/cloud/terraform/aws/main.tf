# AWS Infrastructure as Code
# Multi-region deployment for Insurance AI Bridge

terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket         = "insurance-ai-bridge-terraform-state"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "insurance-ai-bridge"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# Variables
variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
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

# VPC Configuration
resource "aws_vpc" "main" {
  count = length(var.regions)
  
  cidr_block           = "10.${count.index}.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "insurance-ai-bridge-vpc-${var.regions[count.index]}"
  }
}

# Subnets
resource "aws_subnet" "public" {
  count = length(var.regions) * 3
  
  vpc_id                  = aws_vpc.main[floor(count.index / 3)].id
  cidr_block              = "10.${floor(count.index / 3)}.${count.index % 3 * 10}.0/24"
  availability_zone       = data.aws_availability_zones.available[floor(count.index / 3)].names[count.index % 3]
  map_public_ip_on_launch = true
  
  tags = {
    Name = "public-subnet-${count.index}"
    Type = "public"
  }
}

resource "aws_subnet" "private" {
  count = length(var.regions) * 3
  
  vpc_id            = aws_vpc.main[floor(count.index / 3)].id
  cidr_block        = "10.${floor(count.index / 3)}.${count.index % 3 * 10 + 100}.0/24"
  availability_zone = data.aws_availability_zones.available[floor(count.index / 3)].names[count.index % 3]
  
  tags = {
    Name = "private-subnet-${count.index}"
    Type = "private"
  }
}

data "aws_availability_zones" "available" {
  count = length(var.regions)
  state = "available"
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  count  = length(var.regions)
  vpc_id = aws_vpc.main[count.index].id
  
  tags = {
    Name = "igw-${var.regions[count.index]}"
  }
}

# NAT Gateway
resource "aws_eip" "nat" {
  count  = length(var.regions) * 3
  domain = "vpc"
  
  tags = {
    Name = "nat-eip-${count.index}"
  }
}

resource "aws_nat_gateway" "main" {
  count         = length(var.regions) * 3
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index * 3].id
  
  tags = {
    Name = "nat-gateway-${count.index}"
  }
}

# Route Tables
resource "aws_route_table" "public" {
  count  = length(var.regions)
  vpc_id = aws_vpc.main[count.index].id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main[count.index].id
  }
  
  tags = {
    Name = "public-rt-${var.regions[count.index]}"
  }
}

resource "aws_route_table" "private" {
  count  = length(var.regions) * 3
  vpc_id = aws_vpc.main[floor(count.index / 3)].id
  
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }
  
  tags = {
    Name = "private-rt-${count.index}"
  }
}

# Route Table Associations
resource "aws_route_table_association" "public" {
  count          = length(var.regions) * 3
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public[floor(count.index / 3)].id
}

resource "aws_route_table_association" "private" {
  count          = length(var.regions) * 3
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

# Security Groups
resource "aws_security_group" "api" {
  count       = length(var.regions)
  name        = "api-sg-${var.regions[count.index]}"
  description = "Security group for API servers"
  vpc_id      = aws_vpc.main[count.index].id
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "api-sg-${var.regions[count.index]}"
  }
}

resource "aws_security_group" "database" {
  count       = length(var.regions)
  name        = "database-sg-${var.regions[count.index]}"
  description = "Security group for database"
  vpc_id      = aws_vpc.main[count.index].id
  
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.api[count.index].id]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "database-sg-${var.regions[count.index]}"
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  count              = length(var.regions)
  name               = "insurance-ai-bridge-alb-${var.regions[count.index]}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.api[count.index].id]
  subnets            = aws_subnet.public[*].id
  
  enable_deletion_protection = var.environment == "prod" ? true : false
  
  tags = {
    Name = "main-alb-${var.regions[count.index]}"
  }
}

# Auto Scaling Group
resource "aws_launch_template" "backend" {
  count = length(var.regions)
  
  name_prefix   = "backend-${var.regions[count.index]}-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = "t3.large"
  
  vpc_security_group_ids = [aws_security_group.api[count.index].id]
  
  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    region = var.regions[count.index]
  }))
  
  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "backend-instance-${var.regions[count.index]}"
    }
  }
}

resource "aws_autoscaling_group" "backend" {
  count              = length(var.regions)
  name               = "backend-asg-${var.regions[count.index]}"
  vpc_zone_identifier = aws_subnet.private[*].id
  target_group_arns  = [aws_lb_target_group.backend[count.index].arn]
  health_check_type  = "ELB"
  
  min_size         = 10
  max_size         = 100
  desired_capacity = 20
  
  launch_template {
    id      = aws_launch_template.backend[count.index].id
    version = "$Latest"
  }
  
  tag {
    key                 = "Name"
    value               = "backend-asg-${var.regions[count.index]}"
    propagate_at_launch = true
  }
}

resource "aws_lb_target_group" "backend" {
  count    = length(var.regions)
  name     = "backend-tg-${var.regions[count.index]}"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = aws_vpc.main[count.index].id
  
  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/health"
    protocol            = "HTTP"
  }
}

resource "aws_lb_listener" "backend" {
  count             = length(var.regions)
  load_balancer_arn = aws_lb.main[count.index].arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = aws_acm_certificate.main[count.index].arn
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend[count.index].arn
  }
}

# ACM Certificate
resource "aws_acm_certificate" "main" {
  count            = length(var.regions)
  domain_name      = "api-${var.regions[count.index]}.insurance-ai-bridge.com"
  validation_method = "DNS"
  
  lifecycle {
    create_before_destroy = true
  }
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# RDS PostgreSQL Multi-Region
resource "aws_db_subnet_group" "main" {
  count      = length(var.regions)
  name       = "postgres-subnet-group-${var.regions[count.index]}"
  subnet_ids = aws_subnet.private[*].id
  
  tags = {
    Name = "postgres-subnet-group-${var.regions[count.index]}"
  }
}

resource "aws_db_instance" "postgres_primary" {
  count = length(var.regions)
  
  identifier           = "postgres-primary-${var.regions[count.index]}"
  engine               = "postgres"
  engine_version       = "15.4"
  instance_class       = "db.r5.xlarge"
  allocated_storage    = 1000
  storage_type         = "io1"
  iops                 = 10000
  storage_encrypted    = true
  
  db_name  = "insurance_ai_bridge"
  username = var.db_username
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.database[count.index].id]
  db_subnet_group_name   = aws_db_subnet_group.main[count.index].name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "mon:04:00-mon:05:00"
  
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  
  tags = {
    Name = "postgres-primary-${var.regions[count.index]}"
  }
}

# Read Replicas
resource "aws_db_instance" "postgres_replica" {
  count = length(var.regions) * 2
  
  identifier           = "postgres-replica-${count.index % 2 + 1}-${var.regions[floor(count.index / 2)]}"
  replicate_source_db  = aws_db_instance.postgres_primary[floor(count.index / 2)].identifier
  instance_class       = "db.r5.large"
  
  vpc_security_group_ids = [aws_security_group.database[floor(count.index / 2)].id]
  
  tags = {
    Name = "postgres-replica-${count.index}"
  }
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
}

# ElastiCache Redis Cluster
resource "aws_elasticache_subnet_group" "redis" {
  count      = length(var.regions)
  name       = "redis-subnet-group-${var.regions[count.index]}"
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_elasticache_replication_group" "redis" {
  count = length(var.regions)
  
  replication_group_id       = "redis-cluster-${var.regions[count.index]}"
  description                = "Redis cluster for caching"
  
  port               = 6379
  node_type          = "cache.r6g.xlarge"
  num_cache_clusters = 3
  
  parameter_group_name = "default.redis7"
  engine               = "redis"
  engine_version       = "7.0"
  
  subnet_group_name  = aws_elasticache_subnet_group.redis[count.index].name
  security_group_ids = [aws_security_group.redis[count.index].id]
  
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  
  automatic_failover_enabled = true
  multi_az_enabled          = true
  
  snapshot_retention_limit = 7
  snapshot_window         = "03:00-05:00"
  
  tags = {
    Name = "redis-cluster-${var.regions[count.index]}"
  }
}

resource "aws_security_group" "redis" {
  count       = length(var.regions)
  name        = "redis-sg-${var.regions[count.index]}"
  description = "Security group for Redis"
  vpc_id      = aws_vpc.main[count.index].id
  
  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.api[count.index].id]
  }
  
  tags = {
    Name = "redis-sg-${var.regions[count.index]}"
  }
}

# CloudFront CDN
resource "aws_cloudfront_distribution" "frontend" {
  count = length(var.regions)
  
  origin {
    domain_name = aws_s3_bucket.frontend[count.index].bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.frontend[count.index].id}"
    
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.frontend[count.index].cloudfront_access_identity_path
    }
  }
  
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  
  default_cache_behavior {
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.frontend[count.index].id}"
    
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
    
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
    compress               = true
  }
  
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  
  viewer_certificate {
    cloudfront_default_certificate = false
    acm_certificate_arn            = aws_acm_certificate.cloudfront[count.index].arn
    ssl_support_method             = "sni-only"
    minimum_protocol_version       = "TLSv1.2_2021"
  }
  
  tags = {
    Name = "frontend-cdn-${var.regions[count.index]}"
  }
}

resource "aws_s3_bucket" "frontend" {
  count  = length(var.regions)
  bucket = "insurance-ai-bridge-frontend-${var.regions[count.index]}"
  
  tags = {
    Name = "frontend-bucket-${var.regions[count.index]}"
  }
}

resource "aws_cloudfront_origin_access_identity" "frontend" {
  count   = length(var.regions)
  comment = "OAI for frontend bucket"
}

resource "aws_acm_certificate" "cloudfront" {
  count            = length(var.regions)
  provider         = aws.us_east_1
  domain_name      = "*.insurance-ai-bridge.com"
  validation_method = "DNS"
}

provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}

# Global Accelerator for Multi-Region
resource "aws_globalaccelerator_accelerator" "main" {
  name            = "insurance-ai-bridge-global"
  ip_address_type = "IPV4"
  enabled         = true
  
  attributes {
    flow_logs_enabled   = true
    flow_logs_s3_bucket = aws_s3_bucket.global_accelerator_logs.bucket
    flow_logs_s3_prefix = "logs/"
  }
  
  tags = {
    Name = "global-accelerator"
  }
}

resource "aws_globalaccelerator_listener" "main" {
  accelerator_arn = aws_globalaccelerator_accelerator.main.id
  protocol        = "HTTPS"
  
  port_range {
    from_port = 443
    to_port   = 443
  }
  
  default_action {
    target_group_arn = aws_globalaccelerator_endpoint_group.backend[0].arn
  }
}

resource "aws_globalaccelerator_endpoint_group" "backend" {
  count             = length(var.regions)
  listener_arn      = aws_globalaccelerator_listener.main.id
  endpoint_group_region = var.regions[count.index]
  
  endpoint_configuration {
    endpoint_id = aws_lb.main[count.index].arn
    weight      = 100
  }
  
  health_check_protocol            = "HTTPS"
  health_check_path                = "/health"
  health_check_interval_seconds    = 30
  health_check_timeout_seconds     = 5
  healthy_threshold_count          = 2
  unhealthy_threshold_count        = 2
}

resource "aws_s3_bucket" "global_accelerator_logs" {
  bucket = "insurance-ai-bridge-global-accelerator-logs"
  
  tags = {
    Name = "global-accelerator-logs"
  }
}

# Outputs
output "vpc_ids" {
  value = aws_vpc.main[*].id
}

output "alb_dns_names" {
  value = aws_lb.main[*].dns_name
}

output "database_endpoints" {
  value = aws_db_instance.postgres_primary[*].endpoint
}

output "redis_endpoints" {
  value = aws_elasticache_replication_group.redis[*].configuration_endpoint_address
}

output "cloudfront_domains" {
  value = aws_cloudfront_distribution.frontend[*].domain_name
}

output "global_accelerator_dns" {
  value = aws_globalaccelerator_accelerator.main.dns_name
}

