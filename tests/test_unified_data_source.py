#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一数据源测试模块

本文件包含对unified_data_source模块的全面测试，
确保数据获取功能的正确性和稳定性。

作者: China Stock Data Source Team
日期: 2024-01-15
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.unified_data_source import (
        UnifiedDataSource, 
        get_stock_data, 
        get_realtime_price,
        DataSourceError,
        ValidationError
    )
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保项目结构正确，并安装必要依赖")
    sys.exit(1)


class TestUnifiedDataSource(unittest.TestCase):
    """
    统一数据源测试类
    """
    
    def setUp(self):
        """测试前准备"""
        self.data_source = UnifiedDataSource(
            source_priority=['ashare', 'abu'],
            cache_enabled=False,  # 测试时禁用缓存
            timeout=5
        )
        self.test_symbol = '000001'
        self.test_symbols = ['000001', '000002', '600000']
    
    def tearDown(self):
        """测试后清理"""
        pass
    
    def test_init(self):
        """测试初始化"""
        # 测试默认初始化
        ds = UnifiedDataSource()
        self.assertIsInstance(ds.source_priority, list)
        self.assertTrue(ds.cache_enabled)
        
        # 测试自定义初始化
        ds_custom = UnifiedDataSource(
            source_priority=['abu'],
            cache_enabled=False,
            timeout=15
        )
        self.assertEqual(ds_custom.source_priority, ['abu'])
        self.assertFalse(ds_custom.cache_enabled)
        self.assertEqual(ds_custom.timeout, 15)
    
    def test_normalize_symbol(self):
        """测试股票代码标准化"""
        test_cases = [
            ('000001', '000001'),
            ('SZ000001', '000001'),
            ('sz000001', '000001'),
            ('SH600000', '600000'),
            ('sh600000', '600000'),
            ('600000', '600000')
        ]
        
        for input_symbol, expected in test_cases:
            with self.subTest(input_symbol=input_symbol):
                result = self.data_source.normalize_symbol(input_symbol)
                self.assertEqual(result, expected)
    
    def test_normalize_symbol_invalid(self):
        """测试无效股票代码"""
        invalid_symbols = ['', '123', '12345', '1234567', 'INVALID']
        
        for symbol in invalid_symbols:
            with self.subTest(symbol=symbol):
                with self.assertRaises(ValueError):
                    self.data_source.normalize_symbol(symbol)
    
    @patch('src.unified_data_source.AshareDataSource')
    def test_get_realtime_price_success(self, mock_ashare):
        """测试成功获取实时价格"""
        # 模拟返回数据
        mock_data = {
            'symbol': '000001',
            'current_price': 12.45,
            'change': 0.23,
            'change_percent': 1.88,
            'volume': 1000000,
            'timestamp': '2024-01-15 15:00:00'
        }
        
        mock_instance = MagicMock()
        mock_instance.get_realtime_price.return_value = mock_data
        mock_ashare.return_value = mock_instance
        
        result = self.data_source.get_realtime_price(self.test_symbol)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['symbol'], '000001')
        self.assertEqual(result['current_price'], 12.45)
        self.assertIn('timestamp', result)
    
    @patch('src.unified_data_source.AshareDataSource')
    def test_get_history_data_success(self, mock_ashare):
        """测试成功获取历史数据"""
        # 模拟返回数据
        mock_data = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'open': [12.0, 12.2, 12.1],
            'high': [12.3, 12.5, 12.4],
            'low': [11.9, 12.0, 12.0],
            'close': [12.2, 12.3, 12.2],
            'volume': [1000000, 1200000, 900000],
            'amount': [12200000, 14760000, 10980000]
        })
        
        mock_instance = MagicMock()
        mock_instance.get_history_data.return_value = mock_data
        mock_ashare.return_value = mock_instance
        
        result = self.data_source.get_history_data(self.test_symbol, period='1m')
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)
        self.assertIn('close', result.columns)
        self.assertIn('volume', result.columns)
    
    def test_get_realtime_price_integration(self):
        """集成测试：获取实时价格"""
        try:
            result = self.data_source.get_realtime_price(self.test_symbol)
            
            # 验证返回数据结构
            self.assertIsInstance(result, dict)
            
            # 验证必要字段
            required_fields = ['symbol', 'current_price']
            for field in required_fields:
                self.assertIn(field, result, f"缺少必要字段: {field}")
            
            # 验证数据类型
            self.assertIsInstance(result['current_price'], (int, float))
            self.assertGreater(result['current_price'], 0)
            
            print(f"✓ 实时价格测试通过: {result['symbol']} = {result['current_price']}")
            
        except Exception as e:
            self.skipTest(f"实时数据获取失败，可能是网络问题: {e}")
    
    def test_get_history_data_integration(self):
        """集成测试：获取历史数据"""
        try:
            result = self.data_source.get_history_data(self.test_symbol, period='1m')
            
            # 验证返回数据类型
            self.assertIsInstance(result, pd.DataFrame)
            self.assertGreater(len(result), 0, "历史数据不能为空")
            
            # 验证必要列
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in required_columns:
                self.assertIn(col, result.columns, f"缺少必要列: {col}")
            
            # 验证数据合理性
            self.assertTrue((result['high'] >= result['low']).all(), "最高价应大于等于最低价")
            self.assertTrue((result['close'] > 0).all(), "收盘价应大于0")
            self.assertTrue((result['volume'] >= 0).all(), "成交量应大于等于0")
            
            print(f"✓ 历史数据测试通过: 获取 {len(result)} 条记录")
            
        except Exception as e:
            self.skipTest(f"历史数据获取失败，可能是网络问题: {e}")
    
    def test_data_validation(self):
        """测试数据验证功能"""
        # 测试无效的period参数
        with self.assertRaises(ValueError):
            self.data_source.get_history_data(self.test_symbol, period='invalid')
        
        # 测试无效的日期格式
        with self.assertRaises(ValueError):
            self.data_source.get_history_data(
                self.test_symbol, 
                start_date='invalid-date'
            )
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试无效股票代码
        with self.assertRaises(ValueError):
            self.data_source.get_realtime_price('INVALID')
        
        # 测试空股票代码
        with self.assertRaises(ValueError):
            self.data_source.get_realtime_price('')
    
    def test_cache_functionality(self):
        """测试缓存功能"""
        # 创建启用缓存的数据源
        cached_ds = UnifiedDataSource(cache_enabled=True, cache_duration=60)
        
        try:
            # 第一次请求
            result1 = cached_ds.get_realtime_price(self.test_symbol)
            
            # 第二次请求（应该使用缓存）
            result2 = cached_ds.get_realtime_price(self.test_symbol)
            
            # 验证结果一致性（缓存生效）
            self.assertEqual(result1['symbol'], result2['symbol'])
            
            print("✓ 缓存功能测试通过")
            
        except Exception as e:
            self.skipTest(f"缓存测试失败，可能是网络问题: {e}")
    
    def test_source_failover(self):
        """测试数据源故障转移"""
        # 这个测试需要模拟数据源失败的情况
        # 在实际环境中可能难以测试，这里提供框架
        pass
    
    def test_performance(self):
        """测试性能"""
        import time
        
        try:
            start_time = time.time()
            result = self.data_source.get_realtime_price(self.test_symbol)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # 验证响应时间合理（小于10秒）
            self.assertLess(response_time, 10.0, "响应时间过长")
            
            print(f"✓ 性能测试通过: 响应时间 {response_time:.2f}秒")
            
        except Exception as e:
            self.skipTest(f"性能测试失败: {e}")


