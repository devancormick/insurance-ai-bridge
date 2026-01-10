#!/bin/bash
# User data script for Azure backend instances

set -e

# Update system
apt-get update
apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl start docker
systemctl enable docker
usermod -aG docker azureuser

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install monitoring agent (Azure Monitor Agent)
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Create application directory
mkdir -p /opt/insurance-ai-bridge
chown azureuser:azureuser /opt/insurance-ai-bridge

# Configure environment
cat > /opt/insurance-ai-bridge/.env <<EOF
REGION=${region}
ENVIRONMENT=production
CLOUD_PROVIDER=azure
EOF

echo "User data script completed successfully"

