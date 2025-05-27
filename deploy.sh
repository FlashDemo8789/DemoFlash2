#!/bin/bash
# FLASH Platform Deployment Script

set -e

echo "🚀 FLASH Platform Deployment"
echo "=========================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    exit 1
fi

# Load environment variables
source .env

# Function to check dependencies
check_dependencies() {
    echo "📋 Checking dependencies..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker not found. Please install Docker."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose not found. Please install Docker Compose."
        exit 1
    fi
    
    echo "✅ All dependencies satisfied"
}

# Function to build images
build_images() {
    echo "🔨 Building Docker images..."
    docker-compose build --no-cache
    echo "✅ Images built successfully"
}

# Function to run tests
run_tests() {
    echo "🧪 Running tests..."
    docker run --rm \
        -v $(pwd):/app \
        -w /app \
        -e ENVIRONMENT=testing \
        python:3.11-slim \
        sh -c "pip install -r requirements.txt && python -m pytest tests/"
    echo "✅ Tests passed"
}

# Function to start services
start_services() {
    echo "🚀 Starting services..."
    docker-compose up -d
    echo "✅ Services started"
    
    echo "⏳ Waiting for services to be healthy..."
    sleep 10
    
    # Check health
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API is healthy"
    else
        echo "❌ API health check failed"
        docker-compose logs api
        exit 1
    fi
}

# Function to show status
show_status() {
    echo ""
    echo "📊 Deployment Status:"
    echo "===================="
    docker-compose ps
    echo ""
    echo "🌐 Access Points:"
    echo "- Frontend: http://localhost:3000"
    echo "- API: http://localhost:8000"
    echo "- API Docs: http://localhost:8000/docs"
    echo "- Prometheus: http://localhost:9090"
    echo ""
    echo "📋 Useful Commands:"
    echo "- View logs: docker-compose logs -f"
    echo "- Stop services: docker-compose down"
    echo "- Restart services: docker-compose restart"
}

# Main deployment flow
main() {
    case "${1:-deploy}" in
        deploy)
            check_dependencies
            build_images
            run_tests
            start_services
            show_status
            ;;
        build)
            check_dependencies
            build_images
            ;;
        test)
            check_dependencies
            run_tests
            ;;
        start)
            check_dependencies
            start_services
            show_status
            ;;
        stop)
            echo "🛑 Stopping services..."
            docker-compose down
            echo "✅ Services stopped"
            ;;
        restart)
            echo "🔄 Restarting services..."
            docker-compose restart
            show_status
            ;;
        status)
            show_status
            ;;
        logs)
            docker-compose logs -f ${2:-}
            ;;
        *)
            echo "Usage: $0 {deploy|build|test|start|stop|restart|status|logs [service]}"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"