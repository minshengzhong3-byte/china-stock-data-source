#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
China Stock Data Source 安装脚本

统一的A股数据获取模块，支持多数据源、智能故障转移、
高性能缓存，专为量化交易和AI应用设计。
"""

from setuptools import setup, find_packages
import os

# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取requirements文件
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# 版本信息
VERSION = "1.0.0"

setup(
    name="china-stock-data-source",
    version=VERSION,
    author="China Stock Data Source Team",
    author_email="support@example.com",
    description="统一的A股数据获取模块，支持多数据源、智能故障转移，专为量化交易和AI应用设计",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/minshengzhong3-byte/china-stock-data-source",
    project_urls={
        "Bug Reports": "https://github.com/minshengzhong3-byte/china-stock-data-source/issues",
        "Source": "https://github.com/minshengzhong3-byte/china-stock-data-source",
        "Documentation": "https://github.com/minshengzhong3-byte/china-stock-data-source#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "flake8>=3.8",
            "black>=21.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
        "full": [
            "abupy>=0.4.0",
            "beautifulsoup4>=4.9.0",
            "lxml>=4.6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "stock-data-test=src.unified_data_source:main",
        ],
    },
    include_package_data=True,
    package_data={
        "src": ["*.py"],
        "examples": ["*.py"],
        "tests": ["*.py"],
    },
    keywords=[
        "stock", "data", "finance", "trading", "quantitative", 
        "AI", "machine learning", "A股", "中国股市", "数据源"
    ],
    zip_safe=False,
)
