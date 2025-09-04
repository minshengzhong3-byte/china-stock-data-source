#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统一数据源模块 - Unified Data Source Module

整合多个A股数据源，提供统一的数据获取接口。
支持智能故障转移、数据缓存、质量验证。
专为量化交易和AI模型设计。

Integrates multiple A-share data sources with unified interface.
Supports intelligent failover, data caching, and quality validation.
Designed for quantitative trading and AI models.

Author: minshengzhong3-byte
GitHub: https://github.com/minshengzhong3-byte/china-stock-data-source
License: MIT
"""

import pandas as pd
import numpy as np
import requests
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from functools import wraps
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataSourceError(Exception):
    """数据源异常基类"""
    pass

class ConnectionError(DataSourceError):
    """连接异常"""
    pass

class DataQualityError(DataSourceError):
    """数据质量异常"""
    pass

class UnifiedDataSource:
    """
    统一数据源类 - 整合多个A股数据源
    
    Features:
    - 智能故障转移：自动切换可用数据源
    - 数据缓存：减少重复请求，提高性能
    - 质量验证：自动检测和过滤异常数据
    - 并发安全：支持多线程环境
    - AI友好：简洁的API设计，适合模型集成
    """
    
    def __init__(self, 
                 cache_expire_minutes: int = 5,
                 max_retries: int = 3,
                 timeout: int = 10,
                 enable_cache: bool = True,
                 data_sources: Optional[List[str]] = None):
        """
        初始化统一数据源
        
        Args:
            cache_expire_minutes: 缓存过期时间（分钟）
            max_retries: 最大重试次数
            timeout: 请求超时时间（秒）
            enable_cache: 是否启用缓存
            data_sources: 数据源优先级列表，默认为['abu', 'ashare']
        """
        self.cache_expire_minutes = cache_expire_minutes
        self.max_retries = max_retries
        self.timeout = timeout
        self.enable_cache = enable_cache
        
        # 数据源优先级
        self.data_sources = data_sources or ['abu', 'ashare']
        
        # 缓存和锁
        self._cache = {}
        self._cache_lock = threading.RLock()
        
        # 统计信息
        self._stats = {
            'requests': 0,
            'cache_hits': 0,
            'errors': 0,
            'source_usage': {source: 0 for source in self.data_sources}
        }
        
        # 初始化数据源
        self._init_data_sources()
        
        logger.info(f"UnifiedDataSource initialized with sources: {self.data_sources}")
    
    def _init_data_sources(self):
        """初始化数据源实例"""
        self._source_instances = {}
        
        for source in self.data_sources:
            try:
                if source == 'abu':
                    from .abu_source import AbuDataSource
                    self._source_instances[source] = AbuDataSource()
                elif source == 'ashare':
                    from .ashare_source import AshareDataSource
                    self._source_instances[source] = AshareDataSource()
                else:
                    logger.warning(f"Unknown data source: {source}")
            except ImportError as e:
                logger.warning(f"Failed to import {source} data source: {e}")
            except Exception as e:
                logger.error(f"Failed to initialize {source} data source: {e}")
    
    def _get_cache_key(self, method: str, *args, **kwargs) -> str:
        """生成缓存键"""
        key_parts = [method] + [str(arg) for arg in args]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")
        return "|".join(key_parts)
    
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """从缓存获取数据"""
        if not self.enable_cache:
            return None
            
        with self._cache_lock:
            if cache_key in self._cache:
                data, timestamp = self._cache[cache_key]
                if time.time() - timestamp < self.cache_expire_minutes * 60:
                    self._stats['cache_hits'] += 1
                    return data
                else:
                    # 缓存过期，删除
                    del self._cache[cache_key]
        return None
    
    def _set_cache(self, cache_key: str, data: Any):
        """设置缓存"""
        if not self.enable_cache:
            return
            
        with self._cache_lock:
            self._cache[cache_key] = (data, time.time())
    
    def _validate_symbol(self, symbol: str) -> str:
        """验证和标准化股票代码"""
        if not symbol:
            raise ValueError("股票代码不能为空")
        
        # 移除空格和特殊字符
        symbol = str(symbol).strip().upper()
        
        # 标准化为6位数字格式
        if symbol.isdigit():
            symbol = symbol.zfill(6)
        elif '.' in symbol:
            # 处理带后缀的格式，如 000001.SZ
            symbol = symbol.split('.')[0].zfill(6)
        
        # 验证格式
        if not (symbol.isdigit() and len(symbol) == 6):
            raise ValueError(f"无效的股票代码格式: {symbol}")
        
        return symbol
    
    def _validate_data_quality(self, data: Any, data_type: str) -> bool:
        """验证数据质量"""
        if data is None:
            return False
        
        try:
            if data_type == 'realtime':
                # 验证实时数据
                required_fields = ['price']
                if isinstance(data, dict):
                    return all(field in data and data[field] is not None for field in required_fields)
                return False
            
            elif data_type == 'history':
                # 验证历史数据
                if isinstance(data, pd.DataFrame) and not data.empty:
                    required_columns = ['open', 'high', 'low', 'close']
                    return all(col in data.columns for col in required_columns)
                return False
            
        except Exception as e:
            logger.warning(f"Data quality validation error: {e}")
            return False
        
        return True
    
    def get_realtime_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取股票实时价格信息
        
        Args:
            symbol: 股票代码（如'000001'）
        
        Returns:
            包含实时价格信息的字典，失败时返回None
            {
                'symbol': '000001',
                'price': 10.5,
                'change': 0.2,
                'change_percent': 1.94,
                'volume': 1000000,
                'timestamp': '2024-01-15 15:00:00'
            }
        """
        try:
            symbol = self._validate_symbol(symbol)
            cache_key = self._get_cache_key('realtime', symbol)
            
            # 尝试从缓存获取
            cached_data = self._get_from_cache(cache_key)
            if cached_data is not None:
                return cached_data
            
            # 从数据源获取
            self._stats['requests'] += 1
            
            for source_name in self.data_sources:
                if source_name not in self._source_instances:
                    continue
                
                try:
                    source = self._source_instances[source_name]
                    data = source.get_realtime_price(symbol)
                    
                    if self._validate_data_quality(data, 'realtime'):
                        self._stats['source_usage'][source_name] += 1
                        self._set_cache(cache_key, data)
                        return data
                    
                except Exception as e:
                    logger.warning(f"Failed to get realtime price from {source_name}: {e}")
                    continue
            
            # 所有数据源都失败
            self._stats['errors'] += 1
            logger.error(f"Failed to get realtime price for {symbol} from all sources")
            return None
            
        except Exception as e:
            self._stats['errors'] += 1
            logger.error(f"Error in get_realtime_price: {e}")
            return None
    
    def get_history_data(self, 
                        symbol: str, 
                        start_date: str, 
                        end_date: Optional[str] = None,
                        period: str = 'daily') -> Optional[pd.DataFrame]:
        """
        获取股票历史数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期，格式'YYYY-MM-DD'
            end_date: 结束日期，格式'YYYY-MM-DD'，默认为今天
            period: 数据周期，支持'daily', 'weekly', 'monthly'
        
        Returns:
            包含历史数据的DataFrame，失败时返回None
        """
        try:
            symbol = self._validate_symbol(symbol)
            
            if end_date is None:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            cache_key = self._get_cache_key('history', symbol, start_date, end_date, period)
            
            # 尝试从缓存获取
            cached_data = self._get_from_cache(cache_key)
            if cached_data is not None:
                return cached_data
            
            # 从数据源获取
            self._stats['requests'] += 1
            
            for source_name in self.data_sources:
                if source_name not in self._source_instances:
                    continue
                
                try:
                    source = self._source_instances[source_name]
                    data = source.get_history_data(symbol, start_date, end_date, period)
                    
                    if self._validate_data_quality(data, 'history'):
                        self._stats['source_usage'][source_name] += 1
                        self._set_cache(cache_key, data)
                        return data
                    
                except Exception as e:
                    logger.warning(f"Failed to get history data from {source_name}: {e}")
                    continue
            
            # 所有数据源都失败
            self._stats['errors'] += 1
            logger.error(f"Failed to get history data for {symbol} from all sources")
            return None
            
        except Exception as e:
            self._stats['errors'] += 1
            logger.error(f"Error in get_history_data: {e}")
            return None
    
    def normalize_symbol(self, symbol: str) -> str:
        """
        标准化股票代码格式
        
        Args:
            symbol: 原始股票代码
        
        Returns:
            标准化后的6位股票代码
        """
        return self._validate_symbol(symbol)
    
    def test_all_sources(self) -> Dict[str, bool]:
        """
        测试所有数据源的可用性
        
        Returns:
            各数据源的可用性状态
        """
        results = {}
        test_symbol = '000001'  # 使用平安银行作为测试
        
        for source_name in self.data_sources:
            if source_name not in self._source_instances:
                results[source_name] = False
                continue
            
            try:
                source = self._source_instances[source_name]
                data = source.get_realtime_price(test_symbol)
                results[source_name] = self._validate_data_quality(data, 'realtime')
            except Exception as e:
                logger.warning(f"Test failed for {source_name}: {e}")
                results[source_name] = False
        
        return results
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        获取使用统计信息
        
        Returns:
            统计信息字典
        """
        with self._cache_lock:
            cache_size = len(self._cache)
        
        return {
            **self._stats,
            'cache_size': cache_size,
            'cache_hit_rate': self._stats['cache_hits'] / max(self._stats['requests'], 1) * 100
        }
    
    def clear_cache(self):
        """清空缓存"""
        with self._cache_lock:
            self._cache.clear()
        logger.info("Cache cleared")

# 全局实例
_default_instance = None
_instance_lock = threading.Lock()

def get_default_instance() -> UnifiedDataSource:
    """获取默认的UnifiedDataSource实例（单例模式）"""
    global _default_instance
    if _default_instance is None:
        with _instance_lock:
            if _default_instance is None:
                _default_instance = UnifiedDataSource()
    return _default_instance

# 便捷函数
def get_stock_data(symbol: str, 
                  start_date: str, 
                  end_date: Optional[str] = None,
                  period: str = 'daily') -> Optional[pd.DataFrame]:
    """
    获取股票历史数据（便捷函数）
    
    Args:
        symbol: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        period: 数据周期
    
    Returns:
        历史数据DataFrame
    """
    return get_default_instance().get_history_data(symbol, start_date, end_date, period)

def get_realtime_price(symbol: str) -> Optional[Dict[str, Any]]:
    """
    获取股票实时价格（便捷函数）
    
    Args:
        symbol: 股票代码
    
    Returns:
        实时价格信息字典
    """
    return get_default_instance().get_realtime_price(symbol)

def main():
    """主函数 - 用于测试"""
    print("🚀 China Stock Data Source - 测试模式")
    print("=" * 50)
    
    # 创建数据源实例
    ds = UnifiedDataSource()
    
    # 测试数据源状态
    print("📊 测试数据源状态...")
    status = ds.test_all_sources()
    for source, available in status.items():
        status_icon = "✅" if available else "❌"
        print(f"  {status_icon} {source}: {'可用' if available else '不可用'}")
    
    # 测试实时数据
    print("\n💰 测试实时数据获取...")
    test_symbols = ['000001', '000002', '600000']
    for symbol in test_symbols:
        try:
            price_data = ds.get_realtime_price(symbol)
            if price_data:
                print(f"  📈 {symbol}: {price_data.get('price', 'N/A')} ({price_data.get('change_percent', 'N/A')}%)")
            else:
                print(f"  ❌ {symbol}: 获取失败")
        except Exception as e:
            print(f"  ❌ {symbol}: 错误 - {e}")
    
    # 显示统计信息
    print("\n📊 使用统计:")
    stats = ds.get_usage_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n✅ 测试完成!")

if __name__ == "__main__":
    main()