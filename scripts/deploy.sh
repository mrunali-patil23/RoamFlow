#!/bin/bash

# AI Trip Planner Deployment Script
# This script handles the complete deployment process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_TYPE=${1:-"docker"}
ENVIRONMENT=${2:-"production"}

echo -e "${BLUE}🚀 AI Trip Planner Deployment Script${NC}"
echo -e "${BLUE}======================================${NC}"
echo -e "Deployment Type: ${YELLOW}$DEPLOYMENT_TYPE${NC}"
echo -e "Environment: ${YELLOW}$ENVIRONMENT${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check environment variables
check_env_vars() {
    echo -e "${BLUE}🔍 Checking environment variables...${NC}"
    
    required_vars=("SUPABASE_URL" "SUPABASE_KEY" "SERP_API_KEY" "GEMINI_API_KEY" "SECRET_KEY")
    missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        echo -e "${RED}❌ Missing required environment variables:${NC}"
        for var in "${missing_vars[@]}"; do
            echo -e "  - ${RED}$var${NC}"
        done
        echo ""
        echo -e "${YELLOW}Please set these variables in your .env file or environment.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ All required environment variables are set${NC}"
}

# Function to run tests
run_tests() {
    echo -e "${BLUE}🧪 Running tests...${NC}"
    
    # Backend tests
    echo -e "${YELLOW}Running backend tests...${NC}"
    cd backend
    if ! python -m pytest tests/ -v --tb=short; then
        echo -e "${RED}❌ Backend tests failed${NC}"
        exit 1
    fi
    cd ..
    
    # Frontend tests
    echo -e "${YELLOW}Running frontend tests...${NC}"
    cd frontend
    if ! npm test -- --run; then
        echo -e "${RED}❌ Frontend tests failed${NC}"
        exit 1
    fi
    cd ..
    
    echo -e "${GREEN}✅ All tests passed${NC}"
}

# Function to deploy with Docker
deploy_docker() {
    echo -e "${BLUE}🐳 Deploying with Docker...${NC}"
    
    # Check if Docker is installed
    if ! command_exists docker; then
        echo -e "${RED}❌ Docker is not installed${NC}"
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        echo -e "${RED}❌ Docker Compose is not installed${NC}"
        exit 1
    fi
    
    # Stop existing containers
    echo -e "${YELLOW}Stopping existing containers...${NC}"
    docker-compose down --remove-orphans || true
    
    # Build and start containers
    echo -e "${YELLOW}Building and starting containers...${NC}"
    if [ "$ENVIRONMENT" = "production" ]; then
        docker-compose -f docker-compose.prod.yml up --build -d
    else
        docker-compose up --build -d
    fi
    
    # Wait for services to be healthy
    echo -e "${YELLOW}Waiting for services to be healthy...${NC}"
    sleep 30
    
    # Check service health
    if docker-compose ps | grep -q "unhealthy"; then
        echo -e "${RED}❌ Some services are unhealthy${NC}"
        docker-compose logs
        exit 1
    fi
    
    echo -e "${GREEN}✅ Docker deployment completed successfully${NC}"
}

# Function to deploy manually
deploy_manual() {
    echo -e "${BLUE}📦 Manual deployment...${NC}"
    
    # Build frontend
    echo -e "${YELLOW}Building frontend...${NC}"
    cd frontend
    npm ci
    npm run build
    cd ..
    
    # Install backend dependencies
    echo -e "${YELLOW}Installing backend dependencies...${NC}"
    cd backend
    pip install -r requirements.txt
    cd ..
    
    echo -e "${GREEN}✅ Manual build completed${NC}"
    echo -e "${YELLOW}Note: You need to manually start the services:${NC}"
    echo -e "  Backend: cd backend && uvicorn main:app --host 0.0.0.0 --port 8000"
    echo -e "  Frontend: Serve the frontend/dist directory with a web server"
}

# Function to show deployment status
show_status() {
    echo -e "${BLUE}📊 Deployment Status${NC}"
    echo -e "${BLUE}==================${NC}"
    
    if [ "$DEPLOYMENT_TYPE" = "docker" ]; then
        echo -e "${YELLOW}Docker containers:${NC}"
        docker-compose ps
        echo ""
        
        echo -e "${YELLOW}Service URLs:${NC}"
        echo -e "  Frontend: ${GREEN}http://localhost${NC}"
        echo -e "  Backend API: ${GREEN}http://localhost:8000${NC}"
        echo -e "  Health Check: ${GREEN}http://localhost:8000/health${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
}

# Main deployment flow
main() {
    # Load environment variables
    if [ -f .env ]; then
        export $(cat .env | grep -v '^#' | xargs)
    fi
    
    # Check environment variables
    check_env_vars
    
    # Run tests (skip in CI/CD environments)
    if [ "$SKIP_TESTS" != "true" ]; then
        run_tests
    fi
    
    # Deploy based on type
    case $DEPLOYMENT_TYPE in
        "docker")
            deploy_docker
            ;;
        "manual")
            deploy_manual
            ;;
        *)
            echo -e "${RED}❌ Unknown deployment type: $DEPLOYMENT_TYPE${NC}"
            echo -e "${YELLOW}Supported types: docker, manual${NC}"
            exit 1
            ;;
    esac
    
    # Show status
    show_status
}

# Show help
show_help() {
    echo "AI Trip Planner Deployment Script"
    echo ""
    echo "Usage: $0 [deployment_type] [environment]"
    echo ""
    echo "Deployment Types:"
    echo "  docker    - Deploy using Docker Compose (default)"
    echo "  manual    - Manual build for custom deployment"
    echo ""
    echo "Environments:"
    echo "  production - Production environment (default)"
    echo "  staging    - Staging environment"
    echo ""
    echo "Examples:"
    echo "  $0 docker production"
    echo "  $0 manual staging"
    echo ""
    echo "Environment Variables Required:"
    echo "  SUPABASE_URL, SUPABASE_KEY, SERP_API_KEY, GEMINI_API_KEY, SECRET_KEY"
}

# Handle help flag
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
    exit 0
fi

# Run main function
main