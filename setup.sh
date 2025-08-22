#!/bin/bash

# Sol OS MVP Setup Script
# This script sets up the complete development environment

set -e

echo "🚀 Setting up Sol OS MVP..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    print_error "Please run this script from the Sol OS MVP root directory"
    exit 1
fi

# 1. Environment Setup
print_status "Setting up environment configuration..."

if [ ! -f "backend/.env" ]; then
    print_status "Creating backend .env file from example..."
    cp backend/.env.example backend/.env
    print_warning "Please edit backend/.env with your actual values:"
    print_warning "  - DATABASE_URL (PostgreSQL connection)"
    print_warning "  - JWT_SECRET_KEY (generate with: openssl rand -hex 32)"
    print_warning "  - DATA_ENCRYPTION_MASTER_KEY (generate with: openssl rand -hex 64)"
    print_warning "  - OPENAI_API_KEY (from OpenAI dashboard)"
else
    print_success "Backend .env file already exists"
fi

# 2. Database Setup
print_status "Setting up database..."

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
    print_warning "PostgreSQL is not running. Starting with Docker Compose..."
    
    # Navigate to ecosystem root and start PostgreSQL
    if [ -d "../../../infrastructure/docker" ]; then
        print_status "Starting shared infrastructure..."
        cd ../../../infrastructure/docker
        docker-compose up -d postgres redis
        cd - > /dev/null
        print_success "Shared infrastructure started"
    else
        print_error "Shared infrastructure not found. Please start PostgreSQL manually."
        print_error "Or run: docker run -d --name postgres -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:15"
        exit 1
    fi
else
    print_success "PostgreSQL is running"
fi

# Wait for PostgreSQL to be ready
print_status "Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
        print_success "PostgreSQL is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "PostgreSQL did not start in time"
        exit 1
    fi
    sleep 1
done

# 3. Backend Setup
print_status "Setting up backend dependencies..."

cd backend

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Run database migrations (if alembic is configured)
if [ -f "alembic.ini" ]; then
    print_status "Running database migrations..."
    alembic upgrade head
else
    print_warning "No alembic.ini found. Database tables will be created automatically."
fi

cd ..

# 4. Frontend Setup
print_status "Setting up frontend dependencies..."

cd frontend

# Check Node.js version
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+ and try again."
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    print_error "Node.js version 18+ required. Current version: $(node -v)"
    exit 1
fi

# Install dependencies
print_status "Installing Node.js dependencies..."
npm install

cd ..

# 5. Verification
print_status "Verifying installation..."

# Check backend syntax
print_status "Checking backend Python syntax..."
cd backend
source venv/bin/activate
python3 -m py_compile main.py security.py models.py sol_personality.py
print_success "Backend syntax check passed"
cd ..

# Check frontend build
print_status "Checking frontend build..."
cd frontend
npm run build > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_success "Frontend build check passed"
else
    print_warning "Frontend build check failed - this is normal if environment variables are missing"
fi
cd ..

# 6. Generate example secrets
print_status "Generating example secure keys..."
echo ""
echo "🔐 Security Keys (add these to backend/.env):"
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)"
echo "DATA_ENCRYPTION_MASTER_KEY=$(openssl rand -hex 64)"
echo ""

# 7. Final instructions
print_success "✅ Sol OS MVP setup complete!"
echo ""
echo "🚀 To start the development servers:"
echo ""
echo "1. Start the backend:"
echo "   cd backend"
echo "   export JWT_SECRET_KEY=\"$(openssl rand -hex 32)\""
echo "   export DATA_ENCRYPTION_MASTER_KEY=\"$(openssl rand -hex 64)\""
echo "   export OPENAI_API_KEY=\"your-actual-openai-key\""
echo "   uvicorn main:app --reload --port 8004"
echo ""
echo "2. Start the frontend (in a new terminal):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. Visit http://localhost:3001 to use Sol OS"
echo ""
echo "📋 Important next steps:"
echo "   • Edit backend/.env with your OpenAI API key"
echo "   • Update database connection if needed"
echo "   • Check that PostgreSQL is running"
echo ""
echo "🧠 About Sol OS:"
echo "   Your ADHD AI companion with security-first architecture"
echo "   Features: Chat with Sol, Focus Timer, Task Management"
echo ""
print_success "Happy coding! 🎉"