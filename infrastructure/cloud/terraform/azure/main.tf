# Azure Infrastructure as Code
# Multi-region deployment for Insurance AI Bridge

terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.75"
    }
  }
  
  backend "azurerm" {
    resource_group_name  = "insurance-ai-bridge-terraform-rg"
    storage_account_name = "insaibridgetfstate"
    container_name       = "terraform-state"
    key                  = "infrastructure/terraform.tfstate"
  }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "regions" {
  description = "List of Azure regions for multi-region deployment"
  type        = list(string)
  default     = ["eastus", "westus2", "westeurope"]
}

variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

# Resource Groups
resource "azurerm_resource_group" "main" {
  count    = length(var.regions)
  name     = "rg-insurance-ai-bridge-${var.regions[count.index]}"
  location = var.regions[count.index]
  
  tags = {
    Environment = var.environment
    Project     = "insurance-ai-bridge"
    Region      = var.regions[count.index]
  }
}

# Virtual Networks
resource "azurerm_virtual_network" "main" {
  count               = length(var.regions)
  name                = "vnet-insurance-ai-bridge-${var.regions[count.index]}"
  address_space       = ["10.${count.index}.0.0/16"]
  location            = azurerm_resource_group.main[count.index].location
  resource_group_name = azurerm_resource_group.main[count.index].name
  
  tags = {
    Name = "vnet-${var.regions[count.index]}"
  }
}

# Subnets
resource "azurerm_subnet" "public" {
  count                = length(var.regions) * 3
  name                 = "subnet-public-${count.index}"
  resource_group_name  = azurerm_resource_group.main[floor(count.index / 3)].name
  virtual_network_name = azurerm_virtual_network.main[floor(count.index / 3)].name
  address_prefixes     = ["10.${floor(count.index / 3)}.${count.index % 3 * 10}.0/24"]
}

resource "azurerm_subnet" "private" {
  count                = length(var.regions) * 3
  name                 = "subnet-private-${count.index}"
  resource_group_name  = azurerm_resource_group.main[floor(count.index / 3)].name
  virtual_network_name = azurerm_virtual_network.main[floor(count.index / 3)].name
  address_prefixes     = ["10.${floor(count.index / 3)}.${count.index % 3 * 10 + 100}.0/24"]
}

