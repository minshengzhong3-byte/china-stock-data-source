#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
China Stock Data Source - 量化框架适配器

为主流量化框架提供标准化数据接口，实现快速对接。

支持的框架:
- Backtrader
- Zipline
- VeighNa (VN.PY)
- 通用Pandas接口
- 自定义策略框架

使用示例:
    # Backtrader适配器
    from quant_adapters import BacktraderAdapter
    data_feed = BacktraderAdapter('000001')
    
    # VeighNa适配器
    from quant_adapters import VeighNaAdapter
    gateway = VeighNaAdapter()
    
    # 通用适配器
    from quant_adapters import UniversalAdapter
    adapter = UniversalAdapter()
    data = adapter.get_ohlcv('000001', '1d', 100)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
import warnings

try:
    from .unified_data_source import UnifiedDataSource, get_stock_data, get_realtime_price
except ImportError:
    from unified_data_source import UnifiedDataSource, get_stock_data, get_realtime_price

class BaseAdapter:
    """基础适配器类"""
    
    def __init__(self, timeout: int = 30):
        self.data_source = UnifiedDataSource(timeout=timeout)
        self.cache = {}
        self.cache_timeout = 300  # 5分钟缓存
    
    def _get_cached_data(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if (datetime.now() - timestamp).seconds < self.cache_timeout:
                return data
        return None
    
    def _set_cached_data(self, key: str, data: Any) -> None:
        """设置缓存数据"""
        self.cache[key] = (data, datetime.now())
    
    def normalize_symbol(self, symbol: str) -> str:
        """标准化股票代码"""
        # 移除可能的前缀和后缀
        symbol = symbol.upper().replace('.SZ', '').replace('.SH', '')
        
        # 确保6位数字格式
        if symbol.isdigit() and len(symbol) <= 6:
            return symbol.zfill(6)
        
        return symbol

class BacktraderAdapter(BaseAdapter):
    """Backtrader框架适配器"""
    
    def __init__(self, symbol: str, **kwargs):
        super().__init__(**kwargs)
        self.symbol = self.normalize_symbol(symbol)
        self._data = None
        self._current_index = 0
    
    def load_data(self, start_date: str = None, end_date: str = None, period: str = '1d') -> pd.DataFrame:
        """加载历史数据"""
        try:
            # 计算数据量
            if start_date and end_date:
                start = pd.to_datetime(start_date)
                end = pd.to_datetime(end_date)
                days = (end - start).days
                count = min(days * 2, 1000)  # 限制最大数据量
            else:
                count = 250  # 默认一年数据
            
            # 获取数据
            data = get_stock_data(self.symbol, period=period, count=count)
            
            if data is None or data.empty:
                raise ValueError(f"无法获取股票 {self.symbol} 的数据")
            
            # 转换为Backtrader格式
            bt_data = data.copy()
            bt_data.index = pd.to_datetime(bt_data.index)
            
            # 确保列名符合Backtrader要求
            column_mapping = {
                'open': 'open',
                'high': 'high', 
                'low': 'low',
                'close': 'close',
                'volume': 'volume'
            }
            
            for old_col, new_col in column_mapping.items():
                if old_col in bt_data.columns:
                    bt_data[new_col] = bt_data[old_col]
            
            # 添加OpenInterest列（期货用，股票设为0）
            bt_data['openinterest'] = 0
            
            # 过滤日期范围
            if start_date:
                bt_data = bt_data[bt_data.index >= start_date]
            if end_date:
                bt_data = bt_data[bt_data.index <= end_date]
            
            self._data = bt_data
            return bt_data
            
        except Exception as e:
            raise RuntimeError(f"Backtrader数据加载失败: {e}")
    
    def get_data_feed(self):
        """获取Backtrader数据源对象"""
        try:
            import backtrader as bt
            
            if self._data is None:
                self.load_data()
            
            # 创建Backtrader数据源
            data_feed = bt.feeds.PandasData(
                dataname=self._data,
                datetime=None,  # 使用索引作为日期
                open='open',
                high='high',
                low='low',
                close='close',
                volume='volume',
                openinterest='openinterest'
            )
            
            return data_feed
            
        except ImportError:
            raise ImportError("请先安装Backtrader: pip install backtrader")
        except Exception as e:
            raise RuntimeError(f"创建Backtrader数据源失败: {e}")

class VeighNaAdapter(BaseAdapter):
    """VeighNa (VN.PY) 框架适配器"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.subscribed_symbols = set()
    
    def get_contract_info(self, symbol: str) -> Dict:
        """获取合约信息"""
        symbol = self.normalize_symbol(symbol)
        
        # 判断交易所
        if symbol.startswith(('000', '002', '300')):
            exchange = 'SZSE'  # 深交所
        elif symbol.startswith(('600', '601', '603', '688')):
            exchange = 'SSE'   # 上交所
        else:
            exchange = 'SSE'   # 默认上交所
        
        return {
            'symbol': symbol,
            'exchange': exchange,
            'name': f'股票{symbol}',
            'product': 'EQUITY',
            'size': 100,  # 每手100股
            'pricetick': 0.01,  # 最小价格变动
            'min_volume': 100,  # 最小交易量
            'currency': 'CNY'
        }
    
    def get_bar_data(self, symbol: str, interval: str = '1d', count: int = 100) -> List[Dict]:
        """获取K线数据"""
        try:
            symbol = self.normalize_symbol(symbol)
            
            # 转换时间周期
            period_mapping = {
                '1m': '1min',
                '5m': '5min', 
                '15m': '15min',
                '30m': '30min',
                '1h': '1h',
                '1d': '1d',
                '1w': '1w'
            }
            
            period = period_mapping.get(interval, '1d')
            
            # 获取数据
            data = get_stock_data(symbol, period=period, count=count)
            
            if data is None or data.empty:
                return []
            
            # 转换为VeighNa格式
            bars = []
            for timestamp, row in data.iterrows():
                bar = {
                    'symbol': symbol,
                    'exchange': self.get_contract_info(symbol)['exchange'],
                    'datetime': pd.to_datetime(timestamp),
                    'interval': interval,
                    'volume': int(row.get('volume', 0)),
                    'turnover': float(row.get('amount', 0)),
                    'open_price': float(row.get('open', 0)),
                    'high_price': float(row.get('high', 0)),
                    'low_price': float(row.get('low', 0)),
                    'close_price': float(row.get('close', 0))
                }
                bars.append(bar)
            
            return bars
            
        except Exception as e:
            raise RuntimeError(f"获取VeighNa K线数据失败: {e}")
    
    def get_tick_data(self, symbol: str) -> Dict:
        """获取实时行情数据"""
        try:
            symbol = self.normalize_symbol(symbol)
            
            # 获取实时价格
            price_data = get_realtime_price(symbol)
            
            if not price_data:
                return {}
            
            contract_info = self.get_contract_info(symbol)
            
            # 转换为VeighNa Tick格式
            tick = {
                'symbol': symbol,
                'exchange': contract_info['exchange'],
                'datetime': datetime.now(),
                'name': contract_info['name'],
                'volume': int(price_data.get('volume', 0)),
                'turnover': float(price_data.get('amount', 0)),
                'open_price': float(price_data.get('open', 0)),
                'high_price': float(price_data.get('high', 0)),
                'low_price': float(price_data.get('low', 0)),
                'pre_close': float(price_data.get('pre_close', 0)),
                'last_price': float(price_data.get('current_price', 0)),
                'bid_price_1': float(price_data.get('bid1', 0)),
                'ask_price_1': float(price_data.get('ask1', 0)),
                'bid_volume_1': int(price_data.get('bid1_volume', 0)),
                'ask_volume_1': int(price_data.get('ask1_volume', 0))
            }
            
            return tick
            
        except Exception as e:
            raise RuntimeError(f"获取VeighNa Tick数据失败: {e}")

class ZiplineAdapter(BaseAdapter):
    """Zipline框架适配器"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def get_pricing_data(self, symbols: Union[str, List[str]], 
                        start_date: str, end_date: str, 
                        fields: List[str] = None) -> pd.DataFrame:
        """获取定价数据（Zipline格式）"""
        try:
            if isinstance(symbols, str):
                symbols = [symbols]
            
            if fields is None:
                fields = ['open', 'high', 'low', 'close', 'volume']
            
            all_data = {}
            
            for symbol in symbols:
                symbol = self.normalize_symbol(symbol)
                
                # 计算数据量
                start = pd.to_datetime(start_date)
                end = pd.to_datetime(end_date)
                days = (end - start).days
                count = min(days + 10, 1000)  # 多取一些数据确保覆盖
                
                # 获取数据
                data = get_stock_data(symbol, period='1d', count=count)
                
                if data is not None and not data.empty:
                    # 过滤日期范围
                    data.index = pd.to_datetime(data.index)
                    data = data[(data.index >= start_date) & (data.index <= end_date)]
                    
                    # 只保留需要的字段
                    available_fields = [f for f in fields if f in data.columns]
                    if available_fields:
                        all_data[symbol] = data[available_fields]
            
            if not all_data:
                return pd.DataFrame()
            
            # 合并数据
            if len(symbols) == 1:
                return all_data[symbols[0]]
            else:
                # 多股票数据需要重新组织结构
                combined_data = pd.concat(all_data, axis=1)
                return combined_data
                
        except Exception as e:
            raise RuntimeError(f"获取Zipline定价数据失败: {e}")
    
    def create_bundle_data(self, symbols: List[str], start_date: str, end_date: str) -> Dict:
        """创建Zipline数据包格式"""
        try:
            bundle_data = {
                'equities': [],
                'daily_bar_reader': {},
                'adjustment_reader': {}
            }
            
            for i, symbol in enumerate(symbols):
                symbol = self.normalize_symbol(symbol)
                
                # 股票信息
                equity_info = {
                    'sid': i,
                    'symbol': symbol,
                    'asset_name': f'股票{symbol}',
                    'start_date': pd.to_datetime(start_date),
                    'end_date': pd.to_datetime(end_date),
                    'exchange': 'XSHE' if symbol.startswith(('000', '002', '300')) else 'XSHG'
                }
                
                bundle_data['equities'].append(equity_info)
                
                # 获取价格数据
                price_data = self.get_pricing_data(symbol, start_date, end_date)
                if not price_data.empty:
                    bundle_data['daily_bar_reader'][i] = price_data
            
            return bundle_data
            
        except Exception as e:
            raise RuntimeError(f"创建Zipline数据包失败: {e}")

