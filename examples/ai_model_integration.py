#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI模型集成示例

本文件展示如何将股票数据源模块集成到各种AI应用中，
包括机器学习、深度学习和自然语言处理等场景。

作者: China Stock Data Source Team
日期: 2024-01-15
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 添加父目录到路径，以便导入模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.unified_data_source import UnifiedDataSource, get_stock_data, get_realtime_price
except ImportError:
    print("请确保已正确安装依赖包: pip install pandas requests numpy")
    sys.exit(1)


class AIStockDataProvider:
    """
    AI股票数据提供器
    
    专为AI应用设计的数据获取和预处理类，提供标准化的数据接口。
    """
    
    def __init__(self, cache_enabled=True):
        """初始化数据提供器"""
        self.data_source = UnifiedDataSource(cache_enabled=cache_enabled)
        self.cache = {}
    
    def get_ai_features(self, symbol, period='6m', include_technical=True):
        """
        获取AI模型所需的特征数据
        
        Args:
            symbol (str): 股票代码
            period (str): 数据周期
            include_technical (bool): 是否包含技术指标
            
        Returns:
            pd.DataFrame: 包含AI特征的数据框
        """
        try:
            # 获取基础历史数据
            data = self.data_source.get_history_data(symbol, period=period)
            
            if data is None or len(data) == 0:
                raise ValueError(f"无法获取 {symbol} 的历史数据")
            
            # 计算基础特征
            features = data.copy()
            
            # 价格相关特征
            features['price_change'] = features['close'].pct_change()
            features['price_range'] = (features['high'] - features['low']) / features['close']
            features['open_close_ratio'] = features['open'] / features['close']
            
            # 成交量特征
            features['volume_change'] = features['volume'].pct_change()
            features['volume_price_trend'] = features['volume'] * features['price_change']
            
            if include_technical:
                # 技术指标
                features = self._add_technical_indicators(features)
            
            # 移除无穷大和NaN值
            features = features.replace([np.inf, -np.inf], np.nan)
            features = features.fillna(method='ffill').fillna(0)
            
            return features
            
        except Exception as e:
            print(f"获取AI特征数据失败: {e}")
            return None
    
    def _add_technical_indicators(self, data):
        """
        添加技术指标
        
        Args:
            data (pd.DataFrame): 基础数据
            
        Returns:
            pd.DataFrame: 包含技术指标的数据
        """
        # 移动平均线
        data['ma5'] = data['close'].rolling(window=5).mean()
        data['ma10'] = data['close'].rolling(window=10).mean()
        data['ma20'] = data['close'].rolling(window=20).mean()
        
        # 布林带
        data['bb_middle'] = data['close'].rolling(window=20).mean()
        bb_std = data['close'].rolling(window=20).std()
        data['bb_upper'] = data['bb_middle'] + (bb_std * 2)
        data['bb_lower'] = data['bb_middle'] - (bb_std * 2)
        data['bb_width'] = (data['bb_upper'] - data['bb_lower']) / data['bb_middle']
        
        # RSI
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = data['close'].ewm(span=12).mean()
        exp2 = data['close'].ewm(span=26).mean()
        data['macd'] = exp1 - exp2
        data['macd_signal'] = data['macd'].ewm(span=9).mean()
        data['macd_histogram'] = data['macd'] - data['macd_signal']
        
        # 波动率
        data['volatility'] = data['close'].rolling(window=20).std()
        
        return data
    
    def get_market_sentiment(self, symbols, period='1m'):
        """
        获取市场情绪数据
        
        Args:
            symbols (list): 股票代码列表
            period (str): 数据周期
            
        Returns:
            dict: 市场情绪指标
        """
        sentiment_data = {
            'rising_stocks': 0,
            'falling_stocks': 0,
            'average_change': 0,
            'volume_weighted_change': 0,
            'market_strength': 0
        }
        
        changes = []
        volumes = []
        
        for symbol in symbols:
            try:
                price_data = self.data_source.get_realtime_price(symbol)
                if price_data and 'change_percent' in price_data:
                    change = price_data['change_percent']
                    volume = price_data.get('volume', 0)
                    
                    changes.append(change)
                    volumes.append(volume)
                    
                    if change > 0:
                        sentiment_data['rising_stocks'] += 1
                    elif change < 0:
                        sentiment_data['falling_stocks'] += 1
                        
            except Exception as e:
                print(f"获取 {symbol} 情绪数据失败: {e}")
                continue
        
        if changes:
            sentiment_data['average_change'] = np.mean(changes)
            
            # 成交量加权平均变化
            if sum(volumes) > 0:
                weighted_changes = [c * v for c, v in zip(changes, volumes)]
                sentiment_data['volume_weighted_change'] = sum(weighted_changes) / sum(volumes)
            
            # 市场强度 (上涨股票比例)
            total_stocks = sentiment_data['rising_stocks'] + sentiment_data['falling_stocks']
            if total_stocks > 0:
                sentiment_data['market_strength'] = sentiment_data['rising_stocks'] / total_stocks
        
        return sentiment_data


