#!/bin/bash
# SSL certificate setup script using Let's Encrypt

set -e

DOMAIN="${1:-your-domain.com}"
EMAIL="${2:-admin@${DOMAIN}}"

if [ "$DOMAIN" = "your-domain.com" ]; then
    echo "Usage: ./setup_ssl.sh <domain> <email>"
    echo "Example: ./setup_ssl.sh api.example.com admin@example.com"
    exit 1
fi

echo "🔒 Setting up SSL certificates for ${DOMAIN}..."

# Install certbot if not installed
if ! command -v certbot &> /dev/null; then
    echo "Installing certbot..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get update
        sudo apt-get install -y certbot
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install certbot
    else
        echo "Please install certbot manually"
        exit 1
    fi
fi

# Generate certificate
sudo certbot certonly --standalone \
    --non-interactive \
    --agree-tos \
    --email "${EMAIL}" \
    -d "${DOMAIN}"

# Create SSL directory for nginx
mkdir -p nginx/ssl

# Copy certificates
sudo cp "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" nginx/ssl/cert.pem
sudo cp "/etc/letsencrypt/live/${DOMAIN}/privkey.pem" nginx/ssl/key.pem
sudo chown $USER:$USER nginx/ssl/*.pem

echo "✓ SSL certificates installed in nginx/ssl/"
echo ""
echo "Update nginx.conf to use these certificates"
echo "Set up renewal with: sudo certbot renew --dry-run"