# Network Security Groups
resource "azurerm_network_security_group" "api" {
  count               = length(var.regions)
  name                = "nsg-api-${var.regions[count.index]}"
  location            = azurerm_resource_group.main[count.index].location
  resource_group_name = azurerm_resource_group.main[count.index].name
  
  security_rule {
    name                       = "HTTPS"
    priority                   = 1000
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
  
  security_rule {
    name                       = "HTTP"
    priority                   = 1010
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
  
  tags = {
    Name = "nsg-api-${var.regions[count.index]}"
  }
}

resource "azurerm_network_security_group" "database" {
  count               = length(var.regions)
  name                = "nsg-database-${var.regions[count.index]}"
  location            = azurerm_resource_group.main[count.index].location
  resource_group_name = azurerm_resource_group.main[count.index].name
  
  security_rule {
    name                       = "PostgreSQL"
    priority                   = 1000
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "5432"
    source_application_security_group_ids = [azurerm_application_security_group.api[count.index].id]
    destination_address_prefix = "*"
  }
  
  tags = {
    Name = "nsg-database-${var.regions[count.index]}"
  }
}

resource "azurerm_application_security_group" "api" {
  count               = length(var.regions)
  name                = "asg-api-${var.regions[count.index]}"
  location            = azurerm_resource_group.main[count.index].location
  resource_group_name = azurerm_resource_group.main[count.index].name
}

# Public IPs
resource "azurerm_public_ip" "load_balancer" {
  count               = length(var.regions)
  name                = "pip-lb-${var.regions[count.index]}"
  location            = azurerm_resource_group.main[count.index].location
  resource_group_name = azurerm_resource_group.main[count.index].name
  allocation_method   = "Static"
  sku                 = "Standard"
  
  tags = {
    Name = "pip-lb-${var.regions[count.index]}"
  }
}

# Application Gateway
resource "azurerm_application_gateway" "main" {
  count               = length(var.regions)
  name                = "agw-insurance-ai-bridge-${var.regions[count.index]}"
  resource_group_name = azurerm_resource_group.main[count.index].name
  location            = azurerm_resource_group.main[count.index].location
  
  sku {
    name     = "WAF_v2"
    tier     = "WAF_v2"
    capacity = 2
  }
  
  gateway_ip_configuration {
    name      = "gateway-ip-config"
    subnet_id = azurerm_subnet.public[count.index * 3].id
  }
  
  frontend_port {
    name = "https"
    port = 443
  }
  
  frontend_port {
    name = "http"
    port = 80
  }
  
  frontend_ip_configuration {
    name                 = "frontend-ip"
    public_ip_address_id = azurerm_public_ip.load_balancer[count.index].id
  }
  
  backend_address_pool {
    name = "backend-pool"
    ip_addresses = azurerm_network_interface.backend[*].private_ip_address
  }
  
  backend_http_settings {
    name                  = "backend-http-settings"
    cookie_based_affinity = "Disabled"
    path                  = "/"
    port                  = 8000
    protocol              = "Http"
    request_timeout       = 60
    
    probe {
      name = "health-probe"
    }
  }
  
  http_listener {
    name                           = "https-listener"
    frontend_ip_configuration_name = "frontend-ip"
    frontend_port_name             = "https"
    protocol                       = "Https"
    ssl_certificate_name           = "ssl-certificate"
  }
  
  request_routing_rule {
    name                       = "https-rule"
    rule_type                  = "Basic"
    http_listener_name         = "https-listener"
    backend_address_pool_name  = "backend-pool"
    backend_http_settings_name = "backend-http-settings"
  }
  
  ssl_certificate {
    name     = "ssl-certificate"
    data     = var.ssl_certificate_data
    password = var.ssl_certificate_password
  }
  
  probe {
    name                = "health-probe"
    protocol            = "Http"
    path                = "/health"
    interval            = 30
    timeout             = 30
    unhealthy_threshold = 3
    healthy_threshold   = 2
  }
  
  waf_configuration {
    enabled          = true
    firewall_mode    = "Prevention"
    rule_set_type    = "OWASP"
    rule_set_version = "3.2"
  }
  
  tags = {
    Name = "agw-${var.regions[count.index]}"
  }
}

variable "ssl_certificate_data" {
  description = "SSL certificate data (base64 encoded)"
  type        = string
  sensitive   = true
}

variable "ssl_certificate_password" {
  description = "SSL certificate password"
  type        = string
  sensitive   = true
}

# Virtual Machine Scale Set
resource "azurerm_linux_virtual_machine_scale_set" "backend" {
  count               = length(var.regions)
  name                = "vmss-backend-${var.regions[count.index]}"
  resource_group_name = azurerm_resource_group.main[count.index].name
  location            = azurerm_resource_group.main[count.index].location
  sku                 = "Standard_D4s_v3"
  instances           = 10
  
  admin_username = "azureuser"
  admin_ssh_key {
    username   = "azureuser"
    public_key = var.ssh_public_key
  }
  
  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts-gen2"
    version   = "latest"
  }
  
  os_disk {
    storage_account_type = "Premium_LRS"
    caching              = "ReadWrite"
  }
  
  network_interface {
    name    = "nic-backend"
    primary = true
    
    ip_configuration {
      name                                   = "internal"
      primary                                = true
      subnet_id                              = azurerm_subnet.private[count.index * 3].id
      application_security_group_ids         = [azurerm_application_security_group.api[count.index].id]
      load_balancer_backend_address_pool_ids = [azurerm_application_gateway.main[count.index].backend_address_pool[0].id]
    }
  }
  
  identity {
    type = "SystemAssigned"
  }
  
  custom_data = base64encode(templatefile("${path.module}/user_data.sh", {
    region = var.regions[count.index]
  }))
  
  automatic_instance_repair {
    enabled = true
  }
  
  upgrade_mode = "Automatic"
  
  tags = {
    Name = "vmss-backend-${var.regions[count.index]}"
  }
}

variable "ssh_public_key" {
  description = "SSH public key for VM access"
  type        = string
  sensitive   = true
}

resource "azurerm_network_interface" "backend" {
  count               = 10
  name                = "nic-backend-${count.index}"
  location            = azurerm_resource_group.main[0].location
  resource_group_name = azurerm_resource_group.main[0].name
  
  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.private[0].id
    private_ip_address_allocation = "Dynamic"
    application_security_group_ids = [azurerm_application_security_group.api[0].id]
  }
}