class MLModelIntegration:
    """
    机器学习模型集成类
    
    展示如何将股票数据集成到机器学习工作流中。
    """
    
    def __init__(self):
        self.data_provider = AIStockDataProvider()
        self.scaler = None
    
    def prepare_training_data(self, symbols, period='1y', target_days=5):
        """
        准备机器学习训练数据
        
        Args:
            symbols (list): 股票代码列表
            period (str): 数据周期
            target_days (int): 预测目标天数
            
        Returns:
            tuple: (X, y) 特征和标签
        """
        all_features = []
        all_targets = []
        
        for symbol in symbols:
            try:
                # 获取特征数据
                features = self.data_provider.get_ai_features(symbol, period=period)
                
                if features is None or len(features) < target_days + 20:
                    print(f"跳过 {symbol}: 数据不足")
                    continue
                
                # 选择特征列
                feature_columns = [
                    'price_change', 'price_range', 'volume_change',
                    'ma5', 'ma10', 'ma20', 'rsi', 'macd', 'volatility'
                ]
                
                # 确保所有特征列都存在
                available_features = [col for col in feature_columns if col in features.columns]
                
                if len(available_features) < 5:
                    print(f"跳过 {symbol}: 特征不足")
                    continue
                
                X = features[available_features].values
                
                # 创建目标变量 (未来N天的收益率)
                future_returns = features['close'].shift(-target_days) / features['close'] - 1
                y = future_returns.values
                
                # 移除NaN值
                valid_indices = ~(np.isnan(X).any(axis=1) | np.isnan(y))
                X_clean = X[valid_indices]
                y_clean = y[valid_indices]
                
                if len(X_clean) > 0:
                    all_features.append(X_clean)
                    all_targets.append(y_clean)
                    print(f"✓ {symbol}: {len(X_clean)} 个样本")
                
            except Exception as e:
                print(f"处理 {symbol} 数据失败: {e}")
                continue
        
        if not all_features:
            raise ValueError("没有有效的训练数据")
        
        # 合并所有数据
        X = np.vstack(all_features)
        y = np.hstack(all_targets)
        
        return X, y
    
    def create_prediction_features(self, symbol, lookback_days=30):
        """
        创建用于预测的特征
        
        Args:
            symbol (str): 股票代码
            lookback_days (int): 回看天数
            
        Returns:
            np.array: 预测特征
        """
        try:
            # 获取最近的数据
            features = self.data_provider.get_ai_features(symbol, period='3m')
            
            if features is None or len(features) < lookback_days:
                raise ValueError(f"数据不足，需要至少 {lookback_days} 天数据")
            
            # 选择最近的数据
            recent_features = features.tail(lookback_days)
            
            # 选择特征列
            feature_columns = [
                'price_change', 'price_range', 'volume_change',
                'ma5', 'ma10', 'ma20', 'rsi', 'macd', 'volatility'
            ]
            
            available_features = [col for col in feature_columns if col in recent_features.columns]
            X = recent_features[available_features].values
            
            # 移除NaN值
            X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
            
            return X
            
        except Exception as e:
            print(f"创建预测特征失败: {e}")
            return None


