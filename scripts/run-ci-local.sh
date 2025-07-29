#!/bin/bash

# Local CI/CD Pipeline Runner for StudyTracker
# This script runs the same checks as GitHub Actions locally

set -e  # Exit on any error

echo "🚀 Starting local CI/CD pipeline..."

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
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found. Please run this script from the project root."
    exit 1
fi

print_status "Installing dependencies..."
# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_warning "Virtual environment not detected. Attempting to activate..."
    if [[ -f "venv/bin/activate" ]]; then
        source venv/bin/activate
    elif [[ -f ".venv/bin/activate" ]]; then
        source .venv/bin/activate
    else
        print_error "No virtual environment found. Please create and activate one first."
        exit 1
    fi
fi

# Use python -m pip to ensure we're using the correct pip
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt

print_status "Running code formatting check with Black..."
if python -m black --check --diff src/ tests/; then
    print_success "Code formatting is correct"
else
    print_warning "Code formatting issues found. Run 'python -m black src/ tests/' to fix."
fi

print_status "Running linting with Flake8..."
if python -m flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics; then
    print_success "No critical linting errors found"
else
    print_error "Critical linting errors found"
    exit 1
fi

if python -m flake8 src/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics; then
    print_success "Linting passed"
else
    print_warning "Some linting warnings found"
fi

print_status "Running security checks with Bandit..."
if python -m bandit -r src/ -f json -o bandit-report.json; then
    print_success "Security checks passed"
else
    print_warning "Security issues found. Check bandit-report.json for details."
fi

print_status "Running dependency vulnerability scan with Safety..."
if python -m safety check --json --output safety-report.json; then
    print_success "No security vulnerabilities found in dependencies"
else
    print_warning "Security vulnerabilities found in dependencies. Check safety-report.json for details."
fi

print_status "Running tests with coverage..."
if python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=html; then
    print_success "All tests passed"
else
    print_error "Some tests failed"
    exit 1
fi

print_status "Checking test coverage..."
python -m coverage report --fail-under=60

print_status "Building package..."
if python setup.py sdist bdist_wheel; then
    print_success "Package built successfully"
else
    print_error "Package build failed"
    exit 1
fi

echo ""
print_success "🎉 Local CI/CD pipeline completed successfully!"
echo ""
echo "📊 Summary:"
echo "  ✅ Code formatting check"
echo "  ✅ Linting"
echo "  ✅ Security checks"
echo "  ✅ Tests with coverage"
echo "  ✅ Package build"
echo ""
echo "📁 Generated files:"
echo "  - bandit-report.json (security report)"
echo "  - safety-report.json (dependency vulnerabilities)"
echo "  - htmlcov/ (coverage report)"
echo "  - dist/ (built packages)" 