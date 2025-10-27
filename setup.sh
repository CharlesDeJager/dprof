#!/bin/bash

# DProf Setup Script
# This script sets up the complete DProf application

echo "🎯 DProf Setup Script"
echo "====================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Python is installed
check_python() {
    print_step "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
}

# Check if Node.js is installed
check_node() {
    print_step "Checking Node.js installation..."
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION found"
    else
        print_error "Node.js is not installed. Please install Node.js 16 or higher."
        exit 1
    fi
    
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        print_success "npm $NPM_VERSION found"
    else
        print_error "npm is not installed. Please install npm."
        exit 1
    fi
}

# Setup backend
setup_backend() {
    print_step "Setting up backend..."
    
    cd backend || { print_error "Backend directory not found"; exit 1; }
    
    # Create virtual environment
    print_step "Creating Python virtual environment..."
    python3 -m venv venv
    
    # Activate virtual environment
    print_step "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_step "Upgrading pip..."
    python -m pip install --upgrade pip
    
    # Install requirements
    print_step "Installing Python dependencies..."
    python -m pip install -r requirements.txt
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        print_step "Creating .env configuration file..."
        cp .env.example .env
        print_success ".env file created. You can edit it to customize settings."
    else
        print_warning ".env file already exists."
    fi
    
    # Create necessary directories
    mkdir -p temp exports
    
    cd ..
    print_success "Backend setup completed"
}

# Setup frontend
setup_frontend() {
    print_step "Setting up frontend..."
    
    cd frontend || { print_error "Frontend directory not found"; exit 1; }
    
    # Install npm dependencies
    print_step "Installing Node.js dependencies..."
    npm install
    
    cd ..
    print_success "Frontend setup completed"
}

# Create startup scripts
create_scripts() {
    print_step "Creating startup scripts..."
    
    # Create start script for Unix systems
    cat > start_dprof.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting DProf Application..."
echo

# Start backend
echo "📡 Starting backend server..."
cd backend
source venv/bin/activate
python run_server.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "🌐 Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo
echo "✅ DProf is starting up!"
echo "🌐 Frontend: http://localhost:3000"
echo "📡 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo
echo "⏹️  Press Ctrl+C to stop all servers"

# Function to cleanup on exit
cleanup() {
    echo
    echo "🛑 Shutting down DProf..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ All servers stopped"
    exit 0
}

# Set trap for cleanup
trap cleanup INT TERM

# Wait for processes
wait
EOF

    # Make the script executable
    chmod +x start_dprof.sh
    
    # Create Windows batch file
    cat > start_dprof.bat << 'EOF'
@echo off
echo 🚀 Starting DProf Application...
echo.

echo 📡 Starting backend server...
cd backend
call venv\Scripts\activate
start /B python run_server.py
cd ..

echo 🌐 Starting frontend server...
cd frontend
start /B npm start
cd ..

echo.
echo ✅ DProf is starting up!
echo 🌐 Frontend: http://localhost:3000
echo 📡 Backend API: http://localhost:8000
echo 📖 API Docs: http://localhost:8000/docs
echo.
echo ⏹️  Close this window to stop the servers

pause
EOF

    print_success "Startup scripts created (start_dprof.sh and start_dprof.bat)"
}

# Main setup function
main() {
    echo "This script will set up the complete DProf application."
    echo "It will install dependencies and create startup scripts."
    echo
    
    # Check prerequisites
    check_python
    check_node
    
    echo
    print_step "Starting DProf setup..."
    echo
    
    # Setup components
    setup_backend
    echo
    setup_frontend
    echo
    create_scripts
    
    echo
    print_success "🎉 DProf setup completed successfully!"
    echo
    echo "📋 Next steps:"
    echo "  1. Review and edit backend/.env for any custom configuration"
    echo "  2. For database connections:"
    echo "     - Oracle: Install Oracle Instant Client"
    echo "     - SQL Server: Install ODBC Driver 17 or 18"
    echo "  3. Run the application:"
    echo "     - Unix/Linux/macOS: ./start_dprof.sh"
    echo "     - Windows: start_dprof.bat"
    echo "     - Or manually start backend and frontend in separate terminals"
    echo
    echo "📖 For detailed documentation, see README.md"
    echo
}

# Run main function
main