# Azure Database for PostgreSQL
resource "azurerm_postgresql_flexible_server" "main" {
  count                  = length(var.regions)
  name                   = "postgres-${var.regions[count.index]}"
  resource_group_name    = azurerm_resource_group.main[count.index].name
  location               = azurerm_resource_group.main[count.index].location
  version                = "15"
  delegated_subnet_id    = azurerm_subnet.private[count.index * 3].id
  private_dns_zone_id    = azurerm_private_dns_zone.postgres[count.index].id
  
  administrator_login    = var.db_username
  administrator_password = var.db_password
  
  sku_name   = "GP_Standard_D4s_v3"
  storage_mb = 262144
  
  backup_retention_days        = 7
  geo_redundant_backup_enabled = true
  
  high_availability {
    mode                      = "ZoneRedundant"
    standby_availability_zone = 2
  }
  
  maintenance_window {
    day_of_week  = 0
    start_hour   = 4
    start_minute = 0
  }
  
  tags = {
    Name = "postgres-${var.regions[count.index]}"
  }
}

resource "azurerm_private_dns_zone" "postgres" {
  count               = length(var.regions)
  name                = "${var.regions[count.index]}.postgres.database.azure.com"
  resource_group_name = azurerm_resource_group.main[count.index].name
}

resource "azurerm_private_dns_zone_virtual_network_link" "postgres" {
  count                 = length(var.regions)
  name                  = "postgres-link-${var.regions[count.index]}"
  resource_group_name   = azurerm_resource_group.main[count.index].name
  private_dns_zone_name = azurerm_private_dns_zone.postgres[count.index].name
  virtual_network_id    = azurerm_virtual_network.main[count.index].id
}

variable "db_username" {
  description = "Database administrator username"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "Database administrator password"
  type        = string
  sensitive   = true
}

# Read Replicas
resource "azurerm_postgresql_flexible_server" "replica" {
  count              = length(var.regions) * 2
  name               = "postgres-replica-${count.index % 2 + 1}-${var.regions[floor(count.index / 2)]}"
  resource_group_name = azurerm_resource_group.main[floor(count.index / 2)].name
  location            = azurerm_resource_group.main[floor(count.index / 2)].location
  version             = "15"
  
  replica_backup_retention_days = 7
  create_mode                   = "Replica"
  source_server_id              = azurerm_postgresql_flexible_server.main[floor(count.index / 2)].id
  
  sku_name = "GP_Standard_D2s_v3"
  
  tags = {
    Name = "postgres-replica-${count.index}"
  }
}

# Azure Cache for Redis
resource "azurerm_redis_cache" "main" {
  count               = length(var.regions)
  name                = "redis-${var.regions[count.index]}"
  location            = azurerm_resource_group.main[count.index].location
  resource_group_name = azurerm_resource_group.main[count.index].name
  capacity            = 2
  family              = "C"
  sku_name            = "Standard"
  enable_non_ssl_port = false
  minimum_tls_version = "1.2"
  
  redis_configuration {
    maxmemory_reserved = 2
    maxmemory_delta    = 2
    maxmemory_policy   = "allkeys-lru"
  }
  
  patch_schedule {
    day_of_week    = "Sunday"
    start_hour_utc = 3
  }
  
  tags = {
    Name = "redis-${var.regions[count.index]}"
  }
}

