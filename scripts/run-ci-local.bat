@echo off
REM Local CI/CD Pipeline Runner for StudyTracker (Windows)
REM This script runs the same checks as GitHub Actions locally

echo 🚀 Starting local CI/CD pipeline...

REM Check if we're in the right directory
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found. Please run this script from the project root.
    exit /b 1
)

echo [INFO] Installing dependencies...
REM Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    echo [WARNING] Virtual environment not detected. Attempting to activate...
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat
    ) else if exist ".venv\Scripts\activate.bat" (
        call .venv\Scripts\activate.bat
    ) else (
        echo [ERROR] No virtual environment found. Please create and activate one first.
        exit /b 1
    )
)

REM Use python -m pip to ensure we're using the correct pip
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt

echo [INFO] Running code formatting check with Black...
python -m black --check --diff src/ tests/
if %errorlevel% equ 0 (
    echo [SUCCESS] Code formatting is correct
) else (
    echo [WARNING] Code formatting issues found. Run 'python -m black src/ tests/' to fix.
)

echo [INFO] Running linting with Flake8...
python -m flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
if %errorlevel% neq 0 (
    echo [ERROR] Critical linting errors found
    exit /b 1
)

python -m flake8 src/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
if %errorlevel% equ 0 (
    echo [SUCCESS] Linting passed
) else (
    echo [WARNING] Some linting warnings found
)

echo [INFO] Running security checks with Bandit...
python -m bandit -r src/ -f json -o bandit-report.json
if %errorlevel% equ 0 (
    echo [SUCCESS] Security checks passed
) else (
    echo [WARNING] Security issues found. Check bandit-report.json for details.
)

echo [INFO] Running dependency vulnerability scan with Safety...
python -m safety check --json --output safety-report.json
if %errorlevel% equ 0 (
    echo [SUCCESS] No security vulnerabilities found in dependencies
) else (
    echo [WARNING] Security vulnerabilities found in dependencies. Check safety-report.json for details.
)

echo [INFO] Running tests with coverage...
python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=html
if %errorlevel% neq 0 (
    echo [ERROR] Some tests failed
    exit /b 1
)

echo [INFO] Checking test coverage...
python -m coverage report --fail-under=60

echo [INFO] Building package...
python setup.py sdist bdist_wheel
if %errorlevel% equ 0 (
    echo [SUCCESS] Package built successfully
) else (
    echo [ERROR] Package build failed
    exit /b 1
)

echo.
echo 🎉 Local CI/CD pipeline completed successfully!
echo.
echo 📊 Summary:
echo   ✅ Code formatting check
echo   ✅ Linting
echo   ✅ Security checks
echo   ✅ Tests with coverage
echo   ✅ Package build
echo.
echo 📁 Generated files:
echo   - bandit-report.json (security report)
echo   - safety-report.json (dependency vulnerabilities)
echo   - htmlcov/ (coverage report)
echo   - dist/ (built packages) 