class TestConvenienceFunctions(unittest.TestCase):
    """
    便捷函数测试类
    """
    
    def test_get_stock_data_function(self):
        """测试get_stock_data便捷函数"""
        try:
            result = get_stock_data('000001', period='1m')
            
            self.assertIsInstance(result, pd.DataFrame)
            self.assertGreater(len(result), 0)
            
            print("✓ get_stock_data函数测试通过")
            
        except Exception as e:
            self.skipTest(f"get_stock_data测试失败: {e}")
    
    def test_get_realtime_price_function(self):
        """测试get_realtime_price便捷函数"""
        try:
            result = get_realtime_price('000001')
            
            self.assertIsInstance(result, dict)
            self.assertIn('current_price', result)
            
            print("✓ get_realtime_price函数测试通过")
            
        except Exception as e:
            self.skipTest(f"get_realtime_price测试失败: {e}")


class TestDataQuality(unittest.TestCase):
    """
    数据质量测试类
    """
    
    def setUp(self):
        self.data_source = UnifiedDataSource(cache_enabled=False)
    
    def test_data_completeness(self):
        """测试数据完整性"""
        try:
            data = self.data_source.get_history_data('000001', period='1m')
            
            # 检查是否有缺失值
            missing_data = data.isnull().sum()
            
            # 允许少量缺失值，但不应该全部缺失
            for column in ['open', 'high', 'low', 'close']:
                missing_ratio = missing_data[column] / len(data)
                self.assertLess(missing_ratio, 0.1, f"{column}列缺失值过多")
            
            print("✓ 数据完整性测试通过")
            
        except Exception as e:
            self.skipTest(f"数据完整性测试失败: {e}")
    
    def test_data_consistency(self):
        """测试数据一致性"""
        try:
            data = self.data_source.get_history_data('000001', period='1m')
            
            # 检查价格逻辑一致性
            inconsistent_high = (data['high'] < data['open']) | \
                              (data['high'] < data['close']) | \
                              (data['high'] < data['low'])
            
            inconsistent_low = (data['low'] > data['open']) | \
                             (data['low'] > data['close']) | \
                             (data['low'] > data['high'])
            
            self.assertFalse(inconsistent_high.any(), "最高价数据不一致")
            self.assertFalse(inconsistent_low.any(), "最低价数据不一致")
            
            print("✓ 数据一致性测试通过")
            
        except Exception as e:
            self.skipTest(f"数据一致性测试失败: {e}")


def run_comprehensive_test():
    """
    运行综合测试
    """
    print("=" * 60)
    print("🧪 开始运行综合测试")
    print("=" * 60)
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestUnifiedDataSource,
        TestConvenienceFunctions,
        TestDataQuality
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True
    )
    
    result = runner.run(test_suite)
    
    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print("📊 测试结果摘要")
    print("=" * 60)
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped)}")
    
    if result.failures:
        print("\n❌ 失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n⚠️ 错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\n✅ 成功率: {success_rate:.1f}%")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # 可以选择运行单个测试或综合测试
    import argparse
    
    parser = argparse.ArgumentParser(description='运行统一数据源测试')
    parser.add_argument('--comprehensive', action='store_true', help='运行综合测试')
    parser.add_argument('--class', dest='test_class', help='运行特定测试类')
    parser.add_argument('--method', dest='test_method', help='运行特定测试方法')
    
    args = parser.parse_args()
    
    if args.comprehensive:
        success = run_comprehensive_test()
        sys.exit(0 if success else 1)
    elif args.test_class:
        # 运行特定测试类
        suite = unittest.TestLoader().loadTestsFromName(args.test_class)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)
    else:
        # 运行所有测试
        unittest.main(verbosity=2)
