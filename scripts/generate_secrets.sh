#!/bin/bash
# Generate secure secrets for environment variables

echo "🔐 Generating secure secrets..."

generate_secret() {
    openssl rand -hex 32
}

echo ""
echo "Add these to your .env file:"
echo ""
echo "# Security Keys (generated on $(date))"
echo "SECRET_KEY=$(generate_secret)"
echo "ENCRYPTION_KEY=$(generate_secret)"
echo "JWT_SECRET=$(generate_secret)"
echo "NEXTAUTH_SECRET=$(generate_secret)"
echo ""
echo "⚠️  Keep these secrets secure and never commit them to Git!"

