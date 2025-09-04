#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ABu数据源模块 - ABu Data Source Module

基于ABu量化交易系统的数据源实现。
ABu是一个开源的量化交易框架，提供丰富的金融数据接口。

Based on ABu quantitative trading system.
ABu is an open-source quantitative trading framework with rich financial data interfaces.

Author: minshengzhong3-byte
GitHub: https://github.com/minshengzhong3-byte/china-stock-data-source
License: MIT
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class AbuDataSource:
    """
    ABu数据源类
    
    基于ABu量化框架的数据获取实现。
    ABu框架提供了丰富的A股数据接口，包括实时数据和历史数据。
    """
    
    def __init__(self):
        """初始化ABu数据源"""
        self.name = "abu"
        self.description = "ABu量化框架数据源"
        self._abu_available = False
        
        # 尝试导入ABu模块
        try:
            import abupy as abu
            self.abu = abu
            self._abu_available = True
            logger.info("ABu framework loaded successfully")
        except ImportError:
            logger.warning("ABu framework not available. Install with: pip install abupy")
            self.abu = None
    
    def is_available(self) -> bool:
        """检查数据源是否可用"""
        return self._abu_available
    
    def get_realtime_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取股票实时价格
        
        Args:
            symbol: 6位股票代码
        
        Returns:
            实时价格信息字典或None
        """
        if not self.is_available():
            raise ImportError("ABu framework not available")
        
        try:
            # ABu实时数据获取
            # 注意：ABu的实时数据接口可能需要特定配置
            
            # 这里提供一个模拟实现，实际使用时需要根据ABu的具体API调整
            # 由于ABu主要用于历史数据分析，实时数据可能需要其他数据源
            
            # 尝试使用ABu的市场数据接口
            if hasattr(self.abu, 'EMarketDataFetchMode'):
                # 设置数据获取模式
                self.abu.env.g_market_source = self.abu.EMarketDataFetchMode.E_DATA_FETCH_NORMAL
            
            # 模拟返回数据结构（实际实现需要调用ABu的具体API）
            # 这里返回None，表示ABu主要用于历史数据
            logger.info(f"ABu realtime data not implemented for {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"ABu realtime data fetch error for {symbol}: {e}")
            return None
    
    def get_history_data(self, 
                        symbol: str, 
                        start_date: str, 
                        end_date: str,
                        period: str = 'daily') -> Optional[pd.DataFrame]:
        """
        获取股票历史数据
        
        Args:
            symbol: 6位股票代码
            start_date: 开始日期 'YYYY-MM-DD'
            end_date: 结束日期 'YYYY-MM-DD'
            period: 数据周期
        
        Returns:
            历史数据DataFrame或None
        """
        if not self.is_available():
            raise ImportError("ABu framework not available")
        
        try:
            # 转换股票代码格式
            abu_symbol = self._convert_symbol_format(symbol)
            
            # 使用ABu获取历史数据
            if hasattr(self.abu, 'ABuSymbolPd'):
                # ABu的标准数据获取方式
                df = self.abu.ABuSymbolPd.make_kl_df(
                    abu_symbol, 
                    start=start_date, 
                    end=end_date
                )
                
                if df is not None and not df.empty:
                    # 标准化列名
                    df = self._normalize_columns(df)
                    return df
            
            # 备用方法：直接使用pandas_datareader风格的接口
            elif hasattr(self.abu, 'EMarketDataFetchMode'):
                # 设置数据源
                self.abu.env.g_market_source = self.abu.EMarketDataFetchMode.E_DATA_FETCH_NORMAL
                
                # 尝试获取数据
                # 这里需要根据ABu的具体版本和API进行调整
                logger.warning(f"ABu history data fetch not fully implemented for {symbol}")
                return None
            
            logger.warning("ABu data fetch methods not available")
            return None
            
        except Exception as e:
            logger.error(f"ABu history data fetch error for {symbol}: {e}")
            return None
    
    def _convert_symbol_format(self, symbol: str) -> str:
        """
        转换股票代码格式为ABu格式
        
        Args:
            symbol: 6位数字股票代码
        
        Returns:
            ABu格式的股票代码
        """
        # ABu通常使用带市场后缀的格式
        if symbol.startswith('6'):
            # 上海市场
            return f"{symbol}.XSHG"
        elif symbol.startswith(('0', '3')):
            # 深圳市场
            return f"{symbol}.XSHE"
        else:
            # 默认格式
            return symbol
    
    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        标准化DataFrame列名
        
        Args:
            df: 原始数据DataFrame
        
        Returns:
            标准化后的DataFrame
        """
        # ABu的列名映射
        column_mapping = {
            'open': 'open',
            'high': 'high', 
            'low': 'low',
            'close': 'close',
            'volume': 'volume',
            'date': 'date'
        }
        
        # 重命名列
        df_normalized = df.copy()
        
        # 如果有日期索引，重置为列
        if isinstance(df_normalized.index, pd.DatetimeIndex):
            df_normalized = df_normalized.reset_index()
            if 'index' in df_normalized.columns:
                df_normalized = df_normalized.rename(columns={'index': 'date'})
        
        # 标准化列名（转换为小写）
        df_normalized.columns = df_normalized.columns.str.lower()
        
        # 确保必要的列存在
        required_columns = ['open', 'high', 'low', 'close']
        for col in required_columns:
            if col not in df_normalized.columns:
                logger.warning(f"Missing required column: {col}")
        
        # 添加日期列（如果不存在）
        if 'date' not in df_normalized.columns and hasattr(df_normalized.index, 'date'):
            df_normalized['date'] = df_normalized.index
        
        return df_normalized
    
    def test_connection(self) -> bool:
        """
        测试数据源连接
        
        Returns:
            连接是否成功
        """
        if not self.is_available():
            return False
        
        try:
            # 尝试获取测试数据
            test_data = self.get_history_data(
                '000001', 
                (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                datetime.now().strftime('%Y-%m-%d')
            )
            return test_data is not None and not test_data.empty
        except Exception as e:
            logger.error(f"ABu connection test failed: {e}")
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """
        获取数据源信息
        
        Returns:
            数据源信息字典
        """
        info = {
            'name': self.name,
            'description': self.description,
            'available': self.is_available(),
            'supports_realtime': False,  # ABu主要用于历史数据
            'supports_history': True,
            'supported_periods': ['daily'],
            'data_quality': 'high',  # ABu数据质量较高
            'update_frequency': 'daily'
        }
        
        if self.is_available():
            try:
                info['abu_version'] = getattr(self.abu, '__version__', 'unknown')
            except:
                info['abu_version'] = 'unknown'
        
        return info

# 便捷函数
def create_abu_source() -> AbuDataSource:
    """
    创建ABu数据源实例
    
    Returns:
        AbuDataSource实例
    """
    return AbuDataSource()

def test_abu_source() -> bool:
    """
    测试ABu数据源
    
    Returns:
        测试是否成功
    """
    source = create_abu_source()
    return source.test_connection()

if __name__ == "__main__":
    # 测试代码
    print("🔧 ABu Data Source - 测试模式")
    print("=" * 40)
    
    source = create_abu_source()
    info = source.get_info()
    
    print(f"📊 数据源信息:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    if source.is_available():
        print("\n🧪 连接测试...")
        success = source.test_connection()
        print(f"  {'✅ 成功' if success else '❌ 失败'}")
    else:
        print("\n⚠️  ABu框架未安装，请运行: pip install abupy")
    
    print("\n✅ 测试完成!")