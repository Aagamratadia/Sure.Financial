#!/bin/bash

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Credit Card Statement Parser${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker is not running${NC}"
    echo "Please start Docker Desktop"
    exit 1
fi

echo -e "${GREEN}✅ Docker is installed and running${NC}"
echo ""

# Menu
echo "Select an option:"
echo "1) Start Full Stack (Backend + Frontend + MongoDB)"
echo "2) Start Backend Only (Backend + MongoDB)"
echo "3) Stop All Services"
echo "4) View Logs"
echo "5) Clean Up (Remove all data)"
echo "6) Exit"
echo ""
read -p "Enter your choice [1-6]: " choice

case $choice in
    1)
        echo -e "${YELLOW}Starting full stack...${NC}"
        docker-compose -f docker-compose.full.yml up -d
        echo ""
        echo -e "${GREEN}✅ Services started successfully!${NC}"
        echo ""
        echo "Access the application at:"
        echo -e "${BLUE}Frontend: http://localhost:3000${NC}"
        echo -e "${BLUE}Backend API: http://localhost:8000${NC}"
        echo -e "${BLUE}API Docs: http://localhost:8000/docs${NC}"
        echo ""
        echo "To view logs: docker-compose -f docker-compose.full.yml logs -f"
        ;;
    2)
        echo -e "${YELLOW}Starting backend only...${NC}"
        docker-compose up -d
        echo ""
        echo -e "${GREEN}✅ Backend services started!${NC}"
        echo ""
        echo "Access the backend at:"
        echo -e "${BLUE}Backend API: http://localhost:8000${NC}"
        echo -e "${BLUE}API Docs: http://localhost:8000/docs${NC}"
        echo ""
        echo "To view logs: docker-compose logs -f"
        ;;
    3)
        echo -e "${YELLOW}Stopping all services...${NC}"
        docker-compose -f docker-compose.full.yml down
        docker-compose down
        echo -e "${GREEN}✅ All services stopped${NC}"
        ;;
    4)
        echo -e "${YELLOW}Viewing logs (Ctrl+C to exit)...${NC}"
        if docker ps | grep -q "card-parser-frontend"; then
            docker-compose -f docker-compose.full.yml logs -f
        else
            docker-compose logs -f
        fi
        ;;
    5)
        echo -e "${RED}⚠️  This will remove all data. Are you sure? (y/n)${NC}"
        read -p "" confirm
        if [ "$confirm" = "y" ]; then
            echo -e "${YELLOW}Cleaning up...${NC}"
            docker-compose -f docker-compose.full.yml down -v
            docker-compose down -v
            echo -e "${GREEN}✅ All services and data removed${NC}"
        else
            echo "Cancelled"
        fi
        ;;
    6)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac
