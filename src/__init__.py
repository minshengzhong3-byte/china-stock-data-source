#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
China Stock Data Source - 中国A股数据源统一接入模块

A unified data source module for China A-share stock market,
designed for quantitative trading with intelligent failover mechanism.

Author: minshengzhong3-byte
GitHub: https://github.com/minshengzhong3-byte/china-stock-data-source
License: MIT
"""

__version__ = "1.0.0"
__author__ = "minshengzhong3-byte"
__email__ = ""
__license__ = "MIT"
__description__ = "🚀 中国A股数据源统一接入模块 | Unified China A-Share Stock Data Source Module"

# Import main functions for easy access
try:
    from .unified_data_source import (
        UnifiedDataSource,
        get_stock_data,
        get_realtime_price
    )
    from .ashare_source import AshareDataSource
    from .abu_source import AbuDataSource
    
    __all__ = [
        'UnifiedDataSource',
        'get_stock_data', 
        'get_realtime_price',
        'AshareDataSource',
        'AbuDataSource'
    ]
except ImportError as e:
    # Handle import errors gracefully
    print(f"Warning: Some modules could not be imported: {e}")
    __all__ = []

# Package metadata
__package_info__ = {
    'name': 'china-stock-data-source',
    'version': __version__,
    'author': __author__,
    'description': __description__,
    'url': 'https://github.com/minshengzhong3-byte/china-stock-data-source',
    'license': __license__
}

def get_version():
    """Get package version."""
    return __version__

def get_info():
    """Get package information."""
    return __package_info__

# Quick test function
def quick_test():
    """Quick test to verify the package is working."""
    try:
        from .unified_data_source import get_stock_data
        print("✅ Package imported successfully!")
        print(f"📦 Version: {__version__}")
        print(f"👤 Author: {__author__}")
        print("🚀 Ready to use China Stock Data Source!")
        return True
    except Exception as e:
        print(f"❌ Package test failed: {e}")
        return False

if __name__ == "__main__":
    quick_test()