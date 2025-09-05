#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
量化交易示例 - 使用China Stock Data Source模块

本示例展示如何在量化交易程序中集成和使用统一数据源模块
包含策略开发、回测、实时交易等场景的完整示例

Author: minshengzhong3-byte
GitHub: https://github.com/minshengzhong3-byte/china-stock-data-source
"""

import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import time

# 导入统一数据源模块
from unified_data_source import (
    UnifiedDataSource, 
    get_stock_data, 
    get_realtime_price, 
    get_history_data
)

class QuantitativeStrategy:
    """
    量化交易策略基类
    
    展示如何使用统一数据源进行策略开发
    """
    
    def __init__(self, name: str = "BaseStrategy"):
        self.name = name
        self.data_source = UnifiedDataSource()
        self.positions = {}  # 持仓信息
        self.cash = 1000000  # 初始资金100万
        self.total_value = self.cash
        self.trade_history = []  # 交易历史
        
        print(f"🚀 Strategy '{self.name}' initialized with ¥{self.cash:,.0f}")
    
    def get_stock_price(self, symbol: str) -> Optional[float]:
        """获取股票当前价格"""
        try:
            data = self.data_source.get_realtime_price(symbol)
            return data['current_price'] if data else None
        except Exception as e:
            print(f"❌ Error getting price for {symbol}: {e}")
            return None
    
    def get_stock_history(self, symbol: str, days: int = 30) -> Optional[pd.DataFrame]:
        """获取股票历史数据"""
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            return self.data_source.get_history_data(
                symbol, period='1d', start_date=start_date, end_date=end_date
            )
        except Exception as e:
            print(f"❌ Error getting history for {symbol}: {e}")
            return None
    
    def calculate_sma(self, symbol: str, period: int = 20) -> Optional[float]:
        """计算简单移动平均线"""
        history = self.get_stock_history(symbol, days=period + 10)
        if history is not None and len(history) >= period:
            return history['close'].tail(period).mean()
        return None
    
    def calculate_rsi(self, symbol: str, period: int = 14) -> Optional[float]:
        """计算相对强弱指数(RSI)"""
        history = self.get_stock_history(symbol, days=period + 10)
        if history is None or len(history) < period + 1:
            return None
        
        delta = history['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not rsi.empty else None
    
    def buy_stock(self, symbol: str, amount: float) -> bool:
        """买入股票"""
        price = self.get_stock_price(symbol)
        if price is None:
            print(f"❌ Cannot get price for {symbol}")
            return False
        
        cost = amount * price
        if cost > self.cash:
            print(f"❌ Insufficient cash: need ¥{cost:,.0f}, have ¥{self.cash:,.0f}")
            return False
        
        # 执行买入
        self.cash -= cost
        self.positions[symbol] = self.positions.get(symbol, 0) + amount
        
        # 记录交易
        trade = {
            'timestamp': datetime.now(),
            'symbol': symbol,
            'action': 'BUY',
            'amount': amount,
            'price': price,
            'cost': cost
        }
        self.trade_history.append(trade)
        
        print(f"✅ BUY {amount} shares of {symbol} at ¥{price:.2f} (Cost: ¥{cost:,.0f})")
        return True
    
    def sell_stock(self, symbol: str, amount: float) -> bool:
        """卖出股票"""
        if symbol not in self.positions or self.positions[symbol] < amount:
            print(f"❌ Insufficient position: need {amount}, have {self.positions.get(symbol, 0)}")
            return False
        
        price = self.get_stock_price(symbol)
        if price is None:
            print(f"❌ Cannot get price for {symbol}")
            return False
        
        # 执行卖出
        revenue = amount * price
        self.cash += revenue
        self.positions[symbol] -= amount
        
        if self.positions[symbol] == 0:
            del self.positions[symbol]
        
        # 记录交易
        trade = {
            'timestamp': datetime.now(),
            'symbol': symbol,
            'action': 'SELL',
            'amount': amount,
            'price': price,
            'revenue': revenue
        }
        self.trade_history.append(trade)
        
        print(f"✅ SELL {amount} shares of {symbol} at ¥{price:.2f} (Revenue: ¥{revenue:,.0f})")
        return True
    
    def get_portfolio_value(self) -> float:
        """计算投资组合总价值"""
        total_value = self.cash
        
        for symbol, amount in self.positions.items():
            price = self.get_stock_price(symbol)
            if price:
                total_value += amount * price
        
        return total_value
    
    def get_portfolio_status(self) -> Dict[str, Any]:
        """获取投资组合状态"""
        total_value = self.get_portfolio_value()
        return {
            'cash': self.cash,
            'positions': self.positions.copy(),
            'total_value': total_value,
            'profit_loss': total_value - 1000000,  # 相对于初始资金的盈亏
            'profit_loss_percent': (total_value - 1000000) / 1000000 * 100
        }

class MomentumStrategy(QuantitativeStrategy):
    """
    动量策略示例
    
    基于移动平均线和RSI指标的动量交易策略
    """
    
    def __init__(self):
        super().__init__("Momentum Strategy")
        self.sma_short = 5   # 短期均线
        self.sma_long = 20   # 长期均线
        self.rsi_oversold = 30   # RSI超卖阈值
        self.rsi_overbought = 70 # RSI超买阈值
    
    def analyze_stock(self, symbol: str) -> Dict[str, Any]:
        """分析股票"""
        current_price = self.get_stock_price(symbol)
        sma_short = self.calculate_sma(symbol, self.sma_short)
        sma_long = self.calculate_sma(symbol, self.sma_long)
        rsi = self.calculate_rsi(symbol)
        
        if None in [current_price, sma_short, sma_long, rsi]:
            return {'signal': 'HOLD', 'reason': 'Insufficient data'}
        
        # 生成交易信号
        if sma_short > sma_long and rsi < self.rsi_oversold:
            return {
                'signal': 'BUY',
                'reason': f'Golden cross + RSI oversold (RSI: {rsi:.1f})',
                'strength': min((self.rsi_oversold - rsi) / 10, 1.0)
            }
        elif sma_short < sma_long and rsi > self.rsi_overbought:
            return {
                'signal': 'SELL',
                'reason': f'Death cross + RSI overbought (RSI: {rsi:.1f})',
                'strength': min((rsi - self.rsi_overbought) / 10, 1.0)
            }
        else:
            return {
                'signal': 'HOLD',
                'reason': f'No clear signal (SMA: {sma_short:.2f}/{sma_long:.2f}, RSI: {rsi:.1f})'
            }
    
    def execute_strategy(self, symbols: List[str]):
        """执行策略"""
        print(f"\n🎯 Executing {self.name} on {len(symbols)} symbols...")
        
        for symbol in symbols:
            try:
                analysis = self.analyze_stock(symbol)
                print(f"\n📊 Analysis for {symbol}:")
                print(f"   Signal: {analysis['signal']}")
                print(f"   Reason: {analysis['reason']}")
                
                if analysis['signal'] == 'BUY':
                    # 计算买入数量（基于信号强度）
                    max_investment = self.cash * 0.1  # 最多投入10%资金
                    investment = max_investment * analysis.get('strength', 0.5)
                    
                    price = self.get_stock_price(symbol)
                    if price and investment > price * 100:  # 至少买100股
                        amount = int(investment / price / 100) * 100
                        self.buy_stock(symbol, amount)
                
                elif analysis['signal'] == 'SELL' and symbol in self.positions:
                    # 卖出部分或全部持仓
                    sell_ratio = analysis.get('strength', 0.5)
                    amount = int(self.positions[symbol] * sell_ratio)
                    if amount > 0:
                        self.sell_stock(symbol, amount)
                
            except Exception as e:
                print(f"❌ Error processing {symbol}: {e}")

class PairsTradingStrategy(QuantitativeStrategy):
    """
    配对交易策略示例
    
    基于两只相关股票价格差异的套利策略
    """
    
    def __init__(self, pair: tuple = ('000001', '600036')):
        super().__init__("Pairs Trading Strategy")
        self.pair = pair
        self.lookback_period = 30
        self.entry_threshold = 2.0  # 进入阈值（标准差倍数）
        self.exit_threshold = 0.5   # 退出阈值
    
    def calculate_spread(self) -> Optional[Dict[str, Any]]:
        """计算价差统计信息"""
        symbol1, symbol2 = self.pair
        
        # 获取历史数据
        hist1 = self.get_stock_history(symbol1, self.lookback_period + 10)
        hist2 = self.get_stock_history(symbol2, self.lookback_period + 10)
        
        if hist1 is None or hist2 is None:
            return None
        
        # 对齐数据
        common_dates = hist1.index.intersection(hist2.index)
        if len(common_dates) < self.lookback_period:
            return None
        
        price1 = hist1.loc[common_dates, 'close']
        price2 = hist2.loc[common_dates, 'close']
        
        # 计算价差
        spread = price1 - price2
        spread_mean = spread.tail(self.lookback_period).mean()
        spread_std = spread.tail(self.lookback_period).std()
        current_spread = spread.iloc[-1]
        
        # 计算Z-score
        z_score = (current_spread - spread_mean) / spread_std if spread_std > 0 else 0
        
        return {
            'current_spread': current_spread,
            'mean_spread': spread_mean,
            'std_spread': spread_std,
            'z_score': z_score,
            'price1': price1.iloc[-1],
            'price2': price2.iloc[-1]
        }
    
    def execute_pairs_strategy(self):
        """执行配对交易策略"""
        print(f"\n🎯 Executing {self.name} on pair {self.pair}...")
        
        spread_info = self.calculate_spread()
        if spread_info is None:
            print("❌ Cannot calculate spread - insufficient data")
            return
        
        symbol1, symbol2 = self.pair
        z_score = spread_info['z_score']
        
        print(f"\n📊 Spread Analysis:")
        print(f"   Current spread: {spread_info['current_spread']:.2f}")
        print(f"   Mean spread: {spread_info['mean_spread']:.2f}")
        print(f"   Z-score: {z_score:.2f}")
        
        # 交易逻辑
        if abs(z_score) > self.entry_threshold:
            if z_score > 0:  # 价差过大，做空价差
                print(f"🔴 Spread too high - SHORT {symbol1}, LONG {symbol2}")
                # 卖出symbol1，买入symbol2
                investment = self.cash * 0.2  # 使用20%资金
                
                price1 = self.get_stock_price(symbol1)
                price2 = self.get_stock_price(symbol2)
                
                if price1 and price2:
                    amount1 = int(investment / price1 / 100) * 100
                    amount2 = int(investment / price2 / 100) * 100
                    
                    if symbol1 in self.positions and self.positions[symbol1] >= amount1:
                        self.sell_stock(symbol1, amount1)
                    
                    self.buy_stock(symbol2, amount2)
            
            else:  # 价差过小，做多价差
                print(f"🟢 Spread too low - LONG {symbol1}, SHORT {symbol2}")
                # 买入symbol1，卖出symbol2
                investment = self.cash * 0.2
                
                price1 = self.get_stock_price(symbol1)
                price2 = self.get_stock_price(symbol2)
                
                if price1 and price2:
                    amount1 = int(investment / price1 / 100) * 100
                    amount2 = int(investment / price2 / 100) * 100
                    
                    self.buy_stock(symbol1, amount1)
                    
                    if symbol2 in self.positions and self.positions[symbol2] >= amount2:
                        self.sell_stock(symbol2, amount2)
        
        elif abs(z_score) < self.exit_threshold:
            print(f"🔄 Spread normalized - Consider closing positions")
            # 平仓逻辑（简化版）
            for symbol in self.pair:
                if symbol in self.positions:
                    amount = self.positions[symbol] // 2  # 平掉一半仓位
                    if amount > 0:
                        self.sell_stock(symbol, amount)
        
        else:
            print(f"⏸️ Spread within normal range - HOLD")

def backtest_strategy(strategy: QuantitativeStrategy, 
                     symbols: List[str], 
                     days: int = 30):
    """
    简单的策略回测
    
    Args:
        strategy: 策略实例
        symbols: 股票代码列表
        days: 回测天数
    """
    print(f"\n📈 Backtesting {strategy.name} for {days} days...")
    
    initial_value = strategy.get_portfolio_value()
    
    # 模拟每日执行策略
    for day in range(days):
        print(f"\n--- Day {day + 1} ---")
        
        if isinstance(strategy, MomentumStrategy):
            strategy.execute_strategy(symbols)
        elif isinstance(strategy, PairsTradingStrategy):
            strategy.execute_pairs_strategy()
        
        # 显示当日组合状态
        status = strategy.get_portfolio_status()
        print(f"Portfolio Value: ¥{status['total_value']:,.0f} "
              f"(P&L: {status['profit_loss_percent']:+.2f}%)")
        
        # 模拟时间推进（实际应用中不需要）
        time.sleep(0.1)
    
    # 回测结果
    final_value = strategy.get_portfolio_value()
    total_return = (final_value - initial_value) / initial_value * 100
    
    print(f"\n📊 Backtest Results:")
    print(f"   Initial Value: ¥{initial_value:,.0f}")
    print(f"   Final Value: ¥{final_value:,.0f}")
    print(f"   Total Return: {total_return:+.2f}%")
    print(f"   Total Trades: {len(strategy.trade_history)}")

def real_time_monitoring(symbols: List[str], interval: int = 60):
    """
    实时监控示例
    
    Args:
        symbols: 监控的股票代码列表
        interval: 监控间隔（秒）
    """
    print(f"\n👁️ Real-time monitoring {len(symbols)} symbols (interval: {interval}s)")
    print("Press Ctrl+C to stop...")
    
    uds = UnifiedDataSource()
    
    try:
        while True:
            print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Market Update:")
            print("-" * 60)
            
            for symbol in symbols:
                try:
                    data = uds.get_realtime_price(symbol)
                    if data:
                        change_icon = "📈" if data['change'] > 0 else "📉" if data['change'] < 0 else "➡️"
                        print(f"{change_icon} {data['name']} ({data['symbol']}): "
                              f"¥{data['current_price']:.2f} "
                              f"({data['change']:+.2f}, {data['change_percent']:+.2f}%) "
                              f"Vol: {data['volume']:,} [{data['source']}]")
                    else:
                        print(f"❌ {symbol}: No data available")
                except Exception as e:
                    print(f"❌ {symbol}: Error - {e}")
            
            # 显示数据源统计
            stats = uds.get_usage_stats()
            print(f"\n📊 Cache hit rate: {stats['cache_hit_rate']:.1f}% | "
                  f"Available sources: {stats['available_sources']}/{stats['total_sources']}")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n⏹️ Monitoring stopped by user")

def ai_integration_example():
    """
    AI集成示例 - 展示如何为AI模型提供数据
    
    这个函数展示了如何将数据源模块与AI/机器学习模型集成
    """
    print("\n🤖 AI Integration Example")
    print("=" * 40)
    
    # 创建数据源实例
    uds = UnifiedDataSource()
    
    # 定义股票池
    stock_pool = ['000001', '000002', '600000', '600036', '000858']
    
    # 为AI模型准备特征数据
    features_data = []
    
    for symbol in stock_pool:
        try:
            # 获取实时数据
            realtime = uds.get_realtime_price(symbol)
            
            # 获取历史数据
            history = uds.get_history_data(symbol, period='1d')
            
            if realtime and history is not None and len(history) >= 20:
                # 计算技术指标
                sma_5 = history['close'].tail(5).mean()
                sma_20 = history['close'].tail(20).mean()
                volatility = history['close'].tail(20).std()
                
                # 构建特征向量
                features = {
                    'symbol': symbol,
                    'current_price': realtime['current_price'],
                    'change_percent': realtime['change_percent'],
                    'volume_ratio': realtime['volume'] / history['volume'].tail(20).mean(),
                    'sma_5': sma_5,
                    'sma_20': sma_20,
                    'price_to_sma5': realtime['current_price'] / sma_5,
                    'price_to_sma20': realtime['current_price'] / sma_20,
                    'volatility': volatility,
                    'rsi': calculate_rsi_simple(history['close']),
                    'data_quality': realtime['data_quality']
                }
                
                features_data.append(features)
                
                print(f"✅ {symbol}: Features extracted")
            else:
                print(f"❌ {symbol}: Insufficient data")
                
        except Exception as e:
            print(f"❌ {symbol}: Error - {e}")
    
    # 转换为DataFrame（适合机器学习）
    if features_data:
        df = pd.DataFrame(features_data)
        print(f"\n📊 Feature matrix shape: {df.shape}")
        print("\n📋 Sample features:")
        print(df.head())
        
        # 示例：简单的评分模型
        print("\n🎯 Simple scoring model results:")
        for _, row in df.iterrows():
            # 简单评分逻辑
            score = 0
            
            # 动量因子
            if row['price_to_sma5'] > 1.02:
                score += 1
            if row['price_to_sma20'] > 1.05:
                score += 1
            
            # 成交量因子
            if row['volume_ratio'] > 1.5:
                score += 1
            
            # RSI因子
            if 30 < row['rsi'] < 70:
                score += 1
            
            # 数据质量
            if row['data_quality'] == 'high':
                score += 1
            
            recommendation = "BUY" if score >= 4 else "HOLD" if score >= 2 else "SELL"
            print(f"   {row['symbol']}: Score {score}/5 - {recommendation}")
    
    else:
        print("❌ No valid feature data extracted")

def calculate_rsi_simple(prices: pd.Series, period: int = 14) -> float:
    """简单RSI计算"""
    if len(prices) < period + 1:
        return 50  # 默认中性值
    
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1] if not rsi.empty else 50

def main():
    """
    主函数：演示各种使用场景
    """
    print("🚀 China Stock Data Source - Quantitative Trading Examples")
    print("=" * 70)
    
    # 测试数据源连接
    print("\n1️⃣ Testing data source connections...")
    uds = UnifiedDataSource()
    test_results = uds.test_all_sources()
    
    available_count = sum(1 for result in test_results.values() 
                         if result['status'] == 'available')
    print(f"✅ {available_count}/{len(test_results)} data sources available")
    
    if available_count == 0:
        print("❌ No data sources available. Please check your network connection.")
        return
    
    # 定义测试股票池
    test_symbols = ['000001', '000002', '600000', '600036']
    
    print("\n2️⃣ Basic data retrieval examples...")
    
    # 基本数据获取示例
    for symbol in test_symbols[:2]:  # 只测试前两个
        try:
            # 实时数据
            realtime = get_realtime_price(symbol)
            if realtime:
                print(f"📊 {realtime['name']} ({symbol}): ¥{realtime['current_price']:.2f}")
            
            # 历史数据
            history = get_history_data(symbol, days=5)
            if history is not None:
                print(f"   📈 5-day history: {len(history)} records")
        except Exception as e:
            print(f"❌ Error with {symbol}: {e}")
    
    print("\n3️⃣ Momentum strategy example...")
    
    # 动量策略示例
    try:
        momentum_strategy = MomentumStrategy()
        momentum_strategy.execute_strategy(test_symbols[:2])
        
        status = momentum_strategy.get_portfolio_status()
        print(f"\n💰 Portfolio Status:")
        print(f"   Cash: ¥{status['cash']:,.0f}")
        print(f"   Positions: {len(status['positions'])}")
        print(f"   Total Value: ¥{status['total_value']:,.0f}")
        
    except Exception as e:
        print(f"❌ Momentum strategy error: {e}")
    
    print("\n4️⃣ Pairs trading strategy example...")
    
    # 配对交易策略示例
    try:
        pairs_strategy = PairsTradingStrategy(('000001', '600036'))
        pairs_strategy.execute_pairs_strategy()
        
    except Exception as e:
        print(f"❌ Pairs trading strategy error: {e}")
    
    print("\n5️⃣ AI integration example...")
    
    # AI集成示例
    try:
        ai_integration_example()
    except Exception as e:
        print(f"❌ AI integration error: {e}")
    
    print("\n6️⃣ Performance statistics...")
    
    # 性能统计
    stats = uds.get_usage_stats()
    print(f"📊 Total requests: {stats['total_requests']}")
    print(f"📊 Cache hit rate: {stats['cache_hit_rate']:.1f}%")
    print(f"📊 Error count: {stats['error_count']}")
    
    if stats['source_usage']:
        print("📊 Source usage:")
        for source, count in stats['source_usage'].items():
            print(f"   {source}: {count} requests")
    
    print("\n✅ All examples completed!")
    
    print("\n📚 Next Steps:")
    print("   1. Modify strategies according to your needs")
    print("   2. Add more technical indicators")
    print("   3. Implement risk management")
    print("   4. Add backtesting with historical data")
    print("   5. Integrate with your trading platform")
    
    # 可选：启动实时监控
    user_input = input("\n❓ Start real-time monitoring? (y/N): ")
    if user_input.lower() == 'y':
        try:
            real_time_monitoring(test_symbols[:2], interval=30)
        except Exception as e:
            print(f"❌ Real-time monitoring error: {e}")

if __name__ == "__main__":
    main()