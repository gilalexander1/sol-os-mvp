#!/bin/bash

# Sol OS MVP - Vercel Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

print_header() {
    echo -e "\n${PURPLE}===================================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}===================================================${NC}\n"
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header "Sol OS MVP - Vercel Deployment"

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    print_warning "Vercel CLI not found. Installing..."
    npm install -g vercel
    print_success "Vercel CLI installed"
fi

# Check if we're in the right directory
if [ ! -f "vercel.json" ]; then
    print_error "Please run this script from the sol-os-mvp root directory"
    exit 1
fi

print_status "Installing frontend dependencies..."
cd frontend
npm install
cd ..

print_status "Installing backend dependencies..."
pip install -r requirements.txt

print_status "Running pre-deployment checks..."

# Check for required files
REQUIRED_FILES=("vercel.json" "requirements.txt" ".env.example" "api/[...all].py")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Required file $file not found"
        exit 1
    fi
done

print_success "Pre-deployment checks passed"

# Environment variables check
print_header "Environment Variables Setup"

echo "Make sure you have configured these environment variables in Vercel:"
echo "  - DATABASE_URL (PostgreSQL connection string)"
echo "  - OPENAI_API_KEY (OpenAI API key)"
echo "  - JWT_SECRET_KEY (32-character JWT secret)"
echo "  - ENCRYPTION_KEY (64-character encryption key)"
echo ""

read -p "Have you configured all environment variables in Vercel? (y/N): " ENV_CONFIGURED
if [[ ! $ENV_CONFIGURED =~ ^[Yy]$ ]]; then
    print_warning "Please configure environment variables in your Vercel dashboard first"
    print_status "You can generate secure keys with:"
    echo "  JWT Secret: openssl rand -hex 32"
    echo "  Encryption Key: openssl rand -hex 64"
    exit 1
fi

# Deploy to Vercel
print_header "Deploying to Vercel"

print_status "Starting deployment..."
vercel --prod

print_success "Sol OS MVP deployed to Vercel!"

print_header "Post-Deployment Steps"
echo "1. 🔗 Visit your Vercel dashboard to get the deployment URL"
echo "2. 🗄️  Set up your database and run migrations if needed"  
echo "3. 🧪 Test the deployment with a health check"
echo "4. 🎯 Configure custom domain if desired"

print_success "Deployment completed successfully!"