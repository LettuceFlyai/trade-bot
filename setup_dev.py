#!/usr/bin/env python3
"""
SAGE++ Trading Bot Development Setup Script

Automates the development environment setup process.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        if isinstance(command, str):
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        else:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False

def setup_development_environment():
    """Set up the complete development environment"""
    print("🚀 SAGE++ Trading Bot Development Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path('sagepp').exists():
        print("❌ Please run this script from the SAGE++ project root directory")
        return False
    
    # Install development dependencies
    dev_packages = [
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.1", 
        "pytest-cov>=4.1.0",
        "black>=23.7.0",
        "isort>=5.12.0",
        "flake8>=6.0.0",
        "mypy>=1.5.1",
        "pre-commit>=3.3.3"
    ]
    
    print("📦 Installing development dependencies...")
    for package in dev_packages:
        if not run_command([sys.executable, "-m", "pip", "install", package], 
                         f"Installing {package.split('>=')[0]}"):
            return False
    
    # Create development configuration
    dev_config_path = Path("config/development.yaml")
    if not dev_config_path.exists():
        print("📝 Creating development configuration...")
        dev_config = """# SAGE++ Development Configuration
# Overrides for development environment

trading:
  initial_capital: 1000.0  # Smaller amount for testing
  
exchange:
  testnet: true
  
monitoring:
  log_level: "DEBUG"
  
advanced:
  enable_meta_learning: false  # Disable for faster startup during dev
"""
        dev_config_path.write_text(dev_config)
        print("✅ Development configuration created")
    
    # Create pre-commit configuration
    precommit_config = Path(".pre-commit-config.yaml")
    if not precommit_config.exists():
        print("📝 Creating pre-commit configuration...")
        precommit_yaml = """repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3.10
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]
  
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
"""
        precommit_config.write_text(precommit_yaml)
        run_command([sys.executable, "-m", "pre_commit", "install"], "Installing pre-commit hooks")
    
    # Create test directory structure
    test_dir = Path("tests")
    if not test_dir.exists():
        print("📁 Creating test directory structure...")
        test_dirs = [
            "tests",
            "tests/unit",
            "tests/integration", 
            "tests/fixtures"
        ]
        for dir_path in test_dirs:
            Path(dir_path).mkdir(exist_ok=True)
            (Path(dir_path) / "__init__.py").write_text("")
        
        # Create sample test
        sample_test = Path("tests/test_config.py")
        sample_test.write_text("""import pytest
from sagepp.core.config import Config

def test_config_loading():
    \"\"\"Test configuration loading\"\"\"
    config = Config.load('config/default.yaml')
    assert config.trading.primary_pair == "SOL/USDT"
    assert config.paper_trading == True

def test_config_validation():
    \"\"\"Test configuration validation\"\"\"
    config = Config()
    config.paper_trading = True
    # Should not raise for paper trading
    config._validate()
    
    config.paper_trading = False
    # Should raise for live trading without API keys
    with pytest.raises(ValueError):
        config._validate()
""")
        print("✅ Test structure created")
    
    # Create Makefile for common tasks
    makefile = Path("Makefile")
    if not makefile.exists():
        print("📝 Creating Makefile...")
        makefile_content = """# SAGE++ Trading Bot Makefile

.PHONY: install test lint format health run-paper run-live clean

# Install dependencies
install:
	pip install -r requirements.txt
	pip install pytest pytest-asyncio black isort flake8 mypy

# Run tests
test:
	python -m pytest tests/ -v --cov=sagepp

# Run linting
lint:
	python -m flake8 sagepp/
	python -m mypy sagepp/

# Format code
format:
	python -m black sagepp/
	python -m isort sagepp/

# Health check
health:
	python health_check.py

# Run in paper trading mode
run-paper:
	python -m sagepp.main --paper --config config/default.yaml

# Run in development mode
run-dev:
	python -m sagepp.main --paper --config config/development.yaml --log-level DEBUG

# Run in live trading mode (DANGER!)
run-live:
	python -m sagepp.main --live --config config/default.yaml

# Clean up temporary files
clean:
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	rm -f logs/test*.log

# Development environment setup
dev-setup:
	python setup_dev.py
"""
        makefile.write_text(makefile_content)
        print("✅ Makefile created")
    
    print("\n" + "=" * 50)
    print("🎉 Development environment setup complete!")
    print("\nUseful commands:")
    print("  make health     - Run health check")
    print("  make test       - Run tests")  
    print("  make lint       - Run linting")
    print("  make format     - Format code")
    print("  make run-dev    - Run in development mode")
    print("  python health_check.py - Manual health check")
    
    return True

if __name__ == "__main__":
    success = setup_development_environment()
    sys.exit(0 if success else 1)