class NLPIntegration:
    """
    自然语言处理集成类
    
    展示如何将股票数据转换为文本描述，用于NLP模型。
    """
    
    def __init__(self):
        self.data_provider = AIStockDataProvider()
    
    def generate_stock_description(self, symbol):
        """
        生成股票的文本描述
        
        Args:
            symbol (str): 股票代码
            
        Returns:
            str: 股票描述文本
        """
        try:
            # 获取实时数据
            price_data = self.data_provider.data_source.get_realtime_price(symbol)
            
            if not price_data:
                return f"无法获取股票 {symbol} 的数据"
            
            # 获取历史数据用于趋势分析
            history = self.data_provider.get_ai_features(symbol, period='1m')
            
            # 构建描述
            description_parts = []
            
            # 基本信息
            current_price = price_data.get('current_price', 0)
            change_percent = price_data.get('change_percent', 0)
            
            if change_percent > 0:
                trend = "上涨"
                trend_desc = f"较昨日上涨 {change_percent:.2f}%"
            elif change_percent < 0:
                trend = "下跌"
                trend_desc = f"较昨日下跌 {abs(change_percent):.2f}%"
            else:
                trend = "平盘"
                trend_desc = "与昨日持平"
            
            description_parts.append(f"股票代码 {symbol} 当前价格为 {current_price:.2f} 元，{trend_desc}。")
            
            # 成交量分析
            volume = price_data.get('volume', 0)
            if volume > 0:
                if history is not None and len(history) > 5:
                    avg_volume = history['volume'].tail(5).mean()
                    if volume > avg_volume * 1.5:
                        volume_desc = "成交量显著放大"
                    elif volume < avg_volume * 0.5:
                        volume_desc = "成交量明显萎缩"
                    else:
                        volume_desc = "成交量正常"
                else:
                    volume_desc = "成交活跃"
                
                description_parts.append(f"今日{volume_desc}，成交量为 {volume:,} 股。")
            
            # 技术分析
            if history is not None and len(history) > 20:
                recent_data = history.tail(20)
                
                # RSI分析
                if 'rsi' in recent_data.columns:
                    current_rsi = recent_data['rsi'].iloc[-1]
                    if not np.isnan(current_rsi):
                        if current_rsi > 70:
                            rsi_desc = "技术指标显示超买状态"
                        elif current_rsi < 30:
                            rsi_desc = "技术指标显示超卖状态"
                        else:
                            rsi_desc = "技术指标处于正常区间"
                        
                        description_parts.append(f"{rsi_desc}，RSI为 {current_rsi:.1f}。")
                
                # 移动平均线分析
                if 'ma5' in recent_data.columns and 'ma20' in recent_data.columns:
                    ma5 = recent_data['ma5'].iloc[-1]
                    ma20 = recent_data['ma20'].iloc[-1]
                    
                    if not (np.isnan(ma5) or np.isnan(ma20)):
                        if current_price > ma5 > ma20:
                            ma_desc = "价格位于短期和长期均线之上，呈现上升趋势"
                        elif current_price < ma5 < ma20:
                            ma_desc = "价格位于短期和长期均线之下，呈现下降趋势"
                        else:
                            ma_desc = "价格与均线交织，趋势不明确"
                        
                        description_parts.append(f"{ma_desc}。")
            
            return " ".join(description_parts)
            
        except Exception as e:
            return f"生成股票 {symbol} 描述时出错: {e}"
    
    def generate_market_summary(self, symbols):
        """
        生成市场概况文本
        
        Args:
            symbols (list): 股票代码列表
            
        Returns:
            str: 市场概况文本
        """
        try:
            sentiment = self.data_provider.get_market_sentiment(symbols)
            
            summary_parts = []
            
            # 市场整体表现
            total_stocks = sentiment['rising_stocks'] + sentiment['falling_stocks']
            if total_stocks > 0:
                rising_ratio = sentiment['rising_stocks'] / total_stocks
                
                if rising_ratio > 0.6:
                    market_mood = "市场情绪乐观"
                elif rising_ratio < 0.4:
                    market_mood = "市场情绪谨慎"
                else:
                    market_mood = "市场情绪中性"
                
                summary_parts.append(f"今日{market_mood}，")
                summary_parts.append(f"在监控的 {total_stocks} 只股票中，")
                summary_parts.append(f"{sentiment['rising_stocks']} 只上涨，")
                summary_parts.append(f"{sentiment['falling_stocks']} 只下跌。")
            
            # 平均涨跌幅
            avg_change = sentiment.get('average_change', 0)
            if avg_change > 0:
                summary_parts.append(f"平均涨幅为 {avg_change:.2f}%。")
            elif avg_change < 0:
                summary_parts.append(f"平均跌幅为 {abs(avg_change):.2f}%。")
            else:
                summary_parts.append("整体表现平稳。")
            
            # 市场强度
            market_strength = sentiment.get('market_strength', 0)
            if market_strength > 0.7:
                strength_desc = "市场表现强劲"
            elif market_strength < 0.3:
                strength_desc = "市场表现疲弱"
            else:
                strength_desc = "市场表现平衡"
            
            summary_parts.append(f"{strength_desc}，投资者可关注个股机会。")
            
            return "".join(summary_parts)
            
        except Exception as e:
            return f"生成市场概况时出错: {e}"


