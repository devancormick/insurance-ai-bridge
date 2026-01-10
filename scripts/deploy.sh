#!/bin/bash
# Deployment script for Insurance AI Bridge

set -e

echo "🚀 Starting deployment of Insurance AI Bridge..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file not found. Creating from template...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env file with your actual configuration before continuing.${NC}"
    read -p "Press enter to continue after editing .env file..."
fi

# Step 1: Build images
echo -e "${GREEN}Step 1: Building Docker images...${NC}"
docker-compose -f docker-compose.prod.yml build

# Step 2: Run database migrations
echo -e "${GREEN}Step 2: Running database migrations...${NC}"
docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head

# Step 3: Start services
echo -e "${GREEN}Step 3: Starting services...${NC}"
docker-compose -f docker-compose.prod.yml up -d

# Step 4: Wait for services to be healthy
echo -e "${GREEN}Step 4: Waiting for services to be healthy...${NC}"
sleep 10

# Check health
MAX_RETRIES=30
RETRY_COUNT=0
HEALTHY=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        HEALTHY=true
        break
    fi
    echo "Waiting for backend to be healthy... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ "$HEALTHY" = true ]; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${RED}✗ Backend failed to become healthy${NC}"
    docker-compose -f docker-compose.prod.yml logs backend
    exit 1
fi

# Step 5: Display service status
echo -e "${GREEN}Step 5: Deployment complete!${NC}"
echo ""
echo "Services are running:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
echo "View logs with: docker-compose -f docker-compose.prod.yml logs -f"
echo "Stop services with: docker-compose -f docker-compose.prod.yml down"

