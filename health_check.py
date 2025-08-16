#!/usr/bin/env python3
"""
SAGE++ Trading Bot Health Check Script

Performs comprehensive system checks to ensure all components are working properly.
Run this script before deploying or after making changes.
"""

import sys
import os
import traceback
from pathlib import Path
from typing import List, Tuple

def check_python_version() -> Tuple[bool, str]:
    """Check Python version compatibility"""
    if sys.version_info < (3, 10):
        return False, f"Python 3.10+ required, found {sys.version_info.major}.{sys.version_info.minor}"
    return True, f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

def check_dependencies() -> Tuple[bool, str]:
    """Check critical dependencies"""
    critical_deps = [
        'yaml', 'numpy', 'pandas', 'scipy', 
        'aiohttp', 'asyncio', 'pathlib'
    ]
    
    missing = []
    for dep in critical_deps:
        try:
            __import__(dep)
        except ImportError:
            missing.append(dep)
    
    if missing:
        return False, f"Missing dependencies: {', '.join(missing)}"
    return True, f"All {len(critical_deps)} critical dependencies available"

def check_optional_dependencies() -> Tuple[bool, str]:
    """Check optional trading dependencies"""
    optional_deps = ['ccxt', 'sklearn', 'redis', 'psycopg2']
    
    missing = []
    for dep in optional_deps:
        try:
            __import__(dep)
        except ImportError:
            missing.append(dep)
    
    if missing:
        return False, f"Missing optional dependencies: {', '.join(missing)}"
    return True, f"All {len(optional_deps)} optional dependencies available"

def check_directory_structure() -> Tuple[bool, str]:
    """Check required directories and files"""
    required_paths = [
        'sagepp/',
        'sagepp/core/',
        'sagepp/discovery/',
        'config/',
        'logs/',
        'config/default.yaml',
        '.env.example',
        '.gitignore',
        'requirements.txt'
    ]
    
    missing = []
    for path in required_paths:
        if not Path(path).exists():
            missing.append(path)
    
    if missing:
        return False, f"Missing paths: {', '.join(missing)}"
    return True, f"All {len(required_paths)} required paths exist"

def check_package_imports() -> Tuple[bool, str]:
    """Check SAGE++ package imports"""
    try:
        import sagepp
        from sagepp.core.config import Config
        from sagepp.core.logger import setup_logging
        from sagepp.core.engine import TradingEngine
        return True, "All core SAGE++ modules import successfully"
    except Exception as e:
        return False, f"Import error: {str(e)}"

def check_configuration() -> Tuple[bool, str]:
    """Check configuration loading and validation"""
    try:
        from sagepp.core.config import Config
        config = Config.load('config/default.yaml')
        
        # Check paper trading works
        if not config.paper_trading:
            config.paper_trading = True
        
        # Basic validation
        if config.trading.initial_capital <= 0:
            return False, "Invalid initial capital in config"
            
        return True, f"Configuration valid (pair: {config.trading.primary_pair})"
    except Exception as e:
        return False, f"Configuration error: {str(e)}"

def check_logging() -> Tuple[bool, str]:
    """Check logging system"""
    try:
        from sagepp.core.logger import setup_logging, get_trading_logger
        
        # Test setup
        setup_logging(log_level='INFO', log_file='logs/health_check.log')
        
        # Test logger creation
        logger = get_trading_logger('health_check')
        logger.info("Health check logging test")
        
        return True, "Logging system functional"
    except Exception as e:
        return False, f"Logging error: {str(e)}"

def check_permissions() -> Tuple[bool, str]:
    """Check file system permissions"""
    try:
        # Test log directory write
        test_file = Path('logs/permission_test.tmp')
        test_file.write_text('test')
        test_file.unlink()
        
        return True, "File system permissions OK"
    except Exception as e:
        return False, f"Permission error: {str(e)}"

def main():
    """Run all health checks"""
    print("🔍 SAGE++ Trading Bot Health Check")
    print("=" * 40)
    
    checks = [
        ("Python Version", check_python_version),
        ("Critical Dependencies", check_dependencies),
        ("Optional Dependencies", check_optional_dependencies),
        ("Directory Structure", check_directory_structure),
        ("Package Imports", check_package_imports),
        ("Configuration", check_configuration),
        ("Logging System", check_logging),
        ("File Permissions", check_permissions),
    ]
    
    passed = 0
    failed = 0
    warnings = 0
    
    for check_name, check_func in checks:
        try:
            success, message = check_func()
            if success:
                print(f"✅ {check_name}: {message}")
                passed += 1
            else:
                if "optional" in check_name.lower():
                    print(f"⚠️  {check_name}: {message}")
                    warnings += 1
                else:
                    print(f"❌ {check_name}: {message}")
                    failed += 1
        except Exception as e:
            print(f"❌ {check_name}: Unexpected error - {str(e)}")
            failed += 1
            if '--verbose' in sys.argv:
                traceback.print_exc()
    
    print("\n" + "=" * 40)
    print(f"Health Check Results:")
    print(f"  ✅ Passed: {passed}")
    print(f"  ⚠️  Warnings: {warnings}")
    print(f"  ❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 SAGE++ Trading Bot is healthy and ready to run!")
        return 0
    else:
        print(f"\n🚨 {failed} critical issues found. Please fix before running.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
