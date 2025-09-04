#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AShare数据源模块 - AShare Data Source Module

基于AKShare等开源数据接口的A股数据源实现。
提供实时数据和历史数据获取功能。

Based on AKShare and other open-source data interfaces.
Provides real-time and historical data fetching capabilities.

Author: minshengzhong3-byte
GitHub: https://github.com/minshengzhong3-byte/china-stock-data-source
License: MIT
"""

import pandas as pd
import numpy as np
import requests
import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import logging
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class AshareDataSource:
    """
    AShare数据源类
    
    基于多个开源数据接口的A股数据获取实现。
    支持实时数据和历史数据获取。
    """
    
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        """初始化AShare数据源"""
        self.name = "ashare"
        self.description = "AShare开源数据接口"
        self.timeout = timeout
        self.max_retries = max_retries
        
        # 数据接口配置
        self.apis = {
            'realtime': {
                'sina': 'https://hq.sinajs.cn/list=',
                'qq': 'https://qt.gtimg.cn/q=',
                'eastmoney': 'https://push2.eastmoney.com/api/qt/stock/get'
            },
            'history': {
                'sina': 'https://quotes.sina.cn/cn/api/json_v2.php/CN_MarketData.getKLineData',
                'netease': 'https://quotes.money.163.com/service/chddata.html'
            }
        }
        
        # 请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://finance.sina.com.cn/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        logger.info("AShare data source initialized")
    
    def get_realtime_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取股票实时价格
        
        Args:
            symbol: 6位股票代码
        
        Returns:
            实时价格信息字典或None
        """
        # 尝试多个数据源
        for source_name, base_url in self.apis['realtime'].items():
            try:
                data = self._fetch_realtime_from_source(symbol, source_name, base_url)
                if data:
                    return data
            except Exception as e:
                logger.warning(f"Failed to fetch realtime data from {source_name}: {e}")
                continue
        
        logger.error(f"Failed to fetch realtime data for {symbol} from all sources")
        return None
    
    def _fetch_realtime_from_source(self, symbol: str, source: str, base_url: str) -> Optional[Dict[str, Any]]:
        """
        从指定数据源获取实时数据
        
        Args:
            symbol: 股票代码
            source: 数据源名称
            base_url: 基础URL
        
        Returns:
            实时数据字典或None
        """
        if source == 'sina':
            return self._fetch_sina_realtime(symbol, base_url)
        elif source == 'qq':
            return self._fetch_qq_realtime(symbol, base_url)
        elif source == 'eastmoney':
            return self._fetch_eastmoney_realtime(symbol, base_url)
        else:
            return None
    
    def _fetch_sina_realtime(self, symbol: str, base_url: str) -> Optional[Dict[str, Any]]:
        """
        从新浪财经获取实时数据
        """
        try:
            # 转换股票代码格式
            sina_symbol = self._convert_to_sina_format(symbol)
            url = f"{base_url}{sina_symbol}"
            
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            # 解析新浪数据格式
            content = response.text.strip()
            if not content or 'var hq_str_' not in content:
                return None
            
            # 提取数据部分
            data_part = content.split('="')[1].split('";')[0]
            fields = data_part.split(',')
            
            if len(fields) < 32:  # 新浪数据至少有32个字段
                return None
            
            # 解析字段
            try:
                current_price = float(fields[3]) if fields[3] else 0
                prev_close = float(fields[2]) if fields[2] else 0
                change = current_price - prev_close
                change_percent = (change / prev_close * 100) if prev_close > 0 else 0
                
                return {
                    'symbol': symbol,
                    'name': fields[0],
                    'price': current_price,
                    'change': change,
                    'change_percent': round(change_percent, 2),
                    'open': float(fields[1]) if fields[1] else 0,
                    'prev_close': prev_close,
                    'high': float(fields[4]) if fields[4] else 0,
                    'low': float(fields[5]) if fields[5] else 0,
                    'volume': int(fields[8]) if fields[8] else 0,
                    'amount': float(fields[9]) if fields[9] else 0,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'source': 'sina'
                }
            except (ValueError, IndexError) as e:
                logger.error(f"Error parsing sina data: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Sina realtime fetch error: {e}")
            return None
    
    def _fetch_qq_realtime(self, symbol: str, base_url: str) -> Optional[Dict[str, Any]]:
        """
        从腾讯财经获取实时数据
        """
        try:
            # 转换股票代码格式
            qq_symbol = self._convert_to_qq_format(symbol)
            url = f"{base_url}{qq_symbol}"
            
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            # 解析腾讯数据格式
            content = response.text.strip()
            if not content or 'v_' not in content:
                return None
            
            # 提取数据部分
            data_part = content.split('="')[1].split('";')[0]
            fields = data_part.split('~')
            
            if len(fields) < 50:  # 腾讯数据字段较多
                return None
            
            try:
                current_price = float(fields[3]) if fields[3] else 0
                prev_close = float(fields[4]) if fields[4] else 0
                change = current_price - prev_close
                change_percent = float(fields[32]) if fields[32] else 0
                
                return {
                    'symbol': symbol,
                    'name': fields[1],
                    'price': current_price,
                    'change': change,
                    'change_percent': change_percent,
                    'open': float(fields[5]) if fields[5] else 0,
                    'prev_close': prev_close,
                    'high': float(fields[33]) if fields[33] else 0,
                    'low': float(fields[34]) if fields[34] else 0,
                    'volume': int(fields[6]) if fields[6] else 0,
                    'amount': float(fields[37]) if fields[37] else 0,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'source': 'qq'
                }
            except (ValueError, IndexError) as e:
                logger.error(f"Error parsing qq data: {e}")
                return None
                
        except Exception as e:
            logger.error(f"QQ realtime fetch error: {e}")
            return None
    
    def _fetch_eastmoney_realtime(self, symbol: str, base_url: str) -> Optional[Dict[str, Any]]:
        """
        从东方财富获取实时数据
        """
        try:
            # 构建请求参数
            params = {
                'secid': self._convert_to_eastmoney_format(symbol),
                'fields': 'f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f57,f58'
            }
            
            response = requests.get(base_url, params=params, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            if not data or 'data' not in data or not data['data']:
                return None
            
            stock_data = data['data']
            
            try:
                current_price = stock_data.get('f43', 0) / 100  # 东方财富价格需要除以100
                prev_close = stock_data.get('f60', 0) / 100
                change = current_price - prev_close
                change_percent = stock_data.get('f170', 0) / 100
                
                return {
                    'symbol': symbol,
                    'name': stock_data.get('f58', ''),
                    'price': current_price,
                    'change': change,
                    'change_percent': change_percent,
                    'open': stock_data.get('f46', 0) / 100,
                    'prev_close': prev_close,
                    'high': stock_data.get('f44', 0) / 100,
                    'low': stock_data.get('f45', 0) / 100,
                    'volume': stock_data.get('f47', 0),
                    'amount': stock_data.get('f48', 0),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'source': 'eastmoney'
                }
            except (ValueError, KeyError) as e:
                logger.error(f"Error parsing eastmoney data: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Eastmoney realtime fetch error: {e}")
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
        # 尝试多个数据源
        for source_name, base_url in self.apis['history'].items():
            try:
                data = self._fetch_history_from_source(symbol, start_date, end_date, period, source_name, base_url)
                if data is not None and not data.empty:
                    return data
            except Exception as e:
                logger.warning(f"Failed to fetch history data from {source_name}: {e}")
                continue
        
        logger.error(f"Failed to fetch history data for {symbol} from all sources")
        return None
    
    def _fetch_history_from_source(self, symbol: str, start_date: str, end_date: str, 
                                  period: str, source: str, base_url: str) -> Optional[pd.DataFrame]:
        """
        从指定数据源获取历史数据
        """
        if source == 'netease':
            return self._fetch_netease_history(symbol, start_date, end_date, base_url)
        elif source == 'sina':
            return self._fetch_sina_history(symbol, start_date, end_date, base_url)
        else:
            return None
    
    def _fetch_netease_history(self, symbol: str, start_date: str, end_date: str, base_url: str) -> Optional[pd.DataFrame]:
        """
        从网易财经获取历史数据
        """
        try:
            # 转换日期格式
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            
            # 构建请求参数
            params = {
                'code': self._convert_to_netease_format(symbol),
                'start': start_date_obj.strftime('%Y%m%d'),
                'end': end_date_obj.strftime('%Y%m%d'),
                'fields': 'TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER'
            }
            
            response = requests.get(base_url, params=params, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            # 解析CSV数据
            lines = response.text.strip().split('\n')
            if len(lines) < 2:  # 至少需要标题行和一行数据
                return None
            
            # 创建DataFrame
            data_lines = lines[1:]  # 跳过标题行
            data_rows = []
            
            for line in data_lines:
                fields = line.split(',')
                if len(fields) >= 10:
                    try:
                        data_rows.append({
                            'date': datetime.strptime(fields[0], '%Y-%m-%d'),
                            'open': float(fields[6]),
                            'high': float(fields[2]),
                            'low': float(fields[3]),
                            'close': float(fields[1]),
                            'volume': int(fields[8]) if fields[8] != 'None' else 0,
                            'amount': float(fields[9]) if fields[9] != 'None' else 0
                        })
                    except (ValueError, IndexError):
                        continue
            
            if not data_rows:
                return None
            
            df = pd.DataFrame(data_rows)
            df = df.sort_values('date').reset_index(drop=True)
            return df
            
        except Exception as e:
            logger.error(f"Netease history fetch error: {e}")
            return None
    
    def _fetch_sina_history(self, symbol: str, start_date: str, end_date: str, base_url: str) -> Optional[pd.DataFrame]:
        """
        从新浪财经获取历史数据
        """
        try:
            # 构建请求参数
            params = {
                'symbol': self._convert_to_sina_format(symbol),
                'scale': '240',  # 日线
                'ma': 'no',
                'datalen': '1000'
            }
            
            response = requests.get(base_url, params=params, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            # 解析JSON数据
            data = response.json()
            if not data or not isinstance(data, list):
                return None
            
            data_rows = []
            for item in data:
                try:
                    date_obj = datetime.strptime(item['day'], '%Y-%m-%d')
                    # 过滤日期范围
                    if start_date <= item['day'] <= end_date:
                        data_rows.append({
                            'date': date_obj,
                            'open': float(item['open']),
                            'high': float(item['high']),
                            'low': float(item['low']),
                            'close': float(item['close']),
                            'volume': int(item['volume'])
                        })
                except (ValueError, KeyError):
                    continue
            
            if not data_rows:
                return None
            
            df = pd.DataFrame(data_rows)
            df = df.sort_values('date').reset_index(drop=True)
            return df
            
        except Exception as e:
            logger.error(f"Sina history fetch error: {e}")
            return None
    
    def _convert_to_sina_format(self, symbol: str) -> str:
        """转换为新浪格式"""
        if symbol.startswith('6'):
            return f"sh{symbol}"
        else:
            return f"sz{symbol}"
    
    def _convert_to_qq_format(self, symbol: str) -> str:
        """转换为腾讯格式"""
        if symbol.startswith('6'):
            return f"sh{symbol}"
        else:
            return f"sz{symbol}"
    
    def _convert_to_eastmoney_format(self, symbol: str) -> str:
        """转换为东方财富格式"""
        if symbol.startswith('6'):
            return f"1.{symbol}"  # 上海
        else:
            return f"0.{symbol}"  # 深圳
    
    def _convert_to_netease_format(self, symbol: str) -> str:
        """转换为网易格式"""
        if symbol.startswith('6'):
            return f"0{symbol}"  # 上海
        else:
            return f"1{symbol}"  # 深圳
    
    def test_connection(self) -> bool:
        """
        测试数据源连接
        
        Returns:
            连接是否成功
        """
        try:
            # 测试实时数据
            test_data = self.get_realtime_price('000001')
            return test_data is not None
        except Exception as e:
            logger.error(f"AShare connection test failed: {e}")
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """
        获取数据源信息
        
        Returns:
            数据源信息字典
        """
        return {
            'name': self.name,
            'description': self.description,
            'available': True,
            'supports_realtime': True,
            'supports_history': True,
            'supported_periods': ['daily'],
            'data_quality': 'medium',
            'update_frequency': 'realtime',
            'apis': list(self.apis['realtime'].keys()) + list(self.apis['history'].keys())
        }

# 便捷函数
def create_ashare_source() -> AshareDataSource:
    """
    创建AShare数据源实例
    
    Returns:
        AshareDataSource实例
    """
    return AshareDataSource()

def test_ashare_source() -> bool:
    """
    测试AShare数据源
    
    Returns:
        测试是否成功
    """
    source = create_ashare_source()
    return source.test_connection()

if __name__ == "__main__":
    # 测试代码
    print("🌐 AShare Data Source - 测试模式")
    print("=" * 40)
    
    source = create_ashare_source()
    info = source.get_info()
    
    print(f"📊 数据源信息:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\n🧪 连接测试...")
    success = source.test_connection()
    print(f"  {'✅ 成功' if success else '❌ 失败'}")
    
    if success:
        print("\n💰 实时数据测试...")
        price_data = source.get_realtime_price('000001')
        if price_data:
            print(f"  📈 平安银行: {price_data['price']} ({price_data['change_percent']}%)")
        
        print("\n📊 历史数据测试...")
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        history_data = source.get_history_data('000001', start_date, end_date)
        if history_data is not None:
            print(f"  📈 获取到 {len(history_data)} 条历史数据")
    
    print("\n✅ 测试完成!")