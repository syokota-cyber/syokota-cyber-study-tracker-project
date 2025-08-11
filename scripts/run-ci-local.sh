#!/bin/bash

# StudyTracker Local CI Check Script
# 学習目的プロジェクト用のローカル品質チェック

set -e  # エラー時に停止

echo "🔍 StudyTracker Local CI Check"
echo "=================================="

# 色付き出力の関数
print_success() {
    echo -e "\033[32m✅ $1\033[0m"
}

print_error() {
    echo -e "\033[31m❌ $1\033[0m"
}

print_info() {
    echo -e "\033[34mℹ️  $1\033[0m"
}

print_warning() {
    echo -e "\033[33m⚠️  $1\033[0m"
}

# 依存関係の確認
check_dependencies() {
    print_info "Checking dependencies..."
    
    # Python バージョン確認
    python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_info "Python version: $python_version"
    
    # 必要なパッケージの確認
    required_packages=("black" "flake8" "pytest" "bandit")
    for package in "${required_packages[@]}"; do
        if python3 -c "import $package" 2>/dev/null; then
            print_success "$package is installed"
        else
            print_warning "$package is not installed"
            print_info "Install with: pip install -r requirements-dev.txt"
        fi
    done
}

# コードフォーマットチェック
check_formatting() {
    print_info "Running code formatting check..."
    
    if black --check --diff src/ tests/ 2>/dev/null; then
        print_success "Code formatting is correct"
    else
        print_error "Code formatting check failed"
        print_info "Run 'black src/ tests/' to fix formatting"
        return 1
    fi
}

# リンター実行
run_linting() {
    print_info "Running linting..."
    
    # 基本的なエラーチェック
    if flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics 2>/dev/null; then
        print_success "No critical linting errors found"
    else
        print_warning "Critical linting errors found"
    fi
    
    # スタイルチェック（警告のみ）
    flake8 src/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics 2>/dev/null || true
    print_info "Linting completed (warnings may be present)"
}

# セキュリティチェック
run_security_checks() {
    print_info "Running security checks..."
    
    # Bandit セキュリティチェック
    if command -v bandit >/dev/null 2>&1; then
        if bandit -r src/ -f json -o bandit-report.json 2>/dev/null; then
            print_success "Security check completed"
        else
            print_warning "Security issues found (check bandit-report.json)"
        fi
    else
        print_warning "bandit not installed, skipping security check"
    fi
}

# テスト実行
run_tests() {
    print_info "Running tests..."
    
    if pytest tests/ --cov=src --cov-report=term-missing --tb=short 2>/dev/null; then
        print_success "All tests passed"
    else
        print_error "Some tests failed"
        return 1
    fi
}

# カバレッジレポート
show_coverage() {
    print_info "Generating coverage report..."
    
    if pytest tests/ --cov=src --cov-report=html --cov-report=term-missing --tb=no 2>/dev/null; then
        print_success "Coverage report generated"
        print_info "Open htmlcov/index.html to view detailed coverage"
    else
        print_warning "Could not generate coverage report"
    fi
}

# メイン実行
main() {
    echo "Starting local CI checks..."
    echo ""
    
    # 依存関係確認
    check_dependencies
    echo ""
    
    # 各チェックの実行
    local exit_code=0
    
    if check_formatting; then
        print_success "Formatting check passed"
    else
        exit_code=1
    fi
    echo ""
    
    run_linting
    echo ""
    
    run_security_checks
    echo ""
    
    if run_tests; then
        print_success "Tests passed"
    else
        exit_code=1
    fi
    echo ""
    
    show_coverage
    echo ""
    
    # 結果表示
    echo "=================================="
    if [ $exit_code -eq 0 ]; then
        print_success "All CI checks completed successfully!"
        print_info "Your code is ready for deployment"
    else
        print_error "Some CI checks failed"
        print_info "Please fix the issues above before proceeding"
    fi
    
    return $exit_code
}

# スクリプト実行
main "$@" 