class UniversalAdapter(BaseAdapter):
    """通用适配器 - 提供标准化接口"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def get_ohlcv(self, symbol: str, timeframe: str = '1d', 
                  limit: int = 100, since: datetime = None) -> pd.DataFrame:
        """获取OHLCV数据（通用格式）"""
        try:
            symbol = self.normalize_symbol(symbol)
            
            # 缓存键
            cache_key = f"ohlcv_{symbol}_{timeframe}_{limit}"
            cached_data = self._get_cached_data(cache_key)
            if cached_data is not None:
                return cached_data
            
            # 获取数据
            data = get_stock_data(symbol, period=timeframe, count=limit)
            
            if data is None or data.empty:
                return pd.DataFrame()
            
            # 标准化列名
            standard_columns = {
                'open': 'open',
                'high': 'high',
                'low': 'low', 
                'close': 'close',
                'volume': 'volume'
            }
            
            result = pd.DataFrame()
            for old_col, new_col in standard_columns.items():
                if old_col in data.columns:
                    result[new_col] = data[old_col]
            
            # 确保索引是datetime类型
            result.index = pd.to_datetime(result.index)
            
            # 按日期过滤
            if since:
                result = result[result.index >= since]
            
            # 缓存结果
            self._set_cached_data(cache_key, result)
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"获取OHLCV数据失败: {e}")
    
    def get_realtime_quote(self, symbol: str) -> Dict:
        """获取实时报价"""
        try:
            symbol = self.normalize_symbol(symbol)
            
            # 缓存键
            cache_key = f"quote_{symbol}"
            cached_data = self._get_cached_data(cache_key)
            if cached_data is not None:
                return cached_data
            
            # 获取实时数据
            quote_data = get_realtime_price(symbol)
            
            if not quote_data:
                return {}
            
            # 标准化格式
            standard_quote = {
                'symbol': symbol,
                'timestamp': datetime.now(),
                'last_price': float(quote_data.get('current_price', 0)),
                'open': float(quote_data.get('open', 0)),
                'high': float(quote_data.get('high', 0)),
                'low': float(quote_data.get('low', 0)),
                'pre_close': float(quote_data.get('pre_close', 0)),
                'volume': int(quote_data.get('volume', 0)),
                'amount': float(quote_data.get('amount', 0)),
                'change': float(quote_data.get('change', 0)),
                'change_percent': float(quote_data.get('change_percent', 0)),
                'bid_price': float(quote_data.get('bid1', 0)),
                'ask_price': float(quote_data.get('ask1', 0)),
                'bid_volume': int(quote_data.get('bid1_volume', 0)),
                'ask_volume': int(quote_data.get('ask1_volume', 0))
            }
            
            # 缓存结果（较短时间）
            self.cache_timeout = 30  # 实时数据30秒缓存
            self._set_cached_data(cache_key, standard_quote)
            self.cache_timeout = 300  # 恢复默认缓存时间
            
            return standard_quote
            
        except Exception as e:
            raise RuntimeError(f"获取实时报价失败: {e}")
    
    def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Dict]:
        """批量获取实时报价"""
        quotes = {}
        
        for symbol in symbols:
            try:
                quote = self.get_realtime_quote(symbol)
                if quote:
                    quotes[symbol] = quote
            except Exception as e:
                warnings.warn(f"获取 {symbol} 报价失败: {e}")
                continue
        
        return quotes
    
    def calculate_indicators(self, data: pd.DataFrame, indicators: List[str]) -> pd.DataFrame:
        """计算技术指标"""
        try:
            result = data.copy()
            
            for indicator in indicators:
                if indicator.upper() == 'SMA_5':
                    result['sma_5'] = result['close'].rolling(window=5).mean()
                elif indicator.upper() == 'SMA_20':
                    result['sma_20'] = result['close'].rolling(window=20).mean()
                elif indicator.upper() == 'RSI':
                    # 简单RSI计算
                    delta = result['close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / loss
                    result['rsi'] = 100 - (100 / (1 + rs))
                elif indicator.upper() == 'MACD':
                    # 简单MACD计算
                    ema_12 = result['close'].ewm(span=12).mean()
                    ema_26 = result['close'].ewm(span=26).mean()
                    result['macd'] = ema_12 - ema_26
                    result['macd_signal'] = result['macd'].ewm(span=9).mean()
                    result['macd_histogram'] = result['macd'] - result['macd_signal']
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"计算技术指标失败: {e}")

# 便捷函数
def create_backtrader_feed(symbol: str, **kwargs):
    """创建Backtrader数据源"""
    adapter = BacktraderAdapter(symbol, **kwargs)
    return adapter.get_data_feed()

def create_veighna_gateway(**kwargs):
    """创建VeighNa网关"""
    return VeighNaAdapter(**kwargs)

def get_universal_data(symbol: str, timeframe: str = '1d', limit: int = 100):
    """获取通用格式数据"""
    adapter = UniversalAdapter()
    return adapter.get_ohlcv(symbol, timeframe, limit)

def get_multiple_realtime_data(symbols: List[str]):
    """批量获取实时数据"""
    adapter = UniversalAdapter()
    return adapter.get_multiple_quotes(symbols)

# 示例使用
if __name__ == '__main__':
    # 测试通用适配器
    print("测试通用适配器...")
    adapter = UniversalAdapter()
    
    # 获取历史数据
    data = adapter.get_ohlcv('000001', '1d', 10)
    print(f"历史数据: {len(data)} 条")
    print(data.head())
    
    # 获取实时报价
    quote = adapter.get_realtime_quote('000001')
    print(f"实时报价: {quote.get('last_price', 'N/A')}")
    
    print("\n适配器测试完成！")