# Azure CDN
resource "azurerm_cdn_profile" "frontend" {
  count               = length(var.regions)
  name                = "cdn-frontend-${var.regions[count.index]}"
  location            = "global"
  resource_group_name = azurerm_resource_group.main[count.index].name
  sku                 = "Standard_Microsoft"
}

resource "azurerm_cdn_endpoint" "frontend" {
  count               = length(var.regions)
  name                = "cdn-endpoint-${var.regions[count.index]}"
  profile_name        = azurerm_cdn_profile.frontend[count.index].name
  location            = "global"
  resource_group_name = azurerm_resource_group.main[count.index].name
  
  origin {
    name      = "storage-origin"
    host_name = azurerm_storage_account.frontend[count.index].primary_blob_host
  }
  
  delivery_rule {
    name  = "CompressContent"
    order = 1
    
    request_scheme_condition {
      match_values = ["HTTP", "HTTPS"]
    }
    
    url_file_extension_condition {
      operator     = "Contains"
      match_values = ["css", "js", "html", "json"]
    }
    
    modify_response_header_action {
      action = "Overwrite"
      name   = "Content-Encoding"
      value  = "gzip"
    }
  }
  
  global_delivery_rule {
    modify_response_header_action {
      action = "Overwrite"
      name   = "Cache-Control"
      value  = "public, max-age=3600"
    }
  }
}

resource "azurerm_storage_account" "frontend" {
  count                    = length(var.regions)
  name                     = "stafrontend${replace(var.regions[count.index], "-", "")}"
  resource_group_name      = azurerm_resource_group.main[count.index].name
  location                 = azurerm_resource_group.main[count.index].location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  static_website {
    index_document = "index.html"
  }
  
  tags = {
    Name = "frontend-storage-${var.regions[count.index]}"
  }
}

# Azure Traffic Manager (Global Load Balancer)
resource "azurerm_traffic_manager_profile" "main" {
  name                   = "tm-insurance-ai-bridge"
  resource_group_name    = azurerm_resource_group.main[0].name
  traffic_routing_method = "Performance"
  
  dns_config {
    relative_name = "insurance-ai-bridge"
    ttl           = 60
  }
  
  monitor_config {
    protocol                     = "HTTPS"
    port                         = 443
    path                         = "/health"
    interval_in_seconds          = 30
    timeout_in_seconds           = 10
    tolerated_number_of_failures = 2
  }
  
  endpoint {
    name                = "endpoint-eastus"
    target_resource_id  = azurerm_public_ip.load_balancer[0].id
    target              = azurerm_public_ip.load_balancer[0].fqdn
    type                = "azureEndpoints"
    priority            = 1
    weight              = 100
  }
  
  endpoint {
    name                = "endpoint-westus2"
    target_resource_id  = azurerm_public_ip.load_balancer[1].id
    target              = azurerm_public_ip.load_balancer[1].fqdn
    type                = "azureEndpoints"
    priority            = 2
    weight              = 100
  }
  
  endpoint {
    name                = "endpoint-westeurope"
    target_resource_id  = azurerm_public_ip.load_balancer[2].id
    target              = azurerm_public_ip.load_balancer[2].fqdn
    type                = "azureEndpoints"
    priority            = 3
    weight              = 100
  }
  
  tags = {
    Name = "traffic-manager"
  }
}

# Outputs
output "resource_group_names" {
  value = azurerm_resource_group.main[*].name
}

output "application_gateway_public_ips" {
  value = azurerm_public_ip.load_balancer[*].ip_address
}

output "database_endpoints" {
  value = azurerm_postgresql_flexible_server.main[*].fqdn
}

output "redis_endpoints" {
  value = azurerm_redis_cache.main[*].hostname
}

output "cdn_endpoints" {
  value = azurerm_cdn_endpoint.frontend[*].host_name
}

output "traffic_manager_dns" {
  value = azurerm_traffic_manager_profile.main.fqdn
}