def demo_ai_integration():
    """
    AI集成演示函数
    
    展示各种AI集成场景的使用方法。
    """
    print("=" * 60)
    print("🤖 AI模型集成演示")
    print("=" * 60)
    
    # 测试股票列表
    test_symbols = ['000001', '000002', '600000']
    
    # 1. AI数据提供器演示
    print("\n1️⃣ AI数据提供器演示")
    print("-" * 30)
    
    data_provider = AIStockDataProvider()
    
    for symbol in test_symbols[:1]:  # 只测试第一个股票
        print(f"\n📊 获取 {symbol} 的AI特征数据...")
        features = data_provider.get_ai_features(symbol, period='1m')
        
        if features is not None:
            print(f"✓ 成功获取 {len(features)} 条记录")
            print(f"✓ 特征维度: {features.shape[1]} 个特征")
            print(f"✓ 特征列: {list(features.columns[:10])}...")
        else:
            print("✗ 获取特征数据失败")
    
    # 2. 市场情绪分析演示
    print("\n2️⃣ 市场情绪分析演示")
    print("-" * 30)
    
    print("📈 分析市场情绪...")
    sentiment = data_provider.get_market_sentiment(test_symbols)
    
    print(f"✓ 上涨股票: {sentiment['rising_stocks']} 只")
    print(f"✓ 下跌股票: {sentiment['falling_stocks']} 只")
    print(f"✓ 平均变化: {sentiment['average_change']:.2f}%")
    print(f"✓ 市场强度: {sentiment['market_strength']:.2f}")
    
    # 3. 机器学习集成演示
    print("\n3️⃣ 机器学习集成演示")
    print("-" * 30)
    
    ml_integration = MLModelIntegration()
    
    print("🔬 准备机器学习训练数据...")
    try:
        X, y = ml_integration.prepare_training_data(test_symbols, period='3m')
        print(f"✓ 训练数据形状: X={X.shape}, y={y.shape}")
        print(f"✓ 特征统计: 均值={np.mean(X, axis=0)[:3]}, 标准差={np.std(X, axis=0)[:3]}")
        
        # 创建预测特征
        print("\n🎯 创建预测特征...")
        pred_features = ml_integration.create_prediction_features(test_symbols[0])
        if pred_features is not None:
            print(f"✓ 预测特征形状: {pred_features.shape}")
        
    except Exception as e:
        print(f"✗ 机器学习数据准备失败: {e}")
    
    # 4. NLP集成演示
    print("\n4️⃣ 自然语言处理集成演示")
    print("-" * 30)
    
    nlp_integration = NLPIntegration()
    
    # 生成股票描述
    print("📝 生成股票描述...")
    for symbol in test_symbols[:2]:  # 只测试前两个股票
        description = nlp_integration.generate_stock_description(symbol)
        print(f"\n📈 {symbol}:")
        print(f"   {description}")
    
    # 生成市场概况
    print("\n📊 生成市场概况...")
    market_summary = nlp_integration.generate_market_summary(test_symbols)
    print(f"\n🏢 市场概况:")
    print(f"   {market_summary}")
    
    print("\n" + "=" * 60)
    print("✅ AI集成演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    try:
        demo_ai_integration()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断演示")
    except Exception as e:
        print(f"\